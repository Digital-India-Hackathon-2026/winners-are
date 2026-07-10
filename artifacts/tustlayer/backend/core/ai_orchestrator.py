import time
from typing import Protocol, List

class VisionProvider(Protocol):
    async def extract_fields(self, image_bytes: bytes) -> dict:
        ...
    async def detect_anomalies(self, image_bytes: bytes) -> List[str]:
        ...

class AIOrchestrator:
    def __init__(self, primary: VisionProvider, fallback: VisionProvider = None):
        self.primary = primary
        self.fallback = fallback
    
    async def extract_with_fallback(self, image_bytes: bytes) -> dict:
        start_time = time.time()
        print("[TRUSTLAYER-DEBUG] AIOrchestrator: Executing VisionProvider extraction...")
        try:
            res = await self.primary.extract_fields(image_bytes)
            elapsed = int((time.time() - start_time) * 1000)
            print(f"[TRUSTLAYER-DEBUG] AIOrchestrator: Vision extraction completed in {elapsed}ms.")
            return res
        except Exception as e:
            print(f"[TRUSTLAYER-DEBUG] AIOrchestrator: Primary Vision provider failed: {e}. Falling back...")
            if self.fallback:
                return await self.fallback.extract_fields(image_bytes)
            raise e

class ReasoningProvider(Protocol):
    async def generate_reasons(self, context_data: dict) -> List[str]:
        ...
    async def generate_recommendations(self, risk_level: str, context_data: dict) -> List[str]:
        ...
    async def generate_what_to_do_next(self, risk_level: str, context_data: dict) -> List[str]:
        ...

class AIReasoningOrchestrator:
    def __init__(self, primary: ReasoningProvider, fallback: ReasoningProvider):
        self.primary = primary
        self.fallback = fallback
    
    async def get_reasoning_with_fallback(self, context_data: dict) -> List[str]:
        start_time = time.time()
        print("[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Requesting reasoning generation...")
        try:
            res = await self.primary.generate_reasons(context_data)
            elapsed = int((time.time() - start_time) * 1000)
            print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Primary Reasoning completed in {elapsed}ms.")
            return res
        except Exception as e:
            print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Primary reasoning provider failed: {e}. Falling back to degraded mode...")
            try:
                res_fallback = await self.fallback.generate_reasons(context_data)
                print("[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Fallback reasoning generated successfully.")
                return res_fallback
            except Exception as e2:
                print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Fallback reasoning provider failed: {e2}")
                return ["System was unable to generate detailed reasoning due to service unavailability."]

    async def get_recommendations_with_fallback(self, risk_level: str, context_data: dict) -> List[str]:
        start_time = time.time()
        print("[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Requesting recommendations...")
        try:
            res = await self.primary.generate_recommendations(risk_level, context_data)
            elapsed = int((time.time() - start_time) * 1000)
            print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Primary Recommendations completed in {elapsed}ms.")
            return res
        except Exception as e:
            print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Primary recommendation provider failed: {e}. Falling back...")
            try:
                return await self.fallback.generate_recommendations(risk_level, context_data)
            except Exception as e2:
                print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Fallback recommendation provider failed: {e2}")
                return ["Contact support for further assistance."]

    async def get_what_to_do_next_with_fallback(self, risk_level: str, context_data: dict) -> List[str]:
        start_time = time.time()
        print("[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Requesting what-to-do-next steps...")
        try:
            res = await self.primary.generate_what_to_do_next(risk_level, context_data)
            elapsed = int((time.time() - start_time) * 1000)
            print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Primary What-to-do completed in {elapsed}ms.")
            return res
        except Exception as e:
            print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Primary what-to-do provider failed: {e}. Falling back...")
            try:
                return await self.fallback.generate_what_to_do_next(risk_level, context_data)
            except Exception as e2:
                print(f"[TRUSTLAYER-DEBUG] AIReasoningOrchestrator: Fallback what-to-do provider failed: {e2}")
                # Use default fallback list if both fail
                if hasattr(self.primary, "_default_what_to_do"):
                    return self.primary._default_what_to_do(risk_level)
                return ["Verify receipt in bank account before handing over goods."]
