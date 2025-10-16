"""
Módulo para leitura e segmentação de documentos DOCX e PDF
"""

from pathlib import Path
from typing import List, Dict
import docx
import PyPDF2
import pdfplumber
import re


class Document:
    """Representa um documento parseado"""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filename = self.filepath.name
        self.clauses = []
        self.metadata = {}

    def add_clause(self, title: str, content: str, section: str = None):
        """Adiciona uma cláusula ao documento"""
        self.clauses.append({
            'title': title,
            'content': content,
            'section': section,
            'index': len(self.clauses)
        })


def parse_document(filepath: str) -> Document:
    """
    Parse de documento DOCX ou PDF

    Args:
        filepath: Caminho para o arquivo

    Returns:
        Objeto Document com cláusulas extraídas
    """
    path = Path(filepath)
    doc = Document(filepath)

    if path.suffix.lower() == '.docx':
        return parse_docx(doc)
    elif path.suffix.lower() == '.pdf':
        return parse_pdf(doc)
    else:
        raise ValueError(f"Formato não suportado: {path.suffix}")


def parse_docx(doc: Document) -> Document:
    """
    Parse específico para arquivos DOCX

    Identifica cláusulas por padrões comuns:
    - "CLÁUSULA X - TÍTULO"
    - Parágrafos numerados
    - Seções maiúsculas
    """
    docx_file = docx.Document(doc.filepath)

    current_clause = None
    current_content = []
    current_section = None

    for para in docx_file.paragraphs:
        text = para.text.strip()

        if not text:
            continue

        # Detecta cláusula (padrão: CLÁUSULA 1 - TÍTULO ou 1. TÍTULO)
        clause_match = re.match(
            r'^(?:CLÁUSULA\s+)?(\d+\.?\d*)\s*[-–—]?\s*(.+)$',
            text,
            re.IGNORECASE
        )

        if clause_match and (text.isupper() or para.style.name.startswith('Heading')):
            # Salva cláusula anterior
            if current_clause:
                doc.add_clause(
                    current_clause,
                    '\n'.join(current_content),
                    current_section
                )

            # Nova cláusula
            current_clause = text
            current_content = []

        # Detecta seção
        elif text.isupper() and len(text.split()) <= 5:
            current_section = text

        # Conteúdo da cláusula
        elif current_clause:
            current_content.append(text)

    # Adiciona última cláusula
    if current_clause:
        doc.add_clause(current_clause, '\n'.join(current_content), current_section)

    return doc


def parse_pdf(doc: Document) -> Document:
    """
    Parse específico para arquivos PDF

    Usa pdfplumber para melhor extração de texto
    """
    with pdfplumber.open(doc.filepath) as pdf:
        full_text = []

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)

    # Processa texto completo como se fosse DOCX
    content = '\n'.join(full_text)
    lines = content.split('\n')

    current_clause = None
    current_content = []
    current_section = None

    for line in lines:
        text = line.strip()

        if not text:
            continue

        # Detecta cláusula
        clause_match = re.match(
            r'^(?:CLÁUSULA\s+)?(\d+\.?\d*)\s*[-–—]?\s*(.+)$',
            text,
            re.IGNORECASE
        )

        if clause_match and text.isupper():
            if current_clause:
                doc.add_clause(
                    current_clause,
                    '\n'.join(current_content),
                    current_section
                )

            current_clause = text
            current_content = []

        elif text.isupper() and len(text.split()) <= 5:
            current_section = text

        elif current_clause:
            current_content.append(text)

    if current_clause:
        doc.add_clause(current_clause, '\n'.join(current_content), current_section)

    return doc


def extract_paragraphs(text: str) -> List[str]:
    """Divide texto em parágrafos mantendo estrutura"""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs
