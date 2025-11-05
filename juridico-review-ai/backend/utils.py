"""
Funções auxiliares e utilitárias
"""

import yaml
import logging
from pathlib import Path
from typing import Dict


def load_catalog(filepath: str) -> Dict:
    """
    Carrega catálogo YAML

    Args:
        filepath: Caminho para o arquivo YAML

    Returns:
        Dicionário com o catálogo
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)

    return catalog


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configura logging

    Args:
        verbose: Se True, mostra logs DEBUG

    Returns:
        Logger configurado
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger('juridico-review')
    return logger


def normalize_text(text: str) -> str:
    """
    Normaliza texto para comparação

    Args:
        text: Texto original

    Returns:
        Texto normalizado
    """
    import re
    import unicodedata

    # Remove acentos
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')

    # Lowercase
    text = text.lower()

    # Remove pontuação extra
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remove espaços múltiplos
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Divide texto em chunks com overlap

    Args:
        text: Texto a dividir
        chunk_size: Tamanho de cada chunk (em caracteres)
        overlap: Sobreposição entre chunks

    Returns:
        Lista de chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Tenta quebrar em sentença completa
        if end < len(text):
            last_period = chunk.rfind('.')
            if last_period > chunk_size * 0.7:  # Pelo menos 70% do chunk
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = end - overlap

    return chunks


def extract_keywords(text: str, top_n: int = 10) -> list:
    """
    Extrai palavras-chave principais do texto

    Args:
        text: Texto para análise
        top_n: Número de keywords a retornar

    Returns:
        Lista de keywords
    """
    from collections import Counter
    import re

    # Stopwords básicas em português
    stopwords = {
        'a', 'o', 'e', 'de', 'da', 'do', 'em', 'para', 'com', 'por',
        'ao', 'aos', 'das', 'dos', 'na', 'no', 'nas', 'nos', 'um', 'uma',
        'que', 'se', 'os', 'as', 'à', 'pelo', 'pela', 'ser', 'como',
        'mais', 'este', 'esta', 'isso', 'qual', 'seu', 'sua'
    }

    # Normaliza e tokeniza
    text = normalize_text(text)
    words = re.findall(r'\b\w{4,}\b', text)  # Palavras com 4+ letras

    # Remove stopwords
    words = [w for w in words if w not in stopwords]

    # Conta frequências
    counter = Counter(words)

    # Top N
    keywords = [word for word, _ in counter.most_common(top_n)]

    return keywords


def create_placeholder_files(base_path: Path):
    """
    Cria arquivos .gitkeep para diretórios vazios

    Args:
        base_path: Diretório base do projeto
    """
    directories = [
        base_path / 'data' / 'entrada',
        base_path / 'data' / 'saida',
        base_path / 'tests' / 'exemplos_minutas'
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / '.gitkeep'
        gitkeep.touch()
