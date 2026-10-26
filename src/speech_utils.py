"""
Voice and Speech Utilities for NagorikAI.
Includes Bangla Text-to-Speech (gTTS) audio generation and in-browser audio playback.
(Voice input removed as per user requirements; voice output / answer audio playback active).
"""

import os
import hashlib
from typing import Optional

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# Local app cache directory (cross-platform compatible for local and Streamlit Cloud)
AUDIO_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch", "audio_cache")

def text_to_bangla_speech(text: str, max_chars: int = 400) -> Optional[str]:
    """
    Converts Bangla text summary to an MP3 audio file using gTTS.
    Returns local path to the generated audio file or None if unavailable.
    """
    if gTTS is None or not text:
        return None

    try:
        os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
    except Exception:
        pass

    # Clean text: remove markdown symbols and non-speech symbols for natural synthesis
    clean_text = text.replace("#", "").replace("*", "").replace("-", " ").replace("`", "")
    # Remove emojis
    clean_text = "".join([c for c in clean_text if ord(c) < 0x1F600 or ord(c) > 0x1F64F])
    clean_text = clean_text[:max_chars].strip()

    if not clean_text:
        return None

    # Cache key based on md5 hash
    text_hash = hashlib.md5(clean_text.encode('utf-8')).hexdigest()
    out_path = os.path.join(AUDIO_CACHE_DIR, f"speech_{text_hash}.mp3")

    if os.path.exists(out_path):
        return out_path

    try:
        tts = gTTS(text=clean_text, lang='bn', slow=False)
        tts.save(out_path)
        return out_path
    except Exception:
        return None
