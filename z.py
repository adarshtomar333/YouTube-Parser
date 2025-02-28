import os
import time
import yt_dlp
import subprocess
import whisper
import re

# Path to store the downloaded and processed audio
OUTPUT_DIR = "E:/Projects/YT"

# Path to FFmpeg (Ensure it's correctly set)
FFMPEG_PATH = "E:/Projects/YT/ffmpeg-7.1-full_build/bin/ffmpeg.exe"

if not os.path.exists(FFMPEG_PATH):
    print(f"❌ FFmpeg not found at {FFMPEG_PATH}. Please check the path.")
    exit()

# Function to sanitize filenames (remove invalid characters)
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title)

# Function to get video title
def get_video_title(video_url):
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return sanitize_filename(info["title"]) if "title" in info else "video_audio"

# Function to download audio from YouTube
def download_audio(video_url):
    title = get_video_title(video_url)
    audio_path = os.path.join(OUTPUT_DIR, f"{title}.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "outtmpl": os.path.join(OUTPUT_DIR, f"{title}.%(ext)s"),  # Store using title
        "ffmpeg_location": os.path.dirname(FFMPEG_PATH),
    }

    try:
        print(f"\n📥 Downloading audio for '{title}'...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        time.sleep(2)  # Give time for the file to save

        # Check if the file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"❌ MP3 file not found after download!")

        print(f"✅ Audio downloaded successfully at {audio_path}.")
        return title  # Return the title for further steps
    except Exception as e:
        print(f"❌ Error downloading audio: {e}")
        exit()

# Function to convert MP3 to WAV
def convert_to_wav(title):
    mp3_path = os.path.join(OUTPUT_DIR, f"{title}.mp3")
    wav_path = os.path.join(OUTPUT_DIR, f"{title}.wav")

    if not os.path.exists(mp3_path):
        print("❌ Error: MP3 file not found!")
        exit()

    print(f"\n🎵 Converting '{title}.mp3' to WAV...")
    command = [
        FFMPEG_PATH, "-i", mp3_path, "-ar", "16000", "-ac", "1",
        "-c:a", "pcm_s16le", wav_path, "-y"
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Audio converted to WAV: {wav_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting MP3 to WAV: {e}")
        exit()

# Function to transcribe audio using Whisper in English
def transcribe_audio(title):
    """Transcribe audio using Whisper with Hindi language specified."""
    wav_path = os.path.join(OUTPUT_DIR, f"{title}.wav")
    transcript_file = os.path.join(OUTPUT_DIR, f"{title}.txt")

    if not os.path.exists(wav_path):
        print("❌ Error: WAV file not found!")
        exit()

    print(f"\n📝 Transcribing '{title}.wav' with language set to Hindi...")
    model = whisper.load_model("large")  # Consider using "small" or "large" for better accuracy
    result = model.transcribe(wav_path, language="hi")  # Specify Hindi with "hi"

    transcript = result["text"]
    print("\n✅ Transcript Ready!\n")

    # Save transcript to a file
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"📄 Transcript saved to: {transcript_file}")
# Function to clean up temporary files
def cleanup_files(title):
    mp3_path = os.path.join(OUTPUT_DIR, f"{title}.mp3")
    wav_path = os.path.join(OUTPUT_DIR, f"{title}.wav")

    try:
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
            print(f"🗑️ Deleted temporary file: {mp3_path}")
        if os.path.exists(wav_path):
            os.remove(wav_path)
            print(f"🗑️ Deleted temporary file: {wav_path}")
    except Exception as e:
        print(f"❌ Error cleaning up files: {e}")

# Main execution
if __name__ == "__main__":
    video_url = input("\n🎥 Enter YouTube video URL: ").strip()
    title = download_audio(video_url)
    convert_to_wav(title)
    transcribe_audio(title)
    cleanup_files(title)  # Clean up temporary files