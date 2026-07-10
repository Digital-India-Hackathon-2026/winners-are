"""
TrustLayer AI – Deepfake Detection Service v2.0
Wraps HiveDeepfakeDetector with graceful degradation.
"""
from backend.modules.deepfake.schemas import DeepfakeDetectionResult
from backend.integrations.nvidia_client import HiveDeepfakeDetector


class DeepfakeDetectionService:
    def __init__(self):
        self.detector = HiveDeepfakeDetector()

    async def analyze(self, image_bytes: bytes) -> DeepfakeDetectionResult:
        """
        Runs deepfake detection. Returns a neutral result on failure (no false positives).
        """
        try:
            result = await self.detector.detect(image_bytes)
            probability = float(result.get("deepfake_probability", 0.0))
            is_deepfake = bool(result.get("is_deepfake", False)) or probability > 0.30
            signals = result.get("signals", [])
            manip_type = result.get("manipulation_type", "none")
            error = result.get("error")

            print(f"[DEEPFAKE-SERVICE] probability={probability:.3f} is_deepfake={is_deepfake} type={manip_type}")

            return DeepfakeDetectionResult(
                deepfake_probability=round(probability, 4),
                is_deepfake=is_deepfake,
                manipulation_type=manip_type,
                signals=signals if isinstance(signals, list) else [],
                error=error,
            )
        except Exception as e:
            print(f"[DEEPFAKE-SERVICE] Detection error — using neutral result: {e}")
            return DeepfakeDetectionResult(
                deepfake_probability=0.0,
                is_deepfake=False,
                manipulation_type="unknown",
                error=str(e),
            )


def get_deepfake_service() -> DeepfakeDetectionService:
    return DeepfakeDetectionService()
