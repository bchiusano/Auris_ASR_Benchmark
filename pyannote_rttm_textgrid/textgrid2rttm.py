# author = julien karadayi
#
# This script converts transcription in Text Grid / Praat format
# to RTTM format. This is useful for evaluating performances of
# Speech detection algorithms with the *dscore* package,
# in the DiarizationVM virtual machine.
# The 1 and 0 labels are sent to " speech ", and no label / "x" label
# are not written in output (which means it is described as "non speech")

import os
import argparse
# from praatio import tgio
import tgt # tgt is better thant praatio for our application
           # because it allows to manipulate the timestamps,
           # which is something we cannot do with praatio.



def textgrid2rttm(textgrid):
    '''
        Take in input the path to a text grid,
        and output a dictionary of lists *{spkr: [ (onset, duration) ]}*
        that can easily be written in rttm format.
    '''
    # init output
    rttm_out = dict()

    tier_spkr = 'CHI'

    # open textgrid
    #tg = tgio.openTextgrid(textgrid)
    tg = tgt.read_textgrid(textgrid)

    # loop over all speakers in this text grid
    #for spkr in tg.tierNameList:
    for tier in tg:
        
        
        tier_spkr = tier.name

        for interval in tier:

            bg, ed, label = interval.start_time,\
                          interval.end_time,\
                          interval.text
            
            

            if 'chi' in interval.text.lower() and not 'chi_ns' in interval.text.lower():
                spkr = 'CHI'
            elif 'adu' in interval.text.lower():
                spkr = 'ADU'
            else: 
                continue

            if spkr not in rttm_out:
                rttm_out[spkr] = []
            
            # Add (onset, duration) tuple
            rttm_out[spkr].append((bg, ed-bg))

    return rttm_out


def write_rttm(rttm_out, basename_whole):
    '''
        take a dictionary {spkr:[ (onset, duration) ]} as input
        and write on rttm output by speaker
    '''
    # write one rttm file for the whole wav, indicating
    # only regions of speech, and not the speaker
    with open(basename_whole + '.rttm', 'w') as fout:
        for spkr in rttm_out:
            for bg, dur in rttm_out[spkr]:
                fout.write(u'SPEAKER {} 1 {} {} '
                           '<NA> <NA> {} <NA>\n'.format(
                             basename_whole.split('/')[-1], bg, dur, spkr))


def sort_rttm(rttm_file):
    """
    Sort RTTM file by start time.
    Returns a list of segments with start, duration, end, and speaker.
    """
    segments = []
    with open(rttm_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and line.startswith('SPEAKER'):
                parts = line.split()
                if len(parts) >= 8:
                    segments.append({
                        'start': float(parts[3]),
                        'duration': float(parts[4]),
                        'end': float(parts[3]) + float(parts[4]),
                        'speaker': parts[7]
                    })

    segments.sort(key=lambda x: x['start'])

    # Write sorted segments back to the RTTM file
    with open(rttm_file, 'w') as f:
        for segment in segments:
            f.write(f"SPEAKER {segment['speaker']} 1 {segment['start']} "
                    f"{segment['duration']} <NA> <NA> {segment['speaker']} <NA>\n")


if __name__ == '__main__':

    dir = r"C:\Users\b.caissottidichiusan\OneDrive - Stichting Onderwijs Koninklijke Auris Groep - 01JO\Desktop\TOS-6yo\TextGrid"
    
    for file in os.listdir(dir):

        if not file.endswith('.TextGrid'):
            continue
        input_file = os.path.join(dir, file)
        print(f"Processing {input_file}...")
        rttm_out = textgrid2rttm(input_file)
        if 'diarized_clean' in file:
            output_file = file.replace('_diarized_clean.TextGrid', '')
        else :
            output_file = file.replace('_diarized.TextGrid', '')
        write_rttm(rttm_out, f"rttms/TOS6/{output_file}")
        sort_rttm(f"rttms/TOS6/{output_file}.rttm")


