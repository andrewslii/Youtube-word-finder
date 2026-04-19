import subprocess
import whisper
import os
import tempfile

# --- SETTINGS ---
VIDEO_ID = '8UQ6nkR-tXk' 
KEYWORD = 'bro'
PADDING = 0.2  # Seconds before/after the word
MAX_CLIP_DURATION = 1.5  # Skip clips longer than this (multiple words detected)
MIN_GAP = 3.0  # Minimum seconds between clips to avoid duplicates
# ----------------

def download_audio():
    """Download just the audio from YouTube"""
    print("Downloading audio for transcription...")
    audio_file = f"{VIDEO_ID}_audio.mp3"
    
    cmd = ['python', '-m', 'yt_dlp', '-x', '--audio-format', 'mp3', 
           '-o', audio_file, f"https://www.youtube.com/watch?v={VIDEO_ID}"]
    
    subprocess.run(cmd, capture_output=True)
    return audio_file

def get_word_timestamps(audio_file):
    """Use Whisper to get word-level timestamps"""
    print("Transcribing with Whisper (this may take a minute)...")
    model = whisper.load_model("base")  # Use 'tiny' for faster, 'small'/'medium' for better accuracy
    result = model.transcribe(audio_file, word_timestamps=True)
    
    word_matches = []
    for segment in result['segments']:
        if 'words' in segment:
            for word in segment['words']:
                word_text = word['word'].strip().lower().rstrip('.,!?')
                if word_text == KEYWORD.lower():
                    word_matches.append({
                        'start': word['start'],
                        'end': word['end'],
                        'text': word['word']
                    })
    
    return word_matches

def download_clips(matches):
    """Download video clips for each match"""
    if not matches:
        print("No matches found.")
        return
    
    # Filter out duplicates that are too close together
    filtered = []
    last_start = -999
    for match in matches:
        if match['start'] - last_start >= MIN_GAP:
            filtered.append(match)
            last_start = match['start']
    
    print(f"Found {len(matches)} instances, filtered to {len(filtered)} unique clips!")
    print("Downloading clips...")
    
    for i, match in enumerate(filtered):
        start_time = max(0, match['start'] - PADDING)
        end_time = match['end'] + PADDING
        duration = end_time - start_time
        
        # Skip if clip is too long (probably caught multiple words)
        if duration > MAX_CLIP_DURATION:
            print(f"Skipping clip {i+1} (duration {duration:.2f}s too long)")
            continue
        
        output_file = f"{VIDEO_ID}_clip_{i+1}_{KEYWORD}.mp4"
        
        cmd = ['python', '-m', 'yt_dlp', '--download-sections', f"*{start_time}-{end_time}", 
               '--force-keyframes-at-cuts', '-o', output_file, 
               f"https://www.youtube.com/watch?v={VIDEO_ID}"]
        
        subprocess.run(cmd, capture_output=True)
        print(f"Downloaded: {output_file} (at {match['start']:.1f}s, duration: {duration:.2f}s)")

def main():
    try:
        # Download audio
        audio_file = download_audio()
        
        # Get word-level timestamps
        print(f"Searching for '{KEYWORD}'...")
        matches = get_word_timestamps(audio_file)
        
        # Download clips
        download_clips(matches)
        
        # Clean up audio file
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"\nCleaned up temporary audio file")
        
        print("\nDone!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
