import json
import hashlib
import os
import sys

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict
from src.parsers.pdf_pymupdf import extract_blocks
from src.retrieval.index_faiss import build_index, query_topk
from src.rules.engine import apply_rules
from src.agents.gemini_validator import judge_with_gemini
from src.schemas import ClauseJudgement
from src.reports.html_report import render_html

def sha256_file(path: str) -> str:
    """
    Calcula SHA256 de um arquivo.

    Args:
        path: Caminho do arquivo

    Returns:
        Hash SHA256 em hexadecimal
    """
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def validate(pdf_path: str, standard_path: str, k: int = 5, use_llm: bool = True, out_html: str = "report.html"):
    """
    Pipeline completo de validação documental.

    Etapas:
    1. Extração de blocos do PDF (PyMuPDF)
    2. Construção de índice FAISS
    3. Para cada cláusula:
       a. Retrieval top-k
       b. Aplicação de regras determinísticas
       c. Se ambíguo/ausente, escala para Gemini
    4. Geração de relatório HTML

    Args:
        pdf_path: Caminho do PDF a validar
        standard_path: Caminho do standard JSON
        k: Número de blocos a recuperar (default: 5)
        use_llm: Se deve usar LLM para casos ambíguos (default: True)
        out_html: Caminho do relatório HTML de saída (default: report.html)
    """
    print(f"[1/4] Carregando standard: {standard_path}")
    std = json.load(open(standard_path, 'r', encoding='utf-8'))

    print(f"[2/4] Extraindo blocos do PDF: {pdf_path}")
    blocks = extract_blocks(pdf_path)
    print(f"      Blocos extraídos: {len(blocks)}")

    print(f"[3/4] Construindo índice FAISS...")
    index = build_index(blocks)

    results = []
    print(f"[4/4] Validando {len(std['clauses'])} cláusulas...")
    for i, clause in enumerate(std["clauses"], 1):
        print(f"      [{i}/{len(std['clauses'])}] {clause['id']}: {clause['title']}")

        # Retrieval
        cands = query_topk(index, clause, k=k)

        # Regras determinísticas
        prelim = apply_rules(clause, cands)

        out = prelim
        # Se ambíguo/ausente/divergente e LLM habilitado, escala
        if use_llm and prelim["status"] in ("ambigua","ausente","divergente"):
            try:
                print(f"          Escalando para Gemini (status: {prelim['status']})")
                llm_out = judge_with_gemini(clause, cands)
                out = llm_out
                # garante id
                out["clause_id"] = clause["id"]
                ClauseJudgement(**out)
            except Exception as e:
                print(f"          ERRO no LLM: {e}")
                out["notes"] = (out.get("notes","") + f" | LLM erro: {e}")[:1000]

        print(f"          Status final: {out['status']}")
        results.append(out)

    payload = {
        "pdf_sha256": sha256_file(pdf_path),
        "standard_version": std["version"],
        "results": results
    }

    print(f"\n[OK] Gerando relatório HTML: {out_html}")
    html = render_html(payload)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print("\n" + "="*60)
    print("RESUMO DOS RESULTADOS (JSON):")
    print("="*60)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("\n" + "="*60)
    print(f"Relatório salvo em: {out_html}")
    print("="*60)

if __name__ == "__main__":
    import fire
    fire.Fire(validate)
