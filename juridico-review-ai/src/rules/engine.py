from typing import Dict, List, Optional
from ..utils.text_norm import normalize

def _has_all(text: str, terms: List[str]) -> bool:
    """
    Verifica se o texto contém todos os termos (normalizado).

    Args:
        text: Texto a verificar
        terms: Lista de termos obrigatórios

    Returns:
        True se todos os termos estão presentes
    """
    text_n = normalize(text)
    return all(normalize(t) in text_n for t in terms if t)

def apply_rules(clause: Dict, candidates: List[Dict]) -> Optional[Dict]:
    """
    Aplica regras determinísticas must_include/must_not_include antes do LLM.

    Retorna status "conforme" se encontrar bloco que atende todas as regras,
    "ambigua" se parcialmente atendida, ou "ausente" se não encontrada.

    Args:
        clause: Dicionário da cláusula do standard
        candidates: Lista de blocos candidatos do retrieval

    Returns:
        Dicionário com resultado preliminar da validação
    """
    must_inc = clause.get("must_include", [])
    must_not = clause.get("must_not_include", [])
    best = None

    # Primeiro: tenta encontrar bloco que atenda completamente
    for c in candidates:
        tx = c.get("text","")
        ok_inc = _has_all(tx, must_inc) if must_inc else True
        bad = any(normalize(t) in normalize(tx) for t in must_not if t)
        if ok_inc and not bad:
            best = c
            break

    if best:
        return {
            "clause_id": clause["id"],
            "status": "conforme",
            "evidence": {
                "page": best["page"],
                "text": best["text"][:2000],
                "bbox": best.get("bbox")
            },
            "parameters": {},
            "notes": "Atendido por regra determinística"
        }

    # Se há algum candidato contendo partially must_include → ambígua
    for c in candidates:
        tx = c.get("text","")
        if any(normalize(t) in normalize(tx) for t in must_inc if t):
            return {
                "clause_id": clause["id"],
                "status": "ambigua",
                "evidence": {
                    "page": c["page"],
                    "text": c["text"][:2000],
                    "bbox": c.get("bbox")
                },
                "parameters": {},
                "notes": "Parcialmente atendida; requer LLM"
            }

    return {
        "clause_id": clause["id"],
        "status": "ausente",
        "evidence": None,
        "parameters": {},
        "notes": "Não encontrado por regras; pode escalar ao LLM"
    }
