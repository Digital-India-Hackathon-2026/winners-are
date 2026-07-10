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

            if not ai_match:
                blended_score = min(blended_score, 0.70)
                deterministic_result.suspected_clone = True
                deterministic_result.layout_consistency = "LOW"

            deterministic_result.app_authenticity_score = round(blended_score, 3)

            if ai_app and ai_app != "Unknown" and deterministic_result.detected_app == "Unknown":
                deterministic_result.detected_app = ai_app

            if ai_explanation:
                deterministic_result.forensic_explanation = (
                    f"{deterministic_result.forensic_explanation} [AI: {ai_explanation}]"
                )

            print(f"[APP-FORENSICS] Dual-validated — deterministic+AI blended score: {deterministic_result.app_authenticity_score:.2f}")
        except Exception as e:
            print(f"[APP-FORENSICS] AI blend failed (using deterministic only): {e}")

        return deterministic_result

    async def _run_ai_branding(self, image_bytes: bytes) -> dict:
        """Run NemotronNano12BVL branding_auth task only. Returns raw dict or {}."""
        try:
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
