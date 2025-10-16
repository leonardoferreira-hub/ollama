"""
Rankeador Híbrido v2: BM25 + Embeddings + Regex + MMR
"""

from typing import List, Dict, Tuple
import re
import numpy as np
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi


class HybridRanker:
    """Rankeador híbrido usando múltiplas estratégias"""

    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2'):
        """
        Inicializa o rankeador híbrido

        Args:
            embedding_model: Modelo de embeddings da Sentence Transformers
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.bm25 = None
        self.catalog_clauses = []
        self.catalog_embeddings = None
        self.corpus_tokenized = []

    def encode_catalog(self, catalog: Dict):
        """
        Processa catálogo e cria índices

        Args:
            catalog: Catálogo YAML carregado (v2 format)
        """
        self.catalog_clauses = catalog.get('clausulas', [])

        # Textos para indexação
        texts = []
        self.corpus_tokenized = []

        for clause in self.catalog_clauses:
            # Combina título + keywords + template
            text_parts = [
                clause.get('titulo', ''),
                ' '.join(clause.get('keywords', [])),
                clause.get('template', '')
            ]
            full_text = ' '.join(text_parts)
            texts.append(full_text)

            # Tokenização simples para BM25
            tokens = self._tokenize(full_text)
            self.corpus_tokenized.append(tokens)

        # Índice BM25
        self.bm25 = BM25Okapi(self.corpus_tokenized)

        # Embeddings semânticos
        self.catalog_embeddings = self.embedding_model.encode(texts)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenização simples"""
        # Remove pontuação e lowercase
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens

    def regex_score(self, query: str, clause: Dict) -> float:
        """
        Score baseado em regex patterns

        Args:
            query: Texto da cláusula do documento
            clause: Cláusula do catálogo

        Returns:
            Score (0-1)
        """
        patterns = clause.get('regex_patterns', [])
        if not patterns:
            return 0.0

        matches = 0
        for pattern in patterns:
            try:
                if re.search(pattern, query, re.IGNORECASE | re.MULTILINE):
                    matches += 1
            except re.error:
                continue

        # Retorna proporção de patterns que matcharam
        return matches / len(patterns) if patterns else 0.0

    def bm25_score(self, query: str) -> np.ndarray:
        """
        Score BM25 para ranking lexical

        Args:
            query: Texto da query

        Returns:
            Array de scores BM25
        """
        query_tokens = self._tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        # Normaliza para 0-1
        if scores.max() > 0:
            scores = scores / scores.max()
        return scores

    def semantic_score(self, query: str) -> np.ndarray:
        """
        Score semântico usando embeddings

        Args:
            query: Texto da query

        Returns:
            Array de similaridades cosseno
        """
        query_embedding = self.embedding_model.encode([query])
        similarities = cosine_similarity(query_embedding, self.catalog_embeddings)[0]
        return similarities

    def keyword_score(self, query: str, clause: Dict) -> float:
        """
        Score baseado em presença de keywords

        Args:
            query: Texto da cláusula
            clause: Cláusula do catálogo

        Returns:
            Score (0-1)
        """
        keywords = clause.get('keywords', [])
        if not keywords:
            return 0.0

        query_lower = query.lower()
        matches = sum(1 for kw in keywords if kw.lower() in query_lower)

        return matches / len(keywords)

    def hybrid_score(self,
                     query: str,
                     weights: Dict[str, float] = None) -> np.ndarray:
        """
        Score híbrido combinando todas as estratégias

        Args:
            query: Texto da query
            weights: Pesos para cada estratégia

        Returns:
            Array de scores combinados
        """
        if weights is None:
            weights = {
                'bm25': 0.25,
                'semantic': 0.40,
                'regex': 0.20,
                'keyword': 0.15
            }

        # Calcula scores individuais
        bm25_scores = self.bm25_score(query)
        semantic_scores = self.semantic_score(query)

        # Regex e keyword para cada cláusula
        regex_scores = np.array([
            self.regex_score(query, clause)
            for clause in self.catalog_clauses
        ])

        keyword_scores = np.array([
            self.keyword_score(query, clause)
            for clause in self.catalog_clauses
        ])

        # Combina com pesos
        combined = (
            weights['bm25'] * bm25_scores +
            weights['semantic'] * semantic_scores +
            weights['regex'] * regex_scores +
            weights['keyword'] * keyword_scores
        )

        return combined

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
        if len(scores) == 0:
            return []

        selected = []
        candidates = list(range(len(scores)))

        # Primeiro: mais relevante
        first_idx = np.argmax(scores)
        selected.append(first_idx)
        candidates.remove(first_idx)

        # Demais: balancear relevância e diversidade
        for _ in range(min(top_k - 1, len(candidates))):
            if not candidates:
                break

            mmr_scores = []
            for idx in candidates:
                # Relevância
                relevance = scores[idx]

                # Diversidade (menor similaridade com já selecionados)
                selected_embeddings = self.catalog_embeddings[selected]
                candidate_embedding = self.catalog_embeddings[idx:idx+1]
                max_sim = cosine_similarity(
                    candidate_embedding,
                    selected_embeddings
                ).max()
                diversity = 1 - max_sim

                # MMR score
                mmr = lambda_param * relevance + (1 - lambda_param) * diversity
                mmr_scores.append(mmr)

            # Seleciona melhor MMR
            best_idx = candidates[np.argmax(mmr_scores)]
            selected.append(best_idx)
            candidates.remove(best_idx)

        return selected

    def rank_clause(self,
                    clause_text: str,
                    clause_title: str = "",
                    top_k: int = 5,
                    lambda_param: float = 0.7) -> List[Dict]:
        """
        Rankeia uma cláusula contra o catálogo

        Args:
            clause_text: Texto da cláusula
            clause_title: Título da cláusula (opcional)
            top_k: Quantos matches retornar
            lambda_param: Parâmetro MMR

        Returns:
            Lista de matches ordenados
        """
        # Query completa
        query = f"{clause_title} {clause_text}"

        # Score híbrido
        scores = self.hybrid_score(query)

        # MMR para diversidade
        top_indices = self.mmr_rerank(scores, lambda_param, top_k)

        # Monta resultado
        matches = []
        for idx in top_indices:
            clause = self.catalog_clauses[idx]

            # Decompõe scores individuais para debug
            bm25_s = self.bm25_score(query)[idx]
            semantic_s = self.semantic_score(query)[idx]
            regex_s = self.regex_score(query, clause)
            keyword_s = self.keyword_score(query, clause)

            matches.append({
                'catalog_clause': clause,
                'combined_score': float(scores[idx]),
                'scores_breakdown': {
                    'bm25': float(bm25_s),
                    'semantic': float(semantic_s),
                    'regex': float(regex_s),
                    'keyword': float(keyword_s)
                },
                'clause_id': clause.get('id'),
                'importance': clause.get('importancia'),
                'mandatory': clause.get('obrigatoria', False)
            })

        return matches


def rank_document_clauses(document,
                          catalog: Dict,
                          top_k: int = 5,
                          lambda_param: float = 0.7) -> List[Dict]:
    """
    Rankeia todas as cláusulas do documento contra o catálogo

    Args:
        document: Documento parseado
        catalog: Catálogo v2
        top_k: Quantas sugestões por cláusula
        lambda_param: Parâmetro MMR

    Returns:
        Lista de cláusulas com rankings
    """
    ranker = HybridRanker()
    ranker.encode_catalog(catalog)

    results = []

    for clause in document.clauses:
        matches = ranker.rank_clause(
            clause_text=clause['content'],
            clause_title=clause['title'],
            top_k=top_k,
            lambda_param=lambda_param
        )

        results.append({
            'clause': clause,
            'matches': matches
        })

    return results
