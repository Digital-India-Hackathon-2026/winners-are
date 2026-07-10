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
    """Primary vision OCR extractor using Groq API with multi-model fallback."""

    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.models = [
            settings.GROQ_VISION_MODEL,
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "qwen/qwen3.6-27b",
        ]
        # De-duplicate while preserving order
        self.models = list(dict.fromkeys([m for m in self.models if m]))
        self.client = httpx.AsyncClient(timeout=30.0)

    async def extract_fields(self, image_bytes: bytes) -> dict:
        from backend.integrations.nvidia_client import NvidiaOCRExtractor
        b64, mime = _encode_image(image_bytes)
        
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        last_error = None
        for model in self.models:
            payload = {
                "model": model,
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
            try:
                start = time.time()
                print(f"[GROQ-VISION] Requesting '{model}'...")
                response = await self.client.post(self.api_url, json=payload, headers=headers)
                if response.status_code != 200:
                    print(f"[GROQ-VISION] Model {model} failed with status {response.status_code}: {response.text}")
                    response.raise_for_status()
                
                elapsed = int((time.time() - start) * 1000)
                print(f"[GROQ-VISION] Model {model} succeeded in {elapsed}ms")
                content = response.json()["choices"][0]["message"]["content"]
                parsed = _extract_json_from_content(content)
                if parsed:
                    return parsed
            except Exception as e:
                print(f"[GROQ-VISION] Model {model} failed: {e}")
                last_error = e
        
        if last_error:
            raise last_error
        return {}

    async def detect_anomalies(self, image_bytes: bytes) -> List[str]:
        return []

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
        
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        for model in self.models:
            payload = {
                "model": model,
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
            try:
                start = time.time()
                print(f"[GROQ-BRANDING] Requesting '{model}'...")
                response = await self.client.post(self.api_url, json=payload, headers=headers)
                if response.status_code != 200:
                    print(f"[GROQ-BRANDING] Model {model} failed with status {response.status_code}: {response.text}")
                    response.raise_for_status()
                
                elapsed = int((time.time() - start) * 1000)
                print(f"[GROQ-BRANDING] Model {model} succeeded in {elapsed}ms")
                content = response.json()["choices"][0]["message"]["content"]
                parsed = _extract_json_from_content(content)
                if parsed:
                    return parsed
            except Exception as e:
                print(f"[GROQ-BRANDING] Model {model} failed: {e}")
        return {}

    async def verify_page_safety(self, image_bytes: bytes) -> dict:
        b64, mime = _encode_image(image_bytes)
        system_prompt = (
            "You are an automated content safety moderator. "
            "Analyze the provided document page image for safety violations. Check for any explicit nudity, adult content, suggestive imagery, or severe violence. "
            "Return ONLY JSON: {\"is_safe\": bool, \"flagged_category\": \"string\", \"explanation\": \"string\"}"
        )
        
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        for model in self.models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Analyze the safety of this document page."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                    ]}
                ],
                "max_tokens": 512,
                "temperature": 0.1,
            }
            try:
                start = time.time()
                print(f"[GROQ-SAFETY] Requesting safety moderation on '{model}'...")
                response = await self.client.post(self.api_url, json=payload, headers=headers)
                if response.status_code != 200:
                    print(f"[GROQ-SAFETY] Model {model} returned error: {response.text}")
                    response.raise_for_status()
                
                elapsed = int((time.time() - start) * 1000)
                print(f"[GROQ-SAFETY] Model {model} processed in {elapsed}ms")
                content = response.json()["choices"][0]["message"]["content"]
                parsed = _extract_json_from_content(content)
                if parsed:
                    return parsed
            except Exception as e:
                print(f"[GROQ-SAFETY] Model {model} failed: {e}")
        return {"is_safe": True, "flagged_category": "none", "explanation": "Failed to run safety analysis."}


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
                        "If the risk level is high or fraudulent transaction is suspected, you MUST include: "
                        "1. Call the national cyber fraud helpline 1930 immediately. "
                        "2. Report the incident on the National Cyber Crime Reporting Portal (cybercrime.gov.in). "
                        "3. File a complaint on the National Consumer Helpline (NCH). "
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
                        "If the proof is suspected fake/manipulated, prioritize calling the cyber helpline 1930 and reporting to cybercrime.gov.in. "
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
