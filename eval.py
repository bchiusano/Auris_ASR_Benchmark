import os
import glob
import json
import evaluate
import pandas as pd
from collections import defaultdict
import re
import unicodedata
from fractions import Fraction
from typing import Iterator, List, Match, Optional, Union
import regex
from datasets import load_dataset, Audio
import os
import time
from tqdm import tqdm
from transformers import WhisperForConditionalGeneration, WhisperProcessor
import torch
from evaluate import load
from types import SimpleNamespace


def read_manifest(manifest_path: str):
    """
    Reads a manifest file (jsonl format) and returns a list of dictionaries containing samples.
    """
    data = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            if len(line) > 0:
                datum = json.loads(line)
                data.append(datum)
    return data


def write_manifest(
        references: list,
        transcriptions: list,
        model_id: str,
        dataset_path: str,
        dataset_name: str,
        audio_length: list = None,
        transcription_time: list = None,
):
    """
    Writes a manifest file (jsonl format) and returns the path to the file.

    Args:
        references: Ground truth reference texts.
        transcriptions: Model predicted transcriptions.
        model_id: String identifier for the model.
        dataset_path: Path to the dataset.
        dataset_name: Name of the dataset.
        audio_length: Length of each audio sample in seconds.
        transcription_time: Transcription time of each sample in seconds.

    Returns:
        Path to the manifest file.
    """
    model_id = model_id.replace("/", "-")
    dataset_path = dataset_path.replace("/", "-")
    dataset_name = dataset_name.replace("/", "-")

    if len(references) != len(transcriptions):
        raise ValueError(
            f"The number of samples in `references` ({len(references)}) "
            f"must match `transcriptions` ({len(transcriptions)})."
        )

    if audio_length is not None and len(audio_length) != len(references):
        raise ValueError(
            f"The number of samples in `audio_length` ({len(audio_length)}) "
            f"must match `references` ({len(references)})."
        )
    if transcription_time is not None and len(transcription_time) != len(references):
        raise ValueError(
            f"The number of samples in `transcription_time` ({len(transcription_time)}) "
            f"must match `references` ({len(references)})."
        )

    audio_length = (
        audio_length if audio_length is not None else len(references) * [None]
    )
    transcription_time = (
        transcription_time
        if transcription_time is not None
        else len(references) * [None]
    )

    basedir = "./results/clean/"
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    manifest_path = os.path.join(
        basedir, f"MODEL_{model_id}_DATASET_{dataset_path}_{dataset_name}.jsonl"
    )

    with open(manifest_path, "w", encoding="utf-8") as f:
        for idx, (text, transcript, audio_length, transcription_time) in enumerate(
                zip(references, transcriptions, audio_length, transcription_time)
        ):
            datum = {
                "audio_filepath": f"sample_{idx}",  # dummy value for Speech Data Processor
                "duration": audio_length,
                "time": transcription_time,
                "text": text,
                "pred_text": transcript,
            }
            f.write(f"{json.dumps(datum, ensure_ascii=False)}\n")
    return manifest_path


def score_results(directory: str, model_id: str = None):
    """
    Scores all result files in a directory and returns a composite score over all evaluated datasets.

    Args:
        directory: Path to the result directory, containing one or more jsonl files.
        model_id: Optional, model name to filter out result files based on model name.

    Returns:
        Composite score over all evaluated datasets and a dictionary of all results.
    """

    # Strip trailing slash
    if directory.endswith(os.pathsep):
        directory = directory[:-1]

    # Find all result files in the directory
    result_files = list(glob.glob(f"{directory}/**/*.jsonl", recursive=True))
    result_files = list(sorted(result_files))

    # Filter files belonging to a specific model id
    if model_id is not None and model_id != "":
        print("Filtering models by id:", model_id)
        model_id = model_id.replace("/", "-")
        result_files = [fp for fp in result_files if model_id in fp]

    # Check if any result files were found
    if len(result_files) == 0:
        raise ValueError(f"No result files found in {directory}")

    # Utility function to parse the file path and extract model id, dataset path, dataset name and split
    def parse_filepath(fp: str):
        model_index = fp.find("MODEL_")
        fp = fp[model_index:]
        ds_index = fp.find("DATASET_")
        model_id = fp[:ds_index].replace("MODEL_", "").rstrip("_")
        author_index = model_id.find("-")
        model_id = model_id[:author_index] + "/" + model_id[author_index + 1:]

        ds_fp = fp[ds_index:]
        dataset_id = ds_fp.replace("DATASET_", "").rstrip(".jsonl")
        return model_id, dataset_id

    # Compute WER results per dataset, and RTFx over all datasets
    results = {}
    wer_metric = evaluate.load("wer")

    for result_file in result_files:
        manifest = read_manifest(result_file)
        model_id_of_file, dataset_id = parse_filepath(result_file)

        references = [datum["text"] for datum in manifest]
        predictions = [datum["pred_text"] for datum in manifest]

        time = [datum["time"] for datum in manifest]
        duration = [datum["duration"] for datum in manifest]
        compute_rtfx = all(time) and all(duration)

        wer = wer_metric.compute(references=references, predictions=predictions)
        wer = round(100 * wer, 2)

        if compute_rtfx:
            audio_length = sum(duration)
            inference_time = sum(time)
            rtfx = round(sum(duration) / sum(time), 4)
        else:
            audio_length = inference_time = rtfx = None

        result_key = f"{model_id_of_file} | {dataset_id}"
        results[result_key] = {"wer": wer, "audio_length": audio_length, "inference_time": inference_time, "rtfx": rtfx}

    print("*" * 80)
    print("Results per dataset:")
    print("*" * 80)

    for k, v in results.items():
        metrics = f"{k}: WER = {v['wer']:0.2f} %"
        if v["rtfx"] is not None:
            metrics += f", RTFx = {v['rtfx']:0.2f}"
        print(metrics)

    # composite WER should be computed over all datasets and with the same key
    composite_wer = defaultdict(float)
    composite_audio_length = defaultdict(float)
    composite_inference_time = defaultdict(float)
    count_entries = defaultdict(int)
    for k, v in results.items():
        key = k.split("|")[0].strip()
        composite_wer[key] += v["wer"]
        if v["rtfx"] is not None:
            composite_audio_length[key] += v["audio_length"]
            composite_inference_time[key] += v["inference_time"]
        else:
            composite_audio_length[key] = composite_inference_time[key] = None
        count_entries[key] += 1

    # normalize scores & print
    print()
    print("*" * 80)
    print("Composite Results:")
    print("*" * 80)
    for k, v in composite_wer.items():
        wer = v / count_entries[k]
        print(f"{k}: WER = {wer:0.2f} %")
    for k in composite_audio_length:
        if composite_audio_length[k] is not None:
            rtfx = composite_audio_length[k] / composite_inference_time[k]
            print(f"{k}: RTFx = {rtfx:0.2f}")
    print("*" * 80)
    return composite_wer, results


# non-ASCII letters that are not separated by "NFKD" normalization
ADDITIONAL_DIACRITICS = {
    "œ": "oe",
    "Œ": "OE",
    "ø": "o",
    "Ø": "O",
    "æ": "ae",
    "Æ": "AE",
    "ß": "ss",
    "ẞ": "SS",
    "đ": "d",
    "Đ": "D",
    "ð": "d",
    "Ð": "D",
    "þ": "th",
    "Þ": "th",
    "ł": "l",
    "Ł": "L",
}


def remove_symbols_and_diacritics(s: str, keep=""):
    """
    Replace any other markers, symbols, and punctuations with a space, and drop any diacritics (category 'Mn' and some
    manual mappings)
    """

    def replace_character(char):
        if char in keep:
            return char
        elif char in ADDITIONAL_DIACRITICS:
            return ADDITIONAL_DIACRITICS[char]

        elif unicodedata.category(char) == "Mn":
            return ""

        elif unicodedata.category(char)[0] in "MSP":
            return " "

        return char

    return "".join(replace_character(c) for c in unicodedata.normalize("NFKD", s))


def remove_symbols(s: str):
    """
    Replace any other markers, symbols, punctuations with a space, keeping diacritics
    """
    return "".join(" " if unicodedata.category(c)[0] in "MSP" else c for c in unicodedata.normalize("NFKC", s))


class BasicTextNormalizer:
    def __init__(self, remove_diacritics: bool = False, split_letters: bool = False):
        self.clean = remove_symbols_and_diacritics if remove_diacritics else remove_symbols
        self.split_letters = split_letters

    def __call__(self, s: str):
        s = s.lower()
        s = re.sub(r"[<\[][^>\]]*[>\]]", "", s)  # remove words between brackets
        s = re.sub(r"\(([^)]+?)\)", "", s)  # remove words between parenthesis
        s = self.clean(s).lower()

        if self.split_letters:
            s = " ".join(regex.findall(r"\X", s, regex.U))

        s = re.sub(r"\s+", " ", s)  # replace any successive whitespace characters with a space

        return s


normalizer = BasicTextNormalizer()


def normalize(batch):
    batch["norm_text"] = normalizer(batch["transcript"])
    return batch


def load_data(args):
    dataset = load_dataset(
        args.dataset_path,
        args.dataset,
        token=True,
    )

    return dataset


def prepare_data(dataset):
    # Step 1: Resample audio
    dataset = dataset['train'].cast_column("audio", Audio(sampling_rate=16_000))

    # Step 3: Normalize transcripts (optional)
    dataset = dataset.map(normalize)

    return dataset


def benchmark(batch):
    # Load audio inputs
    audios = [audio["array"] for audio in batch["audio"]]
    batch["audio_length_s"] = [len(audio["array"]) / 16000 for audio in batch["audio"]]
    minibatch_size = len(audios)

    # START TIMING
    start_time = time.time()

    # 1. Pre-Processing
    # Padding
    padding_size = None
    if minibatch_size != args.batch_size:
        padding_size = args.batch_size - minibatch_size
        padding_audios = [audios[-1] for _ in range(padding_size)]
        audios.extend(padding_audios)

    # Standard Whisper processing: pad audios to 30-seconds and converted to log-mel
    inputs = processor(audios, sampling_rate=16_000, return_tensors="pt")

    # 2. Model Inference
    input_features = inputs.input_features
    attention_mask = inputs.get("attention_mask")

    with torch.no_grad():
        #predicted_ids = model.generate(input_features.to("cuda"), task="transcribe", language="nl",
         #                              attention_mask=attention_mask)
        predicted_ids = model.generate(input_features, task="transcribe", language="nl",
                                       attention_mask=attention_mask)

    # Remove the padding
    if padding_size is not None:
        predicted_ids = predicted_ids[:-padding_size, ...]

    # Convert token ids to text transcription
    # DECODE OR BATCH DECODE?
    pred_text = processor.batch_decode(predicted_ids, skip_special_tokens=True)

    # END TIMING
    runtime = time.time() - start_time

    # normalize by minibatch size since we want the per-sample time
    batch["transcription_time_s"] = minibatch_size * [runtime / minibatch_size]

    # normalize transcriptions with English normalizer
    batch["predictions"] = [normalizer(pred) for pred in pred_text]
    batch["references"] = batch["norm_text"]
    return batch


# Constants
wer_metric = load("wer")

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
processor = WhisperProcessor.from_pretrained("openai/whisper-small")


# CK-TD, SK-TD, SK-ADHD
all_subsets = ["CK-TD-W-S", "CK-TD-C-S", "SK-TD-W-S", "SK-TD-C-S", "SK-ADHD-W-S", "SK-ADHD-C-S"]

for subset in all_subsets:

    args = SimpleNamespace(
        model_id="openai/whisper-small",
        dataset_path="bchiusano/CleanAsymmetriesCHILDES",
        dataset=subset,
        batch_size=16,
        streaming=False,
    )

    print("evaluating subset: ", subset)
    dataset = load_data(args)
    dataset = prepare_data(dataset)

    results = dataset.map(
        benchmark, batch_size=args.batch_size, batched=True, remove_columns=["audio"],
    )

    # Post-processing - delete weird results
    del_idx = []
    for i in range(len(results)):
        reference = results[i]['references'].split()
        prediction = results[i]['predictions'].split()

        if len(prediction) > 2 * len(reference):
            del_idx.append(i)

    results = results.select(
        (
            i for i in range(len(results))
            if i not in set(del_idx)
        )
    )

    all_results = {
        "audio_length_s": [],
        "transcription_time_s": [],
        "predictions": [],
        "references": [],
    }
    result_iter = iter(results)
    for result in tqdm(result_iter, desc="Samples..."):
        for key in all_results:
            all_results[key].append(result[key])

    # Write manifest results (WER and RTFX)
    manifest_path = write_manifest(
        all_results["references"],
        all_results["predictions"],
        args.model_id,
        args.dataset_path,
        args.dataset,
        audio_length=all_results["audio_length_s"],
        transcription_time=all_results["transcription_time_s"],
    )
    print("Results saved at path:", os.path.abspath(manifest_path))

    wer = wer_metric.compute(
        references=all_results["references"], predictions=all_results["predictions"]
    )
    wer = round(100 * wer, 2)
    rtfx = round(sum(all_results["audio_length_s"]) / sum(all_results["transcription_time_s"]), 2)
    print("WER:", wer, "%", "RTFx:", rtfx)