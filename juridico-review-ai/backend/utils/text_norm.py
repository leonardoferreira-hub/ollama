import re
import unicodedata

def normalize(t: str) -> str:
    """
    Normaliza texto para comparação: remove acentos, lowercases, normaliza espaços.

    Args:
        t: Texto a normalizar

    Returns:
        Texto normalizado
    """
    t = t or ""
    t = unicodedata.normalize("NFKD", t)
    t = t.encode("ascii", "ignore").decode("ascii")
    t = t.lower()
    t = re.sub(r"\s+", " ", t).strip()
    return t
