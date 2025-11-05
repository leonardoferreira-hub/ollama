import fitz  # PyMuPDF
from typing import List, Dict

def extract_blocks(pdf_path: str) -> List[Dict]:
    """
    Extrai blocos de texto de um PDF usando PyMuPDF, preservando página e bbox.

    Args:
        pdf_path: Caminho para o arquivo PDF

    Returns:
        Lista de dicionários com {page, bbox, text}
    """
    doc = fitz.open(pdf_path)
    out = []
    for pno in range(len(doc)):
        page = doc[pno]
        # blocks: (x0, y0, x1, y1, "text", block_no, block_type, ...)
        for b in page.get_text("blocks", sort=True):
            x0, y0, x1, y1, txt, *_ = b
            text = (txt or "").strip()
            if not text:
                continue
            out.append({
                "page": pno + 1,
                "bbox": [float(x0), float(y0), float(x1), float(y1)],
                "text": text
            })
    doc.close()
    return out
