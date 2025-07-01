import datasets

from datasets import Dataset, Audio, DatasetInfo
from pydub import AudioSegment
import pandas as pd
import ast
import os
import sys


def upload(dataset_repo, subset_name, hf_audios, hf_titles, audio_utterances):
    audio_dataset = Dataset.from_dict({"audio": hf_audios,
                                       "file_name": hf_titles,
                                       "transcript": audio_utterances}).cast_column("audio", Audio())
    audio_dataset.push_to_hub(dataset_repo, subset_name)


class CreateHFData:
    def __init__(self, data_csv, audio_output, metadata_output, debug):
        self.data_csv = data_csv
        self.audio_output = audio_output
        self.metadata_output = metadata_output
        self.debug = debug

    def split_audio(self):

        all_audio_names = []
        six_audio_names = []
        all_audio_utterances = []
        six_audio_utterances = []

        hf_audios_all = []
        hf_titles_all = []
        hf_audios_six = []
        hf_titles_six = []

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

                save_title = "audio_{name}_{s}_{e}.mp3".format(name=title_name, s=start, e=end)

                if title_name == "c21":
                    print(utterance)
                    print(start)
                    print(end)
                    print(save_title)

                if len(utterance.split()) > 5:
                    path_to_audio = (self.audio_output + save_title).format(six="Six")
                    # audio_chunk.export(path_to_audio, format="mp3")

                    six_audio_names.append(save_title)
                    six_audio_utterances.append(utterance)
                    hf_audios_six.append(path_to_audio)
                    hf_titles_six.append(cleaned_name)

                path_to_audio = (self.audio_output + save_title).format(six="")
                # audio_chunk.export(path_to_audio, format="mp3")
                all_audio_names.append(save_title)
                all_audio_utterances.append(utterance)
                hf_audios_all.append(path_to_audio)
                hf_titles_all.append(cleaned_name)

        # self.add_metadata(all_audio_names, all_audio_utterances, six_audio_names, six_audio_utterances)

        return hf_audios_all, hf_titles_all, all_audio_utterances, hf_audios_six, hf_titles_six, six_audio_utterances

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
paths_to_data = ["csvs/wrong_data.csv", "csvs/correct_data.csv"]
paths_audio_output = ["datasets/wrongDataset{six}/Asymmetries/", "datasets/correctDataset{six}/Asymmetries/"]
paths_metadata_output = ["datasets/wrongDataset{six}/", "datasets/correctDataset{six}/"]
subsets = [["wrongPatterns", "wrongPatternsSix"], ["correctPatterns", "correctPatternsSix"]]

hf_dataset_repo = "bchiusano/AsymmetriesCHILDES"

for i in range(len(paths_to_data)):
    data = pd.read_csv(paths_to_data[i])
    path_to_audio_output = paths_audio_output[i]
    path_to_metadata_output = paths_metadata_output[i]
    subset = subsets[i]

    create_database = CreateHFData(data_csv=data,
                                   audio_output=path_to_audio_output,
                                   metadata_output=path_to_metadata_output,
                                   debug=False)

    audios, names, transcripts, audios_six, names_six, transcripts_six = create_database.split_audio()

    # upload(dataset_repo=hf_dataset_repo, subset_name=subset[0], hf_audios=audios, hf_titles=names,
    #       audio_utterances=transcripts)
    # upload(dataset_repo=hf_dataset_repo, subset_name=subset[1], hf_audios=audios_six, hf_titles=names_six,
    #       audio_utterances=transcripts_six)
