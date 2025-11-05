"""
App Streamlit - Validador Documental CRI
Interface web para validação de documentos jurídicos
"""
import streamlit as st
import os
import sys
import json
from pathlib import Path
from io import StringIO

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Validador CRI - Travessia",
    page_icon="📄",
    layout="wide"
)

# Estilo customizado
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: 700;
    color: #1E3A8A;
    margin-bottom: 0.5rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #64748B;
    margin-bottom: 2rem;
}
.status-conforme {
    color: #059669;
    font-weight: 600;
}
.status-divergente {
    color: #DC2626;
    font-weight: 600;
}
.status-ausente {
    color: #6B7280;
    font-weight: 600;
}
.status-ambigua {
    color: #D97706;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📄 Validador Documental CRI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Sistema inteligente de validação de contratos com pipeline híbrido (Regras + IA)</p>', unsafe_allow_html=True)

# Sidebar - Configuração
with st.sidebar:
    st.header("⚙️ Configuração")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Obtenha em: https://makersuite.google.com/app/apikey"
    )

    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        st.success("✅ API Key configurada")
    else:
        st.warning("⚠️ Configure a API Key para usar IA")

    st.markdown("---")

    st.markdown("""
    **Links Úteis:**
    - [📖 Documentação](./README.md)
    - [🔑 Obter API Key](https://makersuite.google.com/app/apikey)
    - [💡 Guia de Uso](./GUIA_USO.md)
    """)

# Tabs principais
tab1, tab2, tab3 = st.tabs(["📄 Validar Documento", "📊 Sobre os Standards", "ℹ️ Ajuda"])

with tab1:
    # Upload do documento
    st.header("1️⃣ Upload do Documento")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Escolha um arquivo PDF ou DOCX",
            type=["pdf", "docx"],
            help="Arraste ou clique para fazer upload do contrato CRI"
        )

    with col2:
        if uploaded_file:
            st.info(f"📎 **Arquivo:** {uploaded_file.name}")
            st.info(f"📏 **Tamanho:** {uploaded_file.size / 1024:.1f} KB")

    # Escolha do standard
    st.header("2️⃣ Tipo de CRI")

    standard_choice = st.radio(
        "Selecione o tipo de CRI:",
        [
            "CRI com Destinação Específica (49 cláusulas - v2)",
            "CRI sem Destinação (44 cláusulas - v2)",
            "CRI com Destinação - Básico (8 cláusulas - v1)",
            "CRI sem Destinação - Básico (8 cláusulas - v1)"
        ],
        help="V2 = completo (baseado nos catálogos GOLD), V1 = básico (manual)"
    )

    # Mapeamento de standards
    standard_map = {
        "CRI com Destinação Específica (49 cláusulas - v2)": "standards/CRI/cri_com_destinacao.v2.json",
        "CRI sem Destinação (44 cláusulas - v2)": "standards/CRI/cri_sem_destinacao.v2.json",
        "CRI com Destinação - Básico (8 cláusulas - v1)": "standards/CRI/cri_com_destinacao.v1.json",
        "CRI sem Destinação - Básico (8 cláusulas - v1)": "standards/CRI/cri_sem_destinacao.v1.json"
    }

    standard_path = standard_map[standard_choice]

    # Info sobre o standard selecionado
    try:
        with open(standard_path, 'r', encoding='utf-8') as f:
            std_data = json.load(f)
            st.info(f"📋 **Standard selecionado:** {std_data.get('version', 'N/A')} | "
                   f"{len(std_data.get('clauses', []))} cláusulas")
    except:
        pass

    # Configurações avançadas
    st.header("3️⃣ Configurações")

    col1, col2 = st.columns(2)

    with col1:
        use_llm = st.checkbox(
            "🤖 Usar IA (Gemini) para casos ambíguos",
            value=True,
            help="Se desabilitado, usa apenas regras determinísticas (mais rápido, sem custo)"
        )

    with col2:
        k = st.slider(
            "Blocos para retrieval (k)",
            min_value=3,
            max_value=10,
            value=5,
            help="Número de blocos candidatos a recuperar por cláusula"
        )

    # Botão de validação
    st.markdown("---")

    if st.button("🚀 VALIDAR DOCUMENTO", type="primary", use_container_width=True):
        if not uploaded_file:
            st.error("❌ Por favor, faça upload de um documento!")
        elif use_llm and not api_key:
            st.warning("⚠️ Configure a API Key do Gemini na barra lateral para usar IA!")
            st.info("💡 **Dica:** Você pode prosseguir sem IA desmarcando a opção acima")
        else:
            # Salva arquivo temporário
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / uploaded_file.name
            temp_path.write_bytes(uploaded_file.read())

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                status_text.text("📖 Carregando standard...")
                progress_bar.progress(10)

                status_text.text("🔍 Extraindo blocos do documento...")
                progress_bar.progress(30)

                status_text.text("🧠 Construindo índice FAISS...")
                progress_bar.progress(50)

                status_text.text("⚖️ Aplicando regras determinísticas...")
                progress_bar.progress(70)

                if use_llm:
                    status_text.text("🤖 Consultando Gemini AI...")
                progress_bar.progress(85)

                # Roda validação
                from scripts.validate import validate

                # Captura output
                old_stdout = sys.stdout
                sys.stdout = StringIO()

                validate(
                    pdf_path=str(temp_path),
                    standard_path=standard_path,
                    k=k,
                    use_llm=use_llm,
                    out_html=str(temp_dir / "report.html")
                )

                output = sys.stdout.getvalue()
                sys.stdout = old_stdout

                progress_bar.progress(100)
                status_text.empty()

                # Parse JSON output
                try:
                    # Pega última linha JSON válida
                    json_lines = [line for line in output.split('\n') if line.strip().startswith('{')]
                    if json_lines:
                        results = json.loads(json_lines[-1])
                    else:
                        results = json.loads(output)

                    # Mostra resultados
                    st.success("✅ Validação concluída com sucesso!")

                    # Resumo
                    st.header("📊 Resumo")

                    clause_results = results.get("results", [])
                    total = len(clause_results)
                    conforme = sum(1 for r in clause_results if r.get("status") == "conforme")
                    divergente = sum(1 for r in clause_results if r.get("status") == "divergente")
                    ausente = sum(1 for r in clause_results if r.get("status") == "ausente")
                    ambigua = sum(1 for r in clause_results if r.get("status") == "ambigua")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("✅ Conformes", conforme, f"{conforme/total*100:.0f}%")
                    with col2:
                        st.metric("❌ Divergentes", divergente, f"{divergente/total*100:.0f}%")
                    with col3:
                        st.metric("⚪ Ausentes", ausente, f"{ausente/total*100:.0f}%")
                    with col4:
                        st.metric("❓ Ambíguas", ambigua, f"{ambigua/total*100:.0f}%")

                    # Detalhes por cláusula
                    st.header("📋 Detalhes por Cláusula")

                    for result in clause_results:
                        status = result.get("status", "")
                        clause_id = result.get("clause_id", "")
                        evidence = result.get("evidence", {})
                        notes = result.get("notes", "")

                        # Cor baseada no status
                        status_class = f"status-{status}"

                        with st.expander(f"{clause_id} - Status: {status.upper()}", expanded=(status != "conforme")):
                            col1, col2 = st.columns([1, 2])

                            with col1:
                                st.markdown(f"**Status:** <span class='{status_class}'>{status.upper()}</span>", unsafe_allow_html=True)
                                if evidence:
                                    if evidence.get("page"):
                                        st.markdown(f"**Página:** {evidence['page']}")
                                    elif evidence.get("section_path"):
                                        st.markdown(f"**Seção:** {evidence['section_path']}")

                            with col2:
                                if evidence and evidence.get("text"):
                                    st.text_area("Evidência", evidence["text"][:500], height=100, disabled=True)
                                if notes:
                                    st.info(f"💡 {notes}")

                    # Download do relatório HTML
                    st.header("📥 Download")

                    with open(temp_dir / "report.html", "r", encoding="utf-8") as f:
                        html_content = f.read()

                    col1, col2 = st.columns(2)

                    with col1:
                        st.download_button(
                            "📄 Baixar Relatório HTML",
                            html_content,
                            file_name=f"relatorio_{uploaded_file.name}.html",
                            mime="text/html",
                            use_container_width=True
                        )

                    with col2:
                        st.download_button(
                            "📊 Baixar JSON",
                            json.dumps(results, ensure_ascii=False, indent=2),
                            file_name=f"resultado_{uploaded_file.name}.json",
                            mime="application/json",
                            use_container_width=True
                        )

                except json.JSONDecodeError:
                    st.warning("⚠️ Não foi possível parsear o JSON. Mostrando output bruto:")
                    st.code(output, language="json")

            except Exception as e:
                st.error(f"❌ Erro na validação: {str(e)}")
                with st.expander("🔍 Detalhes do erro"):
                    st.exception(e)
            finally:
                progress_bar.empty()

with tab2:
    st.header("📊 Sobre os Standards")

    st.markdown("""
    Os **standards** são arquivos JSON que definem **como um documento deve ser**.
    Eles contêm as cláusulas obrigatórias e as regras de validação.

    ### Versões Disponíveis

    #### V2 - Completo (Recomendado) ⭐
    - Baseado nos catálogos GOLD
    - **CRI com Destinação:** 49 cláusulas (11 críticas, 14 obrigatórias)
    - **CRI sem Destinação:** 44 cláusulas (3 críticas, 5 obrigatórias)
    - Parâmetros automáticos por categoria
    - Regras inteligentes must_include/must_not_include

    #### V1 - Básico
    - Criado manualmente
    - 8 cláusulas por tipo
    - Bom para testes iniciais
    """)

    # Mostra estatísticas dos standards
    st.subheader("Estatísticas")

    try:
        # V2 com destinação
        with open("standards/CRI/cri_com_destinacao.v2.json", "r", encoding="utf-8") as f:
            std_v2_dest = json.load(f)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("V2 - Com Destinação", f"{len(std_v2_dest['clauses'])} cláusulas")
            criticas = sum(1 for c in std_v2_dest['clauses'] if c.get('importance') == 'critica')
            st.caption(f"💥 {criticas} críticas")

        # V2 sem destinação
        with open("standards/CRI/cri_sem_destinacao.v2.json", "r", encoding="utf-8") as f:
            std_v2_sem = json.load(f)

        with col2:
            st.metric("V2 - Sem Destinação", f"{len(std_v2_sem['clauses'])} cláusulas")
            criticas = sum(1 for c in std_v2_sem['clauses'] if c.get('importance') == 'critica')
            st.caption(f"💥 {criticas} críticas")

    except Exception as e:
        st.warning(f"Não foi possível carregar estatísticas: {e}")

with tab3:
    st.header("ℹ️ Ajuda")

    st.markdown("""
    ### Como Funciona?

    1. **Upload:** Você faz upload do PDF ou DOCX do contrato CRI
    2. **Standard:** Escolhe qual standard usar (com/sem destinação)
    3. **Validação:** O sistema:
       - Extrai blocos do documento
       - Busca cláusulas usando embeddings + FAISS
       - Aplica regras determinísticas
       - Se ambíguo, consulta Gemini AI
    4. **Relatório:** Gera relatório HTML + JSON estruturado

    ### Status Possíveis

    - ✅ **CONFORME:** Cláusula presente e atende todos os requisitos
    - ❌ **DIVERGENTE:** Cláusula presente mas com problemas
    - ⚪ **AUSENTE:** Cláusula não encontrada
    - ❓ **AMBÍGUA:** Inconclusiva (requer análise manual)

    ### Dicas

    💡 **Para testes rápidos:** Desabilite a IA e use apenas regras determinísticas

    💡 **Para máxima precisão:** Habilite a IA com API Key do Gemini

    💡 **Custo:** Gemini Flash custa ~$0.005 por documento (49 cláusulas)

    ### Links Úteis

    - 📖 [README.md](./README.md) - Documentação completa
    - 💡 [GUIA_USO.md](./GUIA_USO.md) - Guia de uso passo a passo
    - 🚀 [DEPLOY.md](./DEPLOY.md) - Como fazer deploy
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; padding: 1rem;">
<strong>Travessia Securitizadora</strong> | Validador Documental CRI v2.0<br>
Pipeline Híbrido (Regras + IA) com Saída 100% Estruturada
</div>
""", unsafe_allow_html=True)
