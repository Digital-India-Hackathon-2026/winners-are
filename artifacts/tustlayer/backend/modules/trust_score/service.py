"""
TrustLayer AI – Trust Score Service v2.0
Orchestrates the full deterministic + AI reasoning pipeline.
"""
import asyncio
from backend.modules.trust_score.schemas import TrustScoreInput, TrustScoreResult
from backend.modules.trust_score.engine import TrustScoreEngine
from backend.modules.trust_score.escalation import RiskEscalationLayer
from backend.modules.trust_score.reasoning import ConfidenceReasoningGenerator, RecommendationEngine
from backend.core.ai_orchestrator import AIReasoningOrchestrator
from backend.integrations.nvidia_client import LlamaReasoningProvider, PhiReasoningProvider


class FinalDecisionAssembler:
    """
    Orchestrates the v2.0 deterministic scoring + AI reasoning pipeline.
    """
    def __init__(self):
        self.engine = TrustScoreEngine()
        self.escalation = RiskEscalationLayer()
        self.qwen = LlamaReasoningProvider()
        self.ai_orchestrator = AIReasoningOrchestrator(
            primary=self.qwen,
            fallback=PhiReasoningProvider()
        )
        self.reasoning = ConfidenceReasoningGenerator(self.ai_orchestrator)
        self.recommendations = RecommendationEngine(self.ai_orchestrator)

    async def evaluate(self, data: TrustScoreInput) -> TrustScoreResult:
        # 1. v2 additive scoring with hard caps
        final_score, breakdown, caps_triggered = TrustScoreEngine.calculate(data)

        # 2. Graduated verdict + risk level
        final_score, risk_level, fraud_prob, verdict = self.escalation.evaluate(data, final_score)

        # 3. Extraction quality label
        extraction_label = RiskEscalationLayer._compute_extraction_quality_label(data)

        # 4. AI reasoning — run ALL 3 calls in parallel (prevents 300s Vercel timeout)
        reasons_task = self.reasoning.generate_reasons(data)
        actions_task = self.recommendations.generate_recommendations(risk_level, data)
        what_to_do_task = self.ai_orchestrator.get_what_to_do_next_with_fallback(risk_level.value, data.model_dump())

        reasons, actions, what_to_do = await asyncio.gather(
            reasons_task, actions_task, what_to_do_task,
            return_exceptions=True
        )

        # Handle exceptions gracefully
        if isinstance(reasons, Exception):
            print(f"[TRUST-SCORE] Reasoning failed: {reasons}")
            reasons = ["Unable to generate forensic reasoning (service unavailable)."]
        if isinstance(actions, Exception):
            print(f"[TRUST-SCORE] Recommendations failed: {actions}")
            actions = ["Contact your bank immediately if you've already transferred money."]
        if isinstance(what_to_do, Exception):
            print(f"[TRUST-SCORE] What-to-do failed: {what_to_do}")
            what_to_do = self.qwen._default_what_to_do(risk_level.value)

        # 5. Append triggered hard-cap warnings to confidence reasoning
        if caps_triggered:
            reasons = [f"[Hard Cap] {cap}" for cap in caps_triggered] + reasons

        return TrustScoreResult(
            trust_score=final_score,
            risk_level=risk_level,
            fraud_probability=fraud_prob,
            confidence_reasoning=reasons,
            recommended_actions=actions,
            verdict=verdict,
            extraction_quality_label=extraction_label,
            what_to_do_next=what_to_do,
            score_breakdown=breakdown,
        )


def get_final_decision_assembler() -> FinalDecisionAssembler:
    return FinalDecisionAssembler()
