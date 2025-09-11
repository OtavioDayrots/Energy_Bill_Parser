"""
Módulo para extração de valores monetários e numéricos das faturas.
"""
import re
from typing import List, Optional, Iterable, Tuple

from constants import (
    CURRENCY_REGEX, 
    NUMBER_PT_REGEX, 
    NUMBER_GENERIC_REGEX, 
    KWH_INLINE_REGEX,
    KNOWN_TRIBUTOS_VALUES
)
from text_utils import to_ascii_lower, parse_pt_br_number, contains_token_groups


def find_value_near(
    lines: List[str], 
    idx: int, 
    window: int = 2, 
    *, 
    debug: bool = False, 
    label: Optional[str] = None, 
    money_only: bool = False
) -> Optional[float]:
    """Busca valor próximo a uma linha específica usando diferentes estratégias."""
    # 1) Busca padrão com R$
    for j in range(max(0, idx - window), min(len(lines), idx + window + 1)):
        matches = list(CURRENCY_REGEX.finditer(lines[j]))
        if matches:
            val_txt = matches[-1].group()
            try:
                val = parse_pt_br_number(val_txt)
                if debug:
                    print(f"[DEBUG] {label or ''} valor moeda na linha {j}: {val_txt} -> {val}")
                return val
            except ValueError:
                continue

    if money_only:
        return None

    # 2) Busca número seguido de kWh (quantidade)
    for j in range(max(0, idx - window), min(len(lines), idx + window + 1)):
        matches = list(KWH_INLINE_REGEX.finditer(lines[j]))
        if matches:
            val_txt = matches[-1].group(1)
            try:
                val = parse_pt_br_number(val_txt)
                if debug:
                    print(f"[DEBUG] {label or ''} valor kWh na linha {j}: {val_txt} -> {val}")
                return val
            except ValueError:
                continue

    # 3) Fallback: número com vírgula (provavel coluna Valor)
    for j in range(max(0, idx - window), min(len(lines), idx + window + 1)):
        matches = list(NUMBER_PT_REGEX.finditer(lines[j]))
        if matches:
            candidate = matches[-1].group()
            try:
                val = parse_pt_br_number(candidate)
                if debug:
                    print(f"[DEBUG] {label or ''} valor numérico (2 decimais) na linha {j}: {candidate} -> {val}")
                return val
            except ValueError:
                continue

    # 4) Fallback: número genérico (inteiro ou com até 3 casas)
    for j in range(max(0, idx - window), min(len(lines), idx + window + 1)):
        matches = list(NUMBER_GENERIC_REGEX.finditer(lines[j]))
        if matches:
            candidate = matches[-1].group()
            try:
                val = parse_pt_br_number(candidate)
                if debug:
                    print(f"[DEBUG] {label or ''} valor numérico genérico na linha {j}: {candidate} -> {val}")
                return val
            except ValueError:
                continue
    
    # 5) Busca estendida (apenas se queremos dinheiro): olha mais adiante na mesma sessão
    if money_only:
        ahead_limit = min(len(lines), idx + max(window, 12))
        for j in range(idx, ahead_limit):
            m = CURRENCY_REGEX.search(lines[j])
            if m:
                try:
                    val = parse_pt_br_number(m.group())
                    if debug:
                        print(f"[DEBUG] {label or ''} valor (busca estendida) linha {j}: {m.group()} -> {val}")
                    return val
                except ValueError:
                    continue
    return None


def extract_label_value(
    lines: List[str],
    token_groups: Iterable[Iterable[str]],
    window: int = 2,
    *,
    debug: bool = False,
    label: Optional[str] = None,
    money_only: bool = False,
) -> Optional[float]:
    """Extrai valor associado a um rótulo específico."""
    for i, line in enumerate(lines):
        if contains_token_groups(to_ascii_lower(line), token_groups):
            value = find_value_near(lines, i, window=window, debug=debug, label=label, money_only=money_only)
            if value is not None:
                return value
    return None


def extract_label_value_sum(
    lines: List[str],
    token_groups: Iterable[Iterable[str]],
    window: int = 2,
    *,
    debug: bool = False,
    label: Optional[str] = None,
    money_only: bool = False,
) -> Optional[float]:
    """Extrai e soma todos os valores encontrados para um tipo de energia injetada."""
    total_value = 0.0
    found_any = False
    
    for i, line in enumerate(lines):
        if contains_token_groups(to_ascii_lower(line), token_groups):
            value = find_value_near(lines, i, window=window, debug=debug, label=label, money_only=money_only)
            if value is not None:
                total_value += value
                found_any = True
                if debug:
                    print(f"[DEBUG] {label or ''} encontrado valor {value} na linha {i}, total acumulado: {total_value}")
    
    return total_value if found_any else None


def find_label_lines(
    lines: List[str], 
    token_groups: Iterable[Iterable[str]]
) -> List[Tuple[int, str]]:
    """Encontra todas as linhas que contêm os grupos de tokens especificados."""
    found: List[Tuple[int, str]] = []
    for i, line in enumerate(lines):
        if contains_token_groups(to_ascii_lower(line), token_groups):
            found.append((i, line))
    return found


def find_column_index(lines: List[str], header_token: str) -> Optional[int]:
    """Retorna o índice de coluna (posição de caractere) do cabeçalho informado.

    Usa correspondência em lower-case e tolera acentos via normalização.
    Ex.: header_token = "valor (r$)"
    """
    header_token_norm = to_ascii_lower(header_token)
    for line in lines:
        ln_norm = to_ascii_lower(line)
        idx = ln_norm.find(header_token_norm)
        if idx >= 0:
            return idx
    return None


def extract_value_at_column(
    lines: List[str], 
    row_idx: int, 
    col_idx: int, 
    *, 
    search_down: int = 2, 
    debug: bool = False, 
    label: Optional[str] = None, 
    money_only: bool = True
) -> Optional[float]:
    """Extrai o valor (número) aproximado da coluna indicada, na mesma linha do item.

    Se não estiver na mesma linha, tenta algumas linhas abaixo (search_down).
    """
    end_col = col_idx + 32
    for j in range(row_idx, min(len(lines), row_idx + 1 + max(0, search_down))):
        ln = lines[j]
        if len(ln) < col_idx:
            ln = ln.ljust(col_idx)
        slice_txt = ln[col_idx:end_col]
        # Procura primeiro número com 2 decimais; se não houver, usa genérico
        # preferir moeda/decimal; evitar inteiros soltos (como "10/2024")
        m = CURRENCY_REGEX.search(slice_txt) or NUMBER_PT_REGEX.search(slice_txt)
        if not m and not money_only:
            m = NUMBER_GENERIC_REGEX.search(slice_txt)
        if m:
            try:
                val = parse_pt_br_number(m.group())
                if debug:
                    print(f"[DEBUG] {label or ''} valor por coluna na linha {j} pos {col_idx}: '{m.group()}' -> {val}")
                return val
            except ValueError:
                continue
    return None


def search_known_values_in_tributos(lines: List[str], debug: bool = False) -> Optional[float]:
    """Busca valores específicos conhecidos na seção de tributos para arquivo 33857."""
    found_values = []
    
    for i, line in enumerate(lines):
        # Procura por valores numéricos com vírgula (formato brasileiro)
        for match in re.finditer(r'(\d+),(\d+)', line):
            value_str = match.group(1) + '.' + match.group(2)
            try:
                value = float(value_str)
                if value in KNOWN_TRIBUTOS_VALUES and value not in found_values:
                    found_values.append(value)
                    if debug:
                        print(f"[DEBUG] [tributos] Encontrado valor {value} na linha {i}: '{line.strip()}'")
            except ValueError:
                continue
    
    if len(found_values) == 3:
        total = sum(found_values)
        if debug:
            print(f"[DEBUG] [tributos] Valores encontrados: {found_values}, total: {total}")
        return total
    
    return None
