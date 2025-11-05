import os
import json
from typing import Dict, List
import google.generativeai as genai
from ..schemas import ClauseJudgement

MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-exp")
API_KEY = os.getenv("GEMINI_API_KEY")

CLAUSE_SCHEMA = {
  "type": "object",
  "properties": {
    "clause_id": {"type":"string"},
    "status": {"type":"string", "enum":["conforme","divergente","ausente","ambigua"]},
    "evidence": {
      "type":"object",
      "properties": {
        "page": {"type":"integer"},
        "text": {"type":"string"},
        "bbox": {"type":"array", "items":{"type":"number"}}
      },
      "required": ["page","text"]
    },
    "parameters": {"type":"object"},
    "notes": {"type":"string"}
  },
  "required": ["clause_id","status"]
}

SYSTEM = (
  "Você é um revisor jurídico brasileiro especializado em documentos de securitização. "
  "Compare a cláusula-padrão com os trechos candidatos do contrato. "
  "Responda SOMENTE em JSON válido, conforme o schema fornecido. "
  "Analise se a cláusula está conforme (atende todos os requisitos), "
  "divergente (presente mas com problemas), ausente (não encontrada) ou ambígua (inconclusiva)."
)

def judge_with_gemini(clause: Dict, candidates: List[Dict]) -> Dict:
    """
    Usa Gemini 2.5 Flash com structured output para julgar cláusulas ambíguas.

    Args:
        clause: Dicionário da cláusula do standard
        candidates: Lista de blocos candidatos

    Returns:
        Dicionário com julgamento estruturado (ClauseJudgement)

    Raises:
        AssertionError: Se GEMINI_API_KEY não estiver definida
        Exception: Se houver erro na chamada à API
    """
    assert API_KEY, "Defina GEMINI_API_KEY no ambiente."
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name=MODEL_ID)

    user_payload = {
      "clause": clause,
      "candidates": candidates[:5]
    }

    res = model.generate_content(
        contents=[{"role":"user","parts":[{"text": SYSTEM}, {"text": json.dumps(user_payload, ensure_ascii=False)}]}],
        generation_config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
            "response_schema": CLAUSE_SCHEMA
        }
    )
    out = json.loads(res.text)
    # valida com pydantic
    ClauseJudgement(**out)
    return out
