# 🤖 Como Gerar Explicações Automáticas para TODOS os Catálogos

## 📊 Situação Atual

- **Catálogo CRI Destinação**: 49 cláusulas sem explicação
- **Catálogo CRI Sem Destinação**: 44 cláusulas sem explicação
- **Total**: 93 cláusulas que precisam de explicação

## ⏱️ Tempo Estimado

- **6 segundos por cláusula** (rate limiting Gemini API - 10 RPM)
- **93 cláusulas × 6 segundos = ~9-10 minutos**

## 🚀 Como Executar

### Opção 1: Com API Key na linha de comando

```bash
cd /home/user/webapp/juridico-review-ai
export GEMINI_API_KEY='SUA_CHAVE_AQUI'
python3 gerar_explicacoes_catalogo.py
```

### Opção 2: Criar arquivo .env

```bash
cd /home/user/webapp/juridico-review-ai
echo "GEMINI_API_KEY=SUA_CHAVE_AQUI" > .env
source .env
python3 gerar_explicacoes_catalogo.py
```

## 📋 O que o script faz:

1. ✅ Carrega cada catálogo (destinação e sem destinação)
2. ✅ Para cada cláusula SEM explicação (ou com < 100 chars):
   - Usa Gemini AI para gerar explicação detalhada
   - Baseada em: título, categoria, keywords, template
   - Aguarda 6 segundos (rate limiting)
3. ✅ Cria **backup automático** dos catálogos originais
4. ✅ Salva catálogos atualizados com as novas explicações
5. ✅ Mostra progresso em tempo real

## 📝 Exemplo de Saída

```
🚀 GERADOR AUTOMÁTICO DE EXPLICAÇÕES DE CATÁLOGO
================================================================================

================================================================================
📂 Processando: data/catalogos/catalogo_cri_destinacao.yaml
================================================================================

Total de cláusulas: 49
Dry run: NÃO (vai salvar)

[1/49] CRI_DEST_001: DEFINIÇÕES...
  🤖 Gerando explicação com Gemini AI...
  ✅ Gerada (542 chars)
  💬 Preview: Esta cláusula deve conter TODAS as definições de termos...

[2/49] CRI_DEST_002: APROVAÇÃO DA EMISSÃO...
  🤖 Gerando explicação com Gemini AI...
  ✅ Gerada (389 chars)
  💬 Preview: Esta cláusula deve documentar a aprovação formal...

...

💾 Salvando catálogo...
  📦 Backup criado: catalogo_cri_destinacao_backup_20251028_214500.yaml
  ✅ Catálogo salvo: catalogo_cri_destinacao.yaml

================================================================================
📊 RESUMO
================================================================================
Total de cláusulas:      49
✅ Modificadas:          49
⏭️  Puladas (já tinham): 0
❌ Erros:                0
================================================================================
```

## ✅ Depois de Executar

1. Os catálogos terão explicações automáticas geradas
2. Você pode **revisar e editar** na interface do Streamlit
3. As explicações estarão **prontas para uso** no matching

## 🎯 Próximos Passos

1. Execute o script (9-10 minutos)
2. Acesse a aba "Editar Catálogo" no Streamlit
3. Revise as explicações geradas
4. Edite conforme necessário
5. Salve as alterações finais
6. Teste o matching melhorado!

---

**💡 Dica**: As explicações geradas pela IA são ótimas como base, mas você pode adicionar nuances específicas do seu contexto!
