from datasets import Dataset, Audio
from pydub import AudioSegment
import pandas as pd
import ast
import os
import re



def save(age_group, group, hf_audios, hf_titles, audio_utterances):
    audio_dataset = Dataset.from_dict({"audio": hf_audios,
                                       "file_name": hf_titles,
                                       "transcript": audio_utterances}).cast_column("audio", Audio())
    audio_dataset.save_to_disk(f"aurisTests/{age_group}_{group}_dataset")



class CreateHFData:
    def __init__(self, data_csv, audio_input, audio_output, metadata_output, debug):
        self.data_csv = data_csv
        self.audio_input = audio_input
        self.audio_output = audio_output
        self.metadata_output = metadata_output
        self.debug = debug

    def split_audio(self):

        all_audio_utterances = []

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
            cleaned_name = file_name + ".wav"

            # AUDIO
            audio_file = os.path.join(self.audio_input, cleaned_name)

            if self.debug: print(audio_file)

            audio = AudioSegment.from_wav(audio_file)
            audio_duration = len(audio)
            
            iterativelistlen = len(timestamps_list)
            if len(transcript_list) < len(timestamps_list):
                iterativelistlen = len(transcript_list)

            for pos in range(iterativelistlen):

                utterance = transcript_list[pos]

                stamp = timestamps_list[pos]
                start = int(stamp[0])
                end = int(stamp[1])

                audio_chunk = audio[start:end]

                save_title = "audio_{name}_{s}_{e}.wav".format(name=file_name, s=start, e=end)

                # skip invalid ranges
                if start >= end or end > audio_duration or (end - start) < 100:
                    if self.debug:
                        print(f"Skipping zero-length segment: {start}-{end}")
                        print(f"Skipping out-of-bounds segment: {start}-{end} > {audio_duration}")
                        print(f"Skipping too-short segment ({end - start} ms): {start}-{end}")
                    continue


                path_to_audio = (self.audio_output + save_title)

                if not os.path.exists(path_to_audio):
                    audio_chunk.export(path_to_audio, format="wav")
                
                
                hf_audios.append(path_to_audio)
                hf_titles.append(save_title.replace(".wav", ""))
                all_audio_utterances.append(utterance)

       

        return hf_audios, hf_titles, all_audio_utterances


    def add_metadata(self, all_audio_names, all_audio_utterances):

        all_metadata = pd.DataFrame(columns=["file_name", "transcript"])

        all_metadata['file_name'] = all_audio_names
        all_metadata['transcript'] = all_audio_utterances

        all_metadata.to_csv(self.metadata_output + "metadata.csv", index=False)


# THINGS TO CHANGE BASED ON WHAT DATASET TO UPLOAD - CK-TD, SK-TD, SK-ADHD
path_to_audio_files = r"C:\Users\b.caissottidichiusan\OneDrive - Stichting Onderwijs Koninklijke Auris Groep - 01JO\Desktop\TOS-6yo\Audio"
csv_data = r".\rttms\csvs\TOS6.csv"
paths_audio_output = "auris_splits/TOS6/"

age = "6yo"
group = "TOS"



data = pd.read_csv(csv_data)

create_database = CreateHFData(data_csv=data,
                                audio_input = path_to_audio_files,
                                audio_output=paths_audio_output,
                                metadata_output=paths_audio_output,
                                debug=True)

#audios, names, transcripts = create_database.split_audio()
#create_database.add_metadata(names, transcripts)
# AFTER THIS MANUALLY CHECK THE METADATA AND ALIGN TRANSCRIPTS TO FILES


manual_csv = pd.read_csv("tos6manual.csv")
filenames = manual_csv['file_name'].to_list()

m_audios = []
m_names = []
m_transcripts = []

for i in range(len(filenames)):
    file = filenames[i]
    path_to_audio = (paths_audio_output + file + ".wav")
    transcript = manual_csv['transcript'].iloc[i]

    # make all transcripts lowercase and remove extra spaces and punctuation
    transcript = transcript.lower().strip()
    transcript = re.sub(r'[^\w\s]', '', transcript)


    m_audios.append(path_to_audio)
    m_names.append(file)    
    m_transcripts.append(transcript)

print(len(m_audios), len(m_names), len(m_transcripts))
print(m_transcripts[:10])
print(m_names[:10])
save(age_group=age, group=group, hf_audios=m_audios, hf_titles=m_names, audio_utterances=m_transcripts)

