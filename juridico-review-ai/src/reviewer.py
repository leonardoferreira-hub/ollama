"""
Módulo para revisão de cláusulas usando LLMs (Ollama + frontier models)
"""

from typing import List, Dict, Optional
import ollama
from openai import OpenAI
from anthropic import Anthropic


class LLMReviewer:
    """Revisor de cláusulas usando LLMs"""

    def __init__(self, model: str = 'qwen2:7b-instruct', provider: str = 'ollama'):
        """
        Inicializa o revisor

        Args:
            model: Nome do modelo
            provider: 'ollama', 'openai', ou 'anthropic'
        """
        self.model = model
        self.provider = provider

        if provider == 'openai':
            self.client = OpenAI()
        elif provider == 'anthropic':
            self.client = Anthropic()
        elif provider == 'ollama':
            self.client = ollama

    def build_prompt(self,
                     clause: Dict,
                     reference_clauses: List[Dict]) -> str:
        """
        Constrói prompt para revisão

        Args:
            clause: Cláusula do documento
            reference_clauses: Cláusulas de referência do catálogo

        Returns:
            Prompt formatado
        """
        prompt = f"""Você é um especialista em revisão de documentos jurídicos.

CLÁUSULA A SER REVISADA:
{clause['title']}

{clause['content']}

CLÁUSULAS DE REFERÊNCIA (catálogo):
"""

        for i, ref in enumerate(reference_clauses, 1):
            catalog_clause = ref['catalog_clause']
            score = ref['combined_score']
            prompt += f"\n{i}. {catalog_clause['title']} (similaridade: {score:.2%})\n"
            prompt += f"   Importância: {catalog_clause['importance']}\n"
            prompt += f"   {catalog_clause['content'][:200]}...\n"

        prompt += """
TAREFA:
Analise a cláusula fornecida e:

1. CONFORMIDADE: A cláusula está adequada comparada às referências? (Sim/Não/Parcial)

2. PONTOS FORTES: O que está bem redigido?

3. PONTOS DE ATENÇÃO: O que precisa ser melhorado ou está faltando?

4. SUGESTÕES ESPECÍFICAS: Forneça recomendações objetivas e práticas.

5. PRIORIDADE: Qual a urgência da revisão? (Alta/Média/Baixa)

Seja objetivo e técnico. Foque em aspectos práticos e jurídicos.
"""

        return prompt

    def review_with_ollama(self, prompt: str) -> str:
        """Revisão usando Ollama"""
        response = ollama.chat(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        return response['message']['content']

    def review_with_openai(self, prompt: str) -> str:
        """Revisão usando OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            temperature=0.3
        )
        return response.choices[0].message.content

    def review_with_anthropic(self, prompt: str) -> str:
        """Revisão usando Claude"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        return response.content[0].text

    def review_clause(self,
                      clause: Dict,
                      reference_clauses: List[Dict]) -> Dict:
        """
        Revisa uma cláusula

        Args:
            clause: Cláusula a revisar
            reference_clauses: Top matches do catálogo

        Returns:
            Dicionário com análise
        """
        prompt = self.build_prompt(clause, reference_clauses)

        # Chama LLM apropriado
        if self.provider == 'ollama':
            review = self.review_with_ollama(prompt)
        elif self.provider == 'openai':
            review = self.review_with_openai(prompt)
        elif self.provider == 'anthropic':
            review = self.review_with_anthropic(prompt)
        else:
            raise ValueError(f"Provider desconhecido: {self.provider}")

        return {
            'clause': clause,
            'review': review,
            'references': reference_clauses,
            'model': self.model,
            'provider': self.provider
        }


def review_document(ranked_clauses: List[Dict],
                    catalog: Dict,
                    model: str = 'qwen2:7b-instruct',
                    provider: str = 'ollama') -> List[Dict]:
    """
    Revisa todas as cláusulas do documento

    Args:
        ranked_clauses: Cláusulas com rankings
        catalog: Catálogo completo
        model: Modelo LLM
        provider: Provider LLM

    Returns:
        Lista de revisões
    """
    reviewer = LLMReviewer(model, provider)
    results = []

    for item in ranked_clauses:
        clause = item['clause']
        matches = item['matches']

        review = reviewer.review_clause(clause, matches)
        results.append(review)

    return results
