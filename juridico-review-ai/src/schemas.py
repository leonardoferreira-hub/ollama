from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Optional, Tuple

Status = Literal["conforme","divergente","ausente","ambigua"]

class Evidence(BaseModel):
    page: int
    text: str
    bbox: Optional[Tuple[float, float, float, float]] = None

class ClauseJudgement(BaseModel):
    clause_id: str
    status: Status
    evidence: Optional[Evidence] = None
    parameters: Dict[str, str] = {}
    notes: Optional[str] = None
