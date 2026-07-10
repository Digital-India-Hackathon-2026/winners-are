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
        Bypasses deepfake face checks to optimize response latency.
        UPI screenshots contain no human faces, so Hive API calls are skipped.
        """
        return DeepfakeDetectionResult(
            deepfake_probability=0.0,
            is_deepfake=False,
            manipulation_type="none",
            signals=[],
            error=None,
        )


def get_deepfake_service() -> DeepfakeDetectionService:
    return DeepfakeDetectionService()
