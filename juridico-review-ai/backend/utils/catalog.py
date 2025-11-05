"""
Funções para carregamento e manipulação de catálogos YAML
"""

import yaml
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