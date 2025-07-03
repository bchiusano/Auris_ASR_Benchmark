import os
import time
from tqdm import tqdm
from transformers import WhisperForConditionalGeneration, WhisperProcessor
import torch
from evaluate import load
from types import SimpleNamespace
from normalizer import data_utils

wer_metric = load("wer")
MIN_DURATION_IN_SECONDS = 3.0


def main(args):
    model = WhisperForConditionalGeneration.from_pretrained(args.model_id).to("cuda")
    processor = WhisperProcessor.from_pretrained(args.model_id)

    # forced_decoder_ids = processor.get_decoder_prompt_ids(language="dutch", task="transcribe")

    def is_audio_length_in_range(input_length):
        return input_length > MIN_DURATION_IN_SECONDS

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
            predicted_ids = model.generate(input_features.to("cuda"), task="transcribe", language="nl",
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
        batch["predictions"] = [data_utils.normalizer(pred) for pred in pred_text]
        batch["references"] = batch["norm_text"]
        return batch

    # Load data
    dataset = data_utils.load_data(args)
    dataset = data_utils.prepare_data(dataset)

    # dataset = dataset.filter(is_audio_length_in_range, input_columns=["input_length"])

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
    manifest_path = data_utils.write_manifest(
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


if __name__ == "__main__":
    args = SimpleNamespace(
        model_id="openai/whisper-medium",
        dataset_path="bchiusano/NewAsymmetriesCHILDES",
        dataset="wrongPatternsSix",
        excel_output="results_wrongPatternsSix.xlsx",
        batch_size=16,
    )

    args.streaming = False

    main(args)
