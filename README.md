# Youtube-word-finder

A Python script that finds every spoken instance of a target word in a YouTube video and automatically downloads short clips centered on each instance.

How it works
Downloads audio from a given YouTube video using yt-dlp
Transcribes the audio with OpenAI's Whisper model, generating word-level timestamps for everything said in the video
Scans the transcript for every instance of a target keyword
Filters near-duplicate matches that occur too close together in time, and skips any clip that runs unusually long (which usually means multiple words were caught together instead of one)
Downloads a short clip around each remaining match using yt-dlp's section-download feature, trimmed to just the keyword plus a small buffer before and after
Requirements
Python 3.9+
yt-dlp
openai-whisper
ffmpeg installed and available on your system PATH (required by both yt-dlp and Whisper)

Install the Python dependencies:

bash
pip install yt-dlp openai-whisper
Usage

Open the script and edit the settings at the top:

python
VIDEO_ID = '8UQ6nkR-tXk'   # the YouTube video ID to search
KEYWORD = 'bro'            # the word to search for
PADDING = 0.2              # seconds of buffer before/after each match
MAX_CLIP_DURATION = 1.5    # skip clips longer than this (likely multiple words)
MIN_GAP = 3.0              # minimum seconds between matches to avoid near-duplicates

Then run:

bash
python keyword_clip_finder.py

The script will:

Download and transcribe the video's audio
Print how many total instances were found, and how many unique clips passed the filtering
Save each clip as {VIDEO_ID}_clip_{n}_{KEYWORD}.mp4 in the working directory
Delete the temporary audio file once finished
Notes
Larger Whisper models (small, medium) improve transcription accuracy at the cost of speed; the script defaults to base as a balance of both.
Clip boundaries depend on Whisper's word-level timing, so very fast or overlapping speech may occasionally produce imprecise cuts.
