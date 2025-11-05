"""
Módulo para ranking de cláusulas usando fuzzy matching, embeddings e MMR
"""

from typing import List, Dict, Tuple
import numpy as np
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class ClauseRanker:
    """Rankeador de cláusulas usando múltiplas estratégias"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Inicializa o rankeador

        Args:
            model_name: Nome do modelo de embeddings
        """
        self.embedding_model = SentenceTransformer(model_name)
        self.catalog_embeddings = None
        self.catalog_clauses = None

    def encode_catalog(self, catalog: Dict):
        """
        Cria embeddings para todas as cláusulas do catálogo

        Args:
            catalog: Dicionário com cláusulas de referência
        """
        self.catalog_clauses = []

        # Extrai todas as cláusulas
        for category, clauses in catalog.get('clausulas', {}).items():
            for clause in clauses:
                self.catalog_clauses.append({
                    'category': category,
                    'title': clause.get('titulo', ''),
                    'content': clause.get('conteudo', ''),
                    'importance': clause.get('importancia', 'media'),
                    'keywords': clause.get('keywords', [])
                })

        # Gera embeddings
        texts = [f"{c['title']} {c['content']}" for c in self.catalog_clauses]
        self.catalog_embeddings = self.embedding_model.encode(texts)

    def fuzzy_match(self, query: str, candidates: List[str]) -> List[float]:
        """
        Fuzzy matching entre query e candidatos

        Returns:
            Lista de scores (0-100)
        """
        return [fuzz.token_sort_ratio(query, candidate) for candidate in candidates]

    def semantic_match(self, query: str) -> np.ndarray:
        """
        Matching semântico usando embeddings

        Returns:
            Array de scores de similaridade cosseno
        """
        query_embedding = self.embedding_model.encode([query])
        similarities = cosine_similarity(query_embedding, self.catalog_embeddings)[0]
        return similarities

    def mmr_rerank(self,
                   scores: np.ndarray,
                   lambda_param: float = 0.7,
                   top_k: int = 5) -> List[int]:
        """
        Maximal Marginal Relevance para diversificar resultados

        Args:
            scores: Scores de relevância
            lambda_param: Trade-off relevância vs diversidade (0-1)
            top_k: Número de resultados

        Returns:
            Índices dos top-k resultados diversificados
        """
        selected = []
        candidates = list(range(len(scores)))

        # Primeiro: mais relevante
        first_idx = np.argmax(scores)
        selected.append(first_idx)
        candidates.remove(first_idx)

        # Demais: balancear relevância e diversidade
        for _ in range(top_k - 1):
            if not candidates:
                break

            mmr_scores = []
            for idx in candidates:
                # Relevância
                relevance = scores[idx]

                # Diversidade (menor similaridade com já selecionados)
                if self.catalog_embeddings is not None:
                    selected_embeddings = self.catalog_embeddings[selected]
                    candidate_embedding = self.catalog_embeddings[idx:idx+1]
                    max_sim = cosine_similarity(
                        candidate_embedding,
                        selected_embeddings
                    ).max()
                    diversity = 1 - max_sim
                else:
                    diversity = 1.0

                # MMR score
                mmr = lambda_param * relevance + (1 - lambda_param) * diversity
                mmr_scores.append(mmr)

            # Seleciona melhor MMR
            best_idx = candidates[np.argmax(mmr_scores)]
            selected.append(best_idx)
            candidates.remove(best_idx)

        return selected


def rank_clauses(document,
                 catalog: Dict,
                 top_k: int = 5,
                 lambda_param: float = 0.7) -> List[Dict]:
    """
    Rankeia cláusulas do documento contra o catálogo

    Args:
        document: Documento parseado
        catalog: Catálogo YAML carregado
        top_k: Quantas sugestões por cláusula
        lambda_param: Parâmetro MMR

    Returns:
        Lista de cláusulas com rankings
    """
    ranker = ClauseRanker()
    ranker.encode_catalog(catalog)

    results = []

    for clause in document.clauses:
        query = f"{clause['title']} {clause['content']}"

        # Scores semânticos
        semantic_scores = ranker.semantic_match(query)

        # Fuzzy scores
        catalog_texts = [
            f"{c['title']} {c['content']}"
            for c in ranker.catalog_clauses
        ]
        fuzzy_scores = np.array(ranker.fuzzy_match(query, catalog_texts)) / 100.0

        # Combina scores (média ponderada)
        combined_scores = 0.7 * semantic_scores + 0.3 * fuzzy_scores

        # MMR para diversidade
        top_indices = ranker.mmr_rerank(combined_scores, lambda_param, top_k)

        # Monta resultado
        matches = []
        for idx in top_indices:
            matches.append({
                'catalog_clause': ranker.catalog_clauses[idx],
                'semantic_score': float(semantic_scores[idx]),
                'fuzzy_score': float(fuzzy_scores[idx]),
                'combined_score': float(combined_scores[idx])
            })

        results.append({
            'clause': clause,
            'matches': matches
        })

    return results
