import os
import logging
import subprocess
import azure.cognitiveservices.speech as speechsdk
import wave

logger = logging.getLogger(__name__)

def get_audio_duration(file_path: str) -> float:
    """
    Gets the duration of a wav file in seconds.
    """
    with wave.open(file_path, 'rb') as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration

def apply_atempo(input_path: str, output_path: str, speed_ratio: float):
    """
    Uses FFmpeg atempo filter to speed up or slow down audio.
    """
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-filter:a", f"atempo={speed_ratio}",
        output_path
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def generate_vietnamese_voice(subtitles: list[dict], output_dir: str) -> list[dict]:
    """
    Generates TTS for each subtitle segment, adjusting speed to fit the time window.
    """
    logger.info(f"Generating Vietnamese voice for {len(subtitles)} segments.")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    speech_key = os.environ.get("AZURE_SPEECH_KEY")
    service_region = os.environ.get("AZURE_SPEECH_REGION")
    
    if not speech_key or not service_region:
        raise ValueError("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables must be set.")
        
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "vi-VN-NamMinhNeural"
    
    processed_segments = []
    
    for idx, segment in enumerate(subtitles):
        text = segment.get("text")
        start_time = segment.get("start")
        end_time = segment.get("end")
        original_duration = end_time - start_time
        
        if not text or original_duration <= 0:
            continue
            
        temp_wav_path = os.path.join(output_dir, f"segment_{idx}_raw.wav")
        final_wav_path = os.path.join(output_dir, f"segment_{idx}_aligned.wav")
        
        # Generate TTS
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_wav_path)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        result = speech_synthesizer.speak_text_async(text).get()
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.error(f"TTS synthesis failed for segment {idx}: {result.reason}")
            continue
            
        # Check duration and align
        try:
            generated_duration = get_audio_duration(temp_wav_path)
            
            # If generated audio duration differs from target window, adjust speed
            # FIX: Correct calculation - if generated_duration > original_duration, slow down (speed < 1)
            if generated_duration > original_duration and generated_duration > 0:
                speed_ratio = original_duration / generated_duration  # FIXED: was reversed
                # FFmpeg atempo works best between 0.5 and 2.0
                if speed_ratio < 0.5:
                    logger.warning(f"Segment {idx} requires {speed_ratio:.2f}x speed, which may sound unnatural.")
                logger.info(f"Segment {idx}: Adjusting speed to {speed_ratio:.2f}x to fit window.")
                apply_atempo(temp_wav_path, final_wav_path, speed_ratio)
            else:
                os.rename(temp_wav_path, final_wav_path)
                
            processed_segments.append({
                "start": start_time,
                "end": end_time,
                "audio_path": final_wav_path
            })
            
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
                
        except Exception as e:
            logger.error(f"Failed to align audio for segment {idx}: {e}")
            
    logger.info(f"Generated {len(processed_segments)} aligned voice segments.")
    return processed_segments
