#!/usr/bin/env python3
"""
CLI principal para revisão de minutas jurídicas
"""

import click
import sys
from pathlib import Path

from parsing import parse_document
from ranker import rank_clauses
from reviewer import review_document
from report import generate_reports
from utils import load_catalog, setup_logging


@click.command()
@click.option('--minuta', '-m', required=True, type=click.Path(exists=True),
              help='Caminho para a minuta (.docx ou .pdf)')
@click.option('--catalogo', '-c', required=True, type=click.Path(exists=True),
              help='Caminho para o catálogo YAML de referência')
@click.option('--output-dir', '-o', default='data/saida',
              help='Diretório de saída para os relatórios')
@click.option('--model', default='qwen2:7b-instruct',
              help='Modelo Ollama a ser usado')
@click.option('--top-k', default=5, type=int,
              help='Número de cláusulas similares a considerar')
@click.option('--verbose', '-v', is_flag=True,
              help='Modo verbose (mais logs)')
def main(minuta, catalogo, output_dir, model, top_k, verbose):
    """
    Sistema de revisão automatizada de minutas jurídicas

    Analisa minutas de CRI, CRA e Debêntures comparando com catálogos
    de referência e gerando sugestões de melhoria.
    """

    # Setup
    logger = setup_logging(verbose)
    logger.info(f"Iniciando revisão de: {minuta}")

    try:
        # 1. Carregar catálogo
        logger.info("Carregando catálogo...")
        catalog = load_catalog(catalogo)

        # 2. Parse do documento
        logger.info("Processando documento...")
        document = parse_document(minuta)

        # 3. Ranking de cláusulas
        logger.info("Analisando cláusulas...")
        ranked_clauses = rank_clauses(document, catalog, top_k=top_k)

        # 4. Revisão com LLM
        logger.info(f"Revisando com modelo {model}...")
        review_results = review_document(ranked_clauses, catalog, model=model)

        # 5. Gerar relatórios
        logger.info("Gerando relatórios...")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        generate_reports(review_results, document, output_path)

        logger.info(f"✓ Revisão concluída! Arquivos salvos em: {output_path}")
        logger.info(f"  - {output_path / 'revisao.xlsx'}")
        logger.info(f"  - {output_path / 'sugestoes.docx'}")

    except Exception as e:
        logger.error(f"Erro durante a revisão: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
