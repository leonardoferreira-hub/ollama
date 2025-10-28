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
    page_title="🏠 Revisor de Documentos - Travessia",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado - Visual Profissional Travessia
st.markdown("""
<style>
    /* Paleta de cores Travessia */
    :root {
        --travessia-primary: #1e3a5f;
        --travessia-secondary: #2c5282;
        --travessia-accent: #3182ce;
        --travessia-success: #38a169;
        --travessia-warning: #d69e2e;
        --travessia-danger: #e53e3e;
    }

    .main {
        padding: 2rem;
        background-color: #f7fafc;
    }

    /* Título principal */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #4a5568;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* Botões */
    .stButton>button {
        width: 100%;
        background: #1e3a5f;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background: #2c5282;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
    }

    /* Cards de métricas */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #1e3a5f;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #1e3a5f;
    }

    /* Headers */
    h1, h2, h3 {
        color: #1e3a5f;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        color: #4a5568;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1e3a5f;
        color: white;
    }

    /* Upload area */
    .stFileUploader {
        background: white;
        border: 2px dashed #cbd5e0;
        border-radius: 8px;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Importa módulos do backend
try:
    from src.parsing_v2 import parse_document  # Parsing V2 baseado em Headings do Word
    from src.utils import load_catalog
    from src.vector_db import DocumentVectorDB, get_rag_context_for_suggestion
except:
    st.error("Erro ao importar módulos do backend. Verifique se está na pasta correta.")
    st.stop()

# Inicializa banco vetorial (persiste entre sessões)
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = DocumentVectorDB(persist_directory="data/vector_db")


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


def classify_and_suggest_with_gemini(clause_title, clause_content, catalog_clause, api_key, vector_db=None, catalog_name=""):
    """Classifica cláusula e gera sugestão usando Gemini API com RAG e rate limiting"""

    # Rate limiting: 10 RPM
    rate_limit_wait()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Trunca conteúdo
    content_preview = clause_content[:800]

    # Keywords
    keywords = ', '.join(catalog_clause.get('keywords', [])[:5])
    template = catalog_clause.get('template', 'Template não disponível')

    # 🆕 BUSCA CONTEXTO RAG de documentos anteriores
    rag_context = ""
    if vector_db:
        try:
            rag_context = get_rag_context_for_suggestion(
                db=vector_db,
                clause_title=clause_title,
                clause_content=clause_content,
                catalog_clause=catalog_clause,
                catalog_name=catalog_name,
                n_examples=2
            )
        except:
            rag_context = ""

    # 🆕 EXPLICAÇÃO CONTEXTUAL (se disponível)
    explicacao = catalog_clause.get('explicacao', '')
    explicacao_section = ""
    if explicacao and len(explicacao.strip()) > 10:
        explicacao_section = f"""
📚 EXPLICAÇÃO DETALHADA DO QUE ESTA CLÁUSULA DEVE CONTER:
{explicacao}

Esta explicação foi fornecida por especialistas e deve ser usada como referência principal para avaliar se o documento atende aos requisitos.
"""

    prompt = f"""Você é um especialista em revisão de documentos jurídicos.

CLÁUSULA ESPERADA: {catalog_clause.get('titulo')}
Keywords: {keywords}
Obrigatória: {'SIM' if catalog_clause.get('obrigatoria') else 'NÃO'}
{explicacao_section}

TEMPLATE PADRÃO:
{template}
{rag_context}

CLÁUSULA DO DOCUMENTO:
Título: {clause_title}
Texto: {content_preview}...

TAREFAS:
1. CLASSIFIQUE como:
   - PRESENTE: contém TODOS elementos essenciais descritos na explicação acima
   - PARCIAL: existe mas faltam elementos descritos na explicação
   - AUSENTE: não trata do tema ou não contém os elementos essenciais

2. Se PARCIAL ou AUSENTE, SUGIRA melhorias baseadas na explicação detalhada, template padrão E nos exemplos de boas práticas acima.

RESPONDA APENAS COM JSON:
{{
  "classificacao": "PRESENTE|PARCIAL|AUSENTE",
  "confianca": 0.0-1.0,
  "justificativa": "breve explicação comparando com a explicação detalhada fornecida",
  "sugestao": "texto da sugestão baseado na explicação, template e exemplos (só se PARCIAL/AUSENTE)"
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
st.markdown("""
<div class="main-title">Revisor de Documentos - Travessia</div>
<div class="subtitle">Sistema inteligente de revisão automatizada de minutas jurídicas</div>
""", unsafe_allow_html=True)

# Dica de navegação
st.info("💡 **Dica:** Use o menu lateral (👈) para acessar o **Gerenciador de Cláusulas GOLD** e personalizar as definições usadas pela IA.")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configurações de Análise")

    # API Key Gemini
    import os
    gemini_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Cole sua API Key do Gemini aqui"
    )

    if gemini_key:
        st.success("API Key configurada")
    else:
        st.warning("Insira sua API Key para continuar")

    st.markdown("---")

    # Seleção de catálogo
    st.subheader("Catálogo")
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
    with st.expander("Opções Avançadas"):
        skip_tier2 = st.checkbox("Pular Tier-2 (apenas classificar)", value=True)
        top_k = st.slider("Top-K matches", 1, 10, 3)

    st.markdown("---")

    # 🆕 Estatísticas do Banco de Conhecimento
    st.subheader("Base de Conhecimento")
    try:
        db_stats = st.session_state.vector_db.get_statistics()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documentos", db_stats['documentos_unicos'])
        with col2:
            st.metric("Cláusulas", db_stats['total_clausulas'])

        if db_stats['total_clausulas'] > 0:
            st.success("RAG ativo")
        else:
            st.info("Primeira análise iniciará a base")
    except:
        st.warning("Banco não inicializado")

    st.markdown("---")

    # Info
    st.info("""
    **Como usar:**
    1. Cole sua API Key do Gemini
    2. Selecione o catálogo
    3. Faça upload da minuta
    4. Clique em Analisar
    5. Baixe os relatórios

    **Cada documento analisado enriquece a base de conhecimento!**
    """)

# Main content - Abas principais
tab1, tab2, tab3 = st.tabs(["📄 Análise", "📊 Resultados", "❓ Ajuda"])

with tab1:
    st.header("Upload da Minuta")

    uploaded_file = st.file_uploader(
        "Selecione o arquivo (.docx ou .pdf)",
        type=['docx', 'pdf'],
        help="Faça upload da minuta que deseja analisar"
    )

    if uploaded_file:
        st.success(f"Arquivo carregado: {uploaded_file.name}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tamanho", f"{uploaded_file.size / 1024:.1f} KB")
        with col2:
            st.metric("Tipo", uploaded_file.type.split('/')[-1].upper())
        with col3:
            st.metric("Catálogo", catalog_key.replace('catalogo_', '').upper())

    st.markdown("---")

    # Botão de análise
    if st.button("Iniciar Análise", disabled=not (uploaded_file and gemini_key)):

        if not gemini_key:
            st.error("Por favor, insira sua Gemini API Key na barra lateral")
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
            status_text.text("Parseando documento...")
            progress_bar.progress(10)

            document = parse_document(str(temp_path))
            st.session_state['document'] = document

            status_text.text(f"{len(document.clauses)} cláusulas encontradas")
            progress_bar.progress(20)
            time.sleep(0.5)

            # 2. Carrega catálogo
            status_text.text("Carregando catálogo...")
            progress_bar.progress(30)

            catalog = load_catalog(str(catalogs[catalog_key]['file']))

            # 3. Classificação - ABORDAGEM CORRETA: itera sobre CATÁLOGO
            status_text.text("Classificando com Gemini AI...")
            progress_bar.progress(40)

            results = []
            catalog_clauses = catalog.get('clausulas', [])
            total_catalog = len(catalog_clauses)

            # Junta todo conteúdo do documento para busca
            doc_full_text = "\n\n".join([
                f"{c['title']}\n{c['content']}" 
                for c in document.clauses
            ]).lower()

            for i, cat_clause in enumerate(catalog_clauses):
                # Update progress
                progress = 40 + int((i / total_catalog) * 50)
                progress_bar.progress(progress)
                cat_title = cat_clause.get('titulo', 'Sem título')
                status_text.text(f"Verificando cláusula {i+1}/{total_catalog}: {cat_title[:50]}...")

                # Encontra melhor match no documento usando múltiplas estratégias
                best_doc_clause = None
                best_score = 0
            
                from rapidfuzz import fuzz
            
                cat_title_lower = cat_title.lower()
                cat_keywords = [kw.lower() for kw in cat_clause.get('keywords', [])]
            
                # 🆕 Extrai palavras-chave da explicação (se houver)
                explicacao = cat_clause.get('explicacao', '')
                cat_explicacao_keywords = []
                if explicacao and len(explicacao.strip()) > 20:
                    # Extrai palavras importantes da explicação (> 5 chars, não stopwords comuns)
                    stopwords = {'esta', 'cláusula', 'deve', 'conter', 'incluir', 'sendo', 'para', 'pela', 'pelo', 'desta', 'deste', 'como', 'também', 'todos', 'todas'}
                    words = explicacao.lower().split()
                    cat_explicacao_keywords = [w for w in words if len(w) > 5 and w not in stopwords][:10]

                for doc_clause in document.clauses:
                    doc_title = doc_clause['title'].lower()
                    doc_text = (doc_clause['title'] + " " + doc_clause['content'][:3000]).lower()  # Aumentado para 3000 chars
                
                    score = 0
                
                    # 1. Similaridade do título (peso alto)
                    title_similarity = fuzz.partial_ratio(cat_title_lower, doc_title) / 100.0
                    score += title_similarity * 50  # Peso 50 para título
                
                    # 2. Similaridade fuzzy de palavras-chave importantes do título do catálogo
                    cat_important_words = [w for w in cat_title_lower.split() if len(w) > 3]
                    for word in cat_important_words:
                        if word in doc_title:
                            score += 10  # Bônus por palavra exata no título
                        elif any(fuzz.ratio(word, doc_word) > 80 for doc_word in doc_title.split()):
                            score += 5  # Bônus por palavra similar no título
                
                    # 3. Keywords no texto (peso médio)
                    keywords_in_text = sum(1 for kw in cat_keywords if kw in doc_text)
                    score += keywords_in_text * 3
                
                    # 🆕 4. Keywords da explicação no texto (peso médio-alto)
                    explicacao_keywords_in_text = sum(1 for kw in cat_explicacao_keywords if kw in doc_text)
                    score += explicacao_keywords_in_text * 4  # Peso maior pois são palavras contextuais importantes
                
                    # 5. Posição no documento (cláusulas iniciais têm leve bônus para empate)
                    position_bonus = (1 - (doc_clause['index'] / max(len(document.clauses), 1))) * 2
                    score += position_bonus

                    if score > best_score:
                        best_score = score
                        best_doc_clause = doc_clause

                # Se não achou match razoável, busca em todo documento
                if not best_doc_clause or best_score < 5:
                    # Verifica se alguma keyword aparece em qualquer lugar do documento
                    keywords_found = sum(1 for kw in cat_keywords if kw in doc_full_text)
                
                    if keywords_found > 0 and document.clauses:
                        # Busca a cláusula que mais menciona as keywords
                        best_kw_clause = None
                        best_kw_count = 0
                        for doc_clause in document.clauses:
                            doc_text = (doc_clause['title'] + " " + doc_clause['content'][:2000]).lower()
                            kw_count = sum(1 for kw in cat_keywords if kw in doc_text)
                            if kw_count > best_kw_count:
                                best_kw_count = kw_count
                                best_kw_clause = doc_clause
                    
                        if best_kw_clause and best_kw_count > best_score:
                            best_doc_clause = best_kw_clause
                            best_score = best_kw_count * 2

                # Classifica e gera sugestão com Gemini + RAG
                if best_doc_clause and best_score > 0:
                    classification = classify_and_suggest_with_gemini(
                        best_doc_clause['title'],
                        best_doc_clause['content'],
                        cat_clause,
                        gemini_key,
                        vector_db=st.session_state.vector_db,
                        catalog_name=catalog_key
                    )

                    results.append({
                        'catalog_clause': cat_clause,
                        'doc_clause': best_doc_clause,
                        'classification': classification,
                        'match_score': best_score
                    })
                else:
                    # Cláusula do catálogo não encontrada no documento
                    results.append({
                        'catalog_clause': cat_clause,
                        'doc_clause': None,
                        'classification': {
                            'classificacao': 'AUSENTE',
                            'confianca': 1.0,
                            'justificativa': f'Cláusula não encontrada no documento. Esperado: {cat_title}',
                            'sugestao': cat_clause.get('template', 'Adicionar esta cláusula ao documento.')
                        },
                        'match_score': 0
                    })

            # Salva resultados
            st.session_state['results'] = results
            st.session_state['catalog'] = catalog

            # 🆕 SALVA DOCUMENTO NO BANCO VETORIAL
            status_text.text("Salvando documento na base de conhecimento...")
            try:
                st.session_state.vector_db.add_document(
                    document_name=uploaded_file.name,
                    clauses=results,
                    catalog_name=catalog_key
                )
                db_stats = st.session_state.vector_db.get_statistics()
                status_text.text(f"Documento salvo! Total na base: {db_stats['total_clausulas']} cláusulas, {db_stats['documentos_unicos']} documentos")
            except Exception as e:
                status_text.text(f"Aviso: Não foi possível salvar no banco: {str(e)[:50]}")

            # Finaliza
            progress_bar.progress(100)
            time.sleep(1)

            st.success("Análise concluída com sucesso!")
            st.balloons()

            # Remove arquivo temporário
            temp_path.unlink()

        except Exception as e:
            st.error(f"Erro durante análise: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

with tab2:
    st.header("Resultados da Análise")

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
                <div class="metric-label">PRESENTE</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-value">{parcial}</div>
                <div class="metric-label">PARCIAL</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <div class="metric-value">{ausente}</div>
                <div class="metric-label">AUSENTE</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            acuracia = ((presente + parcial) / total * 100) if total > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{acuracia:.0f}%</div>
                <div class="metric-label">Acurácia</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Tabela de resultados
        st.subheader("Detalhamento das Cláusulas")

        import pandas as pd

        table_data = []
        for r in results:
            cat_title = r['catalog_clause'].get('titulo', 'N/A')
            doc_title = r.get('doc_clause', {}).get('title', 'Não encontrada') if r.get('doc_clause') else 'Não encontrada'
        
            row = {
                'Cláusula Esperada': cat_title[:60],
                'Encontrada no Doc': doc_title[:60],
                'Status': r['classification']['classificacao'],
                'Confiança': f"{r['classification'].get('confianca', 0):.0%}",
                'Match Score': f"{r['match_score']:.2f}",
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
                styled = df.style.map(color_status, subset=['Status'])
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

        # Sistema de Feedback e Avaliação
        st.subheader("📊 Avaliação da Análise (Sistema de Aprendizado)")
    
        st.markdown("""
        Ajude o sistema a melhorar! Avalie a qualidade das análises abaixo.
        Suas avaliações são salvas e usadas para melhorar futuras análises.
        """)
    
        # Exibe avaliação por cláusula
        with st.expander("🎯 Avaliar Análises Individuais", expanded=False):
            for idx, r in enumerate(results[:10]):  # Primeiras 10 para não sobrecarregar
                cat_title = r['catalog_clause'].get('titulo', 'N/A')
                doc_title = r.get('doc_clause', {}).get('title', 'Não encontrada') if r.get('doc_clause') else 'Não encontrada'
                classification = r['classification']['classificacao']
            
                st.markdown(f"**{idx+1}. {cat_title[:60]}**")
            
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
                with col1:
                    st.text(f"Match: {doc_title[:50]}")
                with col2:
                    st.text(f"Status: {classification}")
                with col3:
                    st.text(f"Score: {r['match_score']:.1f}")
                with col4:
                    # Botões de avaliação
                    feedback_key = f"feedback_{idx}"
                
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("👍", key=f"good_{idx}", help="Análise correta"):
                            st.session_state[feedback_key] = {
                                'rating': 'good',
                                'clause_id': r['catalog_clause'].get('id'),
                                'doc_clause': doc_title,
                                'classification': classification,
                                'match_score': r['match_score']
                            }
                            # Salva feedback
                            try:
                                st.session_state.vector_db.save_feedback(
                                    catalog_clause_id=r['catalog_clause'].get('id'),
                                    doc_clause_title=doc_title,
                                    classification=classification,
                                    match_score=r['match_score'],
                                    rating='good',
                                    catalog_name=catalog_key
                                )
                                st.success("✅ Feedback positivo salvo!")
                            except:
                                pass
                
                    with col_b:
                        if st.button("👎", key=f"bad_{idx}", help="Análise incorreta"):
                            st.session_state[feedback_key] = {
                                'rating': 'bad',
                                'clause_id': r['catalog_clause'].get('id'),
                                'doc_clause': doc_title,
                                'classification': classification,
                                'match_score': r['match_score']
                            }
                            # Salva feedback
                            try:
                                st.session_state.vector_db.save_feedback(
                                    catalog_clause_id=r['catalog_clause'].get('id'),
                                    doc_clause_title=doc_title,
                                    classification=classification,
                                    match_score=r['match_score'],
                                    rating='bad',
                                    catalog_name=catalog_key
                                )
                                st.warning("⚠️ Feedback negativo salvo. Sistema aprenderá com isso!")
                            except:
                                pass
            
                # Mostra se já foi avaliado
                if feedback_key in st.session_state:
                    rating = st.session_state[feedback_key]['rating']
                    emoji = "✅" if rating == 'good' else "❌"
                    st.caption(f"{emoji} Avaliado como: {rating}")
            
                st.markdown("---")
    
        # Estatísticas de feedback
        if 'feedback_stats' in st.session_state:
            stats = st.session_state['feedback_stats']
            st.markdown("### 📈 Estatísticas de Feedback")
        
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avaliações Positivas", stats.get('good', 0))
            with col2:
                st.metric("Avaliações Negativas", stats.get('bad', 0))
            with col3:
                accuracy = stats.get('good', 0) / (stats.get('good', 0) + stats.get('bad', 1)) * 100
                st.metric("Taxa de Acerto", f"{accuracy:.1f}%")

        st.markdown("---")

        # Downloads
        st.subheader("Baixar Relatórios")

        col1, col2 = st.columns(2)

        with col1:
            # Gerar Excel
            import pandas as pd
            from io import BytesIO

            excel_data = []
            for r in results:
                doc_title = r.get('doc_clause', {}).get('title', 'Não encontrada') if r.get('doc_clause') else 'Não encontrada'
                cat_clause = r['catalog_clause']
            
                excel_data.append({
                    'Cláusula Esperada': cat_clause.get('titulo', 'N/A'),
                    'Encontrada no Doc': doc_title,
                    'Status': r['classification']['classificacao'],
                    'Confiança': r['classification'].get('confianca', 0),
                    'Justificativa': r['classification']['justificativa'],
                    'Sugestão': r['classification'].get('sugestao', 'N/A'),
                    'Obrigatória': 'SIM' if cat_clause.get('obrigatoria') else 'NÃO',
                    'Categoria': cat_clause.get('categoria', 'N/A'),
                    'Match Score': r['match_score']
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
                label="Baixar Excel",
                data=buffer,
                file_name=f"analise_juridica_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            # TODO: Gerar DOCX
            st.button("Baixar DOCX", disabled=True, help="Em desenvolvimento")

with tab3:
    st.header("Ajuda")

    st.markdown("""
    ### Como usar o sistema

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

    ### Entendendo os Resultados

    - **PRESENTE:** Cláusula completa e adequada
    - **PARCIAL:** Cláusula existe mas incompleta
    - **AUSENTE:** Cláusula não encontrada ou inadequada

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

# ========================================
# FUNÇÃO: GERAR SUGESTÃO DE EXPLICAÇÃO
# ========================================

def gerar_sugestao_explicacao(titulo: str, categoria: str, keywords: list, template: str, api_key: str) -> str:
    """
    Gera sugestão automática de explicação para uma cláusula usando Gemini AI
    
    Args:
        titulo: Título da cláusula
        categoria: Categoria da cláusula (lastro, remuneração, etc.)
        keywords: Lista de palavras-chave
        template: Template da cláusula (se houver)
        api_key: Gemini API Key
        
    Returns:
        Sugestão de explicação detalhada
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    keywords_str = ', '.join(keywords[:10]) if keywords else 'N/A'
    template_preview = template[:500] if template else 'N/A'

    prompt = f"""Você é um especialista em documentos jurídicos de Certificados de Recebíveis Imobiliários (CRI).

    TAREFA: Gerar uma explicação DETALHADA do que a seguinte cláusula deve conter.

    CLÁUSULA:
    Título: {titulo}
    Categoria: {categoria}
    Keywords: {keywords_str}

    TEMPLATE (se disponível):
    {template_preview}

    INSTRUÇÕES:
    1. Descreva em detalhes O QUE esta cláusula deve conter
    2. Liste elementos ESSENCIAIS que devem aparecer
    3. Mencione informações OBRIGATÓRIAS por lei ou regulação CVM
    4. Dê exemplos concretos de texto esperado
    5. Mencione o que NÃO confundir (se relevante)

    FORMATO DA RESPOSTA:
    Escreva em português, de forma clara e objetiva, usando:
    - Bullets para listar elementos
    - Exemplos práticos
    - Referências legais quando aplicável
    - Estrutura clara

    NÃO repita apenas o título. Seja ESPECÍFICO sobre conteúdo esperado.

    EXPLICAÇÃO DETALHADA:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Erro ao gerar sugestão: {str(e)}"


