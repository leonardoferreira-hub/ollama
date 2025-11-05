"""
Classificador Tier-1 OTIMIZADO: Mais rápido e eficiente
- Prompts mais curtos (reduz tokens)
- Streaming desabilitado para performance
- Cache de resultados
"""

from typing import Dict, List
import json
import ollama
import logging

logger = logging.getLogger(__name__)


class Tier1ClassifierOptimized:
    """Classificador Tier-1 otimizado para performance"""

    def __init__(self, model: str = 'qwen2:7b-instruct'):
        self.model = model
        self.cache = {}  # Cache de classificações

    def build_classification_prompt(self,
                                     clause_title: str,
                                     clause_content: str,
                                     catalog_clause: Dict) -> str:
        """
        Prompt OTIMIZADO - Mais curto e direto
        """
        # Trunca conteúdo para 800 caracteres
        content_preview = clause_content[:800]

        # Keywords esperadas (top 5 apenas)
        keywords = ', '.join(catalog_clause.get('keywords', [])[:5])

        prompt = f"""Classifique se a cláusula está PRESENTE, PARCIAL ou AUSENTE.

ESPERADO: {catalog_clause.get('titulo')}
Keywords: {keywords}
Obrigatória: {'SIM' if catalog_clause.get('obrigatoria') else 'NÃO'}

DOCUMENTO:
Título: {clause_title}
Texto: {content_preview}...

RESPONDA APENAS COM JSON:
{{
  "classificacao": "PRESENTE|PARCIAL|AUSENTE",
  "confianca": 0.0-1.0,
  "justificativa": "breve explicação"
}}

Critérios:
- PRESENTE: contém TODOS elementos essenciais
- PARCIAL: existe mas incompleto
- AUSENTE: não trata do tema OU completamente inadequado"""

        return prompt

    def classify(self,
                 clause_title: str,
                 clause_content: str,
                 catalog_clause: Dict) -> Dict:
        """
        Classifica com cache e otimizações
        """
        # Cache key
        cache_key = f"{catalog_clause.get('id')}_{hash(clause_title)}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit: {cache_key}")
            return self.cache[cache_key]

        prompt = self.build_classification_prompt(
            clause_title,
            clause_content,
            catalog_clause
        )

        try:
            # Ollama com opções otimizadas
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.1,
                    'num_predict': 200,  # Reduzido de 500 para 200
                    'num_ctx': 2048,  # Contexto reduzido
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                },
                stream=False  # Desabilita streaming
            )

            response_text = response['message']['content'].strip()
            result = self._parse_json_response(response_text)

            # Valida e completa resultado
            if result.get('classificacao') not in ['PRESENTE', 'PARCIAL', 'AUSENTE']:
                result['classificacao'] = 'PARCIAL'

            if 'confianca' not in result:
                result['confianca'] = 0.5

            if 'justificativa' not in result:
                result['justificativa'] = 'Classificação automática'

            # Adiciona metadados
            result['catalog_id'] = catalog_clause.get('id')
            result['catalog_titulo'] = catalog_clause.get('titulo')
            result['obrigatoria'] = catalog_clause.get('obrigatoria', False)
            result['model'] = self.model

            # Cache
            self.cache[cache_key] = result

            return result

        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            return {
                'classificacao': 'PARCIAL',
                'confianca': 0.0,
                'justificativa': f'Erro: {str(e)[:100]}',
                'catalog_id': catalog_clause.get('id'),
                'catalog_titulo': catalog_clause.get('titulo'),
                'obrigatoria': catalog_clause.get('obrigatoria', False),
                'error': True
            }

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON com fallbacks"""
        text = response_text.strip()

        # Remove markdown
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text
            text = text.replace('```json', '').replace('```', '')

        # Tenta parsear
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Busca JSON no texto
            import re
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass

            # Fallback: extrai manualmente
            return self._extract_manual(text)

    def _extract_manual(self, text: str) -> Dict:
        """Extração manual quando JSON falha"""
        import re

        result = {
            'classificacao': 'PARCIAL',
            'confianca': 0.5,
            'justificativa': 'Resposta não estruturada'
        }

        # Tenta extrair classificação
        if re.search(r'PRESENTE', text, re.IGNORECASE):
            result['classificacao'] = 'PRESENTE'
            result['confianca'] = 0.7
        elif re.search(r'AUSENTE', text, re.IGNORECASE):
            result['classificacao'] = 'AUSENTE'
            result['confianca'] = 0.7
        elif re.search(r'PARCIAL', text, re.IGNORECASE):
            result['classificacao'] = 'PARCIAL'
            result['confianca'] = 0.6

        return result


def classify_document_matches_optimized(ranked_matches: List[Dict],
                                        model: str = 'qwen2:7b-instruct') -> List[Dict]:
    """
    Versão otimizada da classificação
    """
    classifier = Tier1ClassifierOptimized(model)
    results = []

    logger.info(f"Iniciando classificação de {len(ranked_matches)} cláusulas...")

    for i, item in enumerate(ranked_matches, 1):
        clause = item['clause']
        matches = item['matches']

        logger.info(f"[{i}/{len(ranked_matches)}] Classificando: {clause['title'][:60]}...")

        if matches:
            best_match = matches[0]
            catalog_clause = best_match['catalog_clause']

            classification = classifier.classify(
                clause_title=clause['title'],
                clause_content=clause['content'],
                catalog_clause=catalog_clause
            )

            classification['match_score'] = best_match['combined_score']
            classification['scores_breakdown'] = best_match.get('scores_breakdown', {})

            results.append({
                'clause': clause,
                'classification': classification,
                'all_matches': matches
            })
        else:
            results.append({
                'clause': clause,
                'classification': {
                    'classificacao': 'AUSENTE',
                    'confianca': 0.0,
                    'justificativa': 'Sem correspondência no catálogo',
                    'no_match': True
                },
                'all_matches': []
            })

    logger.info(f"Classificação concluída. Cache hits: {len(classifier.cache)}")

    return results
