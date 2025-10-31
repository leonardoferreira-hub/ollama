# 📚 Guia de Uso - Gerenciador de Sugestões de Cláusulas

## 🎯 O Que É?

Uma interface web interativa para **visualizar, editar e gerenciar as sugestões de explicação** das cláusulas dos documentos GOLD CRI.

## 🌐 Como Acessar

### URL do Gerenciador:
**https://8000-iv5967bfb3rkz50texc1u-cc2fbc16.sandbox.novita.ai/gerenciar_sugestoes.html**

### Método Alternativo (Local):
```bash
cd /home/user/webapp/documentos_gold
python3 servidor.py
# Acesse: http://localhost:8000/gerenciar_sugestoes.html
```

## 📖 Passo a Passo

### 1️⃣ Selecionar Documento
- Clique no dropdown **"📄 Documento"**
- Escolha entre:
  - **CRI com Destinação 2025** - 60 cláusulas
  - **CRI sem Destinação Padrão** - 44 cláusulas

### 2️⃣ Visualizar Cláusulas
Cada cláusula mostra:
- 📝 **Número da cláusula**
- 📋 **Título completo**
- 🏷️ **Tipo** (titulo/clausula)
- 💡 **Sugestão de explicação** (editável)
- ⚠️ **Pontos de atenção** detectados automaticamente
- 📄 **Preview do conteúdo** original

### 3️⃣ Editar Sugestões
1. Localize a cláusula que deseja editar
2. Clique no campo de texto **"💡 Sugestão de Explicação"**
3. Edite o texto conforme necessário
4. O campo ficará **verde** indicando que foi modificado
5. O contador de **"Cláusulas Editadas"** será atualizado

### 4️⃣ Buscar Cláusulas
Use a barra de busca para filtrar por:
- Número da cláusula (ex: "1.1")
- Título (ex: "Definições")
- Conteúdo da sugestão (ex: "obrigações")

### 5️⃣ Salvar Alterações
Clique no botão **"💾 Salvar Alterações"**:
- Salva no navegador (localStorage)
- Mantém suas edições entre sessões
- Mostra quantas cláusulas foram modificadas

### 6️⃣ Exportar JSON
Clique no botão **"📥 Exportar JSON"**:
- Baixa um arquivo JSON com todas as suas edições
- Nome do arquivo: `[DOCUMENTO]_editado.json`
- Pode ser usado para integração com sistemas

### 7️⃣ Resetar Alterações
Clique no botão **"🔄 Resetar"**:
- Volta ao estado original do documento
- Remove todas as edições não salvas
- Requer confirmação

## 📊 Estatísticas

Na parte superior, você vê:
- 📊 **Total de Cláusulas** do documento
- ✏️ **Cláusulas Editadas** por você
- 📝 **Documento Atual** selecionado

## 💡 Dicas de Uso

### Para Revisar Todas as Sugestões:
1. Selecione um documento
2. Role pela lista de cláusulas
3. Edite as sugestões que precisam de ajuste
4. Salve ao final

### Para Ajustar Cláusula Específica:
1. Use a busca para encontrar rapidamente
2. Edite a sugestão
3. Salve imediatamente

### Para Criar Padrão Personalizado:
1. Edite todas as sugestões conforme sua necessidade
2. Exporte o JSON
3. Use esse JSON como referência para a IA

## 🎨 Recursos Visuais

### Cores dos Campos:
- **Cinza** - Campo não editado
- **Verde** - Campo editado (não salvo)
- **Azul** - Destaque ao focar

### Ícones:
- 📄 Documento
- 🔍 Buscar
- 💾 Salvar
- 📥 Exportar
- 🔄 Resetar
- 💡 Sugestão
- ⚠️ Alerta
- 📊 Estatística

## 🔧 Funcionalidades Avançadas

### Edição em Lote:
1. Use a busca para filtrar grupo de cláusulas
2. Edite todas as filtradas
3. Salve em lote

### Comparação de Documentos:
1. Abra dois documentos em abas diferentes
2. Compare sugestões lado a lado
3. Padronize o estilo entre documentos

### Backup de Edições:
1. Faça edições
2. Clique em **"📥 Exportar JSON"**
3. Guarde o arquivo para backup
4. Pode reimportar depois se necessário

## 📝 Formato das Sugestões

### Estrutura Recomendada:

```
[Verbo de Ação] + [Objeto] + [Complemento/Contexto]

Exemplos:
✅ "Define as condições de vencimento antecipado dos CRI."
✅ "Estabelece as regras para convocação e realização de assembleias."
✅ "Lista as obrigações da emissora perante os titulares dos certificados."

❌ "Trata sobre assembleia"
❌ "Cláusula de vencimento"
```

### Elementos Importantes:
1. **Seja claro e objetivo** - 1-2 frases
2. **Use verbos precisos** - Define, Estabelece, Regula, Lista
3. **Adicione contexto** - Para que serve a cláusula
4. **Mencione partes envolvidas** - Emissora, Titulares, Agente

## 🤖 Para Uso com IA

Depois de editar as sugestões, você pode:

### 1. Criar Prompt Personalizado:
```
Use estas definições de cláusulas GOLD como referência:
[Cole o conteúdo do JSON exportado]

Ao analisar documentos CRI, compare cada cláusula com 
os padrões GOLD acima e identifique divergências.
```

### 2. Treinar Modelo:
- Use o JSON exportado como dataset
- Ensine a IA suas definições preferidas
- Melhore a consistência das análises

### 3. Validação Automática:
- Configure sistema para comparar com seu JSON
- Gere alertas quando divergir dos padrões
- Crie relatórios de conformidade

## 📞 Suporte

### Problemas Comuns:

**Documento não carrega?**
- Verifique se está no diretório correto
- Confirme que o arquivo JSON existe

**Edições não salvam?**
- Clique no botão "💾 Salvar Alterações"
- Verifique se o navegador permite localStorage

**Perdeu suas edições?**
- Sempre exporte o JSON antes de resetar
- Faça backups regulares das edições

### Arquivos Importantes:
```
documentos_gold/
├── gerenciar_sugestoes.html              # Interface web
├── GOLD_CRI_DESTINACAO_MODELO_2025_catalogo_completo.json
├── GOLD_CRI_SEM_DESTINACAO_PADRAO_catalogo_completo.json
└── servidor.py                           # Servidor HTTP
```

## ✨ Próximos Passos

Depois de editar as sugestões:

1. ✅ **Exporte o JSON** com suas definições
2. ✅ **Documente padrões** importantes
3. ✅ **Compartilhe com a equipe** jurídica
4. ✅ **Integre com IA** para análise automática
5. ✅ **Crie checklist** de completude documental

---

## 🎯 Resumo Rápido

| Ação | Botão/Campo |
|------|-------------|
| Escolher documento | Dropdown no topo |
| Buscar cláusula | Campo de busca |
| Editar sugestão | Textarea em cada card |
| Salvar no navegador | Botão "💾 Salvar" |
| Baixar JSON | Botão "📥 Exportar" |
| Voltar ao original | Botão "🔄 Resetar" |

---

**Data**: 2025-10-28  
**Versão**: 1.0  
**Status**: ✅ Operacional

**URL**: https://8000-iv5967bfb3rkz50texc1u-cc2fbc16.sandbox.novita.ai/gerenciar_sugestoes.html
