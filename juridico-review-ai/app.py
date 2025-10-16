"""
Jurídico Review AI - Interface Streamlit
Sistema de revisão automatizada de minutas jurídicas usando Gemini API
"""

import streamlit as st
import google.generativeai as genai
from pathlib import Path
import time
import yaml
import io
from datetime import datetime
from collections import deque

# Configuração da página
st.set_page_config(
    page_title="⚖️ Jurídico Review AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        border-radius: 10px;
        font-weight: 600;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Importa módulos do backend
try:
    from src.parsing import parse_document
    from src.utils import load_catalog
except:
    st.error("⚠️ Erro ao importar módulos do backend. Verifique se está na pasta correta.")
    st.stop()


# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def load_available_catalogs():
    """Carrega lista de catálogos disponíveis"""
    catalog_dir = Path("data/catalogos")
    catalogs = {}

    for catalog_file in catalog_dir.glob("*.yaml"):
        try:
            with open(catalog_file, 'r', encoding='utf-8') as f:
                cat = yaml.safe_load(f)
                metadata = cat.get('metadata', {})
                catalogs[catalog_file.stem] = {
                    'file': catalog_file,
                    'nome': metadata.get('nome', catalog_file.stem),
                    'versao': metadata.get('versao', '?'),
                    'clausulas': len(cat.get('clausulas', []))
                }
        except:
            pass

    return catalogs


# Rate limiter global
if 'rate_limiter' not in st.session_state:
    st.session_state.rate_limiter = deque(maxlen=10)  # Últimas 10 chamadas


def rate_limit_wait():
    """Controla rate limit de 10 RPM (6 segundos entre requests)"""
    now = time.time()

    if len(st.session_state.rate_limiter) >= 10:
        oldest = st.session_state.rate_limiter[0]
        time_since_oldest = now - oldest

        # Se as últimas 10 chamadas foram em menos de 60 segundos, aguarda
        if time_since_oldest < 60:
            wait_time = 60 - time_since_oldest + 1
            time.sleep(wait_time)

    # Adiciona timestamp da chamada atual
    st.session_state.rate_limiter.append(time.time())


def classify_and_suggest_with_gemini(clause_title, clause_content, catalog_clause, api_key):
    """Classifica cláusula e gera sugestão usando Gemini API com rate limiting"""

    # Rate limiting: 10 RPM
    rate_limit_wait()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Trunca conteúdo
    content_preview = clause_content[:800]

    # Keywords
    keywords = ', '.join(catalog_clause.get('keywords', [])[:5])
    template = catalog_clause.get('template', 'Template não disponível')

    prompt = f"""Você é um especialista em revisão de documentos jurídicos.

CLÁUSULA ESPERADA: {catalog_clause.get('titulo')}
Keywords: {keywords}
Obrigatória: {'SIM' if catalog_clause.get('obrigatoria') else 'NÃO'}

TEMPLATE PADRÃO:
{template}

CLÁUSULA DO DOCUMENTO:
Título: {clause_title}
Texto: {content_preview}...

TAREFAS:
1. CLASSIFIQUE como:
   - PRESENTE: contém TODOS elementos essenciais
   - PARCIAL: existe mas incompleto
   - AUSENTE: não trata do tema

2. Se PARCIAL ou AUSENTE, SUGIRA melhorias baseadas no template padrão.

RESPONDA APENAS COM JSON:
{{
  "classificacao": "PRESENTE|PARCIAL|AUSENTE",
  "confianca": 0.0-1.0,
  "justificativa": "breve explicação",
  "sugestao": "texto da sugestão baseado no template (só se PARCIAL/AUSENTE)"
}}"""

    try:
        response = model.generate_content(prompt)

        # Parse resposta
        import json
        import re

        text = response.text.strip()
        # Remove markdown
        text = text.replace('```json', '').replace('```', '')

        # Tenta extrair JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            result = json.loads(text)

        # Valida
        if result.get('classificacao') not in ['PRESENTE', 'PARCIAL', 'AUSENTE']:
            result['classificacao'] = 'PARCIAL'

        # Se não veio sugestão mas é PARCIAL/AUSENTE, usa o template
        if result['classificacao'] in ['PARCIAL', 'AUSENTE'] and not result.get('sugestao'):
            result['sugestao'] = template

        return result

    except Exception as e:
        return {
            'classificacao': 'PARCIAL',
            'confianca': 0.0,
            'justificativa': f'Erro: {str(e)[:100]}',
            'sugestao': template
        }


# ========================================
# INTERFACE PRINCIPAL
# ========================================

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("⚖️ Jurídico Review AI")
    st.markdown("**Sistema inteligente de revisão de minutas jurídicas**")
with col2:
    st.image("https://img.icons8.com/3d-fluency/94/law.png", width=100)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")

    # API Key Gemini
    gemini_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        help="Obtenha em: https://makersuite.google.com/app/apikey"
    )

    st.markdown("---")

    # Seleção de catálogo
    st.subheader("📚 Catálogo")
    catalogs = load_available_catalogs()

    catalog_options = {
        f"{info['nome']} v{info['versao']} ({info['clausulas']} cláusulas)": key
        for key, info in catalogs.items()
    }

    selected_catalog = st.selectbox(
        "Selecione o catálogo",
        options=list(catalog_options.keys()),
        index=2 if "v3" in str(catalog_options.keys()) else 0
    )

    catalog_key = catalog_options[selected_catalog]

    st.markdown("---")

    # Opções avançadas
    with st.expander("🔧 Opções Avançadas"):
        skip_tier2 = st.checkbox("Pular Tier-2 (apenas classificar)", value=True)
        top_k = st.slider("Top-K matches", 1, 10, 3)

    st.markdown("---")

    # Info
    st.info("""
    **Como usar:**
    1. Cole sua API Key do Gemini
    2. Selecione o catálogo
    3. Faça upload da minuta
    4. Clique em Analisar
    5. Baixe os relatórios
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["📄 Análise", "📊 Resultados", "❓ Ajuda"])

with tab1:
    st.header("Upload da Minuta")

    uploaded_file = st.file_uploader(
        "Selecione o arquivo (.docx ou .pdf)",
        type=['docx', 'pdf'],
        help="Faça upload da minuta que deseja analisar"
    )

    if uploaded_file:
        st.success(f"✅ Arquivo carregado: {uploaded_file.name}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tamanho", f"{uploaded_file.size / 1024:.1f} KB")
        with col2:
            st.metric("Tipo", uploaded_file.type.split('/')[-1].upper())
        with col3:
            st.metric("Catálogo", catalog_key.replace('catalogo_', '').upper())

    st.markdown("---")

    # Botão de análise
    if st.button("🚀 Iniciar Análise", disabled=not (uploaded_file and gemini_key)):

        if not gemini_key:
            st.error("⚠️ Por favor, insira sua Gemini API Key na barra lateral")
            st.stop()

        # Salva arquivo temporariamente
        temp_path = Path("data/entrada") / uploaded_file.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.read())

        # Progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # 1. Parse documento
            status_text.text("📄 Parseando documento...")
            progress_bar.progress(10)

            document = parse_document(str(temp_path))
            st.session_state['document'] = document

            status_text.text(f"✅ {len(document.clauses)} cláusulas encontradas")
            progress_bar.progress(20)
            time.sleep(0.5)

            # 2. Carrega catálogo
            status_text.text("📚 Carregando catálogo...")
            progress_bar.progress(30)

            catalog = load_catalog(str(catalogs[catalog_key]['file']))

            # 3. Classificação
            status_text.text("🤖 Classificando com Gemini AI...")
            progress_bar.progress(40)

            results = []
            total_clauses = len(document.clauses)

            for i, clause in enumerate(document.clauses):
                # Update progress
                progress = 40 + int((i / total_clauses) * 50)
                progress_bar.progress(progress)
                status_text.text(f"🤖 Analisando cláusula {i+1}/{total_clauses}: {clause['title'][:40]}...")

                # Encontra melhor match no catálogo (simplificado)
                best_match = None
                best_score = 0

                for cat_clause in catalog['clausulas']:
                    # Score simples por keywords
                    score = 0
                    text_combined = (clause['title'] + " " + clause['content'][:500]).lower()

                    for kw in cat_clause.get('keywords', []):
                        if kw.lower() in text_combined:
                            score += 1

                    if score > best_score:
                        best_score = score
                        best_match = cat_clause

                # Classifica e gera sugestão com Gemini
                if best_match:
                    classification = classify_and_suggest_with_gemini(
                        clause['title'],
                        clause['content'],
                        best_match,
                        gemini_key
                    )

                    results.append({
                        'clause': clause,
                        'classification': classification,
                        'catalog_match': best_match,
                        'match_score': best_score
                    })
                else:
                    results.append({
                        'clause': clause,
                        'classification': {
                            'classificacao': 'AUSENTE',
                            'confianca': 0.0,
                            'justificativa': 'Sem match no catálogo'
                        },
                        'catalog_match': None,
                        'match_score': 0
                    })

            # Salva resultados
            st.session_state['results'] = results
            st.session_state['catalog'] = catalog

            # Finaliza
            progress_bar.progress(100)
            status_text.text("✅ Análise concluída!")

            time.sleep(1)
            st.success("🎉 Análise concluída com sucesso!")
            st.balloons()

            # Remove arquivo temporário
            temp_path.unlink()

        except Exception as e:
            st.error(f"❌ Erro durante análise: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

with tab2:
    st.header("📊 Resultados da Análise")

    if 'results' not in st.session_state:
        st.info("👈 Faça upload de uma minuta e clique em 'Iniciar Análise' para ver os resultados")
    else:
        results = st.session_state['results']

        # Métricas
        presente = sum(1 for r in results if r['classification']['classificacao'] == 'PRESENTE')
        parcial = sum(1 for r in results if r['classification']['classificacao'] == 'PARCIAL')
        ausente = sum(1 for r in results if r['classification']['classificacao'] == 'AUSENTE')
        total = len(results)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <div class="metric-value">{presente}</div>
                <div class="metric-label">✅ PRESENTE</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-value">{parcial}</div>
                <div class="metric-label">⚠️ PARCIAL</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <div class="metric-value">{ausente}</div>
                <div class="metric-label">❌ AUSENTE</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            acuracia = ((presente + parcial) / total * 100) if total > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{acuracia:.0f}%</div>
                <div class="metric-label">📈 Acurácia</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Tabela de resultados
        st.subheader("Detalhamento das Cláusulas")

        import pandas as pd

        table_data = []
        for r in results:
            row = {
                'Cláusula': r['clause']['title'][:60],
                'Status': r['classification']['classificacao'],
                'Confiança': f"{r['classification'].get('confianca', 0):.0%}",
                'Match Catálogo': r['catalog_match']['titulo'][:40] if r['catalog_match'] else 'N/A',
                'Justificativa': r['classification']['justificativa'][:80]
            }

            # Adiciona sugestão se PARCIAL ou AUSENTE
            if r['classification']['classificacao'] in ['PARCIAL', 'AUSENTE']:
                row['Sugestão'] = r['classification'].get('sugestao', 'N/A')[:100] + '...'
            else:
                row['Sugestão'] = '-'

            table_data.append(row)

        df = pd.DataFrame(table_data)

        # Colorir status
        def color_status(val):
            if val == 'PRESENTE':
                return 'background-color: #d4edda; color: #155724'
            elif val == 'PARCIAL':
                return 'background-color: #fff3cd; color: #856404'
            else:
                return 'background-color: #f8d7da; color: #721c24'

        # Aplicar estilo condicionalmente: só se a coluna 'Status' existir
        try:
            if 'Status' in df.columns:
                styled = df.style.applymap(color_status, subset=['Status'])
            else:
                styled = df

            st.dataframe(
                styled,
                use_container_width=True,
                height=400
            )
        except Exception as e:
            # Fallback: mostra o dataframe sem estilo e escreve o erro nos logs
            st.error(f"Erro ao aplicar estilo à tabela: {e}")
            st.dataframe(df, use_container_width=True, height=400)

        st.markdown("---")

        # Downloads
        st.subheader("📥 Baixar Relatórios")

        col1, col2 = st.columns(2)

        with col1:
            # Gerar Excel
            import pandas as pd
            from io import BytesIO

            excel_data = []
            for r in results:
                excel_data.append({
                    'Cláusula Documento': r['clause']['title'],
                    'Cláusula Catálogo': r['catalog_match']['titulo'] if r['catalog_match'] else 'N/A',
                    'Status': r['classification']['classificacao'],
                    'Confiança': r['classification'].get('confianca', 0),
                    'Justificativa': r['classification']['justificativa'],
                    'Sugestão': r['classification'].get('sugestao', 'N/A'),
                    'Obrigatória': 'SIM' if r['catalog_match'] and r['catalog_match'].get('obrigatoria') else 'NÃO',
                    'Categoria': r['catalog_match'].get('categoria', 'N/A') if r['catalog_match'] else 'N/A'
                })

            df_excel = pd.DataFrame(excel_data)

            # Cria arquivo Excel em memória
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_excel.to_excel(writer, index=False, sheet_name='Análise')

                # Ajusta largura das colunas
                worksheet = writer.sheets['Análise']
                for idx, col in enumerate(df_excel.columns):
                    max_len = max(df_excel[col].astype(str).apply(len).max(), len(col)) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_len, 50)

            buffer.seek(0)

            st.download_button(
                label="📊 Baixar Excel",
                data=buffer,
                file_name=f"analise_juridica_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            # TODO: Gerar DOCX
            st.button("📄 Baixar DOCX", disabled=True, help="Em desenvolvimento")

with tab3:
    st.header("❓ Ajuda")

    st.markdown("""
    ### 🚀 Como usar o sistema

    1. **Obtenha sua API Key do Gemini:**
       - Acesse: https://makersuite.google.com/app/apikey
       - Crie uma API Key gratuita
       - Cole na barra lateral

    2. **Selecione o catálogo apropriado:**
       - CRI v3: Para Certificados de Recebíveis Imobiliários
       - CRA: Para Certificados de Recebíveis do Agronegócio
       - Debênture: Para Debêntures

    3. **Faça upload da minuta:**
       - Formatos aceitos: .docx ou .pdf
       - Tamanho máximo: 200MB

    4. **Analise:**
       - Clique em "Iniciar Análise"
       - Aguarde o processamento (2-5 minutos)
       - Veja os resultados

    5. **Baixe os relatórios:**
       - Excel: Tabela detalhada
       - DOCX: Relatório narrativo

    ---

    ### 📊 Entendendo os Resultados

    - **✅ PRESENTE:** Cláusula completa e adequada
    - **⚠️ PARCIAL:** Cláusula existe mas incompleta
    - **❌ AUSENTE:** Cláusula não encontrada ou inadequada

    ---

    ### 💰 Custos

    - **Tier Gratuito Gemini:** 1.500 requests/dia
    - **Custo por análise:** ~R$ 0,07 (tier pago)
    - **Streamlit Cloud:** Grátis

    ---

    ### 🔒 Privacidade

    - Documentos são processados temporariamente
    - Análise de texto enviada para Gemini API
    - Nenhum dado é armazenado permanentemente
    - Use servidor interno para máxima privacidade

    ---

    ### 🐛 Problemas?

    - Verifique sua API Key do Gemini
    - Confirme formato do arquivo (.docx ou .pdf)
    - Veja logs de erro na aba Análise

    ---

    **Versão:** 1.0.0 | **Backend:** Gemini 1.5 Flash
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    ⚖️ <strong>Jurídico Review AI</strong> | Powered by Gemini API<br>
    Sistema de revisão automatizada de minutas jurídicas
</div>
""", unsafe_allow_html=True)
