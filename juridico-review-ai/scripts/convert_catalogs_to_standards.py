"""
Script para converter catálogos YAML em standards JSON v2.

Converte os catálogos existentes (data/catalogos/) em standards
JSON otimizados para o pipeline híbrido de validação.
"""
import yaml
import json
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

def extract_must_terms(keywords, importance):
    """
    Extrai termos obrigatórios baseado nas keywords e importância.
    """
    if not keywords:
        return []

    # Para cláusulas críticas, todos os keywords são obrigatórios
    if importance == "critica":
        return keywords[:5]  # Limita a 5 termos mais importantes
    elif importance == "alta":
        return keywords[:3]
    elif importance == "media":
        return keywords[:2]
    else:
        return keywords[:1]

def determine_category_rules(categoria):
    """
    Define regras específicas por categoria.
    """
    rules = {
        "lastro": {
            "must_not_include": ["sem lastro", "lastro inexistente"],
            "param_types": ["lastro_tipo", "percentual_lastro"]
        },
        "remuneracao": {
            "must_include_extra": ["taxa", "percentual", "%"],
            "param_types": ["indexador", "spread", "taxa"]
        },
        "patrimonio_separado": {
            "must_include_extra": ["isolamento", "separação"],
            "must_not_include": ["sem separação", "patrimônio comum"]
        },
        "destinacao": {
            "must_include_extra": ["destinação", "aplicação", "finalidade"],
            "param_types": ["destinacao_especifica", "percentual_destinado"]
        },
        "vencimento": {
            "must_include_extra": ["prazo", "vencimento", "data"],
            "param_types": ["data_vencimento", "prazo_meses"]
        },
        "emissora": {
            "must_include_extra": ["emissora", "securitizadora", "CNPJ"],
            "param_types": ["nome_emissora", "cnpj_emissora"]
        },
        "agente_fiduciario": {
            "must_include_extra": ["agente fiduciário", "representante"],
            "param_types": ["nome_agente", "cnpj_agente"]
        },
        "assembleia": {
            "must_include_extra": ["assembleia", "quorum", "deliberação"],
            "param_types": ["quorum_minimo", "tipo_deliberacao"]
        }
    }
    return rules.get(categoria, {})

def create_parameters(categoria, keywords):
    """
    Cria parâmetros a extrair baseado na categoria.
    """
    params = []

    if categoria == "remuneracao":
        params = [
            {"name": "indexador", "type": "enum", "values": ["CDI", "IPCA", "IGPM", "Prefixado"]},
            {"name": "spread", "type": "percent"},
            {"name": "taxa_anual", "type": "percent"}
        ]
    elif categoria == "lastro":
        params = [
            {"name": "tipo_lastro", "type": "string"},
            {"name": "valor_lastro", "type": "monetary"},
            {"name": "percentual_lastro", "type": "percent"}
        ]
    elif categoria == "destinacao":
        params = [
            {"name": "destinacao_especifica", "type": "string"},
            {"name": "percentual_destinado", "type": "percent"},
            {"name": "prazo_destinacao", "type": "duration"}
        ]
    elif categoria == "vencimento":
        params = [
            {"name": "data_vencimento", "type": "date"},
            {"name": "prazo_meses", "type": "integer"},
            {"name": "forma_amortizacao", "type": "enum", "values": ["price", "sac", "bullet", "series"]}
        ]
    elif categoria == "patrimonio_separado":
        params = [
            {"name": "patrimonio_isolado", "type": "boolean"},
            {"name": "regime_fiduciario", "type": "boolean"}
        ]
    elif categoria in ["emissora", "agente_fiduciario"]:
        params = [
            {"name": f"nome_{categoria}", "type": "string"},
            {"name": f"cnpj_{categoria}", "type": "string"},
            {"name": f"endereco_{categoria}", "type": "string"}
        ]

    return params

def convert_clause(clausula, doc_has_destinacao=True):
    """
    Converte uma cláusula YAML em cláusula JSON do standard.
    """
    categoria = clausula.get("categoria", "outros")
    importancia = clausula.get("importancia", "media")
    obrigatoria = clausula.get("obrigatoria", False)
    keywords = clausula.get("keywords", [])

    # ID convertido (CRI_DEST_001 -> C-001)
    old_id = clausula.get("id", "")
    new_id = old_id.replace("CRI_DEST_", "C-").replace("CRI_SEM_DEST_", "C-")
    if not new_id.startswith("C-"):
        new_id = f"C-{len(new_id):03d}"

    # Termos obrigatórios
    must_include = extract_must_terms(keywords, importancia)

    # Regras específicas da categoria
    cat_rules = determine_category_rules(categoria)
    must_include.extend(cat_rules.get("must_include_extra", []))
    must_not_include = cat_rules.get("must_not_include", [])

    # Para CRI sem destinação, remove referências a destinação
    if not doc_has_destinacao and "destinação" in must_include:
        must_include.remove("destinação")
        must_not_include.append("destinação específica")

    # Remove duplicatas
    must_include = list(dict.fromkeys(must_include))[:6]  # Max 6 termos
    must_not_include = list(dict.fromkeys(must_not_include))

    # Parâmetros
    parameters = create_parameters(categoria, keywords)

    return {
        "id": new_id,
        "title": clausula.get("titulo", ""),
        "category": categoria,
        "importance": importancia,
        "required": obrigatoria,
        "must_include": must_include,
        "must_not_include": must_not_include,
        "parameters": parameters,
        "original_id": old_id  # Mantém referência ao catálogo original
    }

def convert_catalog_to_standard(yaml_path, output_path, has_destinacao=True):
    """
    Converte um catálogo YAML completo em standard JSON v2.
    """
    print(f"[1/3] Carregando catálogo: {yaml_path}")
    with open(yaml_path, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)

    metadata = catalog.get("metadata", {})
    clausulas = catalog.get("clausulas", [])

    print(f"[2/3] Convertendo {len(clausulas)} cláusulas...")

    # Filtra e converte apenas cláusulas importantes
    converted_clauses = []
    for clausula in clausulas:
        # Pula anexos menos importantes
        if clausula.get("categoria") == "anexos" and clausula.get("importancia") == "baixa":
            continue

        # Converte
        try:
            converted = convert_clause(clausula, has_destinacao)
            converted_clauses.append(converted)
        except Exception as e:
            print(f"   AVISO: Erro ao converter {clausula.get('id')}: {e}")

    # Cria o standard JSON v2
    standard = {
        "version": metadata.get("tipo", "CRI").replace("_", "-") + ".v2",
        "jurisdiction": "BR",
        "product": "CRI",
        "metadata": {
            "source": "Converted from YAML catalog",
            "catalog_version": metadata.get("versao", "2.0.0"),
            "catalog_hash": metadata.get("hash", ""),
            "conversion_date": metadata.get("data_atualizacao", ""),
            "total_clauses": len(converted_clauses),
            "critical_clauses": sum(1 for c in converted_clauses if c["importance"] == "critica"),
            "required_clauses": sum(1 for c in converted_clauses if c["required"])
        },
        "clauses": converted_clauses
    }

    print(f"[3/3] Salvando standard: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(standard, f, ensure_ascii=False, indent=2)

    print(f"[OK] Standard criado com sucesso!")
    print(f"  - Total de clausulas: {len(converted_clauses)}")
    print(f"  - Clausulas criticas: {standard['metadata']['critical_clauses']}")
    print(f"  - Clausulas obrigatorias: {standard['metadata']['required_clauses']}")

    return standard

def main():
    """
    Converte ambos os catálogos.
    """
    base_dir = Path(__file__).parent.parent
    catalogs_dir = base_dir / "data" / "catalogos"
    standards_dir = base_dir / "standards" / "CRI"

    print("="*60)
    print("CONVERSAO DE CATALOGOS YAML PARA STANDARDS JSON V2")
    print("="*60)
    print()

    # 1. CRI com destinação
    print("[+] CRI COM DESTINACAO")
    convert_catalog_to_standard(
        yaml_path=catalogs_dir / "catalogo_cri_destinacao.yaml",
        output_path=standards_dir / "cri_com_destinacao.v2.json",
        has_destinacao=True
    )
    print()

    # 2. CRI sem destinação
    print("[+] CRI SEM DESTINACAO")
    convert_catalog_to_standard(
        yaml_path=catalogs_dir / "catalogo_cri_sem_destinacao.yaml",
        output_path=standards_dir / "cri_sem_destinacao.v2.json",
        has_destinacao=False
    )
    print()

    print("="*60)
    print("[OK] CONVERSAO CONCLUIDA!")
    print("="*60)
    print()
    print("Standards criados:")
    print(f"  - {standards_dir / 'cri_com_destinacao.v2.json'}")
    print(f"  - {standards_dir / 'cri_sem_destinacao.v2.json'}")
    print()
    print("Use-os na validação:")
    print("  python scripts/validate.py --pdf_path SEU_DOC.pdf \\")
    print("    --standard_path standards/CRI/cri_com_destinacao.v2.json")

if __name__ == "__main__":
    main()
