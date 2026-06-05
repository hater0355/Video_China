import yt_dlp
import os
import logging

logger = logging.getLogger(__name__)

def download_video(url: str, output_dir: str) -> str:
    """
    Downloads a video from the given URL using yt-dlp.
    Optimized for short video platforms (Douyin, Bilibili, etc.).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    outtmpl = os.path.join(output_dir, '%(id)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': True,
    }
    
    logger.info(f"Downloading video from {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            # Retrieve the path to the downloaded file
            # Fallback to manual string construction if not in requested_downloads
            video_path = None
            if 'requested_downloads' in info_dict and len(info_dict['requested_downloads']) > 0:
                video_path = info_dict['requested_downloads'][0]['filepath']
            else:
                video_id = info_dict.get('id', 'video')
                ext = info_dict.get('ext', 'mp4')
                video_path = os.path.join(output_dir, f"{video_id}.{ext}")
            
            logger.info(f"Successfully downloaded video to {video_path}")
            return video_path
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        raise