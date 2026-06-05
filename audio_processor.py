import subprocess
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

def extract_audio(video_path: str, output_audio_path: str) -> str:
    """
    Extracts 16kHz mono WAV audio from the video using FFmpeg.
    """
    logger.info(f"Extracting audio from {video_path}")
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_audio_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        logger.info(f"Audio extracted to {output_audio_path}")
        return output_audio_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error during audio extraction: {e.stderr.decode('utf-8')}")
        raise

def transcribe_chinese_audio(audio_path: str) -> list[dict]:
    """
    Transcribes audio using OpenAI's Whisper API and returns structured timestamps.
    """
    logger.info(f"Transcribing audio {audio_path}")
    client = OpenAI()
    
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
            
        subtitles = []
        # Handle dict or object access dynamically depending on openai version
        segments = response.segments if hasattr(response, 'segments') else response.get('segments', [])
        
        for segment in segments:
            seg_dict = segment.model_dump() if hasattr(segment, 'model_dump') else (segment if isinstance(segment, dict) else vars(segment))
            subtitles.append({
                "start": seg_dict.get("start", 0.0),
                "end": seg_dict.get("end", 0.0),
                "text": seg_dict.get("text", "")
            })
            
        logger.info(f"Successfully transcribed {len(subtitles)} segments.")
        return subtitles
    except Exception as e:
        logger.error(f"Failed to transcribe audio: {e}")
        raise