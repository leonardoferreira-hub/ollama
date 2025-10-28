"""
Redirecionamento para a página principal de revisão
"""
import streamlit as st

st.set_page_config(
    page_title="Revisor de Documentos - Travessia",
    page_icon="📋",
    layout="wide"
)

st.info("📋 Esta é a página principal de revisão. Volte para a página inicial (Home) para fazer o upload e análise de documentos.")

st.markdown("""
### Como usar o sistema:

1. **Home (app.py)** - Página principal onde você:
   - Faz upload do documento para revisar
   - Seleciona o catálogo de referência
   - Inicia a análise
   - Visualiza o relatório

2. **📚 Gerenciar Cláusulas GOLD** - Página onde você:
   - Visualiza todas as cláusulas dos documentos padrão
   - Edita as sugestões de explicação
   - Personaliza as definições para a IA
   - Exporta os dados editados
""")

st.markdown("---")
st.markdown("👈 Use o menu lateral para navegar entre as páginas")
