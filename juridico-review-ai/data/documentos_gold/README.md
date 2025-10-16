# Documentos Gold Standard

Esta pasta contém os **documentos ideais** de cada tipo de operação.

## O que são Documentos Gold?

São minutas **perfeitas** que servem como referência principal para o RAG.
- ✅ Sempre têm **prioridade** nas sugestões
- ✅ Servem como **modelo de excelência**
- ✅ **Não são substituídos** por documentos ruins

## Como adicionar um documento Gold:

1. Coloque o arquivo `.docx` ou `.pdf` nesta pasta
2. Nomeie seguindo o padrão: `GOLD_[TIPO]_[NOME].docx`

### Exemplos:
- `GOLD_CRI_DESTINACAO_MODELO_2025.docx`
- `GOLD_CRI_SEM_DESTINACAO_PADRAO.docx`
- `GOLD_CRA_AGRO_REFERENCIA.docx`
- `GOLD_DEBENTURE_FINANCEIRA_IDEAL.docx`

## Tipos suportados:

- `CRI_DESTINACAO`: CRI com destinação específica
- `CRI_SEM_DESTINACAO`: CRI sem destinação
- `CRA`: Certificados de Recebíveis do Agronegócio
- `DEBENTURE_FINANCEIRA`: Debêntures financeiras
- `CRI_RES88`: CRI Resolução 88

## Como o sistema usa:

1. **Prioridade máxima**: Documentos gold aparecem primeiro nas sugestões
2. **Peso dobrado**: Valem 2x mais que documentos normais
3. **Sempre disponíveis**: Nunca são removidos da base
4. **Aprendizado seletivo**: Sistema também aprende com outros bons documentos (classificação PRESENTE), mas documentos gold sempre predominam
