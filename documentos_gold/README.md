# 📁 Documentos GOLD - Modelos de Termos de Securitização CRI

## 📋 Visão Geral

Esta pasta contém os documentos GOLD (padrão ouro) de Termos de Securitização de Certificados de Recebíveis Imobiliários (CRI) da Travessia Securitizadora S.A., utilizados como referência para análise e revisão de documentos jurídicos.

## 📄 Documentos Originais

### 1. GOLD_CRI_DESTINACAO_MODELO_2025.docx
- **Tipo**: Termo de Securitização CRI com Destinação
- **Ano**: Modelo 2025
- **Características**: Estrutura formal para emissão de CRI com destinação específica dos recursos
- **Tamanho**: 275 KB
- **Cláusulas Identificadas**: 60

### 2. GOLD_CRI_SEM_DESTINACAO_PADRAO.docx
- **Tipo**: Termo de Securitização CRI sem Destinação
- **Características**: Estrutura padrão para emissão de CRI sem destinação específica
- **Tamanho**: 344 KB
- **Cláusulas Identificadas**: 44

## 🔍 Arquivos de Análise Gerados

### Catálogos em Markdown (.md)

Catálogos completos e formatados com:
- ✅ Listagem de todas as cláusulas
- ✅ Sugestões de explicação para cada cláusula
- ✅ Pontos de atenção identificados automaticamente
- ✅ Preview do conteúdo de cada cláusula
- ✅ Informações sobre tamanho e tipo

**Arquivos:**
- `GOLD_CRI_DESTINACAO_MODELO_2025_CATALOGO.md`
- `GOLD_CRI_SEM_DESTINACAO_PADRAO_CATALOGO.md`

### Dados Estruturados em JSON (.json)

Dados completos em formato JSON para integração com sistemas:
- 📊 Estrutura hierárquica de cláusulas
- 📊 Metadados de cada cláusula
- 📊 Sugestões de explicação
- 📊 Pontos de atenção
- 📊 Conteúdo completo

**Arquivos:**
- `GOLD_CRI_DESTINACAO_MODELO_2025_catalogo_completo.json`
- `GOLD_CRI_SEM_DESTINACAO_PADRAO_catalogo_completo.json`

## 🛠️ Scripts de Processamento

### extrair_clausulas_completo.py
Script Python para extração e catalogação completa de cláusulas:

**Funcionalidades:**
- 📖 Extrai estrutura completa do documento DOCX
- 🔍 Identifica cláusulas, subcláusulas e seções
- 💡 Gera sugestões de explicação baseadas em análise de conteúdo
- ⚠️ Detecta pontos de atenção automaticamente
- 📝 Cria catálogos em Markdown e JSON

**Como usar:**
```bash
cd /home/user/webapp/documentos_gold
python3 extrair_clausulas_completo.py
```

## 📊 Estatísticas

### CRI com Destinação - Modelo 2025
- **Total de Cláusulas**: 60
- **Elementos Extraídos**: 1.285
- **Seções Principais**: Definições, Aprovação, Objeto, Identificação, Subscrição, Remuneração, Vencimento Antecipado, Assembleia, Obrigações, Resgate Antecipado

### CRI sem Destinação - Padrão
- **Total de Cláusulas**: 44
- **Elementos Extraídos**: 1.504
- **Cláusulas Principais**: 7
- **Títulos/Seções**: 37

## 🎯 Sugestões de Explicação Geradas

O sistema gera automaticamente sugestões de explicação baseadas em:

1. **Palavras-chave no título**: Identificação de termos como "Definições", "Obrigações", "Garantias"
2. **Análise de conteúdo**: Detecção de verbos que indicam obrigações, faculdades ou restrições
3. **Contexto jurídico**: Aplicação de conhecimento sobre documentos CRI

### Exemplos de Sugestões:

**Definições:**
> "Esta cláusula estabelece os termos e definições utilizados ao longo do documento, garantindo interpretação uniforme."

**Subscrição:**
> "Estabelece as regras para subscrição e integralização dos certificados."

**Remuneração:**
> "Define a forma de remuneração, atualização monetária e cálculo de juros dos CRI."

**Assembleia:**
> "Regula a convocação e funcionamento das assembleias de titulares de CRI."

## ⚠️ Pontos de Atenção Automáticos

O sistema detecta automaticamente menções a:

- ⏰ **Prazos**: Especificação de prazos importantes
- 📅 **Vencimento**: Condições de vencimento
- 🛡️ **Garantias**: Menção a garantias
- ⚖️ **Penalidades**: Estabelecimento de penalidades
- 💰 **Multas**: Previsão de multas
- 📈 **Juros**: Especificação de taxas
- ⚠️ **Mora**: Regulação de mora
- 🚫 **Inadimplemento**: Tratamento de inadimplemento
- 📜 **Rescisão**: Hipóteses de rescisão
- 👥 **Assembleia**: Necessidade de aprovação
- 📢 **Notificação**: Exigência de notificação
- 📝 **Registro**: Necessidade de registro

## 🔄 Integração com Sistema de Revisão

Os catálogos gerados podem ser integrados ao sistema de revisão de documentos para:

1. **Comparação Automática**: Comparar cláusulas de novos documentos com os modelos GOLD
2. **Validação de Completude**: Verificar se todas as cláusulas essenciais estão presentes
3. **Análise de Divergências**: Identificar diferenças significativas em relação aos padrões
4. **Sugestões de Melhoria**: Propor ajustes baseados nos modelos de referência

## 📝 Uso Recomendado

### Para Revisores Jurídicos:
1. Consultar os catálogos em Markdown para referência rápida
2. Comparar cláusulas específicas com os modelos GOLD
3. Verificar pontos de atenção identificados

### Para Sistemas Automatizados:
1. Utilizar arquivos JSON para processar dados estruturados
2. Implementar validação automática de documentos
3. Gerar relatórios de conformidade

### Para Análise de IA:
1. Treinar modelos com base nos padrões identificados
2. Melhorar sugestões de explicação com feedback humano
3. Expandir detecção de pontos de atenção

## 🚀 Próximos Passos

1. ✅ Documentos salvos e catalogados
2. ✅ Cláusulas extraídas e analisadas
3. ✅ Sugestões de explicação geradas
4. ⏳ Revisar e refinar sugestões manualmente
5. ⏳ Integrar com sistema de revisão existente
6. ⏳ Criar base de conhecimento para IA

## 📧 Contato e Suporte

Para dúvidas ou sugestões sobre os documentos GOLD e seus catálogos, consulte a documentação do sistema de revisão jurídica.

---

**Data de Criação**: 2025-10-28  
**Versão**: 1.0  
**Status**: Catálogos completos e prontos para uso
