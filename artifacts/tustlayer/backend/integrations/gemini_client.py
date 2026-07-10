import os
import time
import json
import re
import itertools
from typing import Dict, List, Any, Optional
import httpx
from backend.core.config import settings
from backend.core.ai_orchestrator import VisionProvider, ReasoningProvider
from backend.integrations.nvidia_client import _encode_image, _extract_json_from_content

def _init_key_pool():
    keys = []
    if settings.GEMINI_API_KEYS:
        keys = [k.strip() for k in settings.GEMINI_API_KEYS.split(",") if k.strip()]
    if not keys and settings.GEMINI_API_KEY:
        keys = [settings.GEMINI_API_KEY.strip()]
    return itertools.cycle(keys) if keys else None

_KEY_POOL = _init_key_pool()

def get_next_gemini_key() -> str:
    if _KEY_POOL:
        return next(_KEY_POOL)
    return settings.GEMINI_API_KEY or ""


class GeminiClientBase:
    """Base client supporting automatic API key rotation and request handling."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _make_request(self, payload: Dict[str, Any], use_json: bool = False, model: str = "gemini-1.5-flash") -> str:
        keys_count = len(settings.GEMINI_API_KEYS.split(",")) if settings.GEMINI_API_KEYS else 1
        last_error = None

        for _ in range(keys_count + 1):
            api_key = get_next_gemini_key()
            if not api_key:
                raise ValueError("No Gemini API keys are configured.")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            # Inject JSON mode configuration if requested
            if use_json:
                if "generationConfig" not in payload:
                    payload["generationConfig"] = {}
                payload["generationConfig"]["responseMimeType"] = "application/json"

            try:
                response = await self.client.post(url, json=payload, headers={"Content-Type": "application/json"})
                
                # Check for rate limiting / quota limits
                if response.status_code == 429 or "quota" in response.text.lower():
                    print(f"[GEMINI-CLIENT] Key ...{api_key[-5:]} hit limit (429/quota). Rotating to next key...")
                    continue
                
                response.raise_for_status()
                res_json = response.json()
                
                # Parse response path: candidates[0].content.parts[0].text
                return res_json["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"[GEMINI-CLIENT] Error using key ...{api_key[-5:]}: {e}")
                last_error = e
                continue

        if last_error:
            raise last_error
        raise ValueError("Failed to get response from Gemini API (all keys exhausted).")


class GeminiVisionProvider(GeminiClientBase, VisionProvider):
    """Multimodal Vision OCR and branding forensic analyzer using Gemini API."""

    async def extract_fields(self, image_bytes: bytes) -> dict:
        from backend.integrations.nvidia_client import NvidiaOCRExtractor
        b64, mime = _encode_image(image_bytes)

        payload = {
            "contents": [{
                "parts": [
                    {"text": f"{NvidiaOCRExtractor.SYSTEM_PROMPT}\n\n{NvidiaOCRExtractor.USER_PROMPT}"},
                    {"inlineData": {"mimeType": mime, "data": b64}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.1
            }
        }
        
        try:
            print("[GEMINI-VISION] Extracting transaction fields...")
            raw_response = await self._make_request(payload, use_json=True)
            parsed = _extract_json_from_content(raw_response)
            return parsed or {}
        except Exception as e:
            print(f"[GEMINI-VISION] Field extraction failed: {e}")
            raise e

    async def verify_branding(self, image_bytes: bytes) -> dict:
        b64, mime = _encode_image(image_bytes)
        system_prompt = (
            "You are a payment app branding authentication expert.\n"
            "Analyze if the UI branding (logo, colors, layout) matches an authentic known payment app.\n"
            "CRITICAL: Identify the app based strictly on visual design system layout and colors, NOT by text contents or recipient VPA details. "
            "For example, a Google Pay screenshot transferring to a PhonePe VPA is still a Google Pay screenshot (NOT PhonePe). "
            "Google Pay uses a blue success circle at the top-center. PhonePe has purple accents. Paytm uses cyan/teal banners. "
            "super.money has a Flipkart-group blue/purple layout with a green success checkbox.\n"
            "Return ONLY JSON: {\"app_name\": \"string\", \"branding_match\": bool, \"confidence\": 0.0-1.0, \"explanation\": \"string\"}"
        )

        payload = {
            "contents": [{
                "parts": [
                    {"text": system_prompt},
                    {"inlineData": {"mimeType": mime, "data": b64}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.1
            }
        }

        try:
            print("[GEMINI-VISION] Verifying branding design system...")
            raw_response = await self._make_request(payload, use_json=True)
            parsed = _extract_json_from_content(raw_response)
            return parsed or {}
        except Exception as e:
            print(f"[GEMINI-VISION] Branding verification failed: {e}")
            raise e

    async def detect_anomalies(self, image_bytes: bytes) -> List[str]:
        return []


class GeminiReasoningProvider(GeminiClientBase, ReasoningProvider):
    """AI Reasoning model generator using Gemini API."""

    async def generate_reasons(self, context_data: Dict[str, Any]) -> List[str]:
        prompt = (
            "You are a forensic payment analyst for India's UPI system.\n"
            "Generate 3-5 SHORT punchy forensic bullet points (max 15 words each).\n"
            "Focus on the most significant risk signals. No preamble. No verbose explanations.\n"
            "Each bullet is a direct, specific observation about the payment's authenticity.\n"
            f"Forensic context: {json.dumps(context_data)}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }

        try:
            raw_response = await self._make_request(payload)
            return self._parse_bullets(raw_response)
        except Exception as e:
            print(f"[GEMINI-REASONING] generate_reasons failed: {e}")
            raise e

    async def generate_recommendations(self, risk_level: str, context_data: Dict[str, Any]) -> List[str]:
        prompt = (
            "You are an expert fraud investigator.\n"
            f"Given a risk level of '{risk_level}', generate 2-3 specific, actionable recommendation bullets (max 18 words each).\n"
            "Address how the merchant should handle this transaction. No preamble. Direct instructions only.\n"
            f"Forensic Context: {json.dumps(context_data)}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }

        try:
            raw_response = await self._make_request(payload)
            return self._parse_bullets(raw_response)
        except Exception as e:
            print(f"[GEMINI-REASONING] generate_recommendations failed: {e}")
            raise e

    async def generate_what_to_do_next(self, risk_level: str, context_data: Dict[str, Any]) -> List[str]:
        prompt = (
            "You are a cash counter supervisor.\n"
            "Provide 2-3 quick actionable steps for the cashier to perform next (max 12 words each).\n"
            f"Risk Level: {risk_level}\n"
            "No preamble. Step-by-step only.\n"
            f"Forensic Context: {json.dumps(context_data)}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }

        try:
            raw_response = await self._make_request(payload)
            return self._parse_bullets(raw_response)
        except Exception as e:
            print(f"[GEMINI-REASONING] generate_what_to_do_next failed: {e}")
            raise e

    def _parse_bullets(self, text: str) -> List[str]:
        bullets = []
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Strip bullet prefixes (e.g. -, *, 1., 2.)
            cleaned = re.sub(r'^(?:[-*+•]|\d+\.)\s*', '', line).strip()
            if cleaned:
                bullets.append(cleaned)
        return bullets[:5]
