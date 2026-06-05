import logging
import json
from openai import OpenAI

logger = logging.getLogger(__name__)

def translate_subtitles(subtitles: list[dict]) -> list[dict]:
    """
    Translates Chinese subtitles to Vietnamese using GPT-4o while preserving structure.
    """
    logger.info(f"Translating {len(subtitles)} subtitle segments.")
    client = OpenAI()
    
    system_prompt = (
        "You are an expert translator specializing in transforming Chinese internet slang, "
        "short-video content, and technical terms into natural, trendy, and engaging Vietnamese. "
        "You will receive a JSON array of subtitle segments. "
        "Translate the 'text' field of each segment to Vietnamese. "
        "Return the output as a JSON object containing a single key 'subtitles' mapped to the updated array of objects. "
        "Maintain the exact array structure and all timestamps. Do not skip any item."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(subtitles, ensure_ascii=False)}
            ],
            response_format={ "type": "json_object" },
            temperature=0.3
        )
        
        result_content = response.choices[0].message.content
        translated_data = json.loads(result_content)
        translated_subtitles = translated_data.get("subtitles", [])
        
        if len(translated_subtitles) != len(subtitles):
            logger.warning("Translated subtitles length mismatch. Output length differs from input length.")
            
        logger.info("Successfully translated subtitles.")
        return translated_subtitles
    except Exception as e:
        logger.error(f"Failed to translate subtitles: {e}")
        raise