# Jurídico Review AI

Sistema inteligente para revisão automatizada de minutas jurídicas de CRI, CRA e Debêntures.

## Descrição

Este projeto utiliza IA (Ollama local + modelos frontier) para revisar minutas jurídicas, identificando cláusulas importantes e sugerindo melhorias com base em catálogos de referência.

## Estrutura do Projeto

```
juridico-review-ai/
├── data/
│   ├── entrada/           # Minutas .docx ou .pdf para análise
│   ├── saida/            # Arquivos de saída (Excel/DOCX)
│   └── catalogos/        # Catálogos YAML de referência
├── src/
│   ├── main.py           # CLI principal
│   ├── parsing.py        # Leitura e segmentação de documentos
│   ├── ranker.py         # Fuzzy matching + embeddings + MMR
│   ├── reviewer.py       # Integração com Ollama/frontier models
│   ├── report.py         # Geração de relatórios
│   └── utils.py          # Funções auxiliares
└── tests/
    └── exemplos_minutas/ # Minutas de teste
```

## Pré-requisitos

- Python 3.8+
- Ollama instalado (para modelos locais)
- Conexão com internet (para modelos frontier, se necessário)

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd juridico-review-ai
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o Ollama (se usar modelos locais):
```bash
ollama pull qwen2:7b-instruct
```

## Uso

### Revisão de uma minuta

```bash
python src/main.py --minuta data/entrada/minuta_cri.docx --catalogo data/catalogos/catalogo_cri.yaml
```

### Opções disponíveis

```bash
python src/main.py --help
```

## Catálogos

Os catálogos YAML contêm cláusulas de referência para cada tipo de documento:

- `catalogo_cri.yaml` - Certificados de Recebíveis Imobiliários
- `catalogo_cra.yaml` - Certificados de Recebíveis do Agronegócio
- `catalogo_debenture.yaml` - Debêntures

## Saída

O sistema gera:

1. **Excel** (`revisao.xlsx`): Tabela com cláusulas encontradas, score de similaridade e sugestões
2. **DOCX** (`sugestoes.docx`): Documento formatado com análise detalhada

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

[Definir licença]

## Contato

[Seu contato]

## Quickstart (PT-BR)

Instruções rápidas para testar uma minuta localmente (Windows PowerShell).

- Onde colocar a minuta:
    - Coloque arquivos .docx ou .pdf em `data/entrada/`.

- Como ativar o ambiente virtual (Windows PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

- Instalar dependências:

```powershell
pip install -r requirements.txt
```

- Executar uma análise (Tier‑1 apenas, sem Tier‑2):

```powershell
.\venv\Scripts\python.exe src\main_v3.py --minuta "data\entrada\sua_minuta.docx" --catalogo data\catalogos\catalogo_cri_v3.yaml --skip-tier2 --verbose
```

- Testar Tier‑2 com o provider Gemini (requer chave de API):

1. Exporte a variável de ambiente `GEMINI_API_KEY` no PowerShell:

```powershell
$env:GEMINI_API_KEY = "sua_chave_aqui"
```

2. Execute com provider `gemini` e modelo (ex.: `text-bison-001`):

```powershell
.\venv\Scripts\python.exe src\main_v3.py --minuta "data\entrada\sua_minuta.docx" --catalogo data\catalogos\catalogo_cri_v3.yaml --tier2-provider gemini --tier2-model text-bison-001 --verbose
```

- Observações sobre arquivos de saída:
    - Os relatórios são gravados em `data/saida/` com um sufixo de timestamp para evitar conflitos (ex.: `revisao_completa_20251016_142030.xlsx`).
    - O caminho exato dos arquivos gerados é impresso no log e salvo no arquivo de auditoria (`data/saida/audit_*.json`).

- Dicas rápidas:
    - Para testar com baixo custo, use `--skip-tier2` ou gere Tier‑2 apenas para cláusulas marcadas como `PARCIAL`.
    - Se estiver no Windows e receber warnings de CRLF, isso é apenas uma normalização de fim de linha; não impede o funcionamento.

