"""
Voice and Speech Utilities for CivicSphere AI.
Includes Bangla Text-to-Speech (gTTS) audio generation and Web Speech API component.
"""

import os
import hashlib
from typing import Optional
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

AUDIO_CACHE_DIR = "/Users/tamimarahmanchoity/.gemini/antigravity/scratch/civicsphere-ai/scratch/audio_cache"

def text_to_bangla_speech(text: str, max_chars: int = 300) -> Optional[str]:
    """
    Converts Bangla text summary to an MP3 audio file using gTTS (if installed).
    Returns path to the generated audio file or None if unavailable.
    """
    if gTTS is None:
        return None

    os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

    # Clean text: remove markdown symbols and emojis for cleaner speech synthesis
    clean_text = text.replace("#", "").replace("*", "").replace("-", " ")
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
    except Exception as e:
        return None

def get_voice_input_html() -> str:
    """
    Returns an HTML snippet with Web Speech API configured for 'bn-BD' (Bengali - Bangladesh).
    Allows direct in-browser voice transcription.
    """
    return """
    <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-weight: 600; color: #166534; font-size: 14px;">🎙️ ভয়েস ইনপুট (বাংলা - bn-BD):</span>
            <button id="voiceBtn" onclick="toggleVoice()" style="background: #16a34a; color: white; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 13px;">
                🎤 বাংলায় কথা বলুন
            </button>
        </div>
        <p id="voiceStatus" style="font-size: 12px; color: #4b5563; margin-top: 6px; margin-bottom: 0px;">
            মাইক্রোফোন বাটনে ক্লিক করে প্রশ্ন করুন (যেমন: "পাসপোর্টের সরকারি ফি কত?")
        </p>
        <div id="transcriptBox" style="margin-top: 6px; font-size: 13px; font-weight: 500; color: #0f172a;"></div>
    </div>

    <script>
        let recognition = null;
        let isRecording = false;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRec();
            recognition.lang = 'bn-BD';
            recognition.continuous = false;
            recognition.interimResults = true;

            recognition.onstart = function() {
                isRecording = true;
                document.getElementById('voiceBtn').innerText = '⏹️ শুনছি... কথা বলুন';
                document.getElementById('voiceBtn').style.background = '#dc2626';
                document.getElementById('voiceStatus').innerText = 'শুনছি... আপনার প্রশ্ন বাংলায় বলুন।';
            };

            recognition.onresult = function(event) {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    transcript += event.results[i][0].transcript;
                }
                document.getElementById('transcriptBox').innerText = 'বলছেন: ' + transcript;
            };

            recognition.onend = function() {
                isRecording = false;
                document.getElementById('voiceBtn').innerText = '🎤 বাংলায় কথা বলুন';
                document.getElementById('voiceBtn').style.background = '#16a34a';
                document.getElementById('voiceStatus').innerText = 'রেকর্ডিং সম্পন্ন। নিচের ইনপুট বক্সে প্রশ্নটি পেস্ট বা টাইপ করুন।';
            };

            recognition.onerror = function(event) {
                isRecording = false;
                document.getElementById('voiceBtn').innerText = '🎤 বাংলায় কথা বলুন';
                document.getElementById('voiceBtn').style.background = '#16a34a';
                document.getElementById('voiceStatus').innerText = 'ভয়েস সনাক্ত করা যায়নি। অনুগ্রহ করে মাইক্রোফোন অনুমতি নিশ্চিত করুন।';
            };
        } else {
            document.getElementById('voiceBtn').disabled = true;
            document.getElementById('voiceStatus').innerText = 'আপনার ব্রাউজার Web Speech API সমর্থন করে না (Google Chrome ব্যবহার করুন)।';
        }

        function toggleVoice() {
            if (!recognition) return;
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        }
    </script>
    """
