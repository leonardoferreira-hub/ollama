# Jurídico Review AI - MVP v2.0

Sistema de revisão automatizada de minutas jurídicas com arquitetura em camadas (Tier-1 local + Tier-2 frontier).

## 🎯 Objetivo

Automatizar a revisão de primeiras rodadas de minutas de CRI, CRA e Debêntures, verificando cláusulas padrão e gerando sugestões de melhoria.

## 🏗️ Arquitetura do MVP

```
┌─────────────────────────────────────────────────────────────┐
│  1. PARSING + SEGMENTAÇÃO (local)                           │
│     ↓ Lê DOCX/PDF e extrai cláusulas numeradas             │
├─────────────────────────────────────────────────────────────┤
│  2. RANKEADOR HÍBRIDO (local)                               │
│     ↓ BM25 + Embeddings + Regex + MMR                       │
├─────────────────────────────────────────────────────────────┤
│  3. CLASSIFICAÇÃO TIER-1 (local - qwen2:7b)                 │
│     ↓ PRESENTE | PARCIAL | AUSENTE + evidências            │
├─────────────────────────────────────────────────────────────┤
│  4. ROTEAMENTO INTELIGENTE                                  │
│     ↓ PRESENTE alta confiança → OK                          │
│     ↓ PARCIAL/AUSENTE → Tier-2                              │
├─────────────────────────────────────────────────────────────┤
│  5. GERAÇÃO TIER-2 (frontier - opcional)                    │
│     ↓ Gera sugestões de cláusulas (JSON)                    │
├─────────────────────────────────────────────────────────────┤
│  6. RELATÓRIOS                                               │
│     ↓ Excel (revisao_completa.xlsx)                         │
│     ↓ DOCX (sugestoes_detalhadas.docx)                      │
├─────────────────────────────────────────────────────────────┤
│  7. AUDITORIA                                                │
│     ↓ Hash do PDF, versão catálogo, modelos, prompts       │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Instalação

### Pré-requisitos

1. **Python 3.8+**
2. **Ollama instalado** com modelo qwen2:7b-instruct

```bash
# Instalar Ollama
# Windows: baixar de https://ollama.com/download

# Baixar modelo
ollama pull qwen2:7b-instruct
```

### Instalação do Projeto

```bash
cd juridico-review-ai

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

## 🚀 Uso do MVP

### Comando Básico (apenas Tier-1 local - SEM CUSTO)

```bash
python src/main_v2.py \
  --minuta data/entrada/sua_minuta.docx \
  --catalogo data/catalogos/catalogo_cri_v2.yaml \
  --skip-tier2
```

Isso vai:
- ✅ Parsear o documento
- ✅ Classificar todas as cláusulas (PRESENTE/PARCIAL/AUSENTE)
- ✅ Gerar relatórios Excel e DOCX
- ✅ Criar log de auditoria
- ❌ NÃO usar frontier models (custo zero!)

### Comando Completo (com Tier-2 local)

```bash
python src/main_v2.py \
  --minuta data/entrada/sua_minuta.docx \
  --catalogo data/catalogos/catalogo_cri_v2.yaml \
  --tier1-model qwen2:7b-instruct \
  --tier2-provider ollama \
  --tier2-model qwen2:7b-instruct
```

Isso vai:
- ✅ Fazer tudo do comando básico
- ✅ Gerar sugestões de cláusulas para PARCIAIS/AUSENTES
- ✅ Ainda local, custo zero!

### Com Frontier Model (OpenAI/Claude - tem custo!)

```bash
# Configurar API key
export OPENAI_API_KEY="sua-chave"
# ou
export ANTHROPIC_API_KEY="sua-chave"

python src/main_v2.py \
  --minuta data/entrada/sua_minuta.docx \
  --catalogo data/catalogos/catalogo_cri_v2.yaml \
  --tier2-provider openai \
  --tier2-model gpt-4o-mini
```

## 📊 Saídas do Sistema

Após rodar, você terá em `data/saida/`:

### 1. `revisao_completa.xlsx`
Excel com 4 abas:
- **Resumo**: Métricas gerais
- **Cláusulas OK**: Aprovadas no Tier-1
- **Sugestões**: Tier-2 com textos sugeridos
- **Detalhamento**: Visão completa

### 2. `sugestoes_detalhadas.docx`
Documento Word com:
- Sumário executivo
- Análise detalhada de cada cláusula
- Textos sugeridos formatados
- Checklists de validação

### 3. `audit_YYYYMMDD_HHMMSS.json`
Log completo de auditoria:
- Hash SHA-256 do documento
- Versão do catálogo usado
- Modelos e providers
- Prompts truncados
- Timeline de eventos
- Metadados completos

## 🧪 Testando o MVP

1. **Coloque sua minuta** em `data/entrada/`

2. **Rode o comando básico** (sem custo):
```bash
python src/main_v2.py \
  --minuta data/entrada/minuta_cri.docx \
  --catalogo data/catalogos/catalogo_cri_v2.yaml \
  --skip-tier2 \
  --verbose
```

3. **Verifique os relatórios** em `data/saida/`

4. **Analise a auditoria** para rastreabilidade

## 📝 Catálogos Disponíveis

O sistema vem com catálogos v2 (com regex patterns e templates):

- `catalogo_cri_v2.yaml` - Certificados de Recebíveis Imobiliários
- `catalogo_cra.yaml` - Certificados de Recebíveis do Agronegócio (v1)
- `catalogo_debenture.yaml` - Debêntures (v1)

### Estrutura do Catálogo v2

```yaml
clausulas:
  - id: "CRI_DEF_001"
    titulo: "Definições Gerais"
    categoria: "definicoes"
    importancia: "alta"
    obrigatoria: true

    keywords:
      - "definições"
      - "termos"

    regex_patterns:
      - "(?i)defini[çc][õo]es\\s+gerais"
      - "(?i)CRI.*Certificado"

    template: |
      CLÁUSULA {{numero}} – DEFINIÇÕES
      ...

    variaveis:
      - nome: "emissora_nome"
        tipo: "string"
        obrigatoria: true

    criterios_validacao:
      - campo: "CRI"
        regra: "deve conter definição completa"
```

## 🔍 Interpretando Resultados

### Status da Cláusula

- **PRESENTE**: ✅ Cláusula OK, não precisa revisão
- **PARCIAL**: ⚠️ Cláusula existe mas falta algo importante
- **AUSENTE**: ❌ Cláusula não encontrada ou inadequada

### Prioridades (Tier-2)

- **ALTA**: Cláusula obrigatória ausente/parcial - AÇÃO URGENTE
- **MÉDIA**: Cláusula importante mas não crítica
- **BAIXA**: Sugestão de melhoria

## 💡 Dicas de Uso

1. **Para MVP sem custo**: Use `--skip-tier2` sempre
2. **Para análise rápida**: Foque na aba "Resumo" do Excel
3. **Para revisão detalhada**: Use o DOCX com sugestões
4. **Para auditoria**: Guarde os arquivos JSON de audit
5. **Catálogos customizados**: Crie seu próprio YAML baseado no v2

## 🐛 Troubleshooting

### Erro: "Ollama not found"
```bash
# Verifique se Ollama está rodando
ollama list

# Tente rodar novamente
ollama serve
```

### Erro: "Model not found"
```bash
# Baixe o modelo
ollama pull qwen2:7b-instruct
```

### Erro de encoding (Windows)
```bash
# Use UTF-8
set PYTHONUTF8=1
python src/main_v2.py ...
```

### Documento não parseado corretamente
- Verifique se é DOCX ou PDF válido
- Certifique-se que cláusulas estão numeradas
- Use `--verbose` para ver logs detalhados

## 📈 Próximos Passos

Para melhorar o MVP:

1. **Criar catálogos CRA e Debênture v2** com regex patterns
2. **Fine-tuning** do modelo local para domínio jurídico
3. **Interface web** para upload de documentos
4. **Comparação de versões** de minutas
5. **Integração com CVM** para validações regulatórias

## 🔒 Segurança e Privacidade

- ✅ **Tier-1 100% local**: Dados não saem da máquina
- ✅ **Logs de auditoria**: Rastreabilidade completa
- ✅ **Hash SHA-256**: Integridade dos documentos
- ⚠️ **Tier-2 frontier**: Dados vão para API externa (se usar)

## 📄 Licença

[Definir]

## 👥 Contato

[Seu contato]

---

**Versão**: 2.0.0
**Data**: Janeiro 2025
**Status**: MVP - Pronto para testes
