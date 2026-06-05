import os
import logging
import shutil
from dotenv import load_dotenv

from video_downloader import download_video
from audio_processor import extract_audio, transcribe_chinese_audio
from translator import translate_subtitles
from voice_generator import generate_vietnamese_voice
from video_composer import compose_final_video

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables (API keys)
    load_dotenv()
    
    video_url = input("Enter Douyin/Bilibili video URL: ").strip()
    if not video_url:
        logger.error("No URL provided. Exiting.")
        return
        
    # Setup directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.join(base_dir, "workspace")
    output_dir = os.path.join(base_dir, "output")
    tts_dir = os.path.join(workspace_dir, "tts_segments")
    
    for directory in [workspace_dir, output_dir, tts_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    try:
        # STEP 1: Video Scraping & Downloading
        logger.info("--- STEP 1: Video Scraping & Downloading ---")
        original_video_path = download_video(video_url, workspace_dir)
        
        # STEP 2: Audio Extraction & STT
        logger.info("--- STEP 2: Audio Extraction & STT ---")
        audio_path = os.path.join(workspace_dir, "extracted_audio.wav")
        extract_audio(original_video_path, audio_path)
        chinese_subtitles = transcribe_chinese_audio(audio_path)
        
        # FIX: Validate that subtitles were extracted
        if not chinese_subtitles:
            logger.error("No subtitles were transcribed from the audio.")
            return
        
        logger.info(f"Transcribed {len(chinese_subtitles)} subtitle segments.")
        
        # STEP 3: Context-Aware Machine Translation
        logger.info("--- STEP 3: Context-Aware Machine Translation ---")
        vietnamese_subtitles = translate_subtitles(chinese_subtitles)
        
        # FIX: Validate translation output
        if not vietnamese_subtitles:
            logger.error("Translation failed or returned empty result.")
            return
            
        logger.info(f"Translated {len(vietnamese_subtitles)} subtitle segments.")
        
        # STEP 4: Vietnamese TTS & Audio Alignment
        logger.info("--- STEP 4: Vietnamese TTS & Audio Alignment ---")
        voice_segments = generate_vietnamese_voice(vietnamese_subtitles, tts_dir)
        
        # FIX: Validate that voice segments were generated
        if not voice_segments:
            logger.error("No voice segments were generated. Pipeline cannot continue.")
            return
            
        logger.info(f"Generated {len(voice_segments)} voice segments.")
        
        # STEP 5: Video Composition & Spintax
        logger.info("--- STEP 5: Video Composition & Spintax ---")
        final_video_name = os.path.basename(original_video_path).rsplit('.', 1)[0] + "_vi.mp4"
        final_video_path = os.path.join(output_dir, final_video_name)
        compose_final_video(original_video_path, voice_segments, final_video_path)
        
        logger.info(f"Pipeline completed successfully! Final video saved at: {final_video_path}")
        
        # Cleanup workspace
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)
            logger.info("Cleaned up temporary workspace files.")
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
