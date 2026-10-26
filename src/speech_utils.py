"""
Voice and Speech Utilities for NagorikAI.
Generates Bangla TTS audio from answer text.
Aggressively cleans input to avoid reading out JSON, URLs, English keys, and markdown.
"""

import os
import re
import hashlib
import ssl
from typing import Optional

# Fix SSL certificate issues on macOS
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

try:
    from gtts import gTTS
    _GTTS_AVAILABLE = True
except ImportError:
    _GTTS_AVAILABLE = False

AUDIO_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch", "audio_cache")


def _clean_for_tts(text: str, max_chars: int = 500) -> str:
    """
    Strips markdown, URLs, JSON fragments, and English technical words
    so gTTS reads clean Bengali text only.
    """
    # 1. Remove URLs (http/https/www)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # 2. Remove markdown headers (#, ##, ###) and bold/italic markers (**, *, `)
    text = re.sub(r'#{1,4}\s*', '', text)
    text = re.sub(r'\*{1,2}', '', text)
    text = re.sub(r'`[^`]*`', '', text)  # inline code
    text = re.sub(r'`', '', text)

    # 3. Remove JSON-like fragments: keys in quotes, curly braces, square brackets
    text = re.sub(r'\{[^}]*\}', '', text)  # {...}
    text = re.sub(r'"[a-z_A-Z0-9]+":\s*', '', text)  # "key":
    text = re.sub(r'\[[^\]]*\]', '', text)  # [...]

    # 4. Remove English-only words that are technical jargon (not needed in speech)
    # Keep Bengali characters and common Bengali-friendly digits/punctuation
    text = re.sub(r'\b[a-zA-Z]{4,}\b', '', text)  # strip long English words
    # But keep short ones that could be meaningful (NID, DCR kept as-is — short)

    # 5. Remove emoji (most ranges)
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    text = re.sub(r'[\u2600-\u27BF]', '', text)
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)

    # 6. Replace bullet/dash list markers with natural speech pause
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)

    # 7. Collapse multiple spaces/newlines
    text = re.sub(r'\n+', '। ', text)
    text = re.sub(r'\s{2,}', ' ', text)

    # 8. Trim and cap
    text = text.strip()
    return text[:max_chars]


def text_to_bangla_speech(text: str, max_chars: int = 500) -> Optional[str]:
    """
    Converts Bangla text to an MP3 audio file using gTTS.
    Returns the local path to the generated MP3, or None if unavailable.
    """
    if not _GTTS_AVAILABLE or not text:
        return None

    try:
        os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
    except Exception:
        pass

    clean_text = _clean_for_tts(text, max_chars=max_chars)

    if not clean_text or len(clean_text.strip()) < 5:
        return None

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
