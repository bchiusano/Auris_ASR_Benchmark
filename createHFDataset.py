from pydub import AudioSegment
import pandas as pd
import ast

DEBUG = False
AT_LEAST_SIX = True

path_to_audio_files = "CHILDES Downloads/DutchAfrikaans/Asymmetries/CK-TD/"

data = pd.read_csv("datasets/wrong_data.csv")

filenames = data['filename'].to_list()

for i in range(len(filenames)):

    # FILES
    file_name = filenames[i]
    if DEBUG: print(file_name)

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

        if AT_LEAST_SIX and len(utterance.split()) > 6:
            if DEBUG: print("SIX")
            audio_chunk.export(
                "wrongDatasetSix/Asymmetries/audio_{name}_{s}_{e}.mp3".format(name=title_name, s=start, e=end),
                format="mp3")

        audio_chunk.export("wrongDataset/Asymmetries/audio_{name}_{s}_{e}.mp3".format(name=title_name, s=start, e=end),
                           format="mp3")
