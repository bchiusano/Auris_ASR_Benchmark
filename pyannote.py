# instantiate the pipeline
from pyannote.audio import Pipeline
from dotenv import load_dotenv
import os
import torchaudio
from pyannote.audio.pipelines.utils.hook import ProgressHook

load_dotenv()

pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
  use_auth_token=os.getenv("HF_TOKEN"))

directory = r"C:\Users\b.caissottidichiusan\OneDrive - Stichting Onderwijs Koninklijke Auris Groep - 01JO\Desktop\Audio"

for audio_file in os.listdir(directory):
      # run the pipeline on each audio file
      with ProgressHook() as hook:
        audio_file_path = os.path.join(directory, audio_file)
        waveform, sample_rate = torchaudio.load(audio_file_path)

        # Create resampler and apply if needed
        if sample_rate != 16000:
          resampler = torchaudio.transforms.Resample(sample_rate, 16000)
          waveform = resampler(waveform)
          sample_rate = 16000

        diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate}, hook=hook)


        # dump the diarization output to disk using RTTM format
        audio_file = audio_file.replace('.wav', '')
        if not os.path.exists("rttms"):
            os.makedirs("rttms")
        with open(f"rttms/{audio_file}.rttm", "w") as rttm:
            diarization.write_rttm(rttm)

# if there are reapeating speakers, you can merge them
# same for the transcripts - split when there is not the same speaker
