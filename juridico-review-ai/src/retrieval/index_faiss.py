import faiss
import numpy as np
from typing import List, Dict
from .embeddings import embed

class BlockIndex:
    """
    Índice FAISS para busca semântica em blocos de documentos.

    Usa inner product (IP) após normalização L2 = cosine similarity.
    """

    def __init__(self, blocks: List[Dict]):
        """
        Inicializa o índice FAISS com blocos de documentos.

        Args:
            blocks: Lista de blocos com {page, bbox, text}
        """
        self.blocks = blocks
        self.texts = [b["text"] for b in blocks]
        self.vecs = embed(self.texts).astype("float32")
        d = self.vecs.shape[1]
        self.index = faiss.IndexFlatIP(d)
        self.index.add(self.vecs)

    def search(self, query_text: str, k: int = 5) -> List[Dict]:
        """
        Busca os k blocos mais similares à query.

        Args:
            query_text: Texto da consulta
            k: Número de resultados

        Returns:
            Lista de blocos mais similares
        """
        qv = embed([query_text]).astype("float32")
        D, I = self.index.search(qv, k)
        out = []
        for idx in I[0]:
            if idx == -1:
                continue
            out.append(self.blocks[idx])
        return out

def build_index(blocks: List[Dict]) -> BlockIndex:
    """
    Constrói índice FAISS a partir de blocos.

    Args:
        blocks: Lista de blocos extraídos do PDF

    Returns:
        Índice FAISS pronto para consultas
    """
    return BlockIndex(blocks)

def query_topk(index: BlockIndex, clause: Dict, k: int = 5) -> List[Dict]:
    """
    Consulta os top-k blocos relevantes para uma cláusula.

    Args:
        index: Índice FAISS construído
        clause: Dicionário da cláusula do standard
        k: Número de resultados

    Returns:
        Lista dos k blocos mais relevantes
    """
    # usa title + termos must_include para montar a query
    query = clause.get("title","")
    inc = " ".join(clause.get("must_include", []))
    q = (query + " " + inc).strip()
    return index.search(q, k=k)
