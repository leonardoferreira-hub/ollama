# Sistema RAG com Gold Standard e Catálogos Especializados

## 🎯 Visão Geral

Sistema de **aprendizado contínuo** com qualidade controlada para revisão de minutas jurídicas.

## ✨ Funcionalidades Principais

### 1. **Catálogos Especializados por Tipo de Operação**

Cada tipo de operação tem seu próprio catálogo e aprende **separadamente**:

| Tipo | Arquivo | Descrição |
|------|---------|-----------|
| CRI Destinação | `catalogo_cri_destinacao.yaml` | CRI com destinação específica de recursos |
| CRI Sem Destinação | `catalogo_cri_sem_destinacao.yaml` | CRI sem destinação específica |
| CRA | `catalogo_cra.yaml` | Certificados de Recebíveis do Agronegócio |
| Debênture Financeira | `catalogo_debenture.yaml` | Debêntures financeiras |
| CRI Res. 88 | (a criar) | CRI Resolução 88 |

### 2. **Sistema de Qualidade (Gold Standard)**

#### Documentos GOLD ⭐
- **Prioridade máxima** nas sugestões do RAG
- **Sempre disponíveis** como referência
- **Não são substituídos** por documentos ruins
- Detectados automaticamente pelo nome: `GOLD_[TIPO]_[NOME].docx`

#### Filtro de Qualidade
Documentos normais passam por filtro rigoroso:
- ✅ **Aceitos**: Cláusulas PRESENTE com confiança ≥ 70%
- ❌ **Rejeitados**: Cláusulas PARCIAL, AUSENTE ou baixa confiança
- 🎯 **Objetivo**: Evitar que documentos ruins contaminem a base

### 3. **RAG com Isolamento por Tipo**

Cada catálogo aprende **apenas com documentos do mesmo tipo**:

```
CRI Destinação → aprende APENAS com CRIs Destinação
CRA → aprende APENAS com CRAs
Debênture → aprende APENAS com Debêntures
```

**Benefício**: Sugestões específicas para cada tipo de operação.

## 📁 Estrutura de Diretórios

```
juridico-review-ai/
├── data/
│   ├── catalogos/                    # Catálogos especializados
│   │   ├── catalogo_cri_destinacao.yaml
│   │   ├── catalogo_cri_sem_destinacao.yaml
│   │   ├── catalogo_cra.yaml
│   │   └── catalogo_debenture.yaml
│   │
│   ├── documentos_gold/              # Documentos ideais
│   │   ├── README.md
│   │   ├── GOLD_CRI_DESTINACAO_MODELO_2025.docx
│   │   ├── GOLD_CRI_SEM_DESTINACAO_PADRAO.docx
│   │   └── GOLD_CRA_AGRO_REFERENCIA.docx
│   │
│   └── vector_db/                    # Banco vetorial persistente
│       └── chroma.sqlite3
```

## 🚀 Como Usar

### Passo 1: Adicionar Documentos GOLD

1. Coloque o documento `.docx` ideal em `data/documentos_gold/`
2. Nomeie com prefixo `GOLD_`:
   - Exemplo: `GOLD_CRI_DESTINACAO_MODELO_2025.docx`
3. Faça upload no Streamlit normalmente
4. Sistema detecta automaticamente e marca como GOLD ⭐

### Passo 2: Selecionar Catálogo Correto

Ao analisar um documento, escolha o catálogo apropriado:
- **CRI com destinação específica** → `Catálogo CRI - Destinação Específica`
- **CRI sem destinação** → `Catálogo CRI - Sem Destinação`
- **CRA** → `Catálogo CRA`
- **Debênture** → `Catálogo Debênture Financeira`

### Passo 3: Análise Automática

O sistema automaticamente:
1. ✅ Classifica cláusulas
2. ✅ Filtra cláusulas ruins (não salva PARCIAL/AUSENTE de docs normais)
3. ✅ Salva apenas cláusulas PRESENTE com confiança ≥ 70%
4. ✅ Marca documentos GOLD (salva TUDO, mesmo PARCIAL/AUSENTE)
5. ✅ Gera sugestões usando exemplos GOLD + bons exemplos do histórico

## 📊 Estatísticas da Base

Na sidebar, você vê:
- **Documentos**: Total de documentos na base
- **Cláusulas**: Total de cláusulas indexadas
- **Documentos GOLD**: Quantos documentos de referência
- **Cláusulas GOLD**: Quantas cláusulas de referência

## 🔍 Como Funciona o RAG

### Fluxo de Sugestão:

```
1. Cláusula PARCIAL/AUSENTE detectada
   ↓
2. Sistema busca exemplos similares NO MESMO CATÁLOGO
   ↓
3. Prioriza documentos GOLD
   ↓
4. Filtra apenas cláusulas PRESENTE
   ↓
5. Retorna 2 melhores exemplos:
   - Primeiro: GOLD (se disponível)
   - Segundo: Melhor documento normal
   ↓
6. Gemini gera sugestão baseada em:
   - Template do catálogo
   - Exemplos GOLD
   - Exemplos de bons documentos anteriores
```

### Exemplo de Sugestão:

**Sem RAG (primeira análise):**
> "Sugestão: CLÁUSULA 1 - DESTINAÇÃO DOS RECURSOS. Os recursos captados..."

**Com RAG (após 5 documentos):**
> "Sugestão: CLÁUSULA 1 - DESTINAÇÃO DOS RECURSOS. Os recursos captados com a Emissão serão destinados exclusivamente para obras de construção civil conforme projeto aprovado, incluindo: (i) Aquisição de materiais; (ii) Mão de obra; (iii) Despesas de engenharia. Conforme observado no [GOLD_CRI_DESTINACAO_MODELO_2025] e no [CRI_ABC_2024], recomenda-se incluir cláusula de vedação de desvio de finalidade..."

## 💡 Vantagens do Sistema

### 1. **Aprendizado Contínuo Controlado**
- ✅ Aprende com cada documento
- ✅ Mas **não** aprende com documentos ruins
- ✅ Documentos GOLD sempre predominam

### 2. **Especialização por Tipo**
- ✅ CRI Destinação não mistura com CRA
- ✅ Sugestões específicas para cada operação
- ✅ Base cresce de forma organizada

### 3. **Qualidade Garantida**
- ✅ Documentos GOLD como âncora
- ✅ Filtro automático (confiança ≥ 70%)
- ✅ Só aprende com cláusulas PRESENTE

### 4. **Zero Manutenção**
- ✅ Tudo automático
- ✅ Basta nomear arquivos com "GOLD_"
- ✅ Sistema detecta e prioriza

## 🎯 Próximos Passos Recomendados

1. **Criar Documentos GOLD para cada tipo**:
   - [ ] GOLD_CRI_DESTINACAO_MODELO_2025.docx
   - [ ] GOLD_CRI_SEM_DESTINACAO_PADRAO.docx
   - [ ] GOLD_CRA_AGRO_REFERENCIA.docx
   - [ ] GOLD_DEBENTURE_FINANCEIRA_IDEAL.docx
   - [ ] GOLD_CRI_RES88_MODELO.docx

2. **Expandir catálogos especializados**:
   - [ ] Criar `catalogo_cri_res88.yaml`
   - [ ] Adicionar mais cláusulas específicas por tipo

3. **Alimentar a base**:
   - Analisar documentos históricos de qualidade
   - Sistema aprenderá automaticamente

## ⚠️ Avisos Importantes

### NÃO faça upload de:
- ❌ Documentos com erros graves
- ❌ Minutas preliminares ruins
- ❌ Rascunhos iniciais

### FAÇA upload de:
- ✅ Documentos finais bem elaborados
- ✅ Minutas aprovadas
- ✅ Modelos da casa (como GOLD)

### Sobre Documentos GOLD:
- 📌 Use para **modelos perfeitos** da securitizadora
- 📌 Eles **nunca** são substituídos
- 📌 Sempre têm **prioridade máxima**
- 📌 Servem de **padrão de qualidade**

## 📈 Crescimento da Base

A cada documento analisado com sucesso:

| Análise | Cláusulas na Base | Qualidade das Sugestões |
|---------|-------------------|-------------------------|
| 1ª | ~20 (do 1º doc) | Apenas templates genéricos |
| 5ª | ~100 (5 docs) | Sugestões com exemplos reais |
| 20ª | ~400 (20 docs) | Sugestões altamente customizadas |
| 100ª | ~2000 (100 docs) | IA adaptada ao estilo da casa |

## 🛠️ Manutenção

### Limpar Base (usar com cuidado!)
Se precisar resetar o banco vetorial:

```python
from src.vector_db import DocumentVectorDB
db = DocumentVectorDB()
db.reset()  # ⚠️ Apaga TUDO, incluindo GOLD!
```

**Recomendação**: Faça backup dos documentos GOLD antes de resetar.

### Verificar Estatísticas

```python
db_stats = st.session_state.vector_db.get_statistics()
print(f"Total: {db_stats['total_clausulas']} cláusulas")
print(f"GOLD: {db_stats['clausulas_gold']} cláusulas")
```

## 📝 Resumo Executivo

✅ **Sistema implementado com sucesso!**

**Principais conquistas**:
1. ✅ Catálogos especializados por tipo de operação
2. ✅ Sistema GOLD com prioridade máxima
3. ✅ Filtro automático de qualidade (≥70% confiança)
4. ✅ RAG isolado por catálogo
5. ✅ Aprendizado contínuo controlado
6. ✅ Zero manutenção manual

**Resultado**: Sistema que **aprende** com documentos bons, **ignora** documentos ruins, e **sempre prioriza** modelos GOLD da securitizadora.
