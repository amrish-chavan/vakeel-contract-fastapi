from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Contract(BaseModel):
    id: Optional[str] = None
    filename: str
    original_name: str
    file_path: str
    text: str
    upload_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    text_count: int
    word_count: int
    page_count: int = 1
    status: str = "uploaded"


class ClauseAnalysis(BaseModel):
    clause_title: str
    clause_text: str
    explanation: str
    is_standard: bool

class RiskFlag(BaseModel):
    risk_title: str
    description: str
    risk_level: str
    recommendation: str
    clause_reference: str

class AnalysisResult(BaseModel):
    id: Optional[str] = None
    contract_id: str
    analysis_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    summary: str = ""
    contract_type: str = ""
    key_clauses: list[ClauseAnalysis] = []
    risk_flags: list[RiskFlag] = []
    overall_risk: RiskLevel = RiskLevel.LOW
    recommendations: list[str] = []
