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


# Usage example
if __name__ == "__main__":
    file = "trail.rttm"
    target = "SPEAKER_00"
    speaker_00_segments = get_speaker_continuous_segments(file, target)

    print(f"Found {len(speaker_00_segments)} continuous speaking segments for {target}:")
    print("=" * 70)

    for segment in speaker_00_segments:
        start_time = int(segment['start'] * 1000)
        end_time = int(segment['end'] * 1000)
        duration = int(segment['duration'] * 1000)

        print(f"Segment {segment['segment_number']}:")
        print(f"  Start: {start_time} ({segment['start']:.3f}s)")
        print(f"  End:   {end_time} ({segment['end']:.3f}s)")
        print(f"  Duration: {duration} ({segment['duration']:.3f}s)")
        print("-" * 50)