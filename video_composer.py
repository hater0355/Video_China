import subprocess
import logging

logger = logging.getLogger(__name__)

def compose_final_video(original_video_path: str, voice_segments: list[dict], output_video_path: str):
    """
    Mixes original audio (10% volume) with new TTS segments, and applies anti-copyright visual filters.
    """
    logger.info(f"Composing final video to {output_video_path}")
    
    filter_complex = ""
    inputs = [original_video_path]
    
    # Video filter: subtle modifications to bypass Content ID
    # eq=brightness=0.02:contrast=1.03
    # scale and crop for a 1.01x zoom (microscopic crop)
    filter_complex += "[0:v]eq=brightness=0.02:contrast=1.03,scale=trunc(iw*1.01/2)*2:trunc(ih*1.01/2)*2,crop=trunc(iw/1.01/2)*2:trunc(ih/1.01/2)*2[vout];"
    
    # Original audio stream: volume=0.1
    filter_complex += "[0:a]volume=0.1[a0];"
    
    amix_inputs = "[a0]"
    for i, seg in enumerate(voice_segments):
        inputs.append(seg["audio_path"])
        input_index = i + 1
        start_ms = int(seg["start"] * 1000)
        # delay audio for all channels to position the segment correctly
        filter_complex += f"[{input_index}:a]adelay={start_ms}:all=1[a{input_index}];"
        amix_inputs += f"[a{input_index}]"
        
    num_audio_streams = len(voice_segments) + 1
    # mix all audio streams
    filter_complex += f"{amix_inputs}amix=inputs={num_audio_streams}:duration=first:dropout_transition=3[aout]"
    
    command = ["ffmpeg", "-y"]
    for inp in inputs:
        command.extend(["-i", inp])
        
    command.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        output_video_path
    ])
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        logger.info("Successfully rendered final video.")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error during composition: {e.stderr.decode('utf-8')}")
        raise