"""
Módulo para extração de texto de arquivos PDF.
"""
import os
import re
from typing import List, Dict, Any, Optional, Tuple

import fitz  # PyMuPDF

from constants import UC_REGEX
from text_utils import to_ascii_lower


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrai texto tentando diferentes modos e escolhe o mais rico.

    - text: texto linear
    - blocks: concatena texto por blocos (pode preservar tabelas melhor)
    """
    doc = fitz.open(pdf_path)
    try:
        # Modo "text"
        text_mode = []
        for i in range(doc.page_count):
            page = doc.load_page(i)
            text_mode.append(page.get_text("text") or "")
        text_combined = "\n".join(text_mode)

        # Modo "blocks"
        blocks_mode = []
        for i in range(doc.page_count):
            page = doc.load_page(i)
            try:
                blocks = page.get_text("blocks")
                if isinstance(blocks, list):
                    blocks_text = []
                    for b in blocks:
                        if isinstance(b, (list, tuple)) and len(b) > 4 and isinstance(b[4], str):
                            blocks_text.append(b[4])
                    blocks_mode.append("\n".join(blocks_text))
            except Exception:
                blocks_mode.append("")
        blocks_combined = "\n".join(blocks_mode)

        # Escolhe o mais longo (heurística simples)
        return blocks_combined if len(blocks_combined) > len(text_combined) else text_combined
    finally:
        doc.close()


def extract_uc(text: str) -> Optional[str]:
    """Extrai UC usando regex simples."""
    m = UC_REGEX.search(text)
    if m:
        return m.group(2)
    return None


def extract_uc_robust(text: str, lines: List[str]) -> Optional[str]:
    """Extrai UC usando múltiplas estratégias robustas."""
    # 1) Busca por padrões comuns no texto inteiro
    patterns = [
        r"(?:unidade\s+consumidora|uc)\s*[:\-]?\s*(\d{8,})",
        r"n[ºo°\.]?\s*(?:da\s*)?(?:unidade\s+consumidora|uc)\s*[:\-]?\s*(\d{8,})",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1)

    # 2) Linha a linha: se contiver indicação de UC, extrai primeiro grupo de dígitos longos
    uc_line_patterns = [
        re.compile(r"\b(?:unidade\s+consumidora)\b.*?(\d{8,})", re.IGNORECASE),
        re.compile(r"\bUC\b\s*[:\-]?\s*(\d{8,})", re.IGNORECASE),
    ]
    for line in lines:
        for pat in uc_line_patterns:
            m = pat.search(line)
            if m:
                return m.group(1)

    # 3) Fallback preferencial: bloco "Código/Cod. do Cliente" seguido do valor (ex.: 10/108132-2)
    for i, line in enumerate(lines):
        ln = to_ascii_lower(line)
        if (("codigo" in ln or "cod." in ln or "cod " in ln) and "cliente" in ln):
            for j in range(i, min(len(lines), i + 4)):
                # Primeiro tenta encontrar formato original como 10/108132-2
                original_format = re.search(r"\b\d{1,3}/\d{4,8}-\d\b", lines[j])
                if original_format:
                    return original_format.group()
                # Se não encontrar, extrai apenas dígitos
                m = re.search(r"[A-Za-z0-9][A-Za-z0-9\/-\.]{6,}", lines[j])
                if m:
                    digits = re.findall(r"\d", m.group())
                    uc_candidate = "".join(digits)
                    if len(uc_candidate) >= 7:
                        return uc_candidate

    # 4) Fallback alternativo: "Código da Instalação" (pode conter letras como 00000R29733)
    for i, line in enumerate(lines):
        ln = to_ascii_lower(line)
        if ("codigo" in ln and ("instalacao" in ln or "instala" in ln)):
            for j in range(i, min(len(lines), i + 4)):
                # Primeiro tenta encontrar formato original como 10/108132-2
                original_format = re.search(r"\b\d{1,3}/\d{4,8}-\d\b", lines[j])
                if original_format:
                    return original_format.group()
                # Se não encontrar, extrai apenas dígitos
                m = re.search(r"[A-Za-z0-9][A-Za-z0-9\/-\.]{6,}", lines[j])
                if m:
                    digits = re.findall(r"\d", m.group())
                    uc_candidate = "".join(digits)
                    if len(uc_candidate) >= 7:
                        return uc_candidate
    
    # 5) Fallback final: padrão numérico estilo "10/108132-2" (ou 10/3211-0) em qualquer lugar do texto
    generic_matches = re.findall(r"\b\d{1,3}/\d{4,8}-\d\b", text)
    if generic_matches:
        return generic_matches[-1]  # Retorna formato original
    return None


def list_pdfs(input_path: str) -> List[str]:
    """Lista todos os arquivos PDF em um diretório ou retorna um único arquivo PDF."""
    if os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
        return [input_path]
    collected: List[str] = []
    for root, _dirs, files in os.walk(input_path):
        for f in files:
            if f.lower().endswith(".pdf"):
                collected.append(os.path.join(root, f))
    return collected


def _collect_page_lines(page_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Coleta e organiza linhas de uma página PDF com informações de posicionamento."""
    lines: List[Dict[str, Any]] = []
    for block in page_dict.get("blocks", []):
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            text_parts: List[str] = []
            span_objs: List[Dict[str, Any]] = []
            y0 = None
            y1 = None
            for sp in spans:
                txt = sp.get("text", "")
                bbox = sp.get("bbox", [0, 0, 0, 0])
                x0, sy0, x1, sy1 = bbox
                if y0 is None or sy0 < y0:
                    y0 = sy0
                if y1 is None or sy1 > y1:
                    y1 = sy1
                text_parts.append(txt)
                span_objs.append({
                    "text": txt,
                    "x0": x0,
                    "x1": x1,
                    "y0": sy0,
                    "y1": sy1,
                })
            line_text = " ".join(tp for tp in text_parts if tp)
            if not line_text.strip():
                continue
            lines.append({
                "text": line_text,
                "text_norm": to_ascii_lower(line_text),
                "y0": y0,
                "y1": y1,
                "spans": span_objs,
            })
    # ordena por y
    lines.sort(key=lambda l: l["y0"])
    return lines
