from pydub import AudioSegment
import pandas as pd
import ast

DEBUG = False
AT_LEAST_SIX = True

path_to_audio_files = "CHILDES Downloads/DutchAfrikaans/Asymmetries/CK-TD/"

data = pd.read_csv("csvs/correct_data.csv")

filenames = data['filename'].to_list()

all_metadata = pd.DataFrame(columns=["filename", "transcript"])
six_metadata = pd.DataFrame(columns=["filename", "transcript"])

for i in range(len(filenames)):

    # FILES
    file_name = filenames[i]
    print(file_name)

    # TRANSCRIPTS
    transcript = data['utterances'].iloc[i]
    transcript_list = ast.literal_eval(transcript)

    # TIMESTAMPS
    list_of_timestamps_str = data['timestamps'].iloc[i]
    timestamps_list = ast.literal_eval(list_of_timestamps_str)

    cleaned_name = file_name.replace(".cha", ".mp3")
    title_name = file_name.replace(".cha", "")

    # AUDIO
    audio_file = path_to_audio_files + cleaned_name
    if DEBUG: print(audio_file)

    audio = AudioSegment.from_mp3(audio_file)

    for pos in range(len(timestamps_list)):
        utterance = transcript_list[pos]

        stamp = timestamps_list[pos]
        start = int(stamp[0])
        end = int(stamp[1])
        audio_chunk = audio[start:end]

        if DEBUG:
            print("split at [{}:{}] ms".format(start, end))
            print(utterance)
            print(len(utterance.split()))

        new_row = pd.DataFrame(
            {"filename": ["audio_{name}_{s}_{e}.mp3".format(name=title_name, s=start, e=end)], "transcript": [utterance]})

        if AT_LEAST_SIX and len(utterance.split()) > 5:
            if DEBUG: print("at least SIX")
            audio_chunk.export(
                "datasets/correctDatasetSix/Asymmetries/audio_{name}_{s}_{e}.mp3".format(name=title_name, s=start, e=end),
                format="mp3")

            six_metadata = pd.concat([six_metadata, new_row], ignore_index=True)

        audio_chunk.export("datasets/correctDataset/Asymmetries/audio_{name}_{s}_{e}.mp3".format(name=title_name, s=start, e=end),
                           format="mp3")
        all_metadata = pd.concat([all_metadata, new_row], ignore_index=True)

all_metadata.to_csv("datasets/correctDataset/metadata.csv", index=False)
six_metadata.to_csv("datasets/correctDatasetSix/metadata.csv", index=False)