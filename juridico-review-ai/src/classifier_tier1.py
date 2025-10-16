"""
Classificador Tier-1: LLM local (Ollama) para classificação rápida
Retorna: PRESENTE | PARCIAL | AUSENTE + evidências
"""

from typing import Dict, List
import json
import ollama
import logging

logger = logging.getLogger(__name__)


class Tier1Classifier:
    """Classificador Tier-1 usando LLM local"""

    def __init__(self, model: str = 'qwen2:7b-instruct'):
        """
        Inicializa classificador

        Args:
            model: Modelo Ollama a usar
        """
        self.model = model

    def build_classification_prompt(self,
                                     clause_title: str,
                                     clause_content: str,
                                     catalog_clause: Dict) -> str:
        """
        Constrói prompt para classificação

        Args:
            clause_title: Título da cláusula do documento
            clause_content: Conteúdo da cláusula
            catalog_clause: Cláusula de referência do catálogo

        Returns:
            Prompt formatado
        """
        prompt = f"""Você é um assistente especializado em revisão de minutas jurídicas.

SUA TAREFA: Classificar se uma cláusula específica está PRESENTE, PARCIAL ou AUSENTE em um documento.

CLÁUSULA ESPERADA (do catálogo de referência):
ID: {catalog_clause.get('id')}
Título: {catalog_clause.get('titulo')}
Categoria: {catalog_clause.get('categoria')}
Importância: {catalog_clause.get('importancia')}
Obrigatória: {'Sim' if catalog_clause.get('obrigatoria') else 'Não'}

Elementos que devem estar presentes:
{self._format_validation_criteria(catalog_clause)}

Keywords esperadas: {', '.join(catalog_clause.get('keywords', []))}

---

CLÁUSULA DO DOCUMENTO (a ser analisada):
Título: {clause_title}

Conteúdo:
{clause_content[:1500]}{'...' if len(clause_content) > 1500 else ''}

---

INSTRUÇÕES:
Analise se a cláusula do documento contém os elementos essenciais esperados.

Classifique como:
- PRESENTE: A cláusula contém TODOS os elementos essenciais esperados
- PARCIAL: A cláusula existe mas falta algum elemento importante OU está incompleta
- AUSENTE: A cláusula NÃO trata do tema esperado OU está completamente ausente

IMPORTANTE: Responda APENAS com um JSON válido no seguinte formato:

{{
  "classificacao": "PRESENTE" | "PARCIAL" | "AUSENTE",
  "confianca": 0.0-1.0,
  "evidencias": ["evidência 1", "evidência 2", ...],
  "elementos_faltantes": ["elemento 1", "elemento 2", ...],
  "justificativa": "explicação breve"
}}

Responda apenas o JSON, sem texto adicional antes ou depois.
"""
        return prompt

    def _format_validation_criteria(self, catalog_clause: Dict) -> str:
        """Formata critérios de validação"""
        criteria = catalog_clause.get('criterios_validacao', [])
        if not criteria:
            return "Não especificado"

        lines = []
        for i, criterion in enumerate(criteria, 1):
            lines.append(f"{i}. {criterion.get('campo')}: {criterion.get('regra')}")

        return '\n'.join(lines)

    def classify(self,
                 clause_title: str,
                 clause_content: str,
                 catalog_clause: Dict) -> Dict:
        """
        Classifica uma cláusula

        Args:
            clause_title: Título da cláusula
            clause_content: Conteúdo da cláusula
            catalog_clause: Cláusula de referência

        Returns:
            Dicionário com classificação
        """
        prompt = self.build_classification_prompt(
            clause_title,
            clause_content,
            catalog_clause
        )

        try:
            # Chama Ollama
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.1,  # Baixa temperatura para classificação
                    'num_predict': 500
                }
            )

            response_text = response['message']['content'].strip()

            # Tenta extrair JSON
            result = self._parse_json_response(response_text)

            # Valida classificação
            if result.get('classificacao') not in ['PRESENTE', 'PARCIAL', 'AUSENTE']:
                logger.warning(f"Classificação inválida: {result.get('classificacao')}")
                result['classificacao'] = 'PARCIAL'  # Fallback seguro

            # Adiciona metadados
            result['catalog_id'] = catalog_clause.get('id')
            result['catalog_titulo'] = catalog_clause.get('titulo')
            result['obrigatoria'] = catalog_clause.get('obrigatoria', False)
            result['model'] = self.model

            return result

        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            # Fallback em caso de erro
            return {
                'classificacao': 'PARCIAL',
                'confianca': 0.0,
                'evidencias': [],
                'elementos_faltantes': ['Erro na análise'],
                'justificativa': f'Erro ao processar: {str(e)}',
                'catalog_id': catalog_clause.get('id'),
                'catalog_titulo': catalog_clause.get('titulo'),
                'obrigatoria': catalog_clause.get('obrigatoria', False),
                'error': True
            }

    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Extrai e parseia JSON da resposta

        Args:
            response_text: Texto da resposta do LLM

        Returns:
            Dict parseado
        """
        # Tenta encontrar JSON na resposta
        # Remove markdown code blocks se existirem
        text = response_text.strip()

        # Remove ```json e ```
        if text.startswith('```'):
            lines = text.split('\n')
            # Remove primeira e última linha
            text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text

        # Tenta parsear
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Tenta encontrar JSON dentro do texto
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("Não foi possível extrair JSON da resposta")


def classify_document_matches(ranked_matches: List[Dict],
                               model: str = 'qwen2:7b-instruct') -> List[Dict]:
    """
    Classifica todos os matches do documento

    Args:
        ranked_matches: Resultado do ranker (cláusulas com matches)
        model: Modelo Ollama

    Returns:
        Lista de cláusulas com classificações
    """
    classifier = Tier1Classifier(model)
    results = []

    for item in ranked_matches:
        clause = item['clause']
        matches = item['matches']

        # Classifica contra o melhor match (mais relevante)
        if matches:
            best_match = matches[0]
            catalog_clause = best_match['catalog_clause']

            classification = classifier.classify(
                clause_title=clause['title'],
                clause_content=clause['content'],
                catalog_clause=catalog_clause
            )

            # Adiciona informações do match
            classification['match_score'] = best_match['combined_score']
            classification['scores_breakdown'] = best_match.get('scores_breakdown', {})

            results.append({
                'clause': clause,
                'classification': classification,
                'all_matches': matches  # Mantém todos os matches para referência
            })
        else:
            # Sem matches - marca como AUSENTE
            results.append({
                'clause': clause,
                'classification': {
                    'classificacao': 'AUSENTE',
                    'confianca': 0.0,
                    'evidencias': [],
                    'elementos_faltantes': ['Nenhuma correspondência encontrada no catálogo'],
                    'justificativa': 'Cláusula não identificada no catálogo de referência',
                    'no_match': True
                },
                'all_matches': []
            })

    return results
