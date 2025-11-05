"""
Testes básicos do pipeline de validação.

Para testes completos com PDFs reais, adicione arquivos em eval/data/
e implemente testes de accuracy/recall.
"""
import sys
import os

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_pipeline_imports():
    """
    Testa se todos os módulos podem ser importados corretamente.
    """
    import importlib
    modules = [
        "src.parsers.pdf_pymupdf",
        "src.retrieval.embeddings",
        "src.retrieval.index_faiss",
        "src.rules.engine",
        "src.agents.gemini_validator",
        "src.reports.html_report",
        "src.schemas",
        "scripts.validate",
    ]

    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"[OK] {mod}")
        except Exception as e:
            print(f"[ERRO] {mod}: {e}")
            raise

def test_schemas():
    """
    Testa validação de schemas Pydantic.
    """
    from src.schemas import ClauseJudgement, Evidence

    # Teste válido
    ev = Evidence(page=1, text="Teste de evidência", bbox=(0, 0, 100, 100))
    cj = ClauseJudgement(
        clause_id="C-001",
        status="conforme",
        evidence=ev,
        parameters={"foo": "bar"},
        notes="Teste"
    )
    assert cj.clause_id == "C-001"
    assert cj.status == "conforme"
    print("[OK] Schemas Pydantic validam corretamente")

def test_text_normalization():
    """
    Testa normalização de texto.
    """
    from src.utils.text_norm import normalize

    assert normalize("Çédílhã") == "cedilha"
    assert normalize("  múltiplos   espaços  ") == "multiplos espacos"
    assert normalize("UPPERCASE") == "uppercase"
    print("[OK] Normalizacao de texto funciona")

def test_embeddings():
    """
    Testa geração de embeddings.
    """
    from src.retrieval.embeddings import embed
    import numpy as np

    texts = ["teste um", "teste dois", "completamente diferente"]
    vecs = embed(texts)

    assert vecs.shape[0] == 3
    assert vecs.dtype == np.float32
    # Verifica normalização L2
    norms = np.linalg.norm(vecs, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)
    print("[OK] Embeddings gerados e normalizados")

def test_rules_engine():
    """
    Testa motor de regras determinísticas.
    """
    from src.rules.engine import apply_rules

    clause = {
        "id": "C-TEST",
        "title": "Teste",
        "must_include": ["cessão definitiva", "irrevogável"],
        "must_not_include": ["recompra automática"]
    }

    # Candidato conforme
    cands_ok = [{
        "page": 1,
        "text": "A cessão definitiva possui caráter irrevogável e irretratável.",
        "bbox": [0, 0, 100, 100]
    }]

    result = apply_rules(clause, cands_ok)
    assert result["status"] == "conforme"
    print("[OK] Regras deterministicas - caso conforme")

    # Candidato com termo proibido
    cands_bad = [{
        "page": 1,
        "text": "A cessão definitiva é irrevogável mas permite recompra automática.",
        "bbox": [0, 0, 100, 100]
    }]

    result = apply_rules(clause, cands_bad)
    assert result["status"] != "conforme"
    print("[OK] Regras deterministicas - termo proibido detectado")

if __name__ == "__main__":
    print("="*60)
    print("TESTES DO PIPELINE")
    print("="*60)

    test_pipeline_imports()
    test_schemas()
    test_text_normalization()
    test_embeddings()
    test_rules_engine()

    print("="*60)
    print("TODOS OS TESTES PASSARAM!")
    print("="*60)
