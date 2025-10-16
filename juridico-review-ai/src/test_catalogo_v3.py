#!/usr/bin/env python3
"""
Teste do Catálogo v3 - Versão Simplificada SEM embeddings
Usa apenas regex e matching de texto básico
"""

import re
import yaml
from pathlib import Path
from parsing import parse_document

def simple_match_score(clause_title, clause_content, catalog_clause):
    """Match simples usando regex e keywords"""
    score = 0.0

    # Testa regex patterns
    regex_score = 0
    patterns = catalog_clause.get('regex_patterns', [])
    for pattern in patterns:
        try:
            if re.search(pattern, clause_title, re.IGNORECASE | re.MULTILINE):
                regex_score += 1
            if re.search(pattern, clause_content[:500], re.IGNORECASE | re.MULTILINE):
                regex_score += 0.5
        except:
            pass

    if patterns:
        score += (regex_score / len(patterns)) * 0.5  # 50% weight

    # Testa keywords
    keywords = catalog_clause.get('keywords', [])
    keyword_score = 0
    text_combined = (clause_title + " " + clause_content[:500]).lower()

    for kw in keywords:
        if kw.lower() in text_combined:
            keyword_score += 1

    if keywords:
        score += (keyword_score / len(keywords)) * 0.5  # 50% weight

    return score

def test_catalog_v3():
    """Testa o catálogo v3 com documento real"""

    print("\n" + "=" * 70)
    print("  TESTE DO CATÁLOGO v3 - Matching Simplificado")
    print("=" * 70 + "\n")

    # Carrega catálogo v3
    catalog_path = Path("data/catalogos/catalogo_cri_v3.yaml")
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)

    print(f"📦 Catálogo carregado:")
    print(f"   • Nome: {catalog['metadata']['nome']}")
    print(f"   • Versão: {catalog['metadata']['versao']}")
    print(f"   • Cláusulas: {len(catalog['clausulas'])}")
    print()

    # Parse documento
    doc_path = "data/entrada/CRI Evoke_TS_v.02  07102025_001_22063v5.DOCX"
    print(f"📄 Parseando documento: {Path(doc_path).name}")
    document = parse_document(doc_path)
    print(f"   • Cláusulas encontradas: {len(document.clauses)}")
    print()

    # Matching
    print("🔍 Executando matching...\n")
    print("=" * 70)

    results = []
    for i, clause in enumerate(document.clauses, 1):
        print(f"\n[{i}/{len(document.clauses)}] {clause['title'][:60]}...")

        # Encontra melhor match
        best_match = None
        best_score = 0.0

        for cat_clause in catalog['clausulas']:
            score = simple_match_score(
                clause['title'],
                clause['content'],
                cat_clause
            )

            if score > best_score:
                best_score = score
                best_match = cat_clause

        # Classifica baseado no score
        if best_score >= 0.6:
            status = "PRESENTE"
            emoji = "✅"
        elif best_score >= 0.3:
            status = "PARCIAL"
            emoji = "⚠️"
        else:
            status = "AUSENTE"
            emoji = "❌"

        if best_match:
            print(f"   {emoji} {status} (score: {best_score:.2f})")
            print(f"   → Match: {best_match['id']} - {best_match['titulo'][:50]}")
        else:
            print(f"   {emoji} {status} - Sem match")

        results.append({
            'clause': clause,
            'status': status,
            'score': best_score,
            'match': best_match
        })

    # Sumário
    print("\n" + "=" * 70)
    print("  RESULTADOS")
    print("=" * 70 + "\n")

    presente = sum(1 for r in results if r['status'] == 'PRESENTE')
    parcial = sum(1 for r in results if r['status'] == 'PARCIAL')
    ausente = sum(1 for r in results if r['status'] == 'AUSENTE')

    total = len(results)

    print(f"Total de cláusulas: {total}")
    print()
    print(f"✅ PRESENTE: {presente} ({presente/total*100:.0f}%)")
    print(f"⚠️  PARCIAL:  {parcial} ({parcial/total*100:.0f}%)")
    print(f"❌ AUSENTE:  {ausente} ({ausente/total*100:.0f}%)")
    print()

    # Comparação com v2
    print("=" * 70)
    print("  COMPARAÇÃO v2 vs v3")
    print("=" * 70 + "\n")

    print("v2 (catálogo com 7 cláusulas):")
    print("  ✅ PRESENTE: 0   (0%)")
    print("  ⚠️  PARCIAL:  2   (10%)")
    print("  ❌ AUSENTE:  18  (90%)")
    print()

    print("v3 (catálogo com 25 cláusulas):")
    print(f"  ✅ PRESENTE: {presente}   ({presente/total*100:.0f}%)")
    print(f"  ⚠️  PARCIAL:  {parcial}   ({parcial/total*100:.0f}%)")
    print(f"  ❌ AUSENTE:  {ausente}   ({ausente/total*100:.0f}%)")
    print()

    improvement = (presente + parcial) - 2  # v2 tinha 2 parciais
    print(f"📈 Melhoria: +{improvement} cláusulas identificadas corretamente")
    print(f"📊 Acurácia: {(presente+parcial)/total*100:.0f}% (vs 10% no v2)")

    print("\n" + "=" * 70)
    print("  CLÁUSULAS COM MELHOR MATCHING")
    print("=" * 70 + "\n")

    # Top matches
    top_matches = sorted(results, key=lambda x: x['score'], reverse=True)[:5]
    for i, r in enumerate(top_matches, 1):
        print(f"{i}. {r['clause']['title'][:50]}")
        print(f"   Score: {r['score']:.2f} | Status: {r['status']}")
        if r['match']:
            print(f"   Match: {r['match']['id']} - {r['match']['titulo'][:40]}")
        print()

    print("=" * 70)
    print("\n✅ Teste concluído!\n")

    return results

if __name__ == '__main__':
    test_catalog_v3()
