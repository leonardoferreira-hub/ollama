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
