"""
Gerador Tier-2: Frontier models para gerar sugestões de cláusulas
Suporta: Ollama (local), OpenAI, Anthropic (Claude)
"""

from typing import Dict, List, Optional
import json
import logging
import os
import requests
import ollama
from openai import OpenAI
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class Tier2Generator:
    """Gerador Tier-2 usando frontier models"""

    def __init__(self,
                 provider: str = 'ollama',
                 model: str = 'qwen2:7b-instruct'):
        """
        Inicializa gerador

        Args:
            provider: 'ollama', 'openai', ou 'anthropic'
            model: Nome do modelo
        """
        self.provider = provider
        self.model = model

        # Initialize provider client or API key handling
        if provider == 'openai':
            self.client = OpenAI()
        elif provider == 'anthropic':
            self.client = Anthropic()
        elif provider == 'ollama':
            self.client = ollama
        elif provider == 'gemini':
            # Gemini / Google Generative API will use REST calls with an API key
            # Expect API key in env var GEMINI_API_KEY or GOOGLE_API_KEY
            self.client = None
            self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                raise ValueError("GEMINI API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        else:
            raise ValueError(f"Provider desconhecido: {provider}")

    def build_generation_prompt(self,
                                 classification: Dict,
                                 clause: Dict,
                                 catalog_clause: Dict) -> str:
        """
        Constrói prompt para geração de sugestão

        Args:
            classification: Resultado do Tier-1
            clause: Cláusula original do documento
            catalog_clause: Cláusula de referência

        Returns:
            Prompt formatado
        """
        status = classification.get('classificacao')
        elementos_faltantes = classification.get('elementos_faltantes', [])

        prompt = f"""Você é um especialista em redação de documentos jurídicos para securitização.

CONTEXTO:
Uma minuta de {catalog_clause.get('categoria', 'documento')} está sendo revisada.
A cláusula "{catalog_clause.get('titulo')}" foi classificada como: {status}

"""

        # Informações da cláusula original (se existe)
        if status != 'AUSENTE':
            prompt += f"""CLÁUSULA ATUAL NO DOCUMENTO:
Título: {clause.get('title')}
Conteúdo:
{clause.get('content', '')[:1000]}{'...' if len(clause.get('content', '')) > 1000 else ''}

PROBLEMAS IDENTIFICADOS:
{chr(10).join('- ' + e for e in elementos_faltantes)}

"""

        # Template de referência
        prompt += f"""TEMPLATE DE REFERÊNCIA (catálogo):
{catalog_clause.get('template', '')}

VARIÁVEIS DO TEMPLATE:
"""
        for var in catalog_clause.get('variaveis', []):
            prompt += f"- {var['nome']} ({var['tipo']})"
            if var.get('obrigatoria'):
                prompt += " [OBRIGATÓRIA]"
            if var.get('exemplo'):
                prompt += f" Ex: {var['exemplo']}"
            prompt += "\n"

        prompt += f"""
CRITÉRIOS DE VALIDAÇÃO:
"""
        for crit in catalog_clause.get('criterios_validacao', []):
            prompt += f"- {crit['campo']}: {crit['regra']}\n"

        # Tarefa específica baseada no status
        if status == 'AUSENTE':
            prompt += """
TAREFA:
Gerar uma cláusula completa com base no template de referência.
"""
        elif status == 'PARCIAL':
            prompt += """
TAREFA:
Sugerir correções e adições para completar a cláusula existente.
"""

        prompt += """
FORMATO DE RESPOSTA:
Responda APENAS com um JSON válido no seguinte formato:

{
  "sugestao_tipo": "NOVA_CLAUSULA" | "CORRECAO" | "ADICAO",
  "texto_sugerido": "texto completo da cláusula sugerida",
  "variaveis_identificadas": {
    "nome_variavel": "valor identificado ou [A COMPLETAR]"
  },
  "explicacao": "breve explicação das mudanças/adições",
  "itens_checklist": [
    "item 1 a verificar",
    "item 2 a verificar"
  ],
  "nivel_prioridade": "ALTA" | "MEDIA" | "BAIXA",
  "conformidade_estimada": 0.0-1.0
}

Responda apenas o JSON, sem markdown ou texto adicional.
"""

        return prompt

    def generate_suggestion(self,
                           classification: Dict,
                           clause: Dict,
                           catalog_clause: Dict) -> Dict:
        """
        Gera sugestão usando frontier model

        Args:
            classification: Resultado Tier-1
            clause: Cláusula original
            catalog_clause: Cláusula de referência

        Returns:
            Dicionário com sugestão
        """
        prompt = self.build_generation_prompt(
            classification,
            clause,
            catalog_clause
        )

        try:
            if self.provider == 'ollama':
                response_text = self._generate_ollama(prompt)
            elif self.provider == 'openai':
                response_text = self._generate_openai(prompt)
            elif self.provider == 'anthropic':
                response_text = self._generate_anthropic(prompt)
            elif self.provider == 'gemini':
                response_text = self._generate_gemini(prompt)

            # Parse JSON
            suggestion = self._parse_json_response(response_text)

            # Adiciona metadados
            suggestion['catalog_id'] = catalog_clause.get('id')
            suggestion['catalog_titulo'] = catalog_clause.get('titulo')
            suggestion['status_original'] = classification.get('classificacao')
            suggestion['provider'] = self.provider
            suggestion['model'] = self.model

            return suggestion

        except Exception as e:
            logger.error(f"Erro na geração Tier-2: {e}")
            # Fallback
            return {
                'sugestao_tipo': 'ERRO',
                'texto_sugerido': f'[ERRO: {str(e)}]',
                'explicacao': 'Erro ao gerar sugestão',
                'error': True,
                'catalog_id': catalog_clause.get('id')
            }

    def _generate_ollama(self, prompt: str) -> str:
        """Geração via Ollama"""
        response = ollama.chat(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            options={
                'temperature': 0.3,
                'num_predict': 2000
            }
        )
        return response['message']['content']

    def _generate_openai(self, prompt: str) -> str:
        """Geração via OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str) -> str:
        """Geração via Claude"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.3,
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        return response.content[0].text

    def _generate_gemini(self, prompt: str) -> str:
        """Geração via Google Generative API (Gemini/text-bison compatible)

        Uses REST endpoint and API key from env var. This implementation is
        conservative in parsing to support small API changes.
        """
        # Map common model names to API model ids if needed
        model_name = self.model or 'text-bison-001'

        # Construct URL (v1beta2 generateText endpoint)
        url = f"https://generativelanguage.googleapis.com/v1beta2/models/{model_name}:generateText"

        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        payload = {
            'prompt': {
                'text': prompt
            },
            # Guidance parameters - keep responses short and deterministic
            'temperature': 0.3,
            'maxOutputTokens': 2000
        }

        params = {
            'key': self.api_key
        }

        resp = requests.post(url, headers=headers, params=params, json=payload, timeout=60)
        if resp.status_code != 200:
            raise ValueError(f"Gemini API error: {resp.status_code} {resp.text}")

        data = resp.json()

        # Try several common fields to extract text
        text = None
        if isinstance(data, dict):
            # v1beta2 typically returns 'candidates' with 'output' or 'content'
            if 'candidates' in data and isinstance(data['candidates'], list) and data['candidates']:
                first = data['candidates'][0]
                # candidate may have 'output' or 'content' or 'text'
                for key in ('output', 'content', 'text'):
                    if key in first:
                        text = first[key]
                        break
            # Some responses embed text in 'output' at top level
            if not text and 'output' in data and isinstance(data['output'], str):
                text = data['output']

        if not text:
            # Fallback: try to stringify whole response (best-effort)
            text = json.dumps(data)

        return text

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON da resposta"""
        text = response_text.strip()

        # Remove markdown
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text

        # Parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Tenta extrair JSON
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("Não foi possível extrair JSON da resposta")


def generate_tier2_suggestions(needs_tier2: List[Dict],
                                provider: str = 'ollama',
                                model: str = 'qwen2:7b-instruct') -> List[Dict]:
    """
    Gera sugestões Tier-2 para todas as cláusulas que precisam

    Args:
        needs_tier2: Lista de cláusulas que precisam Tier-2
        provider: Provider do LLM
        model: Modelo a usar

    Returns:
        Lista com sugestões
    """
    generator = Tier2Generator(provider, model)
    results = []

    for item in needs_tier2:
        clause = item['clause']
        classification = item['classification']
        all_matches = item.get('all_matches', [])

        if all_matches:
            catalog_clause = all_matches[0]['catalog_clause']
        else:
            # Sem match - skip (já foi marcado como problema)
            results.append({
                'clause': clause,
                'classification': classification,
                'suggestion': None,
                'skipped': True,
                'reason': 'Sem correspondência no catálogo'
            })
            continue

        logger.info(f"Gerando sugestão Tier-2 para: {clause['title']}")

        suggestion = generator.generate_suggestion(
            classification,
            clause,
            catalog_clause
        )

        results.append({
            'clause': clause,
            'classification': classification,
            'suggestion': suggestion,
            'catalog_clause': catalog_clause
        })

    return results
