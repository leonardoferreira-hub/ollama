"""
Script para ajustar o catálogo com base nos documentos GOLD
Extrai cláusulas dos documentos GOLD e sugere melhorias no catálogo
"""

import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsing import parse_document
from src.utils import load_catalog
import yaml

def extract_clauses_from_gold(gold_file):
    """Extrai cláusulas de um documento GOLD"""
    print(f"\n[PARSE] {gold_file.name}")
    doc = parse_document(str(gold_file))

    print(f"   [OK] {len(doc.clauses)} clausulas encontradas")

    return doc.clauses

def analyze_catalog_coverage(gold_clauses, catalog):
    """Analisa cobertura do catálogo em relação aos documentos GOLD"""

    catalog_titles = {c['titulo'].lower() for c in catalog['clausulas']}
    gold_titles = {clause['title'].lower() for clause in gold_clauses}

    # Cláusulas GOLD que NÃO estão no catálogo
    missing_in_catalog = []

    for gold_clause in gold_clauses:
        gold_title = gold_clause['title'].lower()

        # Busca match aproximado
        found = False
        for cat_title in catalog_titles:
            # Match se tiver 50% de palavras em comum
            gold_words = set(gold_title.split())
            cat_words = set(cat_title.split())

            if gold_words & cat_words:  # Tem interseção
                found = True
                break

        if not found:
            missing_in_catalog.append(gold_clause)

    return missing_in_catalog

def suggest_new_catalog_entries(missing_clauses):
    """Sugere novas entradas de catálogo baseadas em cláusulas GOLD"""

    suggestions = []

    for clause in missing_clauses:
        # Gera ID
        clause_id = f"CRI_SDEST_{len(suggestions)+100:03d}"

        # Extrai keywords do título
        keywords = [w.lower() for w in clause['title'].split() if len(w) > 3]

        # Template simplificado
        template = f"CLÁUSULA {{{{numero}}}} – {clause['title'].upper()}\n\n{clause['content'][:500]}..."

        suggestion = {
            'id': clause_id,
            'titulo': clause['title'],
            'categoria': 'ajustar',
            'importancia': 'alta',
            'obrigatoria': False,
            'keywords': keywords[:5],
            'template': template
        }

        suggestions.append(suggestion)

    return suggestions

def main():
    print("="*60)
    print("AJUSTE DE CATALOGO COM BASE EM DOCUMENTOS GOLD")
    print("="*60)

    # Documentos GOLD
    gold_dir = Path("data/documentos_gold")
    gold_files = list(gold_dir.glob("GOLD_*.docx"))

    if not gold_files:
        print("[ERRO] Nenhum documento GOLD encontrado em data/documentos_gold/")
        return

    print(f"\n[INFO] {len(gold_files)} documentos GOLD encontrados")

    # Catálogos
    catalog_dir = Path("data/catalogos")

    # Escolhe catálogo (CRI sem destinação)
    catalog_file = catalog_dir / "catalogo_cri_sem_destinacao.yaml"

    if not catalog_file.exists():
        print(f"[ERRO] Catalogo nao encontrado: {catalog_file}")
        return

    print(f"\n[LOAD] Carregando catalogo: {catalog_file.name}")
    catalog = load_catalog(str(catalog_file))
    print(f"   [OK] {len(catalog['clausulas'])} clausulas no catalogo atual")

    # Extrai cláusulas de todos os documentos GOLD
    all_gold_clauses = []
    for gold_file in gold_files:
        clauses = extract_clauses_from_gold(gold_file)
        all_gold_clauses.extend(clauses)

    print(f"\n[STATS] Total de clausulas GOLD: {len(all_gold_clauses)}")

    # Analisa cobertura
    print("\n[ANALISE] Analisando cobertura do catalogo...")
    missing = analyze_catalog_coverage(all_gold_clauses, catalog)

    if missing:
        print(f"\n[AVISO] {len(missing)} clausulas GOLD NAO cobertas pelo catalogo:")
        for i, clause in enumerate(missing[:10], 1):  # Mostra até 10
            print(f"   {i}. {clause['title']}")

        if len(missing) > 10:
            print(f"   ... e mais {len(missing)-10} clausulas")

        # Gera sugestões
        print("\n[SUGESTAO] Gerando sugestoes de novas entradas...")
        suggestions = suggest_new_catalog_entries(missing)

        # Salva sugestões
        output_file = catalog_dir / "sugestoes_catalogo_gold.yaml"
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump({'clausulas_sugeridas': suggestions}, f,
                     allow_unicode=True, default_flow_style=False, sort_keys=False)

        print(f"\n[OK] Sugestoes salvas em: {output_file}")
        print(f"   [INFO] {len(suggestions)} novas entradas sugeridas")
    else:
        print("\n[OK] Catalogo cobre TODAS as clausulas dos documentos GOLD!")

    print("\n" + "="*60)
    print("[CONCLUIDO] ANALISE FINALIZADA")
    print("="*60)

if __name__ == "__main__":
    main()
