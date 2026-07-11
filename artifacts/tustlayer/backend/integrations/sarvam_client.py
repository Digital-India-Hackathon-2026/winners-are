import httpx
from typing import Optional
from backend.core.config import settings

# Supported Indian languages and their Sarvam language codes
LANGUAGE_MAP = {
    "hi": "hi-IN",
    "hindi": "hi-IN",
    "हिंदी": "hi-IN",
    
    "te": "te-IN",
    "telugu": "te-IN",
    "తెలుగు": "te-IN",
    
    "ta": "ta-IN",
    "tamil": "ta-IN",
    "தமிழ்": "ta-IN",
    
    "kn": "kn-IN",
    "kannada": "kn-IN",
    "ಕನ್ನಡ": "kn-IN",
    
    "mr": "mr-IN",
    "marathi": "mr-IN",
    "मराठी": "mr-IN",
    
    "bn": "bn-IN",
    "bengali": "bn-IN",
    "বাংলা": "bn-IN",
    
    "gu": "gu-IN",
    "gujarati": "gu-IN",
    "ગુજરાતી": "gu-IN",
    
    "ml": "ml-IN",
    "malayalam": "ml-IN",
    "മലയാളം": "ml-IN",
    
    "pa": "pa-IN",
    "punjabi": "pa-IN",
    "ਪੰਜਾਬੀ": "pa-IN",
    
    "en": "en-IN",
    "english": "en-IN",
}

class SarvamClient:
    def __init__(self):
        self.api_url = "https://api.sarvam.ai/translate"
        self.api_key = settings.SARVAM_API_KEY
        self.client = httpx.AsyncClient(timeout=15.0)

    async def translate(self, text: str, target_lang_code: str, source_lang_code: str = "en-IN") -> str:
        """
        Translates text to target language using Sarvam Mayura translation model.
        Falls back to returning original text if translation fails or key is missing.
        """
        if not self.api_key or not text or target_lang_code == "en-IN":
            return text

        payload = {
            "input": text,
            "source_language_code": source_lang_code,
            "target_language_code": target_lang_code,
            "model": "sarvam-translate:v1"
        }
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            resp = await self.client.post(self.api_url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("translated_text", "")
                if translated:
                    return translated
            print(f"[SARVAM] Translation API error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"[SARVAM] Translation failed: {e}")
        
        return text

_client: Optional[SarvamClient] = None

def get_sarvam_client() -> SarvamClient:
    global _client
    if _client is None:
        _client = SarvamClient()
    return _client
