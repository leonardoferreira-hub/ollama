"""
Módulo de Banco de Dados Vetorial para armazenar histórico de documentos
Usa ChromaDB para busca semântica e RAG com sistema de qualidade
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import chromadb
from chromadb.config import Settings
from chromadb.api import EmbeddingFunction


def get_vector_client(embedding="sentence-transformers"):
    """
    Initializes vector store client with specified embedding function
    """
    try:
        import chromadb
        from chromadb.config import Settings
        
        if embedding == "sentence-transformers":
            from chromadb.utils import embedding_functions
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
            )
        else:
            # Fallback to default embedding
            ef = None
            
        # Initialize persistent client
        client = chromadb.PersistentClient(
            path=str(Path("data/vector_db")),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        return client, ef
        
    except ImportError as e:
        raise RuntimeError(
            "ChromaDB não instalado. Adicione 'chromadb>=0.5.4' e 'sentence-transformers>=3.1' "
            "ao requirements.txt e faça redeploy."
        ) from e


class DocumentVectorDB:
    """
    Banco de dados vetorial para armazenar e consultar histórico de documentos
    Com sistema de qualidade (Gold Standard + filtro de cláusulas ruins)
    """

    def __init__(self, persist_directory: str = "data/vector_db"):
        """
        Inicializa o banco de dados vetorial

        Args:
            persist_directory: Diretório onde os dados serão persistidos
        """
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize vector client with embeddings
            self.client, self.embedding_function = get_vector_client()
            
            # Collection para cláusulas
            self.collection = self.client.get_or_create_collection(
                name="clausulas_historico",
                metadata={"description": "Histórico de cláusulas analisadas"},
                embedding_function=self.embedding_function
            )
        except Exception as e:
            raise RuntimeError(f"Erro ao inicializar ChromaDB: {e}")

    def add_document(self, document_name: str, clauses: List[Dict], catalog_name: str, is_gold: bool = False):
        """
        Adiciona um documento completo ao banco vetorial

        Args:
            document_name: Nome do documento
            clauses: Lista de cláusulas com title, content, classification
            catalog_name: Nome do catálogo usado
            is_gold: Se True, marca como documento "gold standard" (prioridade máxima)
        """
        doc_hash = self._generate_doc_hash(document_name)
        timestamp = datetime.now().isoformat()

        # Detecta se é documento GOLD pelo nome
        is_gold = is_gold or document_name.upper().startswith('GOLD_')

        documents = []
        metadatas = []
        ids = []
        added_count = 0

        for idx, clause in enumerate(clauses):
            classification = clause.get('classification', {}).get('classificacao', 'DESCONHECIDO')
            confianca = clause.get('classification', {}).get('confianca', 0.0)

            # 🆕 FILTRO DE QUALIDADE:
            # - Documentos GOLD: adiciona TUDO (mesmo PARCIAL/AUSENTE servem de referência)
            # - Documentos normais: só adiciona cláusulas PRESENTE com confiança >= 0.7
            if not is_gold:
                if classification != 'PRESENTE' or confianca < 0.7:
                    continue  # Pula cláusulas ruins

            # ID único para cada cláusula
            clause_id = f"{doc_hash}_{idx}"

            # Texto para embedding (título + conteúdo)
            text = f"{clause['title']}\n\n{clause['content'][:1000]}"

            # Metadata enriquecida
            metadata = {
                "document_name": document_name,
                "clause_title": clause['title'],
                "clause_index": idx,
                "catalog": catalog_name,
                "timestamp": timestamp,
                "classification": classification,
                "confianca": confianca,
                "source": clause.get('source', 'paragraph'),
                "catalog_match": clause.get('catalog_match', {}).get('titulo', '') if clause.get('catalog_match') else '',
                "is_gold": is_gold,  # 🆕 Flag para documentos gold
                "quality_score": 1.0 if is_gold else confianca  # 🆕 Score de qualidade
            }

            documents.append(text)
            metadatas.append(metadata)
            ids.append(clause_id)
            added_count += 1

        if documents:
            # Adiciona em batch ao ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

        gold_tag = " [GOLD⭐]" if is_gold else ""
        print(f"✅ Documento '{document_name}'{gold_tag} adicionado ao banco vetorial ({added_count}/{len(clauses)} cláusulas)")

    def search_similar_clauses(
        self,
        query: str,
        n_results: int = 5,
        filter_classification: Optional[str] = None,
        filter_catalog: Optional[str] = None,
        prioritize_gold: bool = True
    ) -> List[Dict]:
        """
        Busca cláusulas similares usando busca semântica

        Args:
            query: Texto da busca
            n_results: Número de resultados
            filter_classification: Filtrar por classificação (PRESENTE/PARCIAL/AUSENTE)
            filter_catalog: Filtrar por catálogo específico
            prioritize_gold: Se True, documentos GOLD aparecem primeiro

        Returns:
            Lista de cláusulas similares com metadata
        """
        # Monta filtros
        where = {}
        if filter_classification:
            where["classification"] = filter_classification
        if filter_catalog:
            where["catalog"] = filter_catalog

        # Busca semântica (busca o dobro para depois filtrar gold)
        search_limit = n_results * 3 if prioritize_gold else n_results

        results = self.collection.query(
            query_texts=[query],
            n_results=search_limit,
            where=where if where else None
        )

        # Formata resultados
        similar_clauses = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for idx in range(len(results['ids'][0])):
                similar_clauses.append({
                    'text': results['documents'][0][idx],
                    'metadata': results['metadatas'][0][idx],
                    'distance': results['distances'][0][idx] if 'distances' in results else None
                })

        # 🆕 PRIORIZA DOCUMENTOS GOLD
        if prioritize_gold:
            # Separa gold vs normal
            gold_results = [r for r in similar_clauses if r['metadata'].get('is_gold', False)]
            normal_results = [r for r in similar_clauses if not r['metadata'].get('is_gold', False)]

            # Retorna: primeiro todos os gold, depois normais (até completar n_results)
            prioritized = gold_results + normal_results
            return prioritized[:n_results]

        return similar_clauses[:n_results]

    def get_best_examples_for_clause(
        self,
        clause_title: str,
        clause_content: str,
        catalog_name: str,
        n_examples: int = 3
    ) -> List[Dict]:
        """
        Busca os melhores exemplos de cláusulas similares classificadas como PRESENTE

        Args:
            clause_title: Título da cláusula a buscar
            clause_content: Conteúdo da cláusula
            catalog_name: Nome do catálogo (para filtrar por tipo)
            n_examples: Número de exemplos

        Returns:
            Lista de exemplos bem elaborados (priorizando GOLD)
        """
        query = f"{clause_title}\n{clause_content[:500]}"

        # Busca apenas cláusulas PRESENTE do mesmo catálogo (tipo de operação)
        similar = self.search_similar_clauses(
            query=query,
            n_results=n_examples,
            filter_classification="PRESENTE",
            filter_catalog=catalog_name,  # 🆕 Filtra por tipo de operação
            prioritize_gold=True  # 🆕 Gold tem prioridade
        )

        return similar

    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do banco de dados

        Returns:
            Dict com estatísticas
        """
        total = self.collection.count()

        if total == 0:
            return {
                'total_clausulas': 0,
                'documentos_unicos': 0,
                'documentos_gold': 0,
                'clausulas_gold': 0
            }

        all_data = self.collection.get()
        metadatas = all_data['metadatas']

        gold_count = sum(1 for meta in metadatas if meta.get('is_gold', False))
        gold_docs = set([
            meta['document_name']
            for meta in metadatas
            if meta.get('is_gold', False)
        ])

        return {
            'total_clausulas': total,
            'documentos_unicos': len(set([meta['document_name'] for meta in metadatas])),
            'documentos_gold': len(gold_docs),
            'clausulas_gold': gold_count
        }

    def _generate_doc_hash(self, document_name: str) -> str:
        """Gera hash único para o documento"""
        timestamp = datetime.now().isoformat()
        content = f"{document_name}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def save_feedback(
        self,
        catalog_clause_id: str,
        doc_clause_title: str,
        classification: str,
        match_score: float,
        rating: str,
        catalog_name: str,
        notes: str = ""
    ):
        """
        Salva feedback do usuário sobre uma análise
        
        Args:
            catalog_clause_id: ID da cláusula do catálogo
            doc_clause_title: Título da cláusula encontrada no documento
            classification: PRESENTE/PARCIAL/AUSENTE
            match_score: Score de matching
            rating: 'good' ou 'bad'
            catalog_name: Nome do catálogo
            notes: Notas adicionais do usuário
        """
        # Cria collection de feedback se não existir
        try:
            feedback_collection = self.client.get_or_create_collection(
                name="feedback_analises",
                metadata={"description": "Feedback de usuários sobre análises"}
            )
        except:
            return
        
        timestamp = datetime.now().isoformat()
        feedback_id = f"feedback_{hashlib.md5(f'{catalog_clause_id}_{timestamp}'.encode()).hexdigest()[:12]}"
        
        # Salva feedback
        feedback_collection.add(
            documents=[f"{catalog_clause_id}: {doc_clause_title} - {classification}"],
            metadatas=[{
                "catalog_clause_id": catalog_clause_id,
                "doc_clause_title": doc_clause_title,
                "classification": classification,
                "match_score": match_score,
                "rating": rating,
                "catalog_name": catalog_name,
                "notes": notes,
                "timestamp": timestamp
            }],
            ids=[feedback_id]
        )
        
        print(f"{'✅' if rating == 'good' else '⚠️'} Feedback salvo: {catalog_clause_id} - {rating}")
    
    def get_feedback_stats(self, catalog_name: str = None) -> Dict:
        """
        Retorna estatísticas de feedback
        
        Args:
            catalog_name: Filtrar por catálogo específico
            
        Returns:
            Dict com estatísticas
        """
        try:
            feedback_collection = self.client.get_collection("feedback_analises")
            
            # Busca todos os feedbacks
            results = feedback_collection.get()
            
            if not results['metadatas']:
                return {'good': 0, 'bad': 0, 'total': 0}
            
            # Filtra por catálogo se necessário
            metadatas = results['metadatas']
            if catalog_name:
                metadatas = [m for m in metadatas if m.get('catalog_name') == catalog_name]
            
            good_count = sum(1 for m in metadatas if m.get('rating') == 'good')
            bad_count = sum(1 for m in metadatas if m.get('rating') == 'bad')
            
            return {
                'good': good_count,
                'bad': bad_count,
                'total': good_count + bad_count,
                'accuracy': (good_count / (good_count + bad_count) * 100) if (good_count + bad_count) > 0 else 0
            }
        except:
            return {'good': 0, 'bad': 0, 'total': 0, 'accuracy': 0}

    def reset(self):
        """Reseta o banco de dados (use com cuidado!)"""
        self.client.reset()
        print("⚠️ Banco de dados resetado!")


def get_rag_context_for_suggestion(
    db: DocumentVectorDB,
    clause_title: str,
    clause_content: str,
    catalog_clause: Dict,
    catalog_name: str,
    n_examples: int = 2
) -> str:
    """
    Gera contexto RAG para melhorar sugestões de cláusulas
    Prioriza documentos GOLD e filtra por tipo de operação

    Args:
        db: Instância do DocumentVectorDB
        clause_title: Título da cláusula
        clause_content: Conteúdo da cláusula
        catalog_clause: Cláusula do catálogo
        catalog_name: Nome do catálogo (para filtrar por tipo)
        n_examples: Número de exemplos a incluir

    Returns:
        String com contexto formatado para o LLM
    """
    # Busca exemplos similares bem elaborados (priorizando GOLD)
    examples = db.get_best_examples_for_clause(
        clause_title=clause_title,
        clause_content=clause_content,
        catalog_name=catalog_name,
        n_examples=n_examples
    )

    if not examples:
        return ""

    # Formata contexto RAG
    rag_context = "\n\n📚 EXEMPLOS DE BOAS PRÁTICAS (documentos anteriores):\n"

    for idx, example in enumerate(examples, 1):
        meta = example['metadata']
        gold_badge = "⭐ [GOLD] " if meta.get('is_gold', False) else ""

        rag_context += f"""
Exemplo {idx}: {gold_badge}
Documento: {meta['document_name']}
Cláusula: {meta['clause_title']}
Texto: {example['text'][:300]}...
"""

    return rag_context
