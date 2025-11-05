#!/usr/bin/env python3
"""
Pipeline v2: Sistema completo de revisão com arquitetura em camadas
Tier-1 (local) → Roteamento → Tier-2 (frontier)
"""

import click
import sys
from pathlib import Path
import time
import logging

# Importações dos módulos
from parsing import parse_document
from ranker_v2 import rank_document_clauses
from classifier_tier1 import classify_document_matches
from router import ClauseRouter, create_routing_report
from generator_tier2 import generate_tier2_suggestions
from report_v2 import generate_comprehensive_reports
from audit import create_audit_trail
from utils import load_catalog, setup_logging


@click.command()
@click.option('--minuta', '-m', required=True, type=click.Path(exists=True),
              help='Caminho para a minuta (.docx ou .pdf)')
@click.option('--catalogo', '-c', required=True, type=click.Path(exists=True),
              help='Caminho para o catálogo YAML v2')
@click.option('--output-dir', '-o', default='data/saida',
              help='Diretório de saída')
@click.option('--tier1-model', default='qwen2:7b-instruct',
              help='Modelo Ollama para Tier-1 (classificação)')
@click.option('--tier2-provider', default='ollama',
              type=click.Choice(['ollama', 'openai', 'anthropic']),
              help='Provider para Tier-2 (geração)')
@click.option('--tier2-model', default='qwen2:7b-instruct',
              help='Modelo para Tier-2')
@click.option('--top-k', default=3, type=int,
              help='Top-K matches por cláusula')
@click.option('--skip-tier2', is_flag=True,
              help='Pula Tier-2 (apenas classifica)')
@click.option('--verbose', '-v', is_flag=True,
              help='Modo verbose')
def main(minuta, catalogo, output_dir, tier1_model, tier2_provider,
         tier2_model, top_k, skip_tier2, verbose):
    """
    Sistema de Revisão Automatizada de Minutas v2.0

    Pipeline completo:
    1. Parsing + Segmentação
    2. Ranking Híbrido (BM25 + Embeddings + Regex + MMR)
    3. Classificação Tier-1 (PRESENTE/PARCIAL/AUSENTE)
    4. Roteamento Inteligente
    5. Geração Tier-2 (quando necessário)
    6. Relatórios + Auditoria
    """

    # Setup
    logger = setup_logging(verbose)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Inicia auditoria
    audit = create_audit_trail(output_path)

    logger.info("=" * 60)
    logger.info("REVISÃO AUTOMATIZADA DE MINUTAS v2.0")
    logger.info("=" * 60)
    logger.info(f"Sessão: {audit.session_id}")
    logger.info("")

    try:
        # ==========================================
        # ETAPA 1: CARREGA CATÁLOGO
        # ==========================================
        logger.info("⚙ ETAPA 1: Carregando catálogo...")
        catalog = load_catalog(catalogo)
        audit.log_catalog_info(catalog, catalogo)
        logger.info(f"  ✓ Catálogo: {catalog.get('metadata', {}).get('nome')}")
        logger.info(f"  ✓ Versão: {catalog.get('metadata', {}).get('versao')}")
        logger.info(f"  ✓ Cláusulas: {len(catalog.get('clausulas', []))}")
        logger.info("")

        # ==========================================
        # ETAPA 2: PARSING DO DOCUMENTO
        # ==========================================
        logger.info("📄 ETAPA 2: Parseando documento...")
        start_time = time.time()

        document = parse_document(minuta)
        audit.log_document_info(minuta)

        parsing_time = time.time() - start_time
        audit.log_parsing(len(document.clauses), parsing_time)

        logger.info(f"  ✓ Cláusulas encontradas: {len(document.clauses)}")
        logger.info(f"  ✓ Tempo: {parsing_time:.2f}s")
        logger.info("")

        # ==========================================
        # ETAPA 3: RANKING HÍBRIDO
        # ==========================================
        logger.info("🔍 ETAPA 3: Ranking híbrido (BM25 + Embeddings + Regex + MMR)...")
        start_time = time.time()

        ranked_matches = rank_document_clauses(
            document,
            catalog,
            top_k=top_k,
            lambda_param=0.7
        )

        ranking_time = time.time() - start_time
        audit.log_ranking(len(ranked_matches), ranking_time)

        logger.info(f"  ✓ Cláusulas rankeadas: {len(ranked_matches)}")
        logger.info(f"  ✓ Tempo: {ranking_time:.2f}s")
        logger.info("")

        # ==========================================
        # ETAPA 4: CLASSIFICAÇÃO TIER-1
        # ==========================================
        logger.info(f"🤖 ETAPA 4: Classificação Tier-1 (modelo: {tier1_model})...")
        start_time = time.time()

        classifications = classify_document_matches(
            ranked_matches,
            model=tier1_model
        )

        tier1_time = time.time() - start_time

        # Sumário das classificações
        presente = sum(1 for c in classifications
                      if c['classification'].get('classificacao') == 'PRESENTE')
        parcial = sum(1 for c in classifications
                     if c['classification'].get('classificacao') == 'PARCIAL')
        ausente = sum(1 for c in classifications
                     if c['classification'].get('classificacao') == 'AUSENTE')

        summary = {
            'presente': presente,
            'parcial': parcial,
            'ausente': ausente
        }

        audit.log_tier1_classification(
            len(classifications),
            tier1_model,
            tier1_time,
            summary
        )

        logger.info(f"  ✓ Classificações concluídas: {len(classifications)}")
        logger.info(f"  ✓ PRESENTE: {presente}")
        logger.info(f"  ✓ PARCIAL: {parcial}")
        logger.info(f"  ✓ AUSENTE: {ausente}")
        logger.info(f"  ✓ Tempo: {tier1_time:.2f}s")
        logger.info("")

        # ==========================================
        # ETAPA 5: ROTEAMENTO
        # ==========================================
        logger.info("🔀 ETAPA 5: Roteamento inteligente...")
        router = ClauseRouter(tier2_threshold=0.7)
        routing_result = router.route_classifications(classifications)

        routing_events = create_routing_report(routing_result)
        audit.log_routing(routing_events)

        logger.info(router.get_routing_summary(routing_result))
        logger.info("")

        # ==========================================
        # ETAPA 6: TIER-2 (se necessário)
        # ==========================================
        tier2_suggestions = []

        if not skip_tier2 and routing_result['needs_tier2']:
            logger.info(f"🚀 ETAPA 6: Geração Tier-2 ({tier2_provider}/{tier2_model})...")
            logger.info(f"  Processando {len(routing_result['needs_tier2'])} cláusulas...")
            start_time = time.time()

            tier2_suggestions = generate_tier2_suggestions(
                routing_result['needs_tier2'],
                provider=tier2_provider,
                model=tier2_model
            )

            tier2_time = time.time() - start_time
            audit.log_tier2_generation(
                len(tier2_suggestions),
                tier2_provider,
                tier2_model,
                tier2_time
            )

            logger.info(f"  ✓ Sugestões geradas: {len(tier2_suggestions)}")
            logger.info(f"  ✓ Tempo: {tier2_time:.2f}s")
            logger.info("")
        elif skip_tier2:
            logger.info("⏭  ETAPA 6: Tier-2 pulado (--skip-tier2)")
            logger.info("")
        else:
            logger.info("✓ ETAPA 6: Tier-2 não necessário (todas cláusulas OK)")
            logger.info("")

        # ==========================================
        # ETAPA 7: RELATÓRIOS
        # ==========================================
        logger.info("📊 ETAPA 7: Gerando relatórios...")

        generate_comprehensive_reports(
            tier1_results=routing_result['tier1_only'],
            tier2_results=tier2_suggestions,
            document_info=document,
            catalog_info=catalog,
            output_path=output_path,
            audit_trail=audit
        )

        logger.info(f"  ✓ Excel: {output_path / 'revisao_completa.xlsx'}")
        logger.info(f"  ✓ DOCX: {output_path / 'sugestoes_detalhadas.docx'}")
        logger.info("")

        # ==========================================
        # FINALIZAÇÃO
        # ==========================================
        audit_file = audit.finalize()

        logger.info("=" * 60)
        logger.info("✅ REVISÃO CONCLUÍDA COM SUCESSO!")
        logger.info("=" * 60)
        logger.info(audit.get_summary())

        logger.info(f"📁 Arquivos gerados em: {output_path.absolute()}")
        logger.info(f"📋 Auditoria: {audit_file}")
        logger.info("")

        sys.exit(0)

    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ ERRO DURANTE A REVISÃO")
        logger.error("=" * 60)
        logger.error(f"Erro: {str(e)}")

        if verbose:
            import traceback
            traceback.print_exc()

        audit.log_event('ERROR', {'message': str(e)})
        audit.finalize()

        sys.exit(1)


if __name__ == '__main__':
    main()
