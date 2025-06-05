import datasets

from datasets import Dataset, Audio, DatasetInfo
from pydub import AudioSegment
import pandas as pd
import ast
import os
import sys


def upload(hf_audios, hf_titles, six_audio_utterances):

    audio_dataset = Dataset.from_dict(
        {"audio": hf_audios, "file_name": hf_titles, "transcript": six_audio_utterances}).cast_column("audio",
                                                                                                      Audio())
    audio_dataset.push_to_hub("bchiusano/WrongPatternsCHILDES")


class CreateHFData:
    def __init__(self, path_audio, data_csv, audio_output, metadata_output, debug):
        self.path_audio = path_audio
        self.data_csv = data_csv
        self.audio_output = audio_output
        self.metadata_output = metadata_output
        self.debug = debug

    def split_audio(self):

        all_audio_names = []
        six_audio_names = []
        all_audio_utterances = []
        six_audio_utterances = []

        hf_audios = []
        hf_titles = []

        filenames = self.data_csv['filename'].to_list()

        for i in range(len(filenames)):
            # FILES
            file_name = filenames[i]

            # TRANSCRIPTS
            transcripts = self.data_csv['utterances'].iloc[i]
            transcript_list = ast.literal_eval(transcripts)

            # TIMESTAMPS
            list_of_timestamps_str = self.data_csv['timestamps'].iloc[i]
            timestamps_list = ast.literal_eval(list_of_timestamps_str)

            # AUDIO NAMING
            cleaned_name = file_name.replace(".cha", ".mp3")
            title_name = file_name.replace(".cha", "")

            # AUDIO
            audio_file = path_to_audio_files + cleaned_name

            if self.debug: print(audio_file)

            audio = AudioSegment.from_mp3(audio_file)

            for pos in range(len(timestamps_list)):

                utterance = transcript_list[pos]

                stamp = timestamps_list[pos]
                start = int(stamp[0])
                end = int(stamp[1])
                audio_chunk = audio[start:end]

                # new_row = pd.DataFrame(
                #    {"file_name": ["audio_{name}_{s}_{e}.mp3".format(name=title_name, s=start, e=end)],
                #     "transcript": [utterance]})

                save_title = "audio_{name}_{s}_{e}.mp3".format(name=title_name, s=start, e=end)

                if len(utterance.split()) > 5:
                    path_to_audio = (self.audio_output + save_title).format(six="Six")
                    #audio_chunk.export((self.audio_output + save_title).format(six="Six"), format="mp3")

                    six_audio_names.append(save_title)
                    hf_audios.append(path_to_audio)
                    hf_titles.append(cleaned_name)
                    six_audio_utterances.append(utterance)
                    # six_metadata = pd.concat([six_metadata, new_row], ignore_index=True)

                #audio_chunk.export((self.audio_output + save_title).format(six=""), format="mp3")
                # all_metadata = pd.concat([all_metadata, new_row], ignore_index=True)
                all_audio_names.append(save_title)
                all_audio_utterances.append(utterance)

        #self.add_metadata(all_audio_names, all_audio_utterances, six_audio_names, six_audio_utterances)

        return hf_audios, hf_titles, six_audio_utterances

    def add_metadata(self, all_audio_names, all_audio_utterances, six_audio_names, six_audio_utterances):

        all_metadata = pd.DataFrame(columns=["file_name", "transcript"])
        six_metadata = pd.DataFrame(columns=["file_name", "transcript"])

        all_metadata['file_name'] = all_audio_names
        all_metadata['transcript'] = all_audio_utterances

        all_metadata.to_csv((self.metadata_output + "metadata.csv").format(six=""), index=False)

        six_metadata['file_name'] = six_audio_names
        six_metadata['transcript'] = six_audio_utterances
        six_metadata.to_csv((self.metadata_output + "metadata.csv").format(six="Six"), index=False)


path_to_audio_files = "CHILDES Downloads/DutchAfrikaans/Asymmetries/CK-TD/"
path_to_audio_output = "datasets/wrongDataset{six}/Asymmetries/"
path_to_metadata_output = "datasets/wrongDataset{six}/"

data = pd.read_csv("csvs/wrong_data.csv")

create_database = CreateHFData(path_audio=path_to_audio_output,
                               data_csv=data,
                               audio_output=path_to_audio_output,
                               metadata_output=path_to_metadata_output,
                               debug=True)

audios, names, transcripts = create_database.split_audio()

upload(hf_audios=audios, hf_titles=names, six_audio_utterances=transcripts)