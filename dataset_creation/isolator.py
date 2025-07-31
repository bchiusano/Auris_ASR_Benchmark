import pandas as pd
import sys
import os
import re
from sastadev.lexicon import known_word
from chamd.cleanCHILDESMD import cleantext

# stamper (grammatical analysis)
# regular expressions used to obtain the wrong words and their corrections
noncompletionpattern = r'(.*)\((\w*)\)(.*)'
noncompletionre = re.compile(noncompletionpattern)

replacementpattern = r'(\w+(?:\(\w\))?)\s*\[:\s*(\w+(?:\’\w+)?)\s*\]'
replacementre = re.compile(replacementpattern)

explanationpattern = r'(\w+)\s*\[=\s+([ \w]+)\s*\]'
explanationre = re.compile(explanationpattern)

# officially [= must be followed by a space. But this is often not done, and does not lead to ambiguity in some cases
# for these we are robust and allow the absence of space
robustexplanationpattern = r'(\[=)([^!? ])'
robustexplanationre = re.compile(robustexplanationpattern)

# these words are not considered valid words by the function *known_word* but we count them as correct
validwords = {"z'n", 'dees', 'cool'}
punctuationsymbols = """.,?!:;"'"""


def isvalidword(w: str) -> bool:
    '''
    function to determine whether a word is a valid Dutch word
    :param w:
    :return: bool
    '''
    if known_word(w):
        return True
    elif w in punctuationsymbols:
        return True
    elif w in validwords:
        return True
    else:
        return False


def getexplanations(rawutt):
    '''
    function to obtain the explanations from an utterance
    :param rawutt: str
    :return: List of (wrongword, correction) pairs
    '''
    geluid = "brbr"
    geluid2 = "brbrbrbr"
    geluid3 = "brbrbr"
    results = []
    utt = robustexplanationre.sub(r'\1 \2', rawutt)
    matches = explanationre.finditer(utt)
    for match in matches:
        wrong = match.group(1)
        wrong = wrong.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<",
                                                                                                                    "")
        correct = match.group(2)
        correct = correct.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace(
            "<", "")
        full_match = match.group(0)
        full_match = full_match.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">",
                                                                                                             "").replace(
            "<", "")
        '''
        if len(correct) > 4 \
                and len(wrong) > 4 \
                and len(correct.split()) == 1 \
                and wrong.isalpha() \
                and not correct[0].isupper() \
                and wrong != geluid \
                and wrong != geluid2 \
                and wrong != geluid3 \
                and isvalidword(wrong) is False:
        '''
        results.append((full_match, wrong, correct))

    return results


def getreplacements(utt):
    '''
    function to obtain the replacements from an utterance
    :param utt: str
    :return: List of (wrongword, correction) pairs
    '''
    results = []
    matches = replacementre.finditer(utt)
    for match in matches:
        wrong = match.group(1)
        wrong = wrong.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<",
                                                                                                                    "")
        correct = match.group(2)
        correct = correct.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace(
            "<", "")
        full_match = match.group(0)
        full_match = full_match.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">",
                                                                                                             "").replace(
            "<", "")
        '''
        if len(correct) > 4 \
                and len(wrong) > 4 \
                and len(correct.split()) == 1 \
                and wrong.isalpha() \
                and not correct[0].isupper() \
                and isvalidword(wrong) is False:
        '''
        results.append((full_match, wrong, correct))

    return results


def getnoncompletions(line):
    '''
    Function to obtain two lists from noncompletions in a line.
    - Store only the noncompletions where the correct word is more than 4 characters long.
    - The first list contains tuples of (cleaned_word, corrected_word).
    - The second list contains tuples of (original_word, cleaned_word).

    :param line: str
    :return: Tuple[List[Tuple[cleaned_word:str, corrected_word:str]], List[Tuple[original_word:str, cleaned_word:str]]]
    '''
    words = line.split()
    results = []

    for w in words:
        match = noncompletionre.search(w)
        if match:
            w = w.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")
            wrong = undononcompletion(w)
            wrong = wrong.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace(
                "<", "")
            correct = applynoncompletion(w)
            correct = correct.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">",
                                                                                                           "").replace(
                "<", "")

            '''
            if len(correct) > 4 \
                    and len(wrong) > 4 \
                    and len(correct.split()) == 1 \
                    and wrong.isalpha() \
                    and not correct[0].isupper() \
                    and isvalidword(wrong) is False:
            '''
            results.append((w, wrong, correct))

    return results


def undononcompletion(word):
    '''
    function to undo a noncompletion, e.g. *(s)laap* is turned into *laap*.

    :param word: str
    :return: str
    '''
    inword = word
    outword = ''
    while True:
        outword = noncompletionre.sub(r'\1\3', inword)  # iterate for there may be # multiple occurrences
        if outword == inword:
            return outword
        else:
            inword = outword


def applynoncompletion(word):
    '''
    function to apply a noncompletion, e.g. *(s)laap* is turned into *slaap*.

    :param word:
    :return:
    '''
    inword = word
    outword = ''
    while True:
        outword = noncompletionre.sub(r'\1\2\3', inword)  # iterate for there may be # multiple occurrences
        if outword == inword:
            return outword
        else:
            inword = outword


def replace_match_wrong(line, to_correct):
    for match, wrong, correct in to_correct:
        wrong_replace = line.replace(match, wrong)

    return wrong_replace


def replace_match_correct(line, to_correct):
    for match, wrong, correct in to_correct:
        correct_replace = line.replace(match, correct)

    return correct_replace


def clean_chat_patterns_only(utterances, targetspeaker, DEBUG=False):
    wrong_utterances = []
    correct_utterances = []

    # Step 2: Process each utterance
    for utterance in utterances:
        utterancespeaker = get_speaker(utterance)  # Get the speaker code of the utterance

        # Only process utterances from the target speaker
        if utterancespeaker == targetspeaker:
            explanations_results = getexplanations(utterance)
            replacements_results = getreplacements(utterance)
            noncompletions_results = getnoncompletions(utterance)

            if DEBUG:
                print("explanations ", explanations_results)
                print("replacements ", replacements_results)
                print("non completions ", noncompletions_results)
                print("Utterance Before: ", utterance)

            wrong = utterance

            if explanations_results or replacements_results or noncompletions_results:

                temp_collector = [explanations_results, replacements_results, noncompletions_results]

                for result in temp_collector:
                    if result:
                        wrong = replace_match_wrong(utterance, result)
                        correct = replace_match_correct(utterance, result)
                        if DEBUG:
                            print("Utterance Explanation wrong: ", wrong)
                            print("Utterance Explanation correct: ", correct)

            if wrong != utterance:
                wrong_utterances.append(wrong)
                correct_utterances.append(correct)
            else:
                wrong_utterances.append(utterance)
                correct_utterances.append(utterance)

    return wrong_utterances, correct_utterances  # List of tuples (pattern, wrong, correct)


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


def get_timestamps(utterances, target_speaker, s):
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
                clean_ts = re.sub(r'\*CHI:\t|\x15\d+_\d+\x15|\[//\]|\n|[<>()]', '', utterance)
                sasta_clean = cleantext(clean_ts, False)
                cleaned_text = re.sub(' +', ' ', sasta_clean.replace(".", ""))

                if DEBUG:
                    print(s)
                    print("cleaned text before sasta:", clean_ts)
                    print("cleaned text after sasta:", sasta_clean)
                    print("FINAL: ", cleaned_text)

                cleaned_utterances.append(cleaned_text)
                cleaned_timestamps.append(timestamp)

    return cleaned_utterances, cleaned_timestamps


def process_all_cha_files(default_childes_path):
    """
    Process all .cha files in the directory, isolating the child speech part of the transcript and the related timestamp
    :param default_childes_path: str, root directory containing .cha files
    """
    original_dataframe = pd.DataFrame(columns=["filename", "utterances", "timestamps"])
    wrong_dataframe = pd.DataFrame(columns=["filename", "utterances", "timestamps"])
    correct_dataframe = pd.DataFrame(columns=["filename", "utterances", "timestamps"])

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

            wrong_cleaned, correct_cleaned = clean_chat_patterns_only(utterances, target_speaker)

            processed_u, processed_t = get_timestamps(utterances, target_speaker, "ORIGINAL")

            if DEBUG:
                print(processed_u)
                print(processed_u)
                print(len(processed_u))
                print(len(processed_t))

            new_row = pd.DataFrame({"filename": [in_file_name], "utterances": [processed_u], "timestamps": [processed_t]})
            original_dataframe = pd.concat([original_dataframe, new_row], ignore_index=True)

            processed_u, processed_t = get_timestamps(wrong_cleaned, target_speaker, "WRONG")
            new_row = pd.DataFrame({"filename": [in_file_name], "utterances": [processed_u], "timestamps": [processed_t]})
            wrong_dataframe = pd.concat([wrong_dataframe, new_row], ignore_index=True)

            processed_u, processed_t = get_timestamps(correct_cleaned, target_speaker, "CORRECT")
            new_row = pd.DataFrame(
                {"filename": [in_file_name], "utterances": [processed_u], "timestamps": [processed_t]})
            correct_dataframe = pd.concat([correct_dataframe, new_row], ignore_index=True)

    print(len(original_dataframe))
    print(len(wrong_dataframe))
    print(len(correct_dataframe))

    original_dataframe.to_csv("csvs/sk-adhd-csvs/cha_data.csv", index=False)
    wrong_dataframe.to_csv("csvs/sk-adhd-csvs/wrong_data.csv", index=False)
    correct_dataframe.to_csv("csvs/sk-adhd-csvs/correct_data.csv", index=False)


if __name__ == "__main__":
    DEBUG = False
    default_childes_path = '../Asymmetries/SK-ADHD'
    process_all_cha_files(default_childes_path)
