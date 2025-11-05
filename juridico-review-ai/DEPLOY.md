# GUIA DE DEPLOY - Validador Documental

Este guia mostra como fazer deploy e testar o validador documental.

## Índice
1. [Teste Local (mais rápido)](#teste-local)
2. [Deploy no Streamlit Cloud (gratuito)](#streamlit-cloud)
3. [Deploy em Servidor próprio](#servidor-proprio)
4. [Troubleshooting](#troubleshooting)

---

## 1. TESTE LOCAL (Mais Rápido) ⚡ {#teste-local}

### Passo 1: Verificar Instalação

```bash
cd juridico-review-ai

# Windows PowerShell
python --version  # Deve ser Python 3.11+
pip list | findstr "pymupdf pydantic google-generativeai"
```

Se faltar algo, instale:

```bash
pip install -r requirements.txt
```

---

### Passo 2: Configurar API do Gemini

**Obter chave:**
1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave

**Configurar (Windows PowerShell):**
```powershell
$env:GEMINI_API_KEY = "SUA_CHAVE_AQUI"

# Verificar
echo $env:GEMINI_API_KEY
```

**IMPORTANTE:** Essa variável só dura enquanto o terminal estiver aberto!

Para tornar permanente (opcional):
```powershell
# Windows: Adicionar às variáveis de ambiente do sistema
# Painel de Controle > Sistema > Configurações Avançadas > Variáveis de Ambiente
```

---

### Passo 3: Testar com Documento de Exemplo

#### 3.1. Criar Pasta para Testes

```powershell
mkdir documentos_teste
```

#### 3.2. Copiar um Documento

Copie manualmente um PDF ou DOCX de CRI para a pasta `documentos_teste/`

#### 3.3. Rodar Validação

```powershell
# Com PDF
python scripts/validate.py `
  --pdf_path "documentos_teste/seu_contrato.pdf" `
  --standard_path "standards/CRI/cri_com_destinacao.v2.json" `
  --out_html "relatorio_teste.html"

# Com DOCX
python scripts/validate.py `
  --pdf_path "documentos_teste/seu_contrato.docx" `
  --standard_path "standards/CRI/cri_com_destinacao.v2.json" `
  --out_html "relatorio_teste.html"
```

#### 3.4. Ver Resultado

```powershell
# Abrir relatório no navegador
start relatorio_teste.html

# Ou apenas ver o JSON no terminal (já aparece automaticamente)
```

---

### Passo 4: Testar Sem IA (mais rápido, sem custo)

Para testes rápidos sem usar a API do Gemini:

```powershell
python scripts/validate.py `
  --pdf_path "documentos_teste/seu_contrato.pdf" `
  --standard_path "standards/CRI/cri_com_destinacao.v2.json" `
  --use_llm False `
  --out_html "relatorio_rapido.html"
```

**Quando usar `--use_llm False`:**
- ✅ Testes iniciais rápidos
- ✅ Documentos muito claros
- ✅ Economizar custo da API
- ✅ Trabalhar offline

---

## 2. DEPLOY NO STREAMLIT CLOUD (Gratuito) 🌐 {#streamlit-cloud}

### O que é?
- Plataforma gratuita de hosting para apps Python
- Deploy automático via GitHub
- HTTPS gratuito
- Sem necessidade de servidor

### Passo 1: Criar Interface Streamlit

Vou criar um app web simples:

```python
# app_streamlit.py
import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="Validador CRI - Travessia",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Validador Documental CRI")
st.markdown("Sistema de validação de contratos CRI com IA")

# Configuração da API
with st.sidebar:
    st.header("⚙️ Configuração")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    st.markdown("---")
    st.markdown("[Obter API Key](https://makersuite.google.com/app/apikey)")

# Upload do documento
st.header("1. Upload do Documento")
uploaded_file = st.file_uploader(
    "Escolha um arquivo PDF ou DOCX",
    type=["pdf", "docx"]
)

# Escolha do standard
st.header("2. Tipo de CRI")
standard_type = st.radio(
    "Selecione o tipo:",
    ["CRI com Destinação (49 cláusulas)", "CRI sem Destinação (44 cláusulas)"]
)

# Configurações avançadas
with st.expander("⚙️ Configurações Avançadas"):
    use_llm = st.checkbox("Usar IA (Gemini) para casos ambíguos", value=True)
    k = st.slider("Número de blocos para retrieval", 3, 10, 5)

# Botão de validação
if st.button("🚀 Validar Documento", type="primary"):
    if not uploaded_file:
        st.error("Por favor, faça upload de um documento!")
    elif use_llm and not api_key:
        st.error("Configure a API Key do Gemini na barra lateral!")
    else:
        with st.spinner("Validando documento..."):
            # Salva arquivo temporário
            temp_path = Path("temp") / uploaded_file.name
            temp_path.parent.mkdir(exist_ok=True)
            temp_path.write_bytes(uploaded_file.read())

            # Escolhe o standard
            if "com Destinação" in standard_type:
                standard_path = "standards/CRI/cri_com_destinacao.v2.json"
            else:
                standard_path = "standards/CRI/cri_sem_destinacao.v2.json"

            # Roda validação
            try:
                from scripts.validate import validate

                # Captura output
                import sys
                from io import StringIO
                old_stdout = sys.stdout
                sys.stdout = StringIO()

                validate(
                    pdf_path=str(temp_path),
                    standard_path=standard_path,
                    k=k,
                    use_llm=use_llm,
                    out_html="temp_report.html"
                )

                output = sys.stdout.getvalue()
                sys.stdout = old_stdout

                # Mostra resultados
                st.success("✅ Validação concluída!")

                # Mostra JSON
                st.subheader("📊 Resultados")
                st.code(output, language="json")

                # Download do relatório
                with open("temp_report.html", "r", encoding="utf-8") as f:
                    st.download_button(
                        "📥 Baixar Relatório HTML",
                        f.read(),
                        file_name="relatorio_validacao.html",
                        mime="text/html"
                    )

            except Exception as e:
                st.error(f"Erro na validação: {e}")
                st.exception(e)

# Footer
st.markdown("---")
st.markdown("**Travessia Securitizadora** | Validador Documental CRI v2.0")
```

### Passo 2: Fazer Push pro GitHub

```bash
git add app_streamlit.py
git commit -m "feat: adiciona interface Streamlit"
git push origin main
```

### Passo 3: Deploy no Streamlit Cloud

1. Acesse: https://streamlit.io/cloud
2. Clique em "New app"
3. Conecte seu GitHub
4. Selecione o repositório: `ollama`
5. Branch: `main`
6. Main file path: `juridico-review-ai/app_streamlit.py`
7. Clique em "Deploy"

**Pronto!** Seu app estará online em: `https://seu-usuario-ollama.streamlit.app`

---

## 3. DEPLOY EM SERVIDOR PRÓPRIO {#servidor-proprio}

### Opção A: Docker (Recomendado)

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY juridico-review-ai/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY juridico-review-ai/ .

# Porta
EXPOSE 8501

# Comando
CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Build e Run

```bash
# Build
docker build -t validador-cri .

# Run
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=sua-chave \
  validador-cri

# Acessar: http://localhost:8501
```

---

### Opção B: Servidor Linux (Ubuntu/Debian)

```bash
# 1. Conectar no servidor via SSH
ssh usuario@seu-servidor.com

# 2. Instalar Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# 3. Clonar repositório
git clone https://github.com/seu-usuario/ollama.git
cd ollama/juridico-review-ai

# 4. Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# 5. Instalar dependências
pip install -r requirements.txt

# 6. Configurar API Key
export GEMINI_API_KEY="sua-chave"
echo 'export GEMINI_API_KEY="sua-chave"' >> ~/.bashrc

# 7. Rodar Streamlit
streamlit run app_streamlit.py --server.port 8501

# 8. Configurar Nginx (opcional, para HTTPS)
sudo apt install nginx
# ... configurar reverse proxy
```

---

### Opção C: AWS Lambda (Serverless)

Para processamento sob demanda sem servidor 24/7:

```python
# lambda_handler.py
import json
import boto3
from scripts.validate import validate

def lambda_handler(event, context):
    # Pega documento do S3
    s3 = boto3.client('s3')
    bucket = event['bucket']
    key = event['key']

    # Baixa documento
    local_path = f"/tmp/{key}"
    s3.download_file(bucket, key, local_path)

    # Valida
    validate(
        pdf_path=local_path,
        standard_path="standards/CRI/cri_com_destinacao.v2.json",
        out_html="/tmp/report.html"
    )

    # Upload do relatório
    s3.upload_file("/tmp/report.html", bucket, f"reports/{key}.html")

    return {
        'statusCode': 200,
        'body': json.dumps('Validação concluída!')
    }
```

---

## 4. TROUBLESHOOTING {#troubleshooting}

### Erro: "GEMINI_API_KEY não definida"

**Solução:**
```powershell
$env:GEMINI_API_KEY = "sua-chave"
```

---

### Erro: "ModuleNotFoundError"

**Solução:**
```bash
pip install -r requirements.txt
```

---

### Streamlit não abre no navegador

**Solução:**
```bash
# Especificar porta manualmente
streamlit run app_streamlit.py --server.port 8502

# Depois acessar: http://localhost:8502
```

---

### Validação muito lenta

**Causas:**
1. Documento muito grande
2. Muitos blocos para retrieval (k alto)
3. Uso de LLM em todas as cláusulas

**Soluções:**
```bash
# 1. Reduzir k
--k 3  # em vez de 5

# 2. Desabilitar LLM para testes
--use_llm False

# 3. Usar apenas cláusulas críticas
# (editar o standard e remover cláusulas não obrigatórias)
```

---

### Custo da API Gemini muito alto

**Dicas:**
1. Use `--use_llm False` para testes
2. Cache de resultados (implementar)
3. Use tier gratuito do Gemini (15 RPM grátis)
4. Processe em batch offline

**Estimativa de custo:**
- Gemini Flash: ~$0.0001 por requisição
- Documento com 49 cláusulas = ~$0.005 (menos de 1 centavo)
- 1000 documentos = ~$5

---

## 5. PRÓXIMOS PASSOS

Depois de testar localmente:

1. ✅ **Deploy no Streamlit Cloud** (mais fácil, gratuito)
2. ✅ **Adicionar autenticação** (login/senha)
3. ✅ **Banco de dados** para histórico
4. ✅ **Fila de processamento** (Celery/Redis)
5. ✅ **Cache de embeddings** (performance)
6. ✅ **Métricas e logs** (monitoramento)

---

## 6. LINKS ÚTEIS

- 📚 Docs Streamlit: https://docs.streamlit.io
- 🔑 Gemini API: https://makersuite.google.com
- 🐳 Docker Hub: https://hub.docker.com
- ☁️ Streamlit Cloud: https://streamlit.io/cloud

---

**Última atualização:** Janeiro 2025
