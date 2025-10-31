"""
Gerenciador de Sugestões de Cláusulas GOLD
Interface integrada ao sistema de revisão de documentos
"""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="📚 Gerenciar Cláusulas GOLD - Travessia",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado (mantém o estilo Travessia)
st.markdown("""
<style>
    .main {
        padding: 2rem;
        background-color: #f7fafc;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #4a5568;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #1e3a5f;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .clausula-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .clausula-card:hover {
        border-color: #3182ce;
        box-shadow: 0 4px 12px rgba(49, 130, 206, 0.1);
    }
    
    .clausula-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f7fafc;
    }
    
    .clausula-numero {
        background: #edf2f7;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: bold;
        color: #1e3a5f;
    }
    
    .tipo-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: #1e3a5f;
        color: white;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .pontos-atencao {
        background: #fffbeb;
        padding: 1rem;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        margin-top: 1rem;
    }
    
    .preview-content {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 6px;
        font-size: 0.9em;
        color: #4a5568;
        margin-top: 1rem;
        max-height: 150px;
        overflow-y: auto;
    }
    
    .success-message {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
    }
    
    .info-message {
        background: #dbeafe;
        color: #1e40af;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<h1 class="main-title">📚 Gerenciar Cláusulas GOLD</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Edite e personalize as sugestões de explicação das cláusulas dos documentos padrão</p>', unsafe_allow_html=True)

# Caminho para os documentos GOLD
GOLD_PATH = Path("/home/user/webapp/documentos_gold")

# Documentos disponíveis
DOCUMENTOS = {
    "CRI com Destinação 2025": "GOLD_CRI_DESTINACAO_MODELO_2025_catalogo_completo.json",
    "CRI sem Destinação Padrão": "GOLD_CRI_SEM_DESTINACAO_PADRAO_catalogo_completo.json"
}

# Inicializar session state
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'original_data' not in st.session_state:
    st.session_state.original_data = None
if 'edited_clauses' not in st.session_state:
    st.session_state.edited_clauses = set()
if 'selected_doc' not in st.session_state:
    st.session_state.selected_doc = None

# Sidebar
with st.sidebar:
    st.markdown("### 📄 Selecionar Documento")
    
    selected_doc = st.selectbox(
        "Escolha o documento GOLD:",
        [""] + list(DOCUMENTOS.keys()),
        key="doc_selector"
    )
    
    if selected_doc and selected_doc != st.session_state.selected_doc:
        # Carregar novo documento
        try:
            file_path = GOLD_PATH / DOCUMENTOS[selected_doc]
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                st.session_state.current_data = data
                st.session_state.original_data = json.loads(json.dumps(data))  # Deep copy
                st.session_state.edited_clauses = set()
                st.session_state.selected_doc = selected_doc
                st.success(f"✅ Documento carregado: {selected_doc}")
        except Exception as e:
            st.error(f"❌ Erro ao carregar documento: {e}")
    
    st.markdown("---")
    
    # Estatísticas
    if st.session_state.current_data:
        st.markdown("### 📊 Estatísticas")
        
        total = st.session_state.current_data['total_clausulas']
        editadas = len(st.session_state.edited_clauses)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", total, help="Total de cláusulas no documento")
        with col2:
            st.metric("Editadas", editadas, help="Cláusulas modificadas")
        
        # Progresso
        if total > 0:
            progress = editadas / total
            st.progress(progress)
            st.caption(f"{progress*100:.1f}% do documento revisado")
    
    st.markdown("---")
    
    # Busca
    st.markdown("### 🔍 Buscar Cláusulas")
    search_term = st.text_input(
        "Digite número, título ou palavra-chave:",
        key="search_input",
        placeholder="Ex: Definições, 1.1, assembleia..."
    )
    
    st.markdown("---")
    
    # Ações
    st.markdown("### ⚙️ Ações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar", use_container_width=True, type="primary"):
            if st.session_state.current_data:
                try:
                    file_path = GOLD_PATH / DOCUMENTOS[st.session_state.selected_doc]
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.current_data, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ {len(st.session_state.edited_clauses)} cláusulas salvas!")
                    st.session_state.edited_clauses = set()
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {e}")
            else:
                st.warning("⚠️ Nenhum documento carregado")
    
    with col2:
        if st.button("📥 Exportar", use_container_width=True):
            if st.session_state.current_data:
                json_str = json.dumps(st.session_state.current_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="⬇️ Baixar JSON",
                    data=json_str,
                    file_name=f"{st.session_state.selected_doc}_editado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ Nenhum documento carregado")
    
    if st.button("🔄 Resetar", use_container_width=True):
        if st.session_state.current_data:
            st.session_state.current_data = json.loads(json.dumps(st.session_state.original_data))
            st.session_state.edited_clauses = set()
            st.success("✅ Documento resetado para o estado original!")
            st.rerun()

# Conteúdo principal
if not st.session_state.current_data:
    st.info("👈 Selecione um documento GOLD na barra lateral para começar")
    
    # Instruções
    with st.expander("📖 Como usar este gerenciador", expanded=True):
        st.markdown("""
        ### 🎯 Objetivo
        Este gerenciador permite visualizar e **editar as sugestões de explicação** das cláusulas 
        dos documentos GOLD (padrão ouro) usados como referência na revisão de documentos CRI.
        
        ### 📝 Passo a Passo
        
        1. **Selecione um documento** na barra lateral
        2. **Visualize todas as cláusulas** com suas sugestões atuais
        3. **Edite as sugestões** diretamente nos campos de texto
        4. **Use a busca** para encontrar cláusulas específicas
        5. **Salve suas alterações** ou **exporte para JSON**
        
        ### 💡 Dicas
        
        - **Sugestões claras**: Use verbos precisos (Define, Estabelece, Regula)
        - **Contexto**: Mencione o objetivo da cláusula
        - **Partes envolvidas**: Cite emissora, titulares, agente quando relevante
        - **1-2 frases**: Seja objetivo e direto
        
        ### 🤖 Uso com IA
        
        Após editar, **exporte o JSON** e use em prompts para a IA:
        
        ```
        "Use estas definições como referência ao analisar documentos CRI:
        [Cole o JSON aqui]
        
        Compare cada cláusula do documento com os padrões GOLD."
        ```
        """)
else:
    # Filtrar cláusulas se houver busca
    clausulas = st.session_state.current_data['clausulas_com_sugestoes']
    
    if search_term:
        clausulas_filtradas = [
            c for c in clausulas
            if search_term.lower() in c['titulo'].lower() 
            or search_term.lower() in str(c['numero']).lower()
            or search_term.lower() in c['sugestao_explicacao'].lower()
        ]
        
        if clausulas_filtradas:
            st.info(f"🔍 Mostrando {len(clausulas_filtradas)} de {len(clausulas)} cláusulas")
            clausulas = clausulas_filtradas
        else:
            st.warning(f"⚠️ Nenhuma cláusula encontrada para '{search_term}'")
            clausulas = []
    
    # Renderizar cláusulas
    for idx, clausula in enumerate(clausulas):
        with st.container():
            st.markdown('<div class="clausula-card">', unsafe_allow_html=True)
            
            # Header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {clausula['titulo']}")
                st.markdown(f'<span class="tipo-badge">{clausula["tipo"]}</span>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="clausula-numero">Nº {clausula["numero"]}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Sugestão de explicação (editável)
            st.markdown("**💡 Sugestão de Explicação:**")
            
            # Usar um key único baseado no número da cláusula
            key = f"clausula_{clausula['numero']}_{idx}"
            
            nova_sugestao = st.text_area(
                "Edite a sugestão:",
                value=clausula['sugestao_explicacao'],
                height=100,
                key=key,
                label_visibility="collapsed"
            )
            
            # Detectar mudanças
            if nova_sugestao != clausula['sugestao_explicacao']:
                clausula['sugestao_explicacao'] = nova_sugestao
                st.session_state.edited_clauses.add(clausula['numero'])
                st.success("✏️ Cláusula modificada (lembre de salvar)")
            
            # Pontos de atenção
            if clausula.get('pontos_atencao') and len(clausula['pontos_atencao']) > 0:
                with st.expander("⚠️ Pontos de Atenção"):
                    for ponto in clausula['pontos_atencao']:
                        st.markdown(f"- {ponto}")
            
            # Preview do conteúdo
            if clausula.get('preview_conteudo') and len(clausula['preview_conteudo']) > 0:
                with st.expander("📄 Preview do Conteúdo Original"):
                    st.markdown(f'<div class="preview-content">{clausula["preview_conteudo"]}</div>', unsafe_allow_html=True)
                    st.caption(f"Tamanho total: {clausula.get('tamanho_conteudo', 0)} caracteres")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Rodapé com informações
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📊 Total de Cláusulas",
            st.session_state.current_data['total_clausulas']
        )
    
    with col2:
        st.metric(
            "✏️ Cláusulas Editadas",
            len(st.session_state.edited_clauses)
        )
    
    with col3:
        st.metric(
            "📝 Documento",
            st.session_state.selected_doc
        )

# Rodapé
st.markdown("---")
st.caption("📚 Documentos GOLD - Sistema de Revisão Jurídica Travessia | v1.0")
