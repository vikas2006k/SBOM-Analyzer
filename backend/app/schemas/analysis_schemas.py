from pydantic import BaseModel, Field
from typing import Dict

class AnalysisRequestSchema(BaseModel):
    """Schema validating risk evaluation triggers."""
    application_id: int = Field(..., ge=1, description="Database application key index")

class RiskScoreResponseSchema(BaseModel):
    """Schema formatting calculated application risk parameters output."""
    application_id: int
    overall_score: float = Field(..., ge=0.0, le=100.0)
    cvss_subscore: float = Field(..., ge=0.0, le=100.0)
    license_subscore: float = Field(..., ge=0.0, le=100.0)
    maintenance_subscore: float = Field(..., ge=0.0, le=100.0)
    factors_summary: Dict[str, str] = Field(default_factory=dict, description="Summary of risk contributions")
