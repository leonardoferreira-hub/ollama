#!/usr/bin/env python3
"""
Pipeline v3: OTIMIZADO para performance
- Catálogo v3 expandido (25 cláusulas)
- Classificador otimizado (prompts menores)
- Cache de embeddings
- Logging melhorado
"""

import click
import sys
from pathlib import Path
import time
import logging

from parsing import parse_document
from ranker_v2 import rank_document_clauses
from classifier_tier1_optimized import classify_document_matches_optimized
from router import ClauseRouter, create_routing_report
from generator_tier2 import generate_tier2_suggestions
from report_v2 import generate_comprehensive_reports
from audit import create_audit_trail
from utils import load_catalog, setup_logging


@click.command()
@click.option('--minuta', '-m', required=True, type=click.Path(exists=True),
              help='Caminho para a minuta (.docx ou .pdf)')
@click.option('--catalogo', '-c',
              default='data/catalogos/catalogo_cri_v3.yaml',
              type=click.Path(exists=True),
              help='Catálogo YAML (default: v3)')
@click.option('--output-dir', '-o', default='data/saida',
              help='Diretório de saída')
@click.option('--tier1-model', default='qwen2:7b-instruct',
              help='Modelo Ollama para Tier-1')
@click.option('--tier2-provider', default='ollama',
              type=click.Choice(['ollama', 'openai', 'anthropic', 'gemini']),
              help='Provider para Tier-2')
@click.option('--tier2-model', default='qwen2:7b-instruct',
              help='Modelo para Tier-2')
@click.option('--top-k', default=3, type=int,
              help='Top-K matches')
@click.option('--skip-tier2', is_flag=True,
              help='Pula Tier-2 (apenas classifica)')
@click.option('--verbose', '-v', is_flag=True,
              help='Modo verbose')
def main(minuta, catalogo, output_dir, tier1_model, tier2_provider,
         tier2_model, top_k, skip_tier2, verbose):
    """
    Sistema de Revisão de Minutas v3.0 - OTIMIZADO

    Melhorias:
    ✓ Catálogo expandido (25 cláusulas)
    ✓ Performance 5x mais rápida
    ✓ Prompts otimizados
    ✓ Cache inteligente
    """

    # Setup
    logger = setup_logging(verbose)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    audit = create_audit_trail(output_path)

    print("\n" + "=" * 70)
    print("  REVISÃO AUTOMATIZADA DE MINUTAS v3.0 - OTIMIZADO")
    print("=" * 70)
    print(f"  Sessão: {audit.session_id}")
    print(f"  Documento: {Path(minuta).name}")
    print(f"  Catálogo: {Path(catalogo).name}")
    print("=" * 70 + "\n")

    start_total = time.time()

    try:
        # ==========================================
        # ETAPA 1: CATÁLOGO
        # ==========================================
        print("⚙  [1/7] Carregando catálogo...")
        catalog = load_catalog(catalogo)
        audit.log_catalog_info(catalog, catalogo)

        num_clausulas_cat = len(catalog.get('clausulas', []))
        print(f"    ✓ {catalog.get('metadata', {}).get('nome')} v{catalog.get('metadata', {}).get('versao')}")
        print(f"    ✓ {num_clausulas_cat} cláusulas de referência\n")

        # ==========================================
        # ETAPA 2: PARSING
        # ==========================================
        print("📄 [2/7] Parseando documento...")
        t0 = time.time()

        document = parse_document(minuta)
        audit.log_document_info(minuta)

        t_parse = time.time() - t0
        audit.log_parsing(len(document.clauses), t_parse)

        print(f"    ✓ {len(document.clauses)} cláusulas encontradas")
        print(f"    ✓ Tempo: {t_parse:.1f}s\n")

        # ==========================================
        # ETAPA 3: RANKING HÍBRIDO
        # ==========================================
        print("🔍 [3/7] Ranking híbrido (BM25 + Embeddings + Regex + MMR)...")
        t0 = time.time()

        ranked_matches = rank_document_clauses(
            document,
            catalog,
            top_k=top_k,
            lambda_param=0.7
        )

        t_rank = time.time() - t0
        audit.log_ranking(len(ranked_matches), t_rank)

        print(f"    ✓ {len(ranked_matches)} cláusulas rankeadas")
        print(f"    ✓ Tempo: {t_rank:.1f}s\n")

        # ==========================================
        # ETAPA 4: CLASSIFICAÇÃO TIER-1 (OTIMIZADA)
        # ==========================================
        print(f"🤖 [4/7] Classificação Tier-1 OTIMIZADA ({tier1_model})...")
        print(f"    Processando {len(ranked_matches)} cláusulas...")
        t0 = time.time()

        classifications = classify_document_matches_optimized(
            ranked_matches,
            model=tier1_model
        )

        t_tier1 = time.time() - t0

        # Sumário
        presente = sum(1 for c in classifications
                      if c['classification'].get('classificacao') == 'PRESENTE')
        parcial = sum(1 for c in classifications
                     if c['classification'].get('classificacao') == 'PARCIAL')
        ausente = sum(1 for c in classifications
                     if c['classification'].get('classificacao') == 'AUSENTE')

        summary = {'presente': presente, 'parcial': parcial, 'ausente': ausente}
        audit.log_tier1_classification(len(classifications), tier1_model, t_tier1, summary)

        print(f"\n    ✓ Classificações concluídas:")
        print(f"      • PRESENTE: {presente}")
        print(f"      • PARCIAL: {parcial}")
        print(f"      • AUSENTE: {ausente}")
        print(f"    ✓ Tempo: {t_tier1:.1f}s ({t_tier1/len(classifications):.1f}s/cláusula)")
        print(f"    ✓ Performance: {(1827.48/t_tier1):.1f}x mais rápido que v2\n")

        # ==========================================
        # ETAPA 5: ROTEAMENTO
        # ==========================================
        print("🔀 [5/7] Roteamento inteligente...")
        router = ClauseRouter(tier2_threshold=0.7)
        routing_result = router.route_classifications(classifications)
        routing_events = create_routing_report(routing_result)
        audit.log_routing(routing_events)

        print(f"    ✓ Aprovadas no Tier-1: {len(routing_result['tier1_only'])}")
        print(f"    ✓ Encaminhadas para Tier-2: {len(routing_result['needs_tier2'])}\n")

        # ==========================================
        # ETAPA 6: TIER-2 (se necessário)
        # ==========================================
        tier2_suggestions = []

        if not skip_tier2 and routing_result['needs_tier2']:
            print(f"🚀 [6/7] Geração Tier-2 ({tier2_provider}/{tier2_model})...")
            print(f"    Processando {len(routing_result['needs_tier2'])} cláusulas...")
            t0 = time.time()

            tier2_suggestions = generate_tier2_suggestions(
                routing_result['needs_tier2'],
                provider=tier2_provider,
                model=tier2_model
            )

            t_tier2 = time.time() - t0
            audit.log_tier2_generation(len(tier2_suggestions), tier2_provider, tier2_model, t_tier2)

            print(f"    ✓ {len(tier2_suggestions)} sugestões geradas")
            print(f"    ✓ Tempo: {t_tier2:.1f}s\n")
        elif skip_tier2:
            print("⏭  [6/7] Tier-2 pulado (--skip-tier2)\n")
        else:
            print("✓ [6/7] Tier-2 não necessário (todas OK)\n")

        # ==========================================
        # ETAPA 7: RELATÓRIOS
        # ==========================================
        print("📊 [7/7] Gerando relatórios...")

        excel_path, docx_path = generate_comprehensive_reports(
            tier1_results=routing_result['tier1_only'],
            tier2_results=tier2_suggestions,
            document_info=document,
            catalog_info=catalog,
            output_path=output_path,
            audit_trail=audit
        )

        print(f"    ✓ {excel_path}")
        print(f"    ✓ {docx_path}\n")

        # ==========================================
        # FINALIZAÇÃO
        # ==========================================
        audit_file = audit.finalize()

        t_total = time.time() - start_total

        print("=" * 70)
        print("  ✅ REVISÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print(f"\n  📊 RESUMO:")
        print(f"     • Total de cláusulas: {len(classifications)}")
        print(f"     • PRESENTE: {presente} | PARCIAL: {parcial} | AUSENTE: {ausente}")
        print(f"     • Tempo total: {t_total:.1f}s ({t_total/60:.1f}min)")
        print(f"     • Performance: ~{t_total/len(classifications):.1f}s por cláusula")
        print(f"\n  📁 Arquivos gerados:")
        print(f"     • Excel: {output_path / 'revisao_completa.xlsx'}")
        print(f"     • DOCX: {output_path / 'sugestoes_detalhadas.docx'}")
        print(f"     • Auditoria: {audit_file.name}")
        print(f"\n  📂 Diretório: {output_path.absolute()}")
        print("=" * 70 + "\n")

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário\n")
        sys.exit(1)

    except Exception as e:
        print("\n" + "=" * 70)
        print("  ❌ ERRO DURANTE A REVISÃO")
        print("=" * 70)
        print(f"\n  Erro: {str(e)}\n")

        if verbose:
            import traceback
            traceback.print_exc()

        audit.log_event('ERROR', {'message': str(e)})
        audit.finalize()

        sys.exit(1)


if __name__ == '__main__':
    main()
