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
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

    # v2.0 Model IDs
    OCR_MODEL: str = os.getenv("OCR_MODEL", "nvidia/nemotron-ocr-v2")
    VISUAL_AI_MODEL: str = os.getenv("VISUAL_AI_MODEL", "nvidia/nemotron-nano-12b-v2-vl")
    REASONING_MODEL: str = os.getenv("REASONING_MODEL", "meta/llama-3.3-70b-instruct")
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "meta/llama-3.1-8b-instruct")
    DEEPFAKE_MODEL: str = os.getenv("DEEPFAKE_MODEL", "hive/deepfake-image-detection")
    CONTENT_SAFETY_MODEL: str = os.getenv("CONTENT_SAFETY_MODEL", "nvidia/nemotron-content-safety-reasoning-4b")
    LLAMA_GUARD_MODEL: str = os.getenv("LLAMA_GUARD_MODEL", "meta/llama-guard-4-12b")

    # External API keys (new in v2.0)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    GOOGLE_SAFE_BROWSING_KEY: str = os.getenv("GOOGLE_SAFE_BROWSING_KEY", "")
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
