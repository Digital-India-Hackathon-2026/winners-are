import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TrustLayer AI"
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")

    # AI Providers
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY") or ""
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL") or "https://integrate.api.nvidia.com/v1"

    # v2.0 Model IDs
    OCR_MODEL: str = os.getenv("OCR_MODEL") or "nvidia/nemotron-ocr-v2"
    VISUAL_AI_MODEL: str = os.getenv("VISUAL_AI_MODEL") or "nvidia/nemotron-nano-12b-v2-vl"
    REASONING_MODEL: str = os.getenv("REASONING_MODEL") or "meta/llama-3.3-70b-instruct"
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL") or "meta/llama-3.1-8b-instruct"
    DEEPFAKE_MODEL: str = os.getenv("DEEPFAKE_MODEL") or "hive/deepfake-image-detection"
    CONTENT_SAFETY_MODEL: str = os.getenv("CONTENT_SAFETY_MODEL") or "nvidia/nemotron-content-safety-reasoning-4b"
    LLAMA_GUARD_MODEL: str = os.getenv("LLAMA_GUARD_MODEL") or "meta/llama-guard-4-12b"

    # External API keys (new in v2.0)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID") or ""
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET") or ""
    GOOGLE_SAFE_BROWSING_KEY: str = os.getenv("GOOGLE_SAFE_BROWSING_KEY") or ""
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY") or ""

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or ""
    GEMINI_API_KEYS: str = os.getenv("GEMINI_API_KEYS") or ""

    # Groq API keys and models
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY") or ""
    GROQ_MODEL: str = os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"
    GROQ_VISION_MODEL: str = os.getenv("GROQ_VISION_MODEL") or "meta-llama/llama-4-scout-17b-16e-instruct"

    # Twilio WhatsApp Bot
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID") or ""
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN") or ""
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER") or ""  # e.g. whatsapp:+14155238886

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
