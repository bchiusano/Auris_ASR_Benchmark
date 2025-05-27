import pandas as pd
import sys
import os
import re
import xlsxwriter
from collections import defaultdict
from sastadev.lexicon import known_word


def is_metadata(line):
    result = line != "" and line[0] == '@'
    return result


def is_utterance(line):
    result = line != '' and line[0] == '*'
    return result


def is_continuation(line):
    result = line != '' and line[0] == '\t'
    return result


space = ' '


def get_chat_data(in_file_name):
    '''
    Function to parse a CHAT (.cha) file and return a tuple consisting of the headerdata and a list of utterances
    All lines other than headerdata or utterances are left out
    :param infilename:
    :return: Tuple[headerdata:List[str], utterances:List[str]]
    '''
    headerdata = []
    utterances = []
    previousisutt, previousismeta, noprevious, previousisother = 0, 1, 2, 3
    state = noprevious
    with open(in_file_name, 'r', encoding='utf8') as infile:
        for line in infile:
            if is_metadata(line):
                headerdata.append(line)
                state = previousismeta
            elif is_utterance(line):
                utterances.append(line)
                state = previousisutt
            elif is_continuation(line):
                if state == previousisutt:
                    newlast = headerdata[-1][:-1] + space + line
                    utterances = utterances[:-1] + [newlast]
                elif state == previousismeta:
                    newlast = headerdata[-1][:-1] + space + line
                    headerdata = headerdata[:-1] + [newlast]
                elif state == previousisother:
                    pass
                else:
                    print('Unexpected configuration')
                    print(line)
            else:
                state = previousisother
        return headerdata, utterances


def get_target_speaker(metadata):
    '''
    function to obtain the target speaker as specified in the metadata
    :param metadata: List[str]
    :return: speakercode: str
    '''
    for line in metadata:
        if line.lower().startswith('@participants:'):
            participant_str = line[len('@participants:'):]
            participants = participant_str.split(',')
            for participant in participants:
                part_props = participant.split()
                if 'child' in participant.lower():
                    result = part_props[0]
                    return result
    result = 'CHI'
    return result


def get_speaker(utt):
    '''
    function to obtain the speaker of an utterance
    :param utt: str
    :return: speakercode: str
    '''
    end_spk = utt.find(':')
    result = utt[1:end_spk]
    return result


def get_timestamps(utterances, target_speaker):
    cleaned_utterances = []
    cleaned_timestamps = []

    for utterance in utterances:
        utterance_speaker = get_speaker(utterance)  # Get the speaker code of the utterance

        # Only process utterances from the target speaker
        if utterance_speaker == target_speaker:
            isolate_stamp = re.findall('\x15.*\x15', utterance)
            if len(isolate_stamp) != 0:
                timestamp_ = re.sub(r'\x15', '', isolate_stamp[0])
                timestamp = re.sub(r'_', " ", timestamp_).split()
                cleaned_text = re.sub(r'\*CHI:\t|\x15\d+_\d+\x15|\[//\]|\n|[<>()]', '', utterance)

                cleaned_utterances.append(cleaned_text)
                cleaned_timestamps.append(timestamp)

    return cleaned_utterances, cleaned_timestamps


def process_all_cha_files(default_childes_path, output_csv_path):
    """
    Process all .cha files in the directory, isolating the child speech part of the transcript and the related timestamp
    :param default_childes_path: str, root directory containing .cha files
    :param output_csv_path: str, path for the output csv file
    """
    final_dataframe = pd.DataFrame(columns=["filename", "utterances", "timestamps"])

    # Step 1: Walk through the directory to process .cha files
    for root, dirs, thefiles in os.walk(default_childes_path):
        print(f'Processing {root}...', file=sys.stderr)

        # We only want the filenames with extension *cha* except ital.cha
        cha_files = [f for f in thefiles if f.endswith('.cha') and not f.endswith('-ital.cha')]

        for in_file_name in cha_files:
            print(in_file_name)
            in_full_name = os.path.join(root, in_file_name)

            # Extract data and target speaker for the current file
            header_data, utterances = get_chat_data(in_full_name)
            target_speaker = get_target_speaker(header_data)

            # extract info: child utterance and timestamp
            processed_u, processed_t = get_timestamps(utterances, target_speaker)

            if DEBUG:
                print(processed_u)
                print(processed_u)
                print(len(processed_u))
                print(len(processed_t))

            new_row = pd.DataFrame(
                {"filename": [in_file_name], "utterances": [processed_u], "timestamps": [processed_t]})
            final_dataframe = pd.concat([final_dataframe, new_row], ignore_index=True)

    final_dataframe.to_csv(output_csv_path)


DEBUG = False
default_childes_path = 'Asymmetries/CK-TD'
output_csv_path = "cha_data.csv"
process_all_cha_files(default_childes_path, output_csv_path)
