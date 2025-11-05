from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Optional, Tuple

Status = Literal["conforme","divergente","ausente","ambigua"]

class Evidence(BaseModel):
    """
    Evidência de uma cláusula em um documento.

    Suporta PDF (page + bbox) e DOCX (section_path + para_idx + table_ref).
    """
    # modo PDF
    page: Optional[int] = None
    bbox: Optional[Tuple[float, float, float, float]] = None
    # modo DOCX
    section_path: Optional[str] = None   # ex: "1 > 1.2 > Obrigações"
    para_idx: Optional[int] = None       # índice do parágrafo dentro da seção
    table_ref: Optional[str] = None      # ex: "Tabela 2 / R1C3"
    # texto sempre presente
    text: str

class ClauseJudgement(BaseModel):
    clause_id: str
    status: Status
    evidence: Optional[Evidence] = None
    parameters: Dict[str, str] = {}
    notes: Optional[str] = None
