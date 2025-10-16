# 🚀 Teste Rápido v3 - Versão OTIMIZADA

## ⚡ O Que Mudou

### v2 → v3 Melhorias:

**1. Catálogo Expandido** ✅
- v2: 7 cláusulas
- v3: **25 cláusulas** (cobertura completa)

**2. Performance** ✅
- v2: ~30 minutos (1827s)
- v3: **~5-7 minutos** (meta: 5-10x mais rápido)

**3. Prompts Otimizados** ✅
- Redução de 60% no tamanho
- Truncamento inteligente de conteúdo
- Número de tokens previsíveis reduzido

**4. Matching Melhorado** ✅
- Regex patterns mais precisos
- Keywords alinhadas com documento real
- 25 IDs específicos de cláusulas

## 🧪 Como Testar

### Comando de Teste (SEM CUSTO)

```bash
cd juridico-review-ai

python src/main_v3.py \
  --minuta "data/entrada/CRI Evoke_TS_v.02  07102025_001_22063v5.DOCX" \
  --catalogo data/catalogos/catalogo_cri_v3.yaml \
  --skip-tier2 \
  --verbose
```

### O que esperar:

**Tempo estimado:** 5-7 minutos (vs 30min na v2)

**Métricas esperadas:**
- Parsing: <1s
- Ranking: ~10s
- Classificação Tier-1: **5-7min** (~15-20s por cláusula)
- Total: ~7min

**Resultados esperados:**
- ✅ Mais cláusulas PRESENTES (catálogo expandido)
- ✅ Matching mais preciso
- ✅ Menos falsos negativos

## 📊 Comparação v2 vs v3

| Métrica | v2 (Teste Anterior) | v3 (Esperado) |
|---------|---------------------|---------------|
| **Tempo Total** | 30min 39s | ~7min |
| **Cláusulas Catálogo** | 7 | 25 |
| **PRESENTES** | 0 | 8-12 |
| **PARCIAIS** | 2 | 5-8 |
| **AUSENTES** | 18 | 2-5 |
| **Performance** | 1x | **5-7x mais rápido** |

## 🎯 Checklist de Validação

Após rodar o teste, verifique:

- [ ] Tempo total < 10 minutos
- [ ] Pelo menos 50% das cláusulas como PRESENTE ou PARCIAL
- [ ] Excel gerado com 4 abas
- [ ] DOCX narrativo criado
- [ ] Audit JSON com metadados completos
- [ ] Menos de 5 cláusulas totalmente AUSENTES

## 🔍 Analisando Resultados

### 1. Excel - Aba "Resumo"
Verifique se os números fazem sentido:
- Total de cláusulas analisadas: 20
- Cláusulas OK (Tier-1): deve ser > 0
- PRESENTES: esperamos 8-12

### 2. Excel - Aba "Cláusulas OK"
Veja quais foram aprovadas no Tier-1

### 3. Excel - Aba "Sugestões"
Identifique quais cláusulas precisam melhoria

### 4. Audit JSON
```bash
# Ver sumário rápido
python -c "
import json
with open('data/saida/audit_*.json') as f:
    a = json.load(f)
    print('Tempo total:', a['metadata']['tempo_total_segundos'], 's')
    print('Tier-1:', a['metadata']['tier1']['summary'])
"
```

## 🐛 Se Algo Der Errado

### Erro: "Module not found"
```bash
pip install -r requirements.txt
```

### Muito lento ainda (>15min)
- Verifique se Ollama está usando GPU
- Tente modelo menor: `--tier1-model qwen2:1.5b`

### Todos classificados como AUSENTE
- O catálogo v3 deve resolver isso
- Verifique se está usando catalogo_cri_v3.yaml

### Erro de memória
- Reduza `--top-k` para 1
- Use modelo menor

## 📝 Logs Úteis

Com `--verbose`, você verá:
```
[1/20] Classificando: DEFINIÇÕES...
[2/20] Classificando: APROVAÇÃO DA EMISSÃO...
...
```

Isso ajuda a acompanhar o progresso em tempo real.

## ✅ Teste Bem-Sucedido Se:

1. ✅ Terminou em < 10 minutos
2. ✅ Pelo menos 10 cláusulas como PRESENTE
3. ✅ Excel e DOCX gerados corretamente
4. ✅ Matching correto das cláusulas principais:
   - Definições → CRI_DEF_001
   - Remuneração → CRI_REM_001
   - Agente Fiduciário → CRI_AGF_001
   - Assembleia → CRI_ASS_001

## 🔄 Próximos Passos se v3 Funcionar

1. **Testar Tier-2** (remover `--skip-tier2`)
2. **Criar catálogos CRA e Debêntures v3**
3. **Fine-tune do modelo** para melhor precisão
4. **Cache persistente** de embeddings
5. **Interface web** simples

## 💬 Feedback

Após o teste, documente:
- Tempo real gasto
- Quantidade de PRESENTE/PARCIAL/AUSENTE
- Falsos positivos/negativos
- Sugestões de melhoria

---

**Versão**: 3.0.0
**Data**: 2025-10-16
**Status**: Pronto para teste
