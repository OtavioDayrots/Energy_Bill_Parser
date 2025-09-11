"""
Módulo para processamento de layout e extração de valores baseada em coordenadas.
"""
import re
from typing import List, Dict, Any, Optional, Tuple, Iterable

import fitz  # PyMuPDF

from constants import CURRENCY_REGEX, NUMBER_PT_REGEX, NUMBER_GENERIC_REGEX
from text_utils import to_ascii_lower, parse_pt_br_number, contains_token_groups
from pdf_extractor import _collect_page_lines


def _find_header_columns_x(lines: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    """Retorna aproximação das posições x de várias colunas de cabeçalho."""
    result: Dict[str, Optional[float]] = {
        "quant": None,
        "preco": None,
        "valor": None,
        "pis": None,
        "base": None,
        "icms": None,
        "tarifa": None,
    }
    for ln in lines:
        for sp in ln["spans"]:
            txtn = to_ascii_lower(sp["text"]) or ""
            x_mid = (sp["x0"] + sp["x1"]) / 2.0
            if result["valor"] is None and "valor" in txtn:
                result["valor"] = x_mid
            if result["preco"] is None and ("preco" in txtn and "unit" in txtn):
                result["preco"] = x_mid
            if result["quant"] is None and "quant" in txtn:
                result["quant"] = x_mid
            if result["pis"] is None and ("pis" in txtn and "cofins" in txtn):
                result["pis"] = x_mid
            if result["base"] is None and ("base" in txtn and "icms" in txtn):
                result["base"] = x_mid
            if result["icms"] is None and ("icms (r$" in txtn or ("icms" in txtn and "r$" in txtn)):
                result["icms"] = x_mid
            if result["tarifa"] is None and ("tarifa" in txtn and "unit" in txtn):
                result["tarifa"] = x_mid
        if all(v is not None for v in result.values()):
            break
    return result


def _find_line_indices_by_tokens(lines: List[Dict[str, Any]], token_groups: Iterable[Iterable[str]]) -> List[int]:
    """Encontra índices das linhas que contêm os grupos de tokens especificados."""
    indices: List[int] = []
    for i, ln in enumerate(lines):
        if contains_token_groups(ln["text_norm"], token_groups):
            indices.append(i)
    return indices


def _extract_number_near_x_from_line(
    line_obj: Dict[str, Any], 
    target_x: Optional[float], 
    avoid_x: Optional[List[float]] = None, 
    x_tolerance: float = 10.0
) -> Optional[float]:
    """Extrai número mais próximo da posição x especificada em uma linha."""
    best_val: Optional[float] = None
    best_dist: float = float("inf")
    for sp in line_obj["spans"]:
        text = sp["text"]
        # Aceita moeda/decimal pt-BR e números inteiros (quantidade); evita capturar '9/2024'
        m = CURRENCY_REGEX.search(text) or NUMBER_PT_REGEX.search(text) or NUMBER_GENERIC_REGEX.search(text)
        if m:
            try:
                val = parse_pt_br_number(m.group())
            except ValueError:
                continue
            x_center = (sp["x0"] + sp["x1"]) / 2.0
            if target_x is None:
                # prefere o número mais à direita
                dist = -x_center
            else:
                dist = abs(x_center - target_x)
                # Se estiver muito longe da coluna alvo, pula
                if dist > x_tolerance:
                    continue
            # Evita colunas concorrentes, se conhecidas
            if avoid_x:
                other_dists = [abs(x_center - ax) for ax in avoid_x if ax is not None]
                if other_dists:
                    min_other = min(other_dists)
                    # Requer estar pelo menos 10px mais perto da coluna alvo
                    if not (dist + 10 <= min_other):
                        continue
            if dist < best_dist:
                best_dist = dist
                best_val = val
    return best_val


def extract_values_by_layout(pdf_path: str, *, debug: bool = False) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[str]]:
    """Extrai valores usando análise de layout baseada em coordenadas."""
    muc_val: Optional[float] = None
    ouc_val: Optional[float] = None
    fp_val: Optional[float] = None
    uc_found: Optional[str] = None

    doc = fitz.open(pdf_path)
    try:
        for page in doc:
            pdict = page.get_text("dict")
            lines = _collect_page_lines(pdict)
            header_x = _find_header_columns_x(lines)
            quant_x = header_x.get("quant")
            if debug and (quant_x is not None or header_x.get("preco") is not None or header_x.get("valor") is not None):
                print(f"[DEBUG] [layout] colunas x → Quant~{header_x.get('quant')}, Preco~{header_x.get('preco')}, Valor~{header_x.get('valor')}")

            # tenta encontrar UC no layout se ainda não achou (sem confundir com mUC/oUC)
            if uc_found is None:
                # 1) Codigo do Cliente / Cod. do Cliente
                for i, ln in enumerate(lines):
                    t = ln["text_norm"]
                    if (("codigo" in t or "cod." in t or "cod " in t) and "cliente" in t):
                        for j in range(i, min(len(lines), i + 5)):
                            digits = re.findall(r"\d", lines[j]["text"])  # junta digitos mesmo se espaçados
                            if len(digits) >= 8:
                                uc_found = "".join(digits)
                                break
                        if uc_found is not None:
                            break
                # 2) Unidade Consumidora
                if uc_found is None:
                    for ln in lines:
                        t = ln["text_norm"]
                        if ("unidade" in t and "consumidora" in t):
                            digits = re.findall(r"\d", ln["text"])  # junta digitos
                            if len(digits) >= 8:
                                uc_found = "".join(digits)
                                break
                # 3) Codigo da Instalacao
                if uc_found is None:
                    for i, ln in enumerate(lines):
                        t = ln["text_norm"]
                        if ("codigo" in t and ("instalacao" in t or "instala" in t)):
                            for j in range(i, min(len(lines), i + 5)):
                                digits = re.findall(r"\d", lines[j]["text"])  # junta digitos
                                if len(digits) >= 8:
                                    uc_found = "".join(digits)
                                    break
                            if uc_found is not None:
                                break

            # indices dos itens - busca mais específica
            base_groups = [("energia",), ("ativa", "atv", "ativ"), ("injetada", "injet")]
            muc_groups = [*base_groups, ("muc",)]
            ouc_groups = [*base_groups, ("ouc",)]
            fp_groups = [*base_groups, ("fora",), ("ponta",)]

            muc_idx_list = _find_line_indices_by_tokens(lines, muc_groups)
            ouc_idx_list = _find_line_indices_by_tokens(lines, ouc_groups)
            fp_idx_list = _find_line_indices_by_tokens(lines, fp_groups)
            
            if debug:
                print(f"[DEBUG] [layout] mUC indices: {muc_idx_list}")
                print(f"[DEBUG] [layout] oUC indices: {ouc_idx_list}")
                print(f"[DEBUG] [layout] FP indices: {fp_idx_list}")
                for idx in muc_idx_list:
                    print(f"[DEBUG] [layout] mUC linha {idx}: '{lines[idx]['text']}'")

            def _probe_value(idx_list: List[int]) -> Optional[float]:
                total_value = 0.0
                found_any = False
                used_lines = set()  # Para evitar usar a mesma linha duas vezes
                
                # Primeiro, coleta TODOS os valores na coluna de quantidade
                all_quant_values = []
                for j in range(len(lines)):
                    v = _extract_number_near_x_from_line(
                        lines[j], quant_x,
                        avoid_x=[
                            header_x.get("preco"), header_x.get("valor"), header_x.get("pis"),
                            header_x.get("base"), header_x.get("icms"), header_x.get("tarifa"),
                        ],
                        x_tolerance=50.0
                    )
                    if v is not None:
                        y_mid = (lines[j]["y0"] + lines[j]["y1"]) / 2.0
                        all_quant_values.append((v, j, y_mid))
                
                if debug:
                    print(f"[DEBUG] [layout] Todos os valores na coluna Quant: {[v[0] for v in all_quant_values]}")
                
                # Agora associa os valores aos rótulos baseado na proximidade
                for idx in idx_list:
                    y_target = (lines[idx]["y0"] + lines[idx]["y1"]) / 2.0
                    best_v: Optional[float] = None
                    best_dy: float = float("inf")
                    best_line = None
                    
                    # Procura o valor mais próximo que ainda não foi usado
                    for v, line_idx, y_mid in all_quant_values:
                        if line_idx in used_lines:  # Pula linhas já usadas
                            continue
                            
                        dy = abs(y_mid - y_target)
                        if dy > 1000.0:  # Limite de distância
                            continue
                            
                        if debug:
                            print(f"[DEBUG] [layout] Considerando valor {v} na linha {line_idx} (distancia Y: {dy:.1f})")
                            
                        # Prioriza valores que estão mais próximos do rótulo
                        if best_v is None or dy < best_dy:
                            best_dy = dy
                            best_v = v
                            best_line = line_idx
                    
                    if best_v is not None and best_line is not None:
                        used_lines.add(best_line)  # Marca a linha como usada
                        total_value += best_v
                        found_any = True
                        if debug:
                            print(f"[DEBUG] [layout] Valor encontrado: {best_v}, total acumulado: {total_value}")
                
                return total_value if found_any else None

            if muc_val is None:
                muc_val = _probe_value(muc_idx_list)
                if debug and muc_val is not None:
                    print(f"[DEBUG] [layout] mUC valor encontrado: {muc_val}")
            if ouc_val is None:
                ouc_val = _probe_value(ouc_idx_list)
                if debug and ouc_val is not None:
                    print(f"[DEBUG] [layout] oUC valor encontrado: {ouc_val}")
            if fp_val is None:
                fp_val = _probe_value(fp_idx_list)
                if debug and fp_val is not None:
                    print(f"[DEBUG] [layout] FP valor encontrado: {fp_val}")
    finally:
        doc.close()

    if debug:
        print(f"[DEBUG] [layout] Resultado final: mUC={muc_val}, oUC={ouc_val}, FP={fp_val}, UC={uc_found}")
    return muc_val, ouc_val, fp_val, uc_found
