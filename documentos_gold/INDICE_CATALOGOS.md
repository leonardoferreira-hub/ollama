# 📚 Índice de Catálogos - Documentos GOLD CRI

## 🎯 Navegação Rápida

### 📄 [CRI com Destinação - Modelo 2025](GOLD_CRI_DESTINACAO_MODELO_2025_CATALOGO.md)
**60 cláusulas catalogadas**

#### Principais Seções:
1. **Definições** - Termos e conceitos utilizados
2. **Aprovação da Emissão** - Procedimentos de aprovação
3. **Objeto e Créditos Imobiliários** - Descrição dos ativos
4. **Identificação dos CRI** - Características dos certificados
5. **Subscrição e Integralização** - Regras de subscrição
6. **Remuneração e Atualização Monetária** - Cálculo de rendimentos
7. **Vencimento Antecipado** - Hipóteses de antecipação
8. **Assembleia Especial** - Governança dos titulares
9. **Obrigações da Emissora** - Deveres da emissora
10. **Resgate Antecipado** - Procedimentos de resgate

---

### 📄 [CRI sem Destinação - Padrão](GOLD_CRI_SEM_DESTINACAO_PADRAO_CATALOGO.md)
**44 cláusulas catalogadas**

#### Principais Seções:
1. **Partes** - Identificação das partes contratantes
2. **Definições** - Glossário de termos
3. **Objeto** - Descrição do termo de securitização
4. **Créditos Imobiliários** - Especificação dos créditos
5. **Características dos CRI** - Detalhamento técnico
6. **Forma de Distribuição** - Modalidades de oferta
7. **Remuneração** - Cálculo de juros e atualização
8. **Amortização e Pagamento** - Cronograma de pagamentos
9. **Eventos de Vencimento** - Gatilhos de vencimento antecipado
10. **Agente Fiduciário** - Atribuições e responsabilidades

---

## 📊 Comparativo Rápido

| Aspecto | CRI com Destinação | CRI sem Destinação |
|---------|-------------------|-------------------|
| **Total de Cláusulas** | 60 | 44 |
| **Elementos Extraídos** | 1.285 | 1.504 |
| **Foco Principal** | Destinação específica de recursos | Estrutura padrão geral |
| **Complexidade** | Alta - múltiplas séries | Média - série única |
| **Ano do Modelo** | 2025 (mais recente) | Padrão consolidado |

---

## 🔍 Como Usar Este Índice

### Para Busca Rápida:
1. Identifique qual tipo de documento você está revisando
2. Clique no link do catálogo correspondente
3. Use Ctrl+F para buscar por palavras-chave

### Para Comparação:
1. Abra ambos os catálogos em abas separadas
2. Compare cláusulas similares
3. Identifique diferenças estruturais

### Para Análise Detalhada:
1. Consulte os arquivos JSON para dados estruturados
2. Use os scripts Python para análises customizadas
3. Integre com ferramentas de revisão

---

## 📁 Estrutura de Arquivos

```
documentos_gold/
├── README.md                                          # Documentação geral
├── INDICE_CATALOGOS.md                               # Este arquivo
│
├── GOLD_CRI_DESTINACAO_MODELO_2025.docx              # Original DOCX
├── GOLD_CRI_DESTINACAO_MODELO_2025_CATALOGO.md       # Catálogo Markdown
├── GOLD_CRI_DESTINACAO_MODELO_2025_catalogo_completo.json  # Dados JSON
│
├── GOLD_CRI_SEM_DESTINACAO_PADRAO.docx               # Original DOCX
├── GOLD_CRI_SEM_DESTINACAO_PADRAO_CATALOGO.md        # Catálogo Markdown
├── GOLD_CRI_SEM_DESTINACAO_PADRAO_catalogo_completo.json   # Dados JSON
│
└── extrair_clausulas_completo.py                     # Script de extração
```

---

## 🎨 Legenda de Ícones nos Catálogos

- 📝 **Sugestão de Explicação**: Resumo da função da cláusula
- ⚠️ **Pontos de Atenção**: Aspectos críticos identificados automaticamente
- 📄 **Preview do Conteúdo**: Amostra do texto da cláusula

---

## 💡 Dicas de Uso

### Para Revisores:
✅ Sempre compare cláusulas críticas (Garantias, Vencimento, Eventos)  
✅ Verifique consistência de definições entre documentos  
✅ Atenção especial para prazos e valores numéricos  

### Para Desenvolvedores:
🔧 Use os arquivos JSON para processamento automatizado  
🔧 Implemente validações baseadas nos padrões GOLD  
🔧 Crie alertas para desvios significativos  

### Para Gestores:
📈 Monitore conformidade dos documentos produzidos  
📈 Use como base para treinamento de equipe  
📈 Estabeleça KPIs de qualidade documental  

---

## 🔄 Atualização dos Catálogos

Para reprocessar os documentos após alterações:

```bash
cd /home/user/webapp/documentos_gold
python3 extrair_clausulas_completo.py
```

---

**Última Atualização**: 2025-10-28  
**Versão do Catálogo**: 1.0
