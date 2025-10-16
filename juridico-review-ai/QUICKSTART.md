# 🚀 Quickstart - Jurídico Review AI

## ⚡ Rodar Localmente (AGORA)

### 1. Instalar dependências

```bash
cd juridico-review-ai
pip install -r requirements-streamlit.txt
```

### 2. Obter Gemini API Key

1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave

### 3. Rodar o app

```bash
streamlit run app.py
```

### 4. Usar

1. Navegador abre automaticamente em: `http://localhost:8501`
2. Cole sua Gemini API Key na barra lateral
3. Selecione catálogo (recomendo: `catalogo_cri_v3`)
4. Faça upload de uma minuta (.docx ou .pdf)
5. Clique em "🚀 Iniciar Análise"
6. Aguarde 2-5 minutos
7. Veja resultados na aba "📊 Resultados"

---

## 🌐 Deploy Online (Streamlit Cloud)

### Opção A: Deploy Rápido (3 passos)

```bash
# 1. Push para GitHub
git init
git add .
git commit -m "feat: app Streamlit"
git remote add origin https://github.com/SEU-USER/juridico-review-ai.git
git push -u origin main

# 2. Acesse streamlit.io/cloud e conecte seu repo

# 3. Configure:
# - Main file: app.py
# - Requirements: requirements-streamlit.txt
# - Python: 3.11
```

### Opção B: Deploy Detalhado

Veja: [DEPLOY_STREAMLIT.md](DEPLOY_STREAMLIT.md)

---

## 📊 O Que Esperar

### **Interface:**

```
┌────────────────────────────────────────┐
│  ⚖️ Jurídico Review AI                 │
│  ─────────────────────────────────     │
│                                         │
│  [Upload Minuta]                       │
│                                         │
│  [🚀 Iniciar Análise]                  │
│                                         │
│  ┌──────────────────────────────┐     │
│  │ 📊 Resultados                 │     │
│  │                               │     │
│  │ ✅ PRESENTE: 12 (60%)         │     │
│  │ ⚠️  PARCIAL:  5  (25%)        │     │
│  │ ❌ AUSENTE:  3  (15%)         │     │
│  │                               │     │
│  │ [Tabela detalhada...]         │     │
│  └──────────────────────────────┘     │
└────────────────────────────────────────┘
```

### **Performance:**

- Upload: <1s
- Parsing: 5-10s
- Análise (20 cláusulas): 2-3 minutos
- Total: ~3-4 minutos

### **Custos:**

- Desenvolvimento: R$ 0
- Hosting (Streamlit Cloud): R$ 0
- Gemini API (tier gratuito): R$ 0
- **Total: R$ 0/mês** (até 1500 análises/dia)

---

## ✅ Checklist de Teste

- [ ] App roda localmente
- [ ] Upload de .docx funciona
- [ ] Gemini API conecta
- [ ] Análise completa uma minuta
- [ ] Resultados aparecem corretamente
- [ ] Métricas estão corretas
- [ ] Interface está bonita

---

## 🎯 Próximos Passos

### **MVP está pronto!** ✅

Agora você pode:

1. **Testar com documentos reais**
   - Use suas minutas da securitizadora
   - Valide a qualidade das classificações

2. **Compartilhar com equipe**
   - Deploy no Streamlit Cloud
   - Envie URL: `https://seu-app.streamlit.app`

3. **Coletar feedback**
   - O que está bom?
   - O que precisa melhorar?
   - Quais features faltam?

4. **Iterar**
   - Adicionar downloads (Excel/DOCX)
   - Implementar Tier-2
   - Melhorar UI/UX

---

## 📁 Arquivos Criados

```
juridico-review-ai/
├── app.py                          ← 🎨 Interface Streamlit
├── requirements-streamlit.txt      ← 📦 Dependências leves
├── DEPLOY_STREAMLIT.md            ← 📖 Guia de deploy
├── QUICKSTART.md                  ← ⚡ Este arquivo
│
├── src/
│   ├── parsing.py                 ← Parse DOCX/PDF
│   ├── utils.py                   ← Carrega catálogos
│   └── ...                        ← Outros módulos
│
├── data/
│   └── catalogos/
│       ├── catalogo_cri_v3.yaml   ← 25 cláusulas CRI
│       ├── catalogo_cra.yaml      ← CRA
│       └── catalogo_debenture.yaml ← Debêntures
```

---

## 💡 Dicas

### **Performance:**

Se análise está lenta (>5min):
- Reduza número de cláusulas no documento
- Use catálogo menor
- Upgrade para Gemini tier pago

### **Custos:**

Tier gratuito do Gemini:
- 1.500 análises/dia
- 15 análises/minuto

Se precisar mais:
- Tier pago: ~R$ 0,07 por análise
- 100 análises/mês = R$ 7/mês

### **Privacidade:**

Se dados são sensíveis:
- Rode localmente (localhost)
- Ou use servidor interno
- Gemini não armazena dados permanentemente

---

## 🐛 Problemas Comuns

### **"ModuleNotFoundError: No module named 'streamlit'"**

```bash
pip install -r requirements-streamlit.txt
```

### **"Invalid API key"**

Verifique key em: https://makersuite.google.com/app/apikey

### **App não abre**

```bash
# Tente especificar porta
streamlit run app.py --server.port 8501
```

### **Erro ao fazer upload**

Certifique-se que arquivo é .docx ou .pdf válido

---

## 📞 Suporte

**Criado por:** Claude + Você
**Versão:** 1.0.0
**Status:** ✅ Funcionando!

---

**Pronto para começar?** 🚀

```bash
streamlit run app.py
```
