import os
import re
import sys
import pandas as pd
from dataset_creation.isolator import get_chat_data, get_target_speaker
from chamd.cleanCHILDESMD import cleantext

def parse_rttm_file(rttm_file):
    # Parse RTTM file
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
    return segments


def get_all_speakers(segments):
    unique_speakers = list(set(segment['speaker'] for segment in segments))
    unique_speakers.sort()  # Sort for consistent order
    
    print(f"Found {len(unique_speakers)} unique speakers: {unique_speakers}")

    return unique_speakers


def get_speaker_continuous_segments(segments, target_speaker):
    """
    Extract continuous speaking segments for a specific speaker.
    Returns the first start and last end time for each continuous speaking period.
    """
    '''
    grouped_segments = []
    previous_was_not_target = True
    for seg in segments:
        if seg['speaker'] == target_speaker and previous_was_not_target:
            current_segment_start = seg['start']
            previous_was_not_target = False
        elif seg['speaker'] != target_speaker and not previous_was_not_target:
            current_segment_end = seg['start']
            grouped_segments.append({
                'start': current_segment_start,
                'end': current_segment_end,
                'duration': current_segment_end - current_segment_start,
                'speaker': target_speaker
            })
            previous_was_not_target = True
        else: continue
            
    return grouped_segments
    '''

    # Filter for target speaker and sort by start time
    speaker_segments = [seg for seg in segments if seg['speaker'] == target_speaker]
    speaker_segments.sort(key=lambda x: x['start'])

    if not speaker_segments:
        print(f"No segments found for {target_speaker}")
        return []

    # Group continuous segments
    continuous_segments = []
    current_segment_start = speaker_segments[0]['start']
    current_segment_end = speaker_segments[0]['end']

    # Define gap threshold (adjust as needed - e.g., 0.5 seconds)
    gap_threshold = 1

    for i in range(1, len(speaker_segments)):
        current_seg = speaker_segments[i]

        # Check if there's a significant gap between segments
        gap = current_seg['start'] - current_segment_end

        if gap <= gap_threshold:
            # Extend current continuous segment
            current_segment_end = current_seg['end']
        else:
            # End current segment and start a new one
            continuous_segments.append({
                'segment_number': len(continuous_segments) + 1,
                'start': current_segment_start,
                'end': current_segment_end,
                'duration': current_segment_end - current_segment_start,
                'speaker': target_speaker
            })

            # Start new segment
            current_segment_start = current_seg['start']
            current_segment_end = current_seg['end']

    # Add the last segment
    continuous_segments.append({
        'segment_number': len(continuous_segments) + 1,
        'start': current_segment_start,
        'end': current_segment_end,
        'duration': current_segment_end - current_segment_start,
        'speaker': target_speaker
    })

    return continuous_segments

    


def process_child_utt_segments(target, text_list):
    """
    Process a list of CHI or KIN entries and merge consecutive Child utterances,

    Args:
        text_list: utterances
    
    Returns:
        List of dictionaries with segment information
    """
    
    segments = []
    continuous = ""
    for i, text in enumerate(text_list):

        if text.startswith(f"*{target}:"):

            clean_ts = re.sub(rf'\*{target}:\t|\x15\d+_\d+\x15|\[//\]|\n|[<>()]', '', text)
            sasta_clean = cleantext(clean_ts, False)
            cleaned_text = re.sub(' +', ' ', sasta_clean.replace(".", ""))
            cleaned_text = cleaned_text.strip().replace(",", "")
            continuous = continuous + " " + cleaned_text.strip()
        else:
            if continuous != "" :
                segments.append(continuous)
                continuous = ""
    
    return segments


def print_segments(segments):
    print(f"Found {len(segments)} continuous speaking segments for {target}:")
    print("=" * 70)

    for segment in segments:
        start_time = int(segment['start'] * 1000)
        end_time = int(segment['end'] * 1000)
        duration = int(segment['duration'] * 1000)

        #print(f"Segment {segment['segment_number']}:")
        print(f"  Start: {start_time} ({segment['start']:.3f}s)")
        print(f"  End:   {end_time} ({segment['end']:.3f}s)")
        print(f"  Duration: {duration} ({segment['duration']:.3f}s)")
        print("-" * 50)



if __name__ == "__main__":
    folder = "rttms/TOS6"
    target = "CHI"
    dir = r"C:\Users\b.caissottidichiusan\OneDrive - Stichting Onderwijs Koninklijke Auris Groep - 01JO\Desktop\Transcripten"

    filenames = []
    list_timestamps = []
    list_utterances = []
    csv_dir = "rttms/csvs"
    metadata = pd.DataFrame(columns=["filename", "utterances", "timestamps"])


    for file in os.listdir(folder):

        if not file.endswith('.rttm'):
            continue

        ######################################################################################
        # Process the corresponding CHAT file
        cha_file = file.replace('.rttm', '_cht.cha')
        cha_file_path = os.path.join(dir, cha_file)

        header_data, utterances = get_chat_data(cha_file_path)
        target_speaker = get_target_speaker(header_data)

        # list of child utterances
        merged_segments = process_child_utt_segments(target_speaker, utterances)
        #print(merged_segments)
        print("utt: ", len(merged_segments))
        list_utterances.append(merged_segments)

        #####################################################################################
        # Process the RTTM of the audio file

        audio_file_path = os.path.join(folder, file)
        
        segments = parse_rttm_file(audio_file_path)
        #print(segments)

    
        print(f"Processing {audio_file_path} for target {target}...")

        speaker_segments = get_speaker_continuous_segments(segments, str(target))
        #print_segments(speaker_segments)
        
        # list of segments with start and end time converted to milliseconds
        stamps = []
        for segment in speaker_segments:
            start_time = int(segment['start'] * 1000)
            end_time = int(segment['end'] * 1000)
            #if (end_time-start_time) > 1500:  # Only consider segments longer than 1 second
            stamps.append([start_time, end_time])

        print("stamps: ", len(stamps))
        
        list_timestamps.append(stamps)

    
        filename = file.replace('.rttm', '')
        filenames.append(filename)

    print("Timestamps:", len(list_timestamps))
    print("Utterances:", len(list_utterances))

    metadata['filename']= filenames
    metadata['utterances'] = list_utterances
    metadata['timestamps'] = list_timestamps
    metadata.to_csv(f"{csv_dir}/TOS6.csv", index=False)
