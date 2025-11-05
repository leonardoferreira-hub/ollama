from typing import List
import numpy as np

def _tokenize(t: str) -> List[str]:
    """
    Tokeniza texto simples para bag-of-words.

    Args:
        t: Texto a tokenizar

    Returns:
        Lista de tokens
    """
    import re
    t = t.lower()
    t = re.sub(r"[^a-zá-úà-ùâ-ûãõç0-9 ]+", " ", t)
    return [w for w in t.split() if len(w) > 2]

def embed(texts: List[str]) -> np.ndarray:
    """
    Gera embeddings bag-of-words normalizados (MVP simples).

    Este é um embedding MVP para funcionar sem dependências externas.
    Futuramente substituir por embeddings reais (Gemini ou sentence-transformers).

    Args:
        texts: Lista de textos para embeddar

    Returns:
        Matriz numpy de embeddings normalizados (L2)
    """
    # vetor bobo de frequências — substituível depois
    vocab = {}
    vecs = []
    for t in texts:
        toks = _tokenize(t)
        counts = {}
        for w in toks:
            if w not in vocab:
                vocab[w] = len(vocab)
            idx = vocab[w]
            counts[idx] = counts.get(idx, 0) + 1
        # cria vetor esparso -> denso local (MVP)
        size = len(vocab)
        v = np.zeros(size, dtype="float32")
        for idx, c in counts.items():
            v[idx] = c
        vecs.append(v)

    if not vecs:
        return np.array([[]], dtype="float32")

    # pad para mesmo tamanho
    maxd = max(v.shape[0] for v in vecs)
    out = np.zeros((len(vecs), maxd), dtype="float32")
    for i, v in enumerate(vecs):
        out[i, :v.shape[0]] = v
    # normaliza
    norms = np.linalg.norm(out, axis=1, keepdims=True) + 1e-6
    out = out / norms
    return out
