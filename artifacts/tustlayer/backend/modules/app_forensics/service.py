import asyncio
from backend.modules.app_forensics.schemas import AppForensicsResult
from backend.modules.app_forensics.engine import AppForensicsEngine


class AppForensicsService:
    def __init__(self):
        self.engine = AppForensicsEngine()

    async def analyze_image(self, image_bytes: bytes, raw_text: str, claimed_app: str = None) -> AppForensicsResult:
        """
        Dual-validation: deterministic color fingerprint + NemotronNano12BVL AI branding check.
        Runs AI task in parallel with deterministic analysis; blends authenticity_score if AI succeeds.
        """
        from backend.integrations.nvidia_client import NemotronNano12BVLProvider

        deterministic_task = asyncio.get_event_loop().run_in_executor(
            None, self.engine.analyze, image_bytes, raw_text, claimed_app
        )
        ai_task = self._run_ai_branding(image_bytes)

        deterministic_result, ai_branding = await asyncio.gather(
            deterministic_task, ai_task, return_exceptions=True
        )

        if isinstance(deterministic_result, Exception):
            print(f"[APP-FORENSICS] Deterministic engine failed: {deterministic_result}")
            deterministic_result = AppForensicsResult(
                claimed_app=claimed_app or "Unknown",
                detected_app="Unknown",
                logo_match=False,
                layout_consistency="LOW",
                font_consistency="UNKNOWN",
                suspected_clone=False,
                app_authenticity_score=0.5,
                forensic_explanation="Deterministic analysis failed.",
            )

        if isinstance(ai_branding, Exception) or not ai_branding:
            return deterministic_result

        try:
            ai_confidence = float(ai_branding.get("confidence", 0.0))
            ai_match = bool(ai_branding.get("branding_match", True))
            ai_app = ai_branding.get("app_name", "")
            ai_explanation = ai_branding.get("explanation", "")

            blended_score = deterministic_result.app_authenticity_score * 0.65 + ai_confidence * 0.35
            
            # Determine final app detection and brand matching dynamically
            if ai_app and ai_app != "Unknown":
                deterministic_result.detected_app = ai_app
                
                # Check for branding mismatch with claimed OCR app name
                claimed = deterministic_result.claimed_app
                if claimed and claimed != "Unknown" and ai_app.lower() != claimed.lower():
                    deterministic_result.logo_match = False
                    deterministic_result.layout_consistency = "LOW"
                    blended_score = min(blended_score, 0.35)
                    ai_explanation = f"Mismatched Branding: Visual layout is {ai_app}, but text claims {claimed}. {ai_explanation}"
                else:
                    deterministic_result.logo_match = ai_match
                    if not ai_match:
                        deterministic_result.layout_consistency = "LOW"
                    else:
                        deterministic_result.layout_consistency = "HIGH"
            else:
                deterministic_result.detected_app = "Unknown"
                deterministic_result.logo_match = False
                deterministic_result.layout_consistency = "LOW"

            if deterministic_result.logo_match is False:
                deterministic_result.suspected_clone = True
                
            deterministic_result.app_authenticity_score = round(blended_score, 3)

            if ai_explanation:
                deterministic_result.forensic_explanation = ai_explanation

            print(f"[APP-FORENSICS] Dynamic validation complete — Detected: {deterministic_result.detected_app}, Claimed: {deterministic_result.claimed_app}, Match: {deterministic_result.logo_match}")
        except Exception as e:
            print(f"[APP-FORENSICS] Dynamic validation failed: {e}")

        return deterministic_result

    async def _run_ai_branding(self, image_bytes: bytes) -> dict:
        """Run AI branding validation via Gemini (preferred), Groq or Nemotron VL."""
        try:
            from backend.core.config import settings
            if settings.GEMINI_API_KEY or settings.GEMINI_API_KEYS:
                from backend.integrations.gemini_client import GeminiVisionProvider
                provider = GeminiVisionProvider()
                return await provider.verify_branding(image_bytes)
            elif settings.GROQ_API_KEY:
                from backend.integrations.groq_client import GroqVisionProvider
                provider = GroqVisionProvider()
                return await provider.verify_branding(image_bytes)

            from backend.integrations.nvidia_client import NemotronNano12BVLProvider
            provider = NemotronNano12BVLProvider()
            result = await provider._run_task(
                "branding_auth",
                provider.TASK_PROMPTS["branding_auth"][1],
                image_bytes
            )
            return result or {}
        except Exception as e:
            print(f"[APP-FORENSICS] AI branding task failed: {e}")
            return {}


def get_app_forensics_service() -> AppForensicsService:
    return AppForensicsService()
