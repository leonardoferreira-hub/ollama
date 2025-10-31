# 📝 Como Adicionar Explicações ao Catálogo para Melhorar o Matching

## 🎯 Objetivo

Você solicitou uma forma de **explicar cada cláusula do catálogo** para dar mais contexto ao sistema de matching. Agora você pode fazer isso!

## ✨ Nova Funcionalidade

Uma nova aba **"📝 Editar Catálogo"** foi adicionada à interface onde você pode:
- Ver todas as cláusulas do catálogo selecionado
- Adicionar explicações detalhadas para cada cláusula
- Filtrar e buscar cláusulas específicas
- Salvar as alterações diretamente no arquivo YAML

## 🚀 Como Usar

### Passo 1: Acesse a Aba "Editar Catálogo"

1. Abra o aplicativo Streamlit
2. Clique na aba **"📝 Editar Catálogo"** (ao lado de "Análise de Documentos")

### Passo 2: Selecione o Catálogo

Na barra lateral, escolha o catálogo que deseja editar (ex: "Catálogo CRI - Com Destinação Específica")

### Passo 3: Adicione Explicações

Para cada cláusula que você quer melhorar o matching:

1. **Localize a cláusula** usando os filtros ou busca:
   - Filtrar por: Todas / Obrigatórias / Opcionais
   - Categoria: Todas / lastro / remuneração / etc.
   - Explicação: Todas / Com explicação / Sem explicação
   - Busca: Digite palavras-chave do título ou ID

2. **Clique no expander da cláusula** (marcado com ⚠️ se sem explicação ou ✅ se já tem)

3. **Adicione uma explicação detalhada** na caixa de texto, descrevendo:

   - **O que a cláusula deve conter** (elementos essenciais)
   - **Informações específicas** que devem aparecer
   - **Formato esperado** ou estrutura
   - **Exemplos concretos** do que procurar

### Passo 4: Salve as Alterações

1. Após adicionar/modificar explicações, role até o final
2. Clique no botão **"💾 Salvar Alterações"**
3. As alterações serão salvas no arquivo YAML do catálogo

## 💡 Exemplo de Boa Explicação

**Cláusula:** IDENTIFICAÇÃO DAS PARTES

**Explicação ruim** ❌:
```
As partes do contrato
```

**Explicação boa** ✅:
```
Esta cláusula deve conter a identificação completa de todas as partes envolvidas no contrato, incluindo:

- Nome/Razão Social completa de cada parte
- CNPJ ou CPF  
- Endereço completo (rua, número, cidade, estado, CEP)
- Representantes legais de cada pessoa jurídica
- Documentos de identificação dos representantes (RG, CPF)
- Qualificação de cada parte no contrato (Emissora, Devedora, Avalista, Securitizadora, etc.)

É essencial que TODAS as partes estejam claramente identificadas e qualificadas
para garantir a validade jurídica do documento.

Exemplo de estrutura esperada:
"TRAVESSIA SECURITIZADORA S.A., sociedade por ações, inscrita no CNPJ sob nº 
26.609.050/0001-64, com sede na Rua Tabapuã, 41, 13º andar, São Paulo - SP, 
neste ato representada por seu diretor..."
```

## 🎯 Como as Explicações Melhoram o Matching

As explicações são usadas de 3 formas:

### 1. **Matching Inteligente**
- O sistema extrai automaticamente palavras-chave importantes da explicação
- Essas keywords são usadas para calcular o score de similaridade
- Peso maior (4 pontos) para keywords contextuais da explicação

### 2. **Classificação Gemini**
- O prompt enviado para o Gemini inclui uma seção "EXPLICAÇÃO DETALHADA"
- A IA compara o documento com a explicação fornecida
- Classificação mais precisa (PRESENTE/PARCIAL/AUSENTE)

### 3. **Sugestões Melhores**
- Quando a cláusula está PARCIAL ou AUSENTE
- O Gemini gera sugestões baseadas na explicação
- Recomendações específicas do que está faltando

## 📊 Acompanhando o Progresso

Na tela de edição, você verá:
- **Barra de progresso**: quantas cláusulas já têm explicação
- **Marcadores visuais**: ✅ (com explicação) ou ⚠️ (sem explicação)
- **Contador**: "Progresso: X/Y cláusulas com explicação"

## 💾 Onde as Explicações São Salvas

As explicações são salvas diretamente no arquivo YAML do catálogo:

```yaml
- id: CRI_DEST_001
  titulo: DEFINIÇÕES
  categoria: definicoes
  importancia: critica
  obrigatoria: true
  keywords:
  - definições
  explicacao: |
    Esta cláusula deve conter todas as definições de termos...
    [sua explicação aqui]
```

## 🔄 Fluxo de Trabalho Recomendado

1. **Comece pelas cláusulas obrigatórias** (filtro: "Obrigatórias")
2. **Priorize cláusulas críticas** (categoria: lastro, remuneração, patrimônio)
3. **Use o documento GOLD** como referência para escrever as explicações
4. **Teste o matching** após adicionar explicações a 5-10 cláusulas
5. **Refine** as explicações baseado nos resultados

## 🎓 Dicas para Boas Explicações

✅ **Seja específico** - Não diga "informações das partes", diga "CNPJ, endereço completo, representantes"
✅ **Liste elementos** - Use bullets para listar o que deve aparecer
✅ **Dê exemplos** - Mostre trechos de texto esperados
✅ **Mencione obrigatoriedade** - "É essencial que...", "Deve conter..."
✅ **Inclua estrutura** - "Formato esperado:", "Sequência típica:"

❌ **Evite ser vago** - "Dados importantes" não ajuda
❌ **Evite repetir título** - A explicação deve COMPLEMENTAR, não repetir
❌ **Evite ser muito curto** - Menos de 50 caracteres é pouco contexto

## 🔍 Exemplo Prático

Suponha que o matching está confundindo "Seção Partes" com qualquer menção a "partes da emissão".

**Solução:**

1. Vá em "Editar Catálogo"
2. Busque pela cláusula "PARTES" ou "IDENTIFICAÇÃO DAS PARTES"
3. Adicione explicação detalhada:
   ```
   Esta seção deve identificar TODAS as pessoas físicas e jurídicas que são
   parte contratante do termo de securitização, incluindo:
   
   - Emissora (Securitizadora)
   - Devedora
   - Avalistas (se houver)
   - Agente Fiduciário
   
   Para cada parte deve constar:
   - Razão Social / Nome completo
   - CNPJ/CPF
   - Endereço completo
   - Representantes legais
   
   NÃO confundir com:
   - Partes da emissão (séries de CRI)
   - Partes do documento (seções)
   - Parcelas de pagamento
   ```
4. Salve
5. Teste novamente - o matching agora vai usar keywords como "securitizadora", 
   "devedora", "avalista", "representantes" para encontrar a seção correta

## 🎯 Resultados Esperados

Após adicionar explicações:
- ✅ **Matching mais preciso** - Menos falsos positivos
- ✅ **Scores mais confiáveis** - Diferencia melhor cláusulas similares
- ✅ **Classificações corretas** - Gemini entende o contexto completo
- ✅ **Sugestões úteis** - Recomendações específicas e acionáveis

## 🆘 Problemas?

Se após adicionar explicações o matching ainda não melhorar:

1. **Verifique se salvou** - Clique em "Salvar Alterações"
2. **Verifique o YAML** - Abra `data/catalogos/*.yaml` e confirme que campo `explicacao:` está preenchido
3. **Teste com cláusula simples** - Comece com uma cláusula óbvia (ex: DEFINIÇÕES)
4. **Veja os logs** - Analise o score de matching na aba "Resultados"

---

**📧 Dúvidas?** Entre em contato ou consulte a documentação adicional.
