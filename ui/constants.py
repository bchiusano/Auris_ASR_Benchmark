##########################
# Text definitions       #
##########################

TITLE = "<html> <head> <style> h1 {text-align: center;} </style> </head> <body> <h1> Dutch Child Speech Automatic Speech Recognition Leaderboard </b> </body> </html>"

INTRODUCTION_TEXT = """
## About 
The Dutch Child Speech ASR Leaderboard ranks and evaluates Dutch speech recognition models on the Hugging Face Hub. \
\n This leaderboard is highly inspired by the 🤗[Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) \
which currently only focuses on English speech recognition.
"""

AURIS_ORIGINAL_DESCRIPTION = """
## Koninklijke Auris Groep
[Auris](https://auris.nl/) provides assistance to anyone who has difficulty hearing, speaking, or speaking languages. \
Auris assesses, treats, supports, and provides education. Tailored to your needs. And for all ages. \
"""

METRICS_TEXT = """
## Metrics
The following explanations are derived from the 🤗[Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
"""

WER = """
### Word Error Rate - [WER](https://huggingface.co/spaces/evaluate-metric/wer) (⬇️ lower the better)
Word Error Rate is used to measure the **accuracy** of automatic speech recognition systems. It calculates the percentage 
of words in the system's output that differ from the reference (correct) transcript. **A lower WER value indicates higher accuracy**.
Consider:
* S = Substitution ("sit" instead of "sat")
* I = insertions (a new word)
* D = deletion (a word that is missing)
\nTo get our word error rate, we divide the total number of errors (S + I + D) by the total number of words in our
reference (N).
```
WER = (S + I + D) / N 
```
"""

RTFX = """
### Inverse Real Time Factor - [RTFx](https://github.com/NVIDIA/DeepLearningExamples/blob/master/Kaldi/SpeechRecognition/README.md#metrics) (⬆️ higher the better)
Inverse Real Time Factor is a measure of  the **latency** of automatic speech recognition systems, i.e. how long it takes an 
model to process a given amount of speech. It is defined as:
```
RTFx = (number of seconds of audio inferred) / (compute time in seconds)
``` 
Therefore, and RTFx of 1 means a system processes speech as fast as it's spoken, while an RTFx of 2 means it takes half the time. 
Thus, **a higher RTFx value indicates lower latency**.
"""

GITHUB_REPO = """
## Reproducing Results:
Head over to our github repo at: https://github.com/bchiusano/auris
"""

DATASETS = """
## Benchmark datasets
Evaluating Speech Recognition systems is a hard problem. We use the multi-dataset benchmarking strategy proposed in the 
[ESB paper](https://arxiv.org/abs/2210.13352) to obtain robust evaluation scores for each model.
ESB is a benchmark for evaluating the performance of a single automatic speech recognition (ASR) system across a broad 
set of speech datasets. It comprises eight English speech recognition datasets, capturing a broad range of domains, 
acoustic conditions, speaker styles, and transcription requirements. As such, it gives a better indication of how 
a model is likely to perform on downstream ASR compared to evaluating it on one dataset alone.
The ESB score is calculated as a macro-average of the WER scores across the ESB datasets. The models in the leaderboard
are ranked based on their average WER scores, from lowest to highest.
| Dataset                                                                                 | Domain                      | Speaking Style        | Train (h) | Dev (h) | Test (h) | Transcriptions     | License         |
|-----------------------------------------------------------------------------------------|-----------------------------|-----------------------|-----------|---------|----------|--------------------|-----------------|
| [LibriSpeech](https://huggingface.co/datasets/librispeech_asr)                          | Audiobook                   | Narrated              | 960       | 11      | 11       | Normalised         | CC-BY-4.0       |
| [VoxPopuli](https://huggingface.co/datasets/facebook/voxpopuli)                         | European Parliament         | Oratory               | 523       | 5       | 5        | Punctuated         | CC0             |
| [TED-LIUM](https://huggingface.co/datasets/LIUM/tedlium)                                | TED talks                   | Oratory               | 454       | 2       | 3        | Normalised         | CC-BY-NC-ND 3.0 |
| [GigaSpeech](https://huggingface.co/datasets/speechcolab/gigaspeech)                    | Audiobook, podcast, YouTube | Narrated, spontaneous | 2500      | 12      | 40       | Punctuated         | apache-2.0      |
| [SPGISpeech](https://huggingface.co/datasets/kensho/spgispeech)                         | Financial meetings          | Oratory, spontaneous  | 4900      | 100     | 100      | Punctuated & Cased | User Agreement  |
| [Earnings-22](https://huggingface.co/datasets/revdotcom/earnings22)                     | Financial meetings          | Oratory, spontaneous  | 105       | 5       | 5        | Punctuated & Cased | CC-BY-SA-4.0    |
| [AMI](https://huggingface.co/datasets/edinburghcstr/ami)                                | Meetings                    | Spontaneous           | 78        | 9       | 9        | Punctuated & Cased | CC-BY-4.0       |
For more details on the individual datasets and how models are evaluated to give the ESB score, refer to the [ESB paper](https://arxiv.org/abs/2210.13352).
"""