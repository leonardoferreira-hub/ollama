# Validador Documental Jurídico

Pipeline híbrido (regras determinísticas + IA) para validação de documentos jurídicos de CRI (Certificados de Recebíveis Imobiliários) com saída 100% estruturada em JSON.

**Formatos suportados: PDF (.pdf) e DOCX (.docx)**

## Visão Geral

Este sistema valida documentos jurídicos comparando-os com standards versionados (política como código), utilizando:

1. **Parsing determinístico** de PDF (PyMuPDF com página + bbox) e DOCX (python-docx com seção + parágrafo + tabela)
2. **Retrieval por blocos** usando embeddings + FAISS (top-k)
3. **Regras determinísticas** must_include/must_not_include (execução antes do LLM)
4. **Gemini 2.5 Flash** com structured output para casos ambíguos
5. **Relatório HTML** com status por cláusula e evidências

### Arquitetura

```
PDF/DOCX → Parser (PyMuPDF/python-docx) → Blocos → FAISS Index
                                                        ↓
Standards ────────────────────────────────→ Retrieval (top-k)
                                                        ↓
                                                  Regras Determinísticas
                                                        ↓
                                                ┌───────┴────────┐
                                                │                │
                                           Conforme         Ambíguo/Ausente
                                                │                │
                                                │           Gemini LLM
                                                │                │
                                                └───────┬────────┘
                                                        ↓
                                                Relatório HTML + JSON
```

## Instalação

### Pré-requisitos

- Python 3.11+
- Conta Google Cloud com API Key do Gemini

### Passos

```bash
cd juridico-review-ai
pip install -r requirements.txt
```

### Configurar API Key do Gemini

```bash
# Linux/Mac
export GEMINI_API_KEY="sua-api-key-aqui"

# Windows PowerShell
$env:GEMINI_API_KEY = "sua-api-key-aqui"
```

Opcionalmente, defina o modelo (padrão: `gemini-2.0-flash-exp`):

```bash
export GEMINI_MODEL_ID="gemini-2.0-flash-exp"
```

## Uso

### Validação Básica (PDF ou DOCX)

```bash
# Com PDF
python scripts/validate.py --pdf_path caminho/para/contrato.pdf --standard_path standards/CRI/cri_com_destinacao.v1.json --k 5 --use_llm True --out_html report.html

# Com DOCX
python scripts/validate.py --pdf_path caminho/para/contrato.docx --standard_path standards/CRI/cri_com_destinacao.v1.json --k 5 --use_llm True --out_html report.html
```

### Parâmetros

- `pdf_path`: Caminho do documento a validar (.pdf ou .docx)
- `standard_path`: Caminho do standard JSON (política como código)
- `k`: Número de blocos candidatos a recuperar (default: 5)
- `use_llm`: Usar LLM para casos ambíguos (default: True)
- `out_html`: Caminho do relatório HTML de saída (default: report.html)

### Exemplo CRI com Destinação (PDF)

```bash
python scripts/validate.py --pdf_path docs/exemplo_cri_destinacao.pdf --standard_path standards/CRI/cri_com_destinacao.v1.json
```

### Exemplo CRI sem Destinação (DOCX)

```bash
python scripts/validate.py --pdf_path docs/exemplo_cri_sem_destinacao.docx --standard_path standards/CRI/cri_sem_destinacao.v1.json
```

### Conversão de .doc para .docx

Para arquivos .doc antigos, converta para .docx usando LibreOffice:

```bash
libreoffice --headless --convert-to docx arquivo.doc
```

## Standards (Política como Código)

Os standards definem as cláusulas obrigatórias e suas regras de validação.

### Estrutura do Standard

```json
{
  "version": "CRI-com-destinacao.v1",
  "jurisdiction": "BR",
  "product": "CRI",
  "clauses": [
    {
      "id": "C-001",
      "title": "Objeto da Operação",
      "required": true,
      "must_include": ["certificados de recebíveis imobiliários", "destinação específica"],
      "must_not_include": [],
      "parameters": [
        {"name":"destinacao","type":"string"}
      ]
    }
  ]
}
```

### Standards Disponíveis

- `standards/CRI/cri_com_destinacao.v1.json`: CRI com destinação específica
- `standards/CRI/cri_sem_destinacao.v1.json`: CRI sem destinação

## Estrutura do Projeto

```
juridico-review-ai/
├── standards/              # Standards versionados (política como código)
│   └── CRI/
│       ├── cri_com_destinacao.v1.json
│       └── cri_sem_destinacao.v1.json
├── src/
│   ├── parsers/           # Parsers de PDF (PyMuPDF) e DOCX (python-docx)
│   ├── retrieval/         # Embeddings + FAISS
│   ├── rules/             # Motor de regras determinísticas
│   ├── agents/            # Validador Gemini
│   ├── reports/           # Gerador de relatórios HTML
│   ├── utils/             # Utilidades
│   └── schemas.py         # Schemas Pydantic
├── eval/                  # Testes e avaliação
├── scripts/
│   └── validate.py       # CLI principal
└── requirements.txt
```

## Testes

### Executar Todos os Testes

```bash
python -m pytest -v eval/test_pipeline.py
```

### Executar Diretamente

```bash
cd juridico-review-ai
python eval/test_pipeline.py
```

## CI/CD

O projeto inclui GitHub Actions configurado em `.github/workflows/ci.yml`.

## Saída JSON

O sistema gera JSON estruturado com evidências específicas por formato:

### Exemplo PDF

```json
{
  "pdf_sha256": "hash-do-documento",
  "standard_version": "CRI-com-destinacao.v1",
  "results": [
    {
      "clause_id": "C-001",
      "status": "conforme",
      "evidence": {
        "page": 5,
        "text": "trecho relevante...",
        "bbox": [100.5, 200.3, 400.2, 250.8]
      },
      "parameters": {},
      "notes": "Atendido por regra determinística"
    }
  ]
}
```

### Exemplo DOCX

```json
{
  "pdf_sha256": "hash-do-documento",
  "standard_version": "CRI-com-destinacao.v1",
  "results": [
    {
      "clause_id": "C-001",
      "status": "conforme",
      "evidence": {
        "section_path": "1 > 1.2 > Obrigações",
        "para_idx": 3,
        "text": "trecho relevante..."
      },
      "parameters": {},
      "notes": "Atendido por regra determinística"
    }
  ]
}
```

### Status Possíveis

- `conforme`: Cláusula presente e atende todos os requisitos
- `divergente`: Cláusula presente mas com problemas
- `ausente`: Cláusula não encontrada
- `ambigua`: Inconclusiva (requer análise adicional)

## Relatório HTML

Gerado automaticamente com tabela de cláusulas, status colorido, evidências e hash SHA256.

## Licença

MIT

