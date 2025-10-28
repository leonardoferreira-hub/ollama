"""
Script para gerar catálogos completos a partir de documentos GOLD
Extrai todas as cláusulas e cria catálogos estruturados
"""

import sys
from pathlib import Path
import re

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsing import parse_document
import yaml

def clean_clause_title(title):
    """Remove numeração extra do título"""
    # Remove números finais tipo "42", "48" etc
    title = re.sub(r'\s+\d+$', '', title)
    # Remove numeração inicial tipo "12.", "13."
    title = re.sub(r'^\d+\.\s*', '', title)
    return title.strip()

def extract_keywords(title, content):
    """Extrai keywords inteligentes do título e conteúdo"""
    # Palavras do título
    title_words = [w.lower() for w in re.findall(r'\w+', title) if len(w) > 3]

    # Palavras importantes do conteúdo
    important_words = []
    content_lower = content.lower()

    # Termos jurídicos comuns
    legal_terms = [
        'emissora', 'cedente', 'devedor', 'garantia', 'lastro', 'crédito',
        'recebível', 'patrimônio', 'separado', 'fiduciário', 'assembleia',
        'vencimento', 'antecipado', 'resgate', 'amortização', 'juros',
        'remuneração', 'subordinação', 'declaração', 'obrigação', 'cessão',
        'destinação', 'recursos', 'imóvel', 'elegível', 'tributário'
    ]

    for term in legal_terms:
        if term in content_lower:
            important_words.append(term)

    # Combina e limita a 8 keywords
    keywords = list(dict.fromkeys(title_words + important_words))[:8]
    return keywords

def categorize_clause(title):
    """Categoriza a cláusula baseado no título"""
    title_lower = title.lower()

    if 'definição' in title_lower or 'definições' in title_lower:
        return 'definicoes', 'critica'
    elif 'emissora' in title_lower:
        return 'emissora', 'alta'
    elif 'cedente' in title_lower or 'devedor' in title_lower:
        return 'partes', 'alta'
    elif 'crédito' in title_lower or 'lastro' in title_lower or 'recebível' in title_lower:
        return 'lastro', 'critica'
    elif 'destinação' in title_lower:
        return 'destinacao', 'critica'
    elif 'garantia' in title_lower or 'coobrigação' in title_lower:
        return 'garantias', 'alta'
    elif 'subordinação' in title_lower:
        return 'subordinacao', 'media'
    elif 'patrimônio' in title_lower and 'separado' in title_lower:
        return 'patrimonio_separado', 'critica'
    elif 'assembleia' in title_lower:
        return 'assembleia', 'alta'
    elif 'vencimento' in title_lower or 'resgate' in title_lower:
        return 'vencimento', 'alta'
    elif 'amortização' in title_lower:
        return 'amortizacao', 'alta'
    elif 'remuneração' in title_lower or 'juros' in title_lower or 'rentabilidade' in title_lower:
        return 'remuneracao', 'critica'
    elif 'agente' in title_lower and 'fiduciário' in title_lower:
        return 'agente_fiduciario', 'alta'
    elif 'declaração' in title_lower or 'declarações' in title_lower:
        return 'declaracoes', 'media'
    elif 'obrigação' in title_lower or 'obrigações' in title_lower:
        return 'obrigacoes', 'alta'
    elif 'evento' in title_lower and 'inadimplemento' in title_lower:
        return 'eventos_inadimplemento', 'alta'
    elif 'liquidação' in title_lower:
        return 'liquidacao', 'media'
    elif 'publicidade' in title_lower:
        return 'publicidade', 'media'
    elif 'disposição' in title_lower or 'disposições' in title_lower:
        return 'disposicoes_gerais', 'baixa'
    elif 'notificação' in title_lower or 'notificações' in title_lower:
        return 'notificacoes', 'baixa'
    elif 'assinatura' in title_lower:
        return 'assinatura', 'baixa'
    elif 'anexo' in title_lower:
        return 'anexos', 'media'
    else:
        return 'outros', 'media'

def is_obligatory(title, category):
    """Define se a cláusula é obrigatória"""
    obligatory_categories = ['definicoes', 'lastro', 'destinacao', 'patrimonio_separado', 'remuneracao']

    if category in obligatory_categories:
        return True

    # Algumas cláusulas específicas também são obrigatórias
    title_lower = title.lower()
    if any(term in title_lower for term in ['emissora', 'cedente', 'crédito', 'garantia', 'vencimento']):
        return True

    return False

def generate_catalog_from_gold(gold_file, catalog_type):
    """Gera catálogo a partir de documento GOLD"""
    print(f"\n[PARSE] {gold_file.name}")
    doc = parse_document(str(gold_file))
    print(f"   [OK] {len(doc.clauses)} clausulas encontradas")

    clauses_data = []

    for idx, clause in enumerate(doc.clauses, 1):
        # Limpa título
        clean_title = clean_clause_title(clause['title'])

        # Extrai keywords
        keywords = extract_keywords(clean_title, clause['content'])

        # Categoriza
        category, importance = categorize_clause(clean_title)

        # Define se é obrigatória
        obligatory = is_obligatory(clean_title, category)

        # Template (primeiros 1000 caracteres do conteúdo)
        template = f"CLÁUSULA {{{{numero}}}} – {clean_title.upper()}\n\n{clause['content'][:1000]}"
        if len(clause['content']) > 1000:
            template += "...\n\n[Conteúdo completo no documento GOLD]"

        # Cria entrada do catálogo
        clause_entry = {
            'id': f"{catalog_type}_{idx:03d}",
            'titulo': clean_title,
            'categoria': category,
            'importancia': importance,
            'obrigatoria': obligatory,
            'keywords': keywords,
            'regex_patterns': [
                f"(?i){re.escape(clean_title[:20])}"  # Pattern básico
            ],
            'template': template
        }

        clauses_data.append(clause_entry)

    return clauses_data

def create_catalog_yaml(clauses, catalog_name, catalog_type, description):
    """Cria estrutura YAML do catálogo"""
    catalog = {
        'metadata': {
            'nome': catalog_name,
            'versao': '2.0.0',
            'tipo': catalog_type,
            'hash': f"{catalog_type.lower()}_gold_2025",
            'descricao': description,
            'data_atualizacao': '2025-10-28',
            'origem': 'Gerado automaticamente de documentos GOLD'
        },
        'clausulas': clauses
    }

    return catalog

def main():
    print("="*60)
    print("GERACAO DE CATALOGOS A PARTIR DE DOCUMENTOS GOLD")
    print("="*60)

    gold_dir = Path("data/documentos_gold")
    catalog_dir = Path("data/catalogos")

    # Documentos GOLD
    gold_destinacao = gold_dir / "GOLD_CRI_DESTINACAO_MODELO_2025.docx"
    gold_sem_destinacao = gold_dir / "GOLD_CRI_SEM_DESTINACAO_PADRAO.docx"

    # Verifica se existem
    if not gold_destinacao.exists():
        print(f"[ERRO] Documento GOLD nao encontrado: {gold_destinacao}")
        return

    if not gold_sem_destinacao.exists():
        print(f"[ERRO] Documento GOLD nao encontrado: {gold_sem_destinacao}")
        return

    print("\n[INFO] Documentos GOLD encontrados")

    # 1. Gera catálogo CRI COM DESTINAÇÃO
    print("\n" + "="*60)
    print("[1/2] CATALOGO CRI COM DESTINACAO")
    print("="*60)

    clauses_dest = generate_catalog_from_gold(gold_destinacao, "CRI_DEST")
    catalog_dest = create_catalog_yaml(
        clauses_dest,
        "Catálogo CRI - Com Destinação Específica",
        "CRI_COM_DESTINACAO",
        "Catálogo completo para CRI com destinação específica de recursos (gerado de documento GOLD)"
    )

    output_dest = catalog_dir / "catalogo_cri_destinacao.yaml"
    with open(output_dest, 'w', encoding='utf-8') as f:
        yaml.dump(catalog_dest, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\n[OK] Catalogo salvo: {output_dest}")
    print(f"   [INFO] {len(clauses_dest)} clausulas")

    # 2. Gera catálogo CRI SEM DESTINAÇÃO
    print("\n" + "="*60)
    print("[2/2] CATALOGO CRI SEM DESTINACAO")
    print("="*60)

    clauses_sem = generate_catalog_from_gold(gold_sem_destinacao, "CRI_SDEST")
    catalog_sem = create_catalog_yaml(
        clauses_sem,
        "Catálogo CRI - Sem Destinação Específica",
        "CRI_SEM_DESTINACAO",
        "Catálogo completo para CRI sem destinação específica de recursos (gerado de documento GOLD)"
    )

    output_sem = catalog_dir / "catalogo_cri_sem_destinacao.yaml"
    with open(output_sem, 'w', encoding='utf-8') as f:
        yaml.dump(catalog_sem, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\n[OK] Catalogo salvo: {output_sem}")
    print(f"   [INFO] {len(clauses_sem)} clausulas")

    # 3. Remove catálogos antigos
    print("\n" + "="*60)
    print("[3/3] LIMPEZA DE CATALOGOS ANTIGOS")
    print("="*60)

    old_catalogs = [
        'catalogo_cra.yaml',
        'catalogo_cri.yaml',
        'catalogo_cri_v2.yaml',
        'catalogo_cri_v3.yaml',
        'catalogo_debenture.yaml',
        'sugestoes_catalogo_gold.yaml'
    ]

    for old_cat in old_catalogs:
        old_path = catalog_dir / old_cat
        if old_path.exists():
            old_path.unlink()
            print(f"[REMOVE] {old_cat}")

    print("\n" + "="*60)
    print("[CONCLUIDO] CATALOGOS GERADOS COM SUCESSO")
    print("="*60)
    print(f"\nCatalogos disponiveis:")
    print(f"  1. {output_dest.name} ({len(clauses_dest)} clausulas)")
    print(f"  2. {output_sem.name} ({len(clauses_sem)} clausulas)")

if __name__ == "__main__":
    main()
