# Fix do Deploy - Streamlit Cloud

## Problema Identificado

O erro "source code string cannot contain null bytes" ocorria porque:

1. **Conflito de estrutura**: O código tentava importar de `src/` (que não existe) ao invés de `backend/` (que existe)
2. **App errado**: O `app.py` e `scripts/validate.py` referenciavam módulos inexistentes
3. **Sistema duplicado**: Havia tentativa de criar novo sistema com `src/` mas o sistema funcional está em `backend/`

## Solução Aplicada

### 1. Arquivo Principal Corrigido

- **ANTES**: `app.py` importava de `src/` (não existe)
- **DEPOIS**: `app.py` agora é o `app_old.py` renomeado (importa de `backend/`)

```bash
# O que foi feito:
mv app.py app_broken.py          # Salva versão quebrada
mv app_old.py app.py              # Usa versão funcional com RAG
```

### 2. TESTE_RAPIDO.bat Atualizado

```batch
# ANTES: streamlit run app_streamlit.py (comando falhava)
# DEPOIS: python -m streamlit run app.py (comando correto)
```

### 3. Estrutura Correta

```
juridico-review-ai/
├── app.py                    ← FUNCIONAL (usa backend/)
├── backend/                  ← Sistema REAL
│   ├── parsing.py           ← Parse DOCX/PDF
│   ├── vector_db.py         ← RAG com ChromaDB
│   ├── utils/
│   │   └── catalog.py       ← Carrega catálogos YAML
│   └── ...
├── data/
│   ├── catalogos/           ← catálogo_cri_*.yaml
│   └── vector_db/           ← Base ChromaDB persistente
├── requirements.txt         ← Dependências corretas
└── TESTE_RAPIDO.bat         ← Launcher Windows

# ❌ NÃO EXISTE (causava erro):
# src/                        ← Tentativa de novo sistema, incompleta
```

## Sistema Funcional

O [app.py](app.py) atual possui:

- ✅ Sistema RAG completo com ChromaDB
- ✅ Parsing robusto de DOCX e PDF (tabelas, cláusulas, placeholders)
- ✅ Integração com Gemini 2.0 Flash (rate limiting 10 RPM)
- ✅ Catálogos YAML (catalogo_cri_destinacao.yaml, catalogo_cri_sem_destinacao.yaml)
- ✅ Base de conhecimento persistente (aprende com cada documento)
- ✅ Documentos GOLD (prioridade máxima, prefixo GOLD_)
- ✅ Download Excel com sugestões
- ✅ Sistema de feedback para aprendizado contínuo

## Como Testar Localmente

### Windows:
```batch
# Opção 1: Duplo clique em TESTE_RAPIDO.bat
TESTE_RAPIDO.bat

# Opção 2: Command line
cd juridico-review-ai
python -m streamlit run app.py
```

### Linux/Mac:
```bash
cd juridico-review-ai
python3 -m streamlit run app.py
```

Acesse: http://localhost:8501

## Deploy no Streamlit Cloud

### 1. Requisitos

Certifique-se que estes arquivos estão commitados:

- `app.py` (versão correta, usa backend/)
- `requirements.txt` (com todas dependências)
- `backend/` (diretório completo)
- `data/catalogos/` (catálogos YAML)

### 2. Configuração no Streamlit Cloud

1. Conecte o repositório GitHub
2. **Main file**: `app.py`
3. **Python version**: 3.11
4. **Secrets** (opcional): Configure `GEMINI_API_KEY` se quiser fixar

### 3. Verificação

No sidebar do app, você verá:

```
CWD: /mount/src/juridico-review-ai
APP_DIR: /mount/src/juridico-review-ai
sys.path[0:3]: ['/mount/src/juridico-review-ai', ...]
backend spec: /mount/src/juridico-review-ai/backend/__init__.py
```

✅ Se backend spec mostrar caminho → **DEPLOY OK**
❌ Se backend spec mostrar None → Erro de importação

## Dependências (requirements.txt)

```
# Core
streamlit>=1.37
PyYAML==6.0.1
google-generativeai>=0.7.2
pydantic>=2.6

# Vector store & embeddings (RAG)
chromadb>=0.5.4
sentence-transformers>=3.1

# Document processing
python-docx>=0.8.11
PyPDF2>=3.0.0
pdfplumber>=0.9.0

# Utils
requests>=2.28.0
jinja2>=3.1.0
rapidfuzz>=3.0.0
openpyxl>=3.1.0
pandas>=2.0.0
```

## Troubleshooting

### Erro: "backend spec: None"
**Causa**: Streamlit Cloud não encontra o diretório backend/
**Solução**: Verifique se `backend/__init__.py` existe e está commitado no git

### Erro: "null bytes"
**Causa**: Tentativa de importar de `src/` que não existe
**Solução**: Use `app.py` atual (não `app_broken.py`)

### Erro: "streamlit não é reconhecido"
**Causa**: Streamlit não instalado ou não no PATH
**Solução**: Use `python -m streamlit run app.py` ao invés de `streamlit run`

### Erro: "google-generativeai not found"
**Causa**: Biblioteca não instalada
**Solução**: O app tem fallback, funciona sem Gemini (sem IA, apenas RAG)

## Arquivos Importantes

| Arquivo | Status | Descrição |
|---------|--------|-----------|
| `app.py` | ✅ USAR | App funcional com RAG (era app_old.py) |
| `app_broken.py` | ❌ IGNORAR | Tentativa com src/ (não funciona) |
| `backend/` | ✅ ESSENCIAL | Sistema completo de parsing + RAG |
| `data/catalogos/` | ✅ ESSENCIAL | Catálogos YAML (CRI com/sem destinação) |
| `requirements.txt` | ✅ ESSENCIAL | Dependências corretas |
| `TESTE_RAPIDO.bat` | ✅ USAR | Launcher Windows atualizado |

## Próximos Passos

1. ✅ Testar localmente com `TESTE_RAPIDO.bat`
2. ✅ Commitar as mudanças:
   ```bash
   git add app.py app_broken.py TESTE_RAPIDO.bat FIX_DEPLOY.md
   git commit -m "fix: corrige deploy substituindo app quebrado por versão funcional com RAG"
   git push
   ```
3. ✅ Fazer deploy no Streamlit Cloud apontando para `app.py`
4. ✅ Testar upload de documento DOCX/PDF
5. ✅ Verificar se base vetorial persiste entre sessões

## Funcionalidades Principais

### Sistema RAG (Retrieval-Augmented Generation)

- **ChromaDB**: Banco vetorial persistente em `data/vector_db/`
- **Sentence Transformers**: Embeddings para busca semântica
- **Documentos GOLD**: Prefixo `GOLD_` garante prioridade máxima
- **Filtro de qualidade**: Apenas cláusulas PRESENTE (conf ≥70%) são salvas (exceto GOLD)
- **Aprendizado contínuo**: Cada documento analisado enriquece a base

### Parsing Robusto

- **DOCX**: Detecta CLÁUSULA, CAPÍTULO, ANEXO, SEÇÃO, numeração, tabelas
- **PDF**: Extrai texto e tabelas com pdfplumber
- **Placeholders**: Remove {=}, [=] automaticamente
- **Fallback inteligente**: Se encontra poucas cláusulas, divide em chunks

### Integração Gemini

- **Modelo**: gemini-2.0-flash-exp
- **Rate limiting**: 10 RPM (6s entre requests)
- **Contexto RAG**: Busca 2 exemplos similares da base
- **Fallback**: Funciona sem API key (apenas classificação básica)

---

**Data da correção**: 2025-11-05
**Versão do sistema**: 1.0.0 (RAG + Gold Standard)
