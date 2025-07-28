import os
import re
from dataset_creation.isolator import get_chat_data, get_target_speaker, clean_chat_patterns_only
from chamd.cleanCHILDESMD import cleantext

def get_speaker_continuous_segments(rttm_file, target_speaker="SPEAKER_00"):
    """
    Extract continuous speaking segments for a specific speaker.
    Returns the first start and last end time for each continuous speaking period.
    """

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
    gap_threshold = 0.5

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


def print_segments(segments):
    print(f"Found {len(segments)} continuous speaking segments for {target}:")
    print("=" * 70)

    for segment in segments:
        start_time = int(segment['start'] * 1000)
        end_time = int(segment['end'] * 1000)
        duration = int(segment['duration'] * 1000)

        print(f"Segment {segment['segment_number']}:")
        print(f"  Start: {start_time} ({segment['start']:.3f}s)")
        print(f"  End:   {end_time} ({segment['end']:.3f}s)")
        print(f"  Duration: {duration} ({segment['duration']:.3f}s)")
        print("-" * 50)



if __name__ == "__main__":
    folder = "rttms"
    target = "SPEAKER_00"

    for file in os.listdir(folder):
        if not file.endswith('.rttm'):
            continue

        file_path = os.path.join(folder, file)
        print(f"Processing {file_path} for target {target}...")

        # Get continuous segments for the target speaker
        speaker_00_segments = get_speaker_continuous_segments(file_path, target)
        print_segments(speaker_00_segments)

        for segment in speaker_00_segments:
            start_time = int(segment['start'] * 1000)
            end_time = int(segment['end'] * 1000)


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
            continuous = continuous + " " + cleaned_text.strip()
        else:
            if continuous != "":
                segments.append(continuous)
                continuous = ""
    # TODO: handle if the child is the last utterance
    
    return segments


dir = r"C:\Users\b.caissottidichiusan\OneDrive - Stichting Onderwijs Koninklijke Auris Groep - 01JO\Desktop\fiveTDTranscripts"

#for file in os.listdir(dir):
#    if not file.endswith('.cha'):
#        continue
file = "P108_SPONTAAL_M1_cht.cha"
file_path = os.path.join(dir, file)

header_data, utterances = get_chat_data(file_path)
target_speaker = get_target_speaker(header_data)
#wrong_cleaned, correct_cleaned = clean_chat_patterns_only(utterances, target_speaker, DEBUG=True)
merged_segments = process_child_utt_segments(target_speaker, utterances)
print(merged_segments)

# TODO: merge utterances with timestamps