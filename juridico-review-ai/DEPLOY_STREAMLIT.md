# 🚀 Deploy no Streamlit Cloud

## ✅ Pré-requisitos

1. **Conta GitHub** (gratuita)
2. **Conta Streamlit Cloud** (gratuita)
3. **Gemini API Key** (gratuita)

---

## 📝 Passo a Passo

### 1️⃣ **Preparar Repositório GitHub**

```bash
# Se ainda não fez, inicializa git
cd juridico-review-ai
git init
git add .
git commit -m "feat: adiciona interface Streamlit + Gemini"

# Cria repo no GitHub e faz push
git remote add origin https://github.com/SEU-USER/juridico-review-ai.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ **Criar Conta Streamlit Cloud**

1. Acesse: https://streamlit.io/cloud
2. Clique em "Sign up" (use conta GitHub)
3. Autorize Streamlit a acessar seus repos

---

### 3️⃣ **Deploy do App**

1. **No Streamlit Cloud, clique em "New app"**

2. **Preencha:**
   ```
   Repository: seu-user/juridico-review-ai
   Branch: main
   Main file path: app.py
   ```

3. **Clique em "Advanced settings"**

4. **Adicione variável de ambiente (opcional):**
   ```
   GEMINI_API_KEY = sua-chave-aqui
   ```
   *(Nota: Usuários podem inserir própria key na interface)*

5. **Em "Python version":**
   ```
   3.11
   ```

6. **Em "Requirements file":**
   ```
   requirements-streamlit.txt
   ```

7. **Clique em "Deploy!"**

---

### 4️⃣ **Aguardar Deploy**

```
⏱️ Tempo estimado: 3-5 minutos

Você verá:
├─ Installing dependencies... ⏳
├─ Building app... ⏳
└─ App is live! ✅
```

---

### 5️⃣ **Acessar App**

Sua URL será algo como:
```
https://juridico-review-ai-xxxxx.streamlit.app
```

**Compartilhe com sua equipe!** 🎉

---

## 🔑 Obter Gemini API Key

### **Para você (Administrador):**

1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave
4. Pode adicionar nas configurações do Streamlit OU
5. Cada usuário insere a própria key na interface

### **Para sua equipe (Usuários):**

Cada pessoa pode:
1. Criar própria conta Google (grátis)
2. Obter própria API Key (grátis)
3. Inserir na barra lateral do app

**Ou** você cria UMA key compartilhada e configura no Streamlit Cloud.

---

## ⚙️ Configurações Avançadas

### **Variáveis de Ambiente**

No Streamlit Cloud, você pode adicionar:

```
GEMINI_API_KEY = sk-...  # Key compartilhada
MAX_FILE_SIZE = 200      # Tamanho máximo MB
DEFAULT_CATALOG = catalogo_cri_v3  # Catálogo padrão
```

### **Atualizar App**

```bash
# Faça mudanças localmente
git add .
git commit -m "feat: melhoria X"
git push

# Streamlit Cloud atualiza AUTOMATICAMENTE! 🎉
```

### **Logs e Monitoramento**

No dashboard do Streamlit Cloud você vê:
- ✅ Status do app
- 📊 Métricas de uso
- 📝 Logs em tempo real
- ⚠️ Erros

---

## 💰 Custos

### **Streamlit Cloud:**
```
✅ GRÁTIS para apps públicos
✅ 1GB RAM
✅ 1 CPU
✅ Apps ilimitados
```

### **Gemini API (Tier Gratuito):**
```
✅ 1.500 requests/dia
✅ 15 requests/minuto
✅ Gemini 1.5 Flash

Análise de 1 minuta = ~1 request
Limite diário: ~1.500 análises
```

### **Gemini API (Tier Pago) - Se precisar:**
```
💰 $0.35 por 1M tokens de entrada
💰 $1.05 por 1M tokens de saída

Custo por análise: ~$0.014 (R$ 0,07)
100 análises/mês: ~R$ 7,00/mês
```

---

## 🔒 Privacidade

### **O que vai para nuvem:**

```
Streamlit Cloud:
├─ Código do app (público no GitHub)
├─ Arquivo .docx (temporário, deletado após análise)
└─ Processamento do PDF/DOCX

Gemini API:
├─ Texto das cláusulas (para análise)
└─ NÃO armazena dados permanentemente
```

### **Se privacidade é crítica:**

**Opção 1:** Servidor interno
```bash
# Na rede da empresa
streamlit run app.py --server.port 8501

# Equipe acessa: http://servidor-interno:8501
```

**Opção 2:** Gemini Enterprise (contato Google)
- Dados ficam on-premises
- Custo negociado

---

## 🐛 Troubleshooting

### **Erro: "ModuleNotFoundError"**
```
Solução: Adicione o módulo em requirements-streamlit.txt
```

### **Erro: "API Key inválida"**
```
Solução: Verifique a chave em https://makersuite.google.com
```

### **App muito lento**
```
Possíveis causas:
- Arquivo muito grande (>50MB)
- Muitas cláusulas (>50)
- Tier gratuito com limite

Solução: Use servidor próprio ou tier pago
```

### **Erro 429: "Too Many Requests"**
```
Causa: Atingiu limite do Gemini (1500/dia ou 15/min)
Solução: Aguarde ou upgrade para tier pago
```

---

## 📊 Monitoramento de Uso

### **Dashboard Streamlit:**
```
https://share.streamlit.io/

Ver:
- Quantas pessoas acessaram
- Quando o app foi usado
- Logs de erro
```

### **Dashboard Gemini:**
```
https://console.cloud.google.com/apis/

Ver:
- Requests consumidos
- Quota restante
- Custos (se tier pago)
```

---

## 🎯 Próximos Passos

### **Após deploy bem-sucedido:**

1. ✅ **Teste com documento real**
2. ✅ **Compartilhe URL com 2-3 colegas**
3. ✅ **Colete feedback**
4. ✅ **Itere e melhore**

### **Melhorias futuras:**

- [ ] Adicionar geração de Excel/DOCX
- [ ] Implementar Tier-2 com sugestões
- [ ] Adicionar histórico de análises
- [ ] Dashboard com estatísticas
- [ ] Autenticação de usuários
- [ ] Dark mode
- [ ] Logo da empresa

---

## 📞 Suporte

**Problemas com Streamlit:**
- Docs: https://docs.streamlit.io
- Forum: https://discuss.streamlit.io

**Problemas com Gemini:**
- Docs: https://ai.google.dev/docs
- Forum: https://discuss.ai.google.dev

---

**Versão:** 1.0.0
**Data:** 2025-10-16
**Status:** Pronto para deploy! 🚀
