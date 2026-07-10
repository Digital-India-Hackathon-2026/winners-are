from pydantic import BaseModel, Field

class AppForensicsResult(BaseModel):
    """
    App Forensic verification result details.
    Represents payment app detection, layout consistency, and suspected cloning indicator.
    """
    detected_app: str = Field(..., description="Google Pay, PhonePe, Paytm, BHIM, Cred, Unknown, Suspicious clone UI")
    app_authenticity_score: float = Field(..., ge=0.0, le=1.0, description="Calculated app structure authenticity score (0.0 to 1.0)")
    logo_match: bool = Field(..., description="True if dominant color and logos match claimed app")
    layout_consistency: str = Field(..., description="HIGH, MEDIUM, LOW")
    font_consistency: str = Field(..., description="NORMAL, SUSPICIOUS, INCONSISTENT")
    suspected_clone: bool = Field(..., description="True if UI anomalies indicate a cloned interface")
    ela_anomaly_score: float = Field(0.0, description="Error Level Analysis max anomaly score (0.0 to 1.0)")
    forensic_explanation: str = Field(..., description="Detailed explanation of the findings")
