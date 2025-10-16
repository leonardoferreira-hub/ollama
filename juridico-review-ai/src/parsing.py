"""
Módulo para leitura e segmentação de documentos DOCX e PDF
Suporta: CLÁUSULA, CAPÍTULO, ANEXO, tabelas e placeholders
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

    def add_clause(self, title: str, content: str, section: str = None, source: str = "paragraph"):
        """Adiciona uma cláusula ao documento"""
        self.clauses.append({
            'title': title,
            'content': content,
            'section': section,
            'source': source,  # paragraph, table, anexo, capitulo
            'index': len(self.clauses)
        })


def normalize_text(text: str) -> str:
    """
    Normaliza texto removendo placeholders e field codes
    Remove: {=}, [=], etc.
    """
    # Remove placeholders
    text = re.sub(r'\{=\}|\[=\]|\{.*?\}', '', text)

    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


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


def extract_table_content(table) -> List[Dict]:
    """
    Extrai conteúdo de tabelas do DOCX
    Retorna lista de células relevantes
    """
    table_data = []

    for i, row in enumerate(table.rows):
        row_text = []
        for cell in row.cells:
            cell_text = normalize_text(cell.text)
            if cell_text:
                row_text.append(cell_text)

        if row_text:
            # Junta células da linha
            full_row = ' | '.join(row_text)
            table_data.append({
                'row_index': i,
                'text': full_row
            })

    return table_data


def parse_docx(doc: Document) -> Document:
    """
    Parse ROBUSTO para arquivos DOCX

    Captura:
    - CLÁUSULA X - TÍTULO
    - CAPÍTULO NOME
    - ANEXO NOME
    - Conteúdo de TABELAS
    - Parágrafos numerados (1., 1.1, etc.)
    """
    docx_file = docx.Document(doc.filepath)

    current_clause = None
    current_content = []
    current_section = None

    # Lista para rastrear se já processamos certa tabela
    processed_elements = set()

    # Processa PARÁGRAFOS
    for idx, para in enumerate(docx_file.paragraphs):
        text = normalize_text(para.text)

        if not text or len(text) < 3:
            continue

        # REGEX EXPANDIDA: CLÁUSULA | CAPÍTULO | ANEXO | SEÇÃO | Numeração
        heading_match = re.match(
            r'^(cl[áa]usula|se[çc][ãa]o|cap[íi]tulo|anexo)\s+(.+)$',
            text,
            re.IGNORECASE
        )

        # Numeração (1., 1.1, etc.)
        number_match = re.match(
            r'^(\d+(\.\d+){0,2})\s*[-–—]?\s*(.+)$',
            text
        )

        # Verifica se é estilo Heading
        is_heading_style = False
        try:
            style_name = getattr(para.style, 'name', '').lower()
            is_heading_style = 'heading' in style_name or 'título' in style_name
        except:
            pass

        # DETECTA CABEÇALHO (CLÁUSULA, CAPÍTULO, ANEXO, etc.)
        if heading_match or (number_match and (text.isupper() or is_heading_style)):
            # Salva cláusula anterior
            if current_clause:
                doc.add_clause(
                    current_clause,
                    '\n'.join(current_content),
                    current_section,
                    source="paragraph"
                )

            # Nova cláusula
            current_clause = text
            current_content = []

            # Determina seção pelo tipo
            if heading_match:
                tipo = heading_match.group(1).upper()
                current_section = f"{tipo}: {heading_match.group(2)}"

        # Detecta SEÇÃO (texto curto em MAIÚSCULAS)
        elif text.isupper() and len(text.split()) <= 6 and len(text) > 10:
            current_section = text

        # Conteúdo da cláusula atual
        elif current_clause:
            current_content.append(text)

    # Adiciona última cláusula dos parágrafos
    if current_clause:
        doc.add_clause(
            current_clause,
            '\n'.join(current_content),
            current_section,
            source="paragraph"
        )

    # Processa TABELAS
    for table_idx, table in enumerate(docx_file.tables):
        table_content = extract_table_content(table)

        if not table_content:
            continue

        # Primeira linha geralmente é cabeçalho/título
        first_row = table_content[0]['text']

        # Junta todas as linhas
        all_rows = '\n'.join([row['text'] for row in table_content])

        # Adiciona como cláusula (com título da primeira linha)
        doc.add_clause(
            title=f"TABELA {table_idx + 1}: {first_row[:80]}",
            content=all_rows,
            section="TABELAS",
            source="table"
        )

    # Metadata
    doc.metadata['total_clauses'] = len(doc.clauses)
    doc.metadata['has_tables'] = len(docx_file.tables) > 0
    doc.metadata['num_paragraphs'] = len(docx_file.paragraphs)
    doc.metadata['num_tables'] = len(docx_file.tables)

    return doc


def parse_pdf(doc: Document) -> Document:
    """
    Parse específico para arquivos PDF
    Usa pdfplumber para melhor extração de texto e tabelas
    """
    with pdfplumber.open(doc.filepath) as pdf:
        full_text = []
        all_tables = []

        for page_num, page in enumerate(pdf.pages):
            # Extrai texto
            text = page.extract_text()
            if text:
                full_text.append(text)

            # Extrai tabelas
            tables = page.extract_tables()
            if tables:
                for table_idx, table in enumerate(tables):
                    all_tables.append({
                        'page': page_num + 1,
                        'table_idx': table_idx,
                        'data': table
                    })

    # Processa texto completo
    content = '\n'.join(full_text)
    lines = content.split('\n')

    current_clause = None
    current_content = []
    current_section = None

    for line in lines:
        text = normalize_text(line)

        if not text or len(text) < 3:
            continue

        # REGEX EXPANDIDA: CLÁUSULA | CAPÍTULO | ANEXO | SEÇÃO
        heading_match = re.match(
            r'^(cl[áa]usula|se[çc][ãa]o|cap[íi]tulo|anexo)\s+(.+)$',
            text,
            re.IGNORECASE
        )

        # Numeração
        number_match = re.match(
            r'^(\d+(\.\d+){0,2})\s*[-–—]?\s*(.+)$',
            text
        )

        if heading_match or number_match:
            if current_clause:
                doc.add_clause(
                    current_clause,
                    '\n'.join(current_content),
                    current_section,
                    source="paragraph"
                )

            current_clause = text
            current_content = []

            if heading_match:
                tipo = heading_match.group(1).upper()
                current_section = f"{tipo}: {heading_match.group(2)}"

        elif text.isupper() and len(text.split()) <= 6 and len(text) > 10:
            current_section = text

        elif current_clause:
            current_content.append(text)

    if current_clause:
        doc.add_clause(
            current_clause,
            '\n'.join(current_content),
            current_section,
            source="paragraph"
        )

    # Processa TABELAS do PDF
    for table_info in all_tables:
        table_data = table_info['data']
        page = table_info['page']

        # Junta linhas da tabela
        table_text = []
        for row in table_data:
            if row:
                row_text = ' | '.join([str(cell) if cell else '' for cell in row])
                if row_text.strip():
                    table_text.append(row_text)

        if table_text:
            first_row = table_text[0]
            all_text = '\n'.join(table_text)

            doc.add_clause(
                title=f"TABELA Pág.{page}: {first_row[:80]}",
                content=all_text,
                section="TABELAS",
                source="table"
            )

    # Metadata
    doc.metadata['total_clauses'] = len(doc.clauses)
    doc.metadata['has_tables'] = len(all_tables) > 0
    doc.metadata['num_tables'] = len(all_tables)

    return doc


def extract_paragraphs(text: str) -> List[str]:
    """Divide texto em parágrafos mantendo estrutura"""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs
