import base64
import json
import re
import time
from typing import Dict, List, Any, Optional
import httpx
from backend.core.config import settings
from backend.core.ai_orchestrator import VisionProvider, ReasoningProvider
from backend.integrations.nvidia_client import _encode_image, _extract_json_from_content

class GroqVisionProvider(VisionProvider):
    """Primary vision OCR extractor using Groq API."""

    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = settings.GROQ_VISION_MODEL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def extract_fields(self, image_bytes: bytes) -> dict:
        from backend.integrations.nvidia_client import NvidiaOCRExtractor
        b64, mime = _encode_image(image_bytes)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": NvidiaOCRExtractor.SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": NvidiaOCRExtractor.USER_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                ]}
            ],
            "max_tokens": 1024,
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        try:
            start = time.time()
            print(f"[GROQ-VISION] Requesting '{self.model}'...")
            response = await self.client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            elapsed = int((time.time() - start) * 1000)
            print(f"[GROQ-VISION] Response in {elapsed}ms")
            content = response.json()["choices"][0]["message"]["content"]
            parsed = _extract_json_from_content(content)
            return parsed or {}
        except Exception as e:
            print(f"[GROQ-VISION] FAILED: {e}")
            raise e

    async def detect_anomalies(self, image_bytes: bytes) -> List[str]:
        return []

    async def verify_branding(self, image_bytes: bytes) -> dict:
        b64, mime = _encode_image(image_bytes)
        system_prompt = (
            "You are a payment app branding authentication expert. "
            "Analyze if the UI branding (logo, colors, layout) matches an authentic known payment app. "
            "Return ONLY JSON: {\"app_name\": \"string\", \"branding_match\": bool, \"confidence\": 0.0-1.0, \"explanation\": \"string\"}"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyze the branding and authenticity of this UPI payment screenshot."},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                ]}
            ],
            "max_tokens": 512,
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        try:
            start = time.time()
            print(f"[GROQ-BRANDING] Requesting '{self.model}'...")
            response = await self.client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            elapsed = int((time.time() - start) * 1000)
            print(f"[GROQ-BRANDING] Response in {elapsed}ms")
            content = response.json()["choices"][0]["message"]["content"]
            parsed = _extract_json_from_content(content)
            return parsed or {}
        except Exception as e:
            print(f"[GROQ-BRANDING] FAILED: {e}")
            return {}


class GroqReasoningProvider(ReasoningProvider):
    """Primary reasoning logic provider using Groq API."""

    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = settings.GROQ_MODEL
        self.client = httpx.AsyncClient(timeout=20.0)

    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        start = time.time()
        print(f"[GROQ-REASONING] Requesting model '{self.model}'...")
        response = await self.client.post(self.api_url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"[GROQ-REASONING] Response in {int((time.time()-start)*1000)}ms")
        return response.json()

    async def generate_reasons(self, context_data: Dict[str, Any]) -> List[str]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a forensic payment analyst for India's UPI system. "
                        "Generate 3-5 SHORT punchy forensic bullet points (max 15 words each). "
                        "Focus on the most significant risk signals. No preamble. No verbose explanations. "
                        "Each bullet is a direct, specific observation about the payment's authenticity."
                    )
                },
                {
                    "role": "user",
                    "content": f"Forensic context: {json.dumps(context_data)}\nGenerate 3-5 forensic finding bullets."
                }
            ],
            "temperature": 0.3,
            "max_tokens": 400
        }
        try:
            result = await self._make_request(payload)
            content = result["choices"][0]["message"]["content"]
            return self._parse_bullets(content)
        except Exception as e:
            print(f"[GROQ-REASONING] generate_reasons failed: {e}")
            raise e

    async def generate_recommendations(self, risk_level: str, context_data: Dict[str, Any]) -> List[str]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a financial fraud prevention advisor for India. "
                        "Generate 3-4 SHORT, specific, actionable recommended steps (max 15 words each). "
                        "Tailor them to the risk level and specific fraud signals detected. No preamble."
                    )
                },
                {
                    "role": "user",
                    "content": f"Risk Level: {risk_level}\nContext: {json.dumps(context_data)}\nGenerate 3-4 actionable steps."
                }
            ],
            "temperature": 0.3,
            "max_tokens": 400
        }
        try:
            result = await self._make_request(payload)
            content = result["choices"][0]["message"]["content"]
            return self._parse_bullets(content)
        except Exception as e:
            print(f"[GROQ-REASONING] generate_recommendations failed: {e}")
            raise e

    async def generate_what_to_do_next(self, risk_level: str, context_data: Dict[str, Any]) -> List[str]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert Indian UPI payments advisor. "
                        "Generate 3 simple, direct, sequential next steps (max 10 words each) for the merchant receiving this payment proof. "
                        "Focus on quick validation actions. Output ONLY the bullets. No numbering. No headers. No preamble."
                    )
                },
                {
                    "role": "user",
                    "content": f"Risk Level: {risk_level}\nContext: {json.dumps(context_data)}"
                }
            ],
            "temperature": 0.3,
            "max_tokens": 400
        }
        try:
            result = await self._make_request(payload)
            content = result["choices"][0]["message"]["content"]
            return self._parse_bullets(content)
        except Exception as e:
            print(f"[GROQ-REASONING] generate_what_to_do_next failed: {e}")
            raise e

    def _parse_bullets(self, content: str) -> List[str]:
        if not content:
            return []
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        bullets = []
        for line in lines:
            line = re.sub(r'^[-*•\d\.\s]+', '', line).strip()
            if line:
                bullets.append(line)
        return bullets
