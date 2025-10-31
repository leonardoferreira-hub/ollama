"""
Script para gerar explicações automáticas para todas as cláusulas do catálogo
usando Gemini AI
"""

import yaml
import google.generativeai as genai
import time
from datetime import datetime
import os
import sys

def gerar_explicacao_clausula(titulo, categoria, keywords, template, api_key):
    """Gera explicação detalhada para uma cláusula"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    keywords_str = ', '.join(keywords[:10]) if keywords else 'N/A'
    template_preview = template[:800] if template else 'N/A'
    
    prompt = f"""Você é um especialista em documentos jurídicos de Certificados de Recebíveis Imobiliários (CRI).

TAREFA: Gerar uma explicação DETALHADA e PRÁTICA do que a seguinte cláusula deve conter em um Termo de Securitização de CRI.

CLÁUSULA:
Título: {titulo}
Categoria: {categoria}
Keywords: {keywords_str}

TEMPLATE/CONTEXTO:
{template_preview}

INSTRUÇÕES OBRIGATÓRIAS:
1. Descreva EXATAMENTE o que esta cláusula deve conter
2. Liste TODOS os elementos ESSENCIAIS que devem aparecer
3. Mencione informações OBRIGATÓRIAS por lei (Resolução CVM 60/2021, Lei 14.430/2022)
4. Dê EXEMPLOS CONCRETOS de texto esperado
5. Mencione o que NÃO confundir (se relevante)
6. Seja ESPECÍFICO sobre formato, estrutura e conteúdo

FORMATO DA RESPOSTA:
- Use português claro e objetivo
- Use bullets/listas para organizar
- Inclua exemplos práticos
- Mencione obrigatoriedade legal quando aplicável
- Seja completo mas conciso (máximo 500 palavras)

NÃO repita apenas o título. Seja MUITO ESPECÍFICO sobre o conteúdo esperado.

EXPLICAÇÃO DETALHADA:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Erro ao gerar explicação: {str(e)}")
        return f"[Erro ao gerar: {str(e)}]"


def processar_catalogo(catalog_file, api_key, dry_run=False):
    """Processa um catálogo completo gerando explicações"""
    
    print(f"\n{'='*80}")
    print(f"📂 Processando: {catalog_file}")
    print(f"{'='*80}\n")
    
    # Carrega catálogo
    with open(catalog_file, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)
    
    clausulas = catalog.get('clausulas', [])
    total = len(clausulas)
    
    print(f"Total de cláusulas: {total}")
    print(f"Dry run: {'SIM (não vai salvar)' if dry_run else 'NÃO (vai salvar)'}")
    print()
    
    # Processa cada cláusula
    modificadas = 0
    puladas = 0
    erros = 0
    
    for idx, clausula in enumerate(clausulas, 1):
        clausula_id = clausula.get('id', 'SEM_ID')
        titulo = clausula.get('titulo', 'Sem título')
        explicacao_atual = clausula.get('explicacao', '')
        
        print(f"\n[{idx}/{total}] {clausula_id}: {titulo[:60]}...")
        
        # Se já tem explicação longa, pula
        if explicacao_atual and len(explicacao_atual.strip()) > 100:
            print(f"  ⏭️  Já tem explicação ({len(explicacao_atual)} chars) - pulando")
            puladas += 1
            continue
        
        # Gera explicação
        print(f"  🤖 Gerando explicação com Gemini AI...")
        
        try:
            explicacao = gerar_explicacao_clausula(
                titulo=titulo,
                categoria=clausula.get('categoria', 'outros'),
                keywords=clausula.get('keywords', []),
                template=clausula.get('template', ''),
                api_key=api_key
            )
            
            if explicacao and not explicacao.startswith('[Erro'):
                clausula['explicacao'] = explicacao
                modificadas += 1
                print(f"  ✅ Gerada ({len(explicacao)} chars)")
                
                # Preview
                preview = explicacao[:150].replace('\n', ' ')
                print(f"  💬 Preview: {preview}...")
            else:
                erros += 1
                print(f"  ❌ Erro na geração")
            
            # Rate limiting - aguarda 6 segundos entre requests (10 RPM)
            if idx < total:
                time.sleep(6)
                
        except Exception as e:
            erros += 1
            print(f"  ❌ Exceção: {str(e)}")
    
    # Salva catálogo atualizado
    if not dry_run and modificadas > 0:
        print(f"\n💾 Salvando catálogo...")
        
        # Atualiza metadata
        catalog['metadata']['data_atualizacao'] = datetime.now().strftime('%Y-%m-%d')
        
        # Backup
        backup_file = catalog_file.replace('.yaml', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
        with open(backup_file, 'w', encoding='utf-8') as f:
            yaml.dump(catalog, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"  📦 Backup criado: {backup_file}")
        
        # Salva original
        with open(catalog_file, 'w', encoding='utf-8') as f:
            yaml.dump(catalog, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"  ✅ Catálogo salvo: {catalog_file}")
    
    # Resumo
    print(f"\n{'='*80}")
    print(f"📊 RESUMO")
    print(f"{'='*80}")
    print(f"Total de cláusulas:      {total}")
    print(f"✅ Modificadas:          {modificadas}")
    print(f"⏭️  Puladas (já tinham): {puladas}")
    print(f"❌ Erros:                {erros}")
    print(f"{'='*80}\n")
    
    return modificadas


if __name__ == "__main__":
    # API Key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERRO: Configure a variável de ambiente GEMINI_API_KEY")
        print("   export GEMINI_API_KEY='sua-chave-aqui'")
        sys.exit(1)
    
    print("🚀 GERADOR AUTOMÁTICO DE EXPLICAÇÕES DE CATÁLOGO")
    print("="*80)
    print("Este script vai gerar explicações detalhadas para cada cláusula")
    print("dos catálogos usando Gemini AI.")
    print("="*80)
    
    # Processa catálogos
    catalogos = [
        "data/catalogos/catalogo_cri_destinacao.yaml",
        "data/catalogos/catalogo_cri_sem_destinacao.yaml"
    ]
    
    total_modificadas = 0
    
    for catalogo in catalogos:
        if os.path.exists(catalogo):
            mods = processar_catalogo(catalogo, api_key, dry_run=False)
            total_modificadas += mods
        else:
            print(f"⚠️  Catálogo não encontrado: {catalogo}")
    
    print(f"\n✅ CONCLUÍDO! Total de explicações geradas: {total_modificadas}")
    print(f"📝 Os catálogos foram atualizados e backups foram criados.")
    print(f"🎯 Agora você pode revisar e editar as explicações na interface do Streamlit.")

