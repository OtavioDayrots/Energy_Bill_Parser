"""
Utilitários para processamento e normalização de texto.
"""
import re
import unicodedata
from typing import List, Tuple, Optional, Iterable

from constants import MMYYYY_REGEX, MONTH_ABBR_PT


def to_ascii_lower(value: str) -> str:
    """Normaliza (remove acentos) e converte para lower-case."""
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def parse_pt_br_number(num_str: str) -> float:
    """Converte número no formato brasileiro (1.234,56) para float."""
    cleaned = (
        num_str.replace("R$", "")
        .replace(" ", "")
        .replace("\xa0", "")
        .replace(".", "")
        .strip()
    )
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Não foi possível converter número PT-BR: {num_str}")


def month_abbr_pt(month: int) -> str:
    """Retorna abreviação do mês em português."""
    return MONTH_ABBR_PT.get(month, "")


def format_mm_yyyy_to_abbr(mm: int, yyyy: int) -> str:
    """Formata mês/ano para abreviação (ex: 01/2024 -> JAN/24)."""
    return f"{month_abbr_pt(mm)}/{str(yyyy)[-2:]}"


def _all_mm_yyyy(text: str) -> List[Tuple[int, int]]:
    """Extrai todos os pares (ano, mês) do texto."""
    months: List[Tuple[int, int]] = []
    for m in MMYYYY_REGEX.finditer(text):
        mm = int(m.group(1))
        yyyy = int(m.group(2))
        months.append((yyyy, mm))
    return months


def _pick_latest_mm_yyyy(pairs: List[Tuple[int, int]]) -> Optional[str]:
    """Seleciona o par mês/ano mais recente."""
    if not pairs:
        return None
    yyyy, mm = max(pairs)
    return format_mm_yyyy_to_abbr(mm, yyyy)


def extract_month_year(text: str) -> Optional[str]:
    """Extrai o mm/yyyy mais recente do texto completo."""
    pairs = _all_mm_yyyy(text)
    return _pick_latest_mm_yyyy(pairs)


def contains_token_groups(text_norm: str, token_groups: Iterable[Iterable[str]]) -> bool:
    """Verifica se cada grupo de tokens possui pelo menos uma alternativa presente.

    token_groups pode conter strings (equivalentes a um grupo unitário) ou iteráveis
    de strings representando alternativas.
    """
    for group in token_groups:
        if isinstance(group, (list, tuple, set)):
            if not any(token in text_norm for token in group):
                return False
        else:
            # grupo unitário (string)
            if str(group) not in text_norm:
                return False
    return True


def extract_month_year_prefer_discount_lines(
    lines: List[str],
    muc_groups: Iterable[Iterable[str]],
    ouc_groups: Iterable[Iterable[str]],
    window: int = 2,
) -> Optional[str]:
    """Tenta pegar mm/yyyy mais próximo das linhas de desconto; se não achar, pega o mais recente do documento."""
    pairs: List[Tuple[int, int]] = []
    for i, line in enumerate(lines):
        ln_norm = to_ascii_lower(line)
        if contains_token_groups(ln_norm, muc_groups) or contains_token_groups(ln_norm, ouc_groups):
            for j in range(max(0, i - window), min(len(lines), i + window + 1)):
                for m in MMYYYY_REGEX.finditer(lines[j]):
                    mm = int(m.group(1))
                    yyyy = int(m.group(2))
                    pairs.append((yyyy, mm))
    if pairs:
        return _pick_latest_mm_yyyy(pairs)
    # fallback: todo o documento
    return extract_month_year("\n".join(lines))
