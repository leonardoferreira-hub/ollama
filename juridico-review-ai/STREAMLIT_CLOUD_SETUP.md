# Configuração Streamlit Cloud - Passo a Passo

## 1. Acesse o Streamlit Cloud

URL: https://share.streamlit.io/

Faça login com sua conta GitHub.

## 2. Criar Novo App

Clique em **"New app"** (botão azul no canto superior direito).

## 3. Configuração Principal

Você verá um formulário com os seguintes campos:

### Campo 1: Repository
```
Repository: seu-usuario/juridico-review-ai
```
- Selecione o repositório GitHub onde está o código
- Exemplo: `travessia/juridico-review-ai`

### Campo 2: Branch
```
Branch: main
```
- Use `main` ou o nome da branch que você quer deployar
- Geralmente é `main` ou `master`

### Campo 3: Main file path
```
Main file path: app.py
```
⚠️ **IMPORTANTE**: Digite exatamente `app.py` (não `app_streamlit.py`, não `app_old.py`)

## 4. Advanced Settings (Configurações Avançadas)

Clique em **"Advanced settings"** para expandir opções adicionais:

### Python Version
```
Python version: 3.11
```
- Selecione `3.11` no dropdown
- Compatível com todas as dependências

### Secrets (Opcional - Recomendado)

Se você quiser fixar a API Key do Gemini, adicione:

```toml
GEMINI_API_KEY = "sua-api-key-aqui"
```

**Como obter a API Key:**
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie uma nova API Key
3. Copie e cole no campo Secrets

**Nota**: Se não configurar, o usuário precisará inserir manualmente no sidebar do app.

## 5. Deploy

1. Clique no botão **"Deploy!"**
2. Aguarde o build (leva 2-5 minutos)
3. Você verá logs em tempo real do processo

## 6. Verificação de Sucesso

### Durante o Build

Você verá mensagens como:
```
Collecting dependencies...
Installing requirements...
Starting Streamlit...
```

### App Rodando

Quando finalizar com sucesso:
```
✓ App is live at: https://seu-app.streamlit.app
```

### No App (Sidebar)

Verifique se aparece:
```
CWD: /mount/src/juridico-review-ai
backend spec: /mount/src/juridico-review-ai/backend/__init__.py ✓
```

✅ Se `backend spec` mostrar um caminho → **SUCESSO!**
❌ Se mostrar `None` → Erro (veja troubleshooting abaixo)

## 7. Configurações Pós-Deploy

### Renomear App (Opcional)

1. Clique em **"Settings"** (engrenagem)
2. Vá em **"General"**
3. Altere o campo **"App name"**
4. Exemplo: `revisor-documentos-travessia`
5. Salve

### Configurar Secrets Depois

1. Clique em **"Settings"** (engrenagem)
2. Vá em **"Secrets"**
3. Adicione:
```toml
GEMINI_API_KEY = "sua-api-key-aqui"
```
4. Clique **"Save"**
5. O app reinicia automaticamente

### Atualizar o App

Sempre que você fizer `git push` para o repositório:
- Streamlit Cloud detecta automaticamente
- Faz rebuild do app
- Atualiza em ~2-3 minutos

## Screenshot da Configuração

```
┌─────────────────────────────────────────────┐
│  Deploy an app                              │
├─────────────────────────────────────────────┤
│                                             │
│  Repository *                               │
│  [seu-usuario/juridico-review-ai        ▼] │
│                                             │
│  Branch *                                   │
│  [main                                  ▼] │
│                                             │
│  Main file path *                           │
│  [app.py                                 ] │
│                                             │
│  [ Advanced settings ▼ ]                   │
│                                             │
│  Python version                             │
│  [3.11                                  ▼] │
│                                             │
│  Secrets                                    │
│  [GEMINI_API_KEY = "..."                 ] │
│                                             │
│                    [Deploy!]                │
└─────────────────────────────────────────────┘
```

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'backend'"

**Causa**: O diretório `backend/` não está no repositório ou falta `__init__.py`

**Solução**:
```bash
# Verifique localmente
ls backend/__init__.py

# Se não existir, crie
echo "" > backend/__init__.py

# Commit e push
git add backend/__init__.py
git commit -m "fix: adiciona __init__.py ao backend"
git push
```

### Erro: "source code string cannot contain null bytes"

**Causa**: App usando `app_broken.py` ao invés de `app.py` correto

**Solução**: Verifique que o campo "Main file path" está como `app.py`

### Erro: "No module named 'google.generativeai'"

**Causa**: Dependência faltando em `requirements.txt`

**Solução**: O app tem fallback, funciona sem Gemini. Para adicionar:
```bash
# Verifique requirements.txt
grep "google-generativeai" requirements.txt

# Se não tiver, adicione
echo "google-generativeai>=0.7.2" >> requirements.txt
git add requirements.txt
git commit -m "fix: adiciona google-generativeai ao requirements"
git push
```

### App Fica em "Starting..."

**Causa**: Erro durante inicialização (geralmente imports)

**Solução**: Clique em "Manage app" → "Logs" para ver detalhes do erro

### Secrets Não Funcionam

**Causa**: Formato incorreto no campo Secrets

**Solução**: Use formato TOML simples:
```toml
GEMINI_API_KEY = "AIza..."
```

NÃO use:
```python
# ❌ Errado
os.environ["GEMINI_API_KEY"] = "..."

# ❌ Errado
GEMINI_API_KEY: "..."

# ✅ Correto
GEMINI_API_KEY = "..."
```

## Checklist Final

Antes de fazer deploy, confirme:

- [ ] Arquivo `app.py` está commitado no repositório
- [ ] Arquivo `requirements.txt` está atualizado
- [ ] Diretório `backend/` está completo no repositório
- [ ] Arquivo `backend/__init__.py` existe
- [ ] Diretório `data/catalogos/` com os YAMLs está commitado
- [ ] `.streamlit/config.toml` está commitado (opcional, para tema)

```bash
# Verifique tudo de uma vez
git status
git add .
git commit -m "feat: deploy streamlit cloud pronto"
git push
```

## URLs Importantes

- **Streamlit Cloud Dashboard**: https://share.streamlit.io/
- **Obter Gemini API Key**: https://makersuite.google.com/app/apikey
- **Documentação Streamlit Deploy**: https://docs.streamlit.io/deploy/streamlit-community-cloud
- **Troubleshooting Oficial**: https://docs.streamlit.io/deploy/streamlit-community-cloud/troubleshooting

## Suporte

Se continuar com problemas:

1. Clique em "Manage app" no dashboard
2. Vá em "Logs" para ver erros detalhados
3. Clique em "Reboot app" para reiniciar
4. Se necessário, delete o app e crie novamente com as configurações corretas

---

**Última atualização**: 2025-11-05
**Versão do app**: 1.0.0 (RAG + Gold Standard)
