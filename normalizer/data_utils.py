from datasets import load_dataset, Audio
from normalizer import BasicTextNormalizer

from .eval_utils import read_manifest, write_manifest

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
