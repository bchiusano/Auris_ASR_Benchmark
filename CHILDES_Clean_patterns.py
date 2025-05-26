import sys
import os
import re
import xlsxwriter
from collections import defaultdict
from sastadev.lexicon import known_word

#stamper (grammatical analysis)

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


def getspeaker(utt):
    '''
    function to obtain the speaker of an utterance
    :param utt: str
    :return: speakercode: str
    '''
    endspk = utt.find(':')
    result = utt[1:endspk]
    return result


# functions to determine the nature of a line in a CHAT file
def ismetadata(line):
    result = line != "" and line[0] == '@'
    return result


def isutterance(line):
    result = line != '' and line[0] == '*'
    return result


def iscontinuation(line):
    result = line != '' and line[0] == '\t'
    return result


space = ' '


def getchatdata(infilename):
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
    with open(infilename, 'r', encoding='utf8') as infile:
        for line in infile:
            if ismetadata(line):
                headerdata.append(line)
                state = previousismeta
            elif isutterance(line):
                utterances.append(line)
                state = previousisutt
            elif iscontinuation(line):
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


def gettargetspeaker(metadata):
    '''
    function to obtain the target speaker as specified in the metadata
    :param metadata: List[str]
    :return: speakercode: str
    '''
    for line in metadata:
        if line.lower().startswith('@participants:'):
            participantstr = line[len('@participants:'):]
            participants = participantstr.split(',')
            for participant in participants:
                partprops = participant.split()
                if 'child' in participant.lower():
                    result = partprops[0]
                    return result
    result = 'CHI'
    return result

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
        wrong = wrong.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")
        correct = match.group(2)
        correct = correct.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")
        full_match = match.group(0)
        full_match = full_match.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")

        if len(correct) > 4 \
                and len(wrong) > 4 \
                and len(correct.split()) == 1 \
                and wrong.isalpha() \
                and not correct[0].isupper()\
                and wrong != geluid\
                and wrong != geluid2\
                and wrong != geluid3\
                and isvalidword(wrong) is False:
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
        wrong = wrong.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")
        correct = match.group(2)
        correct = correct.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")
        full_match = match.group(0)
        full_match = full_match.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")

        if len(correct) > 4 \
                and len(wrong) > 4 \
                and len(correct.split()) == 1 \
                and wrong.isalpha() \
                and not correct[0].isupper()\
                and isvalidword(wrong) is False:
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
            wrong = wrong.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")
            correct = applynoncompletion(w)
            correct = correct.replace(".", "").replace("?", "").replace("‹", "").replace("@c", "").replace(">", "").replace("<", "")

            if len(correct) > 4 \
                    and len(wrong) > 4 \
                    and len(correct.split()) == 1 \
                    and wrong.isalpha() \
                    and not correct[0].isupper()\
                    and isvalidword(wrong) is False:
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
        outword = noncompletionre.sub(r'\1\3', inword)     #  iterate for there may be # multiple occurrences
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
        outword = noncompletionre.sub(r'\1\2\3', inword)     #  iterate for there may be # multiple occurrences
        if outword == inword:
            return outword
        else:
            inword = outword


def clean_annotation_patterns(line):
    """
    Function to extract, clean patterns from a line and replace them in the line.
    :param line: str
    :return: str, cleaned line
    """
    _, explanations = getexplanations(line)
    _, replacements = getreplacements(line)
    _, noncompletions = getnoncompletions(line)

    # Process and replace patterns in the line
    for match, wrong in explanations:
      line = line.replace(match, wrong)

    for match, wrong in replacements:
        line = line.replace(match, wrong)

    for match, wrong in noncompletions:
        line = line.replace(match, wrong)

    return line


def clean_chat_patterns_only(utterances, targetspeaker):
    """
    Function to clean a CHA file by extracting patterns from utterances of the target speaker.
    :param file_path: str, path to the CHA file
    :param targetspeaker: str, the code for the target speaker
    :return: List[tuple], list of (pattern, wrong, correct) tuples found in the target speaker's utterances
    """

    patterns = []

    # Step 2: Process each utterance
    for utterance in utterances:
        utterancespeaker = getspeaker(utterance)  # Get the speaker code of the utterance

        # Only process utterances from the target speaker
        if utterancespeaker == targetspeaker:
            explanations_results = getexplanations(utterance)
            replacements_results = getreplacements(utterance)
            noncompletions_results = getnoncompletions(utterance)

            # Collect all (pattern, wrong, correct) tuples
            patterns.extend(explanations_results)
            patterns.extend(replacements_results)
            patterns.extend(noncompletions_results)

    return patterns  # List of tuples (pattern, wrong, correct)


def process_all_cha_files(defaultchildespath, output_xlsx_path):
    """
    Process all .cha files in the directory, collect patterns, count their frequency,
    and write them to an Excel file, sorted by frequency.
    :param defaultchildespath: str, root directory containing .cha files
    :param output_xlsx_path: str, path for the output Excel file
    """
    # Dictionary to store pattern frequencies across all files
    pattern_freq_dict = defaultdict(int)

    # Step 1: Walk through the directory to process .cha files
    for root, dirs, thefiles in os.walk(defaultchildespath):
        print(f'Processing {root}...', file=sys.stderr)

        # We only want the filenames with extension *cha* except ital.cha
        chafiles = [f for f in thefiles if f.endswith('.cha') and not f.endswith('-ital.cha')]

        for infilename in chafiles:
            print(infilename)
            infullname = os.path.join(root, infilename)

            # Extract data and target speaker for the current file
            headerdata, utterances = getchatdata(infullname)
            targetspeaker = gettargetspeaker(headerdata)

            # Step 2: Extract patterns from the file
            patterns = clean_chat_patterns_only(utterances, targetspeaker)

            # Step 3: Update the dictionary with pattern frequencies
            for pattern in patterns:
                pattern_tuple = (pattern[0], pattern[1], pattern[2])  # (Pattern, Wrong, Correct)
                pattern_freq_dict[pattern_tuple] += 1  # Increment frequency for this pattern

    # Step 4: Sort the patterns by frequency in descending order
    sorted_patterns = sorted(pattern_freq_dict.items(), key=lambda x: x[1], reverse=True)

    # Step 5: Write the sorted pattern frequencies to the Excel file
    # Create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(output_xlsx_path)
    worksheet = workbook.add_worksheet()

    # Write the header row
    worksheet.write(0, 0, 'Pattern')
    worksheet.write(0, 1, 'Wrong')
    worksheet.write(0, 2, 'Correct')
    worksheet.write(0, 3, 'Frequency')

    row = 1  # Start writing data from the second row

    # Write the sorted dictionary content to the worksheet
    for pattern_tuple, frequency in sorted_patterns:
        worksheet.write(row, 0, pattern_tuple[0])  # Pattern
        worksheet.write(row, 1, pattern_tuple[1])  # Wrong
        worksheet.write(row, 2, pattern_tuple[2])  # Correct
        worksheet.write(row, 3, frequency)         # Frequency

        row += 1  # Move to the next row

    workbook.close()  # Save the Excel file


defaultchildespath = 'CHILDES'
output_xlsx_path = "Patterns_CHILDES.xlsx"
process_all_cha_files(defaultchildespath, output_xlsx_path)




