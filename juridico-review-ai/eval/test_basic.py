"""
Testes básicos sem dependências externas.
"""
import sys
import os

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_schemas():
    """
    Testa validação de schemas Pydantic.
    """
    print("[TESTE] Schemas Pydantic...")
    try:
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
        return True
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def test_text_normalization():
    """
    Testa normalização de texto.
    """
    print("[TESTE] Normalização de texto...")
    try:
        from src.utils.text_norm import normalize

        assert normalize("Çédílhã") == "cedilha"
        assert normalize("  múltiplos   espaços  ") == "multiplos espacos"
        assert normalize("UPPERCASE") == "uppercase"
        print("[OK] Normalizacao de texto funciona")
        return True
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def test_standards_json():
    """
    Testa se os standards JSON são válidos.
    """
    print("[TESTE] Standards JSON...")
    try:
        import json

        std_com = os.path.join(os.path.dirname(__file__), '..', 'standards', 'CRI', 'cri_com_destinacao.v1.json')
        std_sem = os.path.join(os.path.dirname(__file__), '..', 'standards', 'CRI', 'cri_sem_destinacao.v1.json')

        with open(std_com, 'r', encoding='utf-8') as f:
            data_com = json.load(f)
            assert data_com['version'] == 'CRI-com-destinacao.v1'
            assert len(data_com['clauses']) == 8
            print(f"[OK] CRI com destinacao: {len(data_com['clauses'])} clausulas")

        with open(std_sem, 'r', encoding='utf-8') as f:
            data_sem = json.load(f)
            assert data_sem['version'] == 'CRI-sem-destinacao.v1'
            assert len(data_sem['clauses']) == 8
            print(f"[OK] CRI sem destinacao: {len(data_sem['clauses'])} clausulas")

        return True
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("TESTES BASICOS (sem dependencias externas)")
    print("="*60)

    results = []
    results.append(("Standards JSON", test_standards_json()))
    results.append(("Schemas Pydantic", test_schemas()))
    results.append(("Normalizacao de texto", test_text_normalization()))

    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "[OK]" if result else "[ERRO]"
        print(f"{status} {name}")

    print("="*60)
    print(f"Testes: {passed}/{total} passaram")
    print("="*60)

    if passed == total:
        print("\nTODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print(f"\n{total - passed} TESTE(S) FALHARAM!")
        sys.exit(1)
