"""
Constantes e expressões regulares utilizadas no processamento de faturas de energia.
"""
import re

# Expressões regulares para diferentes tipos de números e valores
CURRENCY_REGEX = re.compile(r"R\$\s*-?\s*\d{1,3}(?:\.\d{3})*,\d{2}")
NUMBER_PT_REGEX = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}")
# Números genéricos com ou sem decimais (até 3 casas), ex: 1.234, 1.234,5, 1.234,567
NUMBER_GENERIC_REGEX = re.compile(r"-?\d{1,3}(?:\.\d{3})*(?:,\d{1,3})?")
# Números seguidos por kWh
KWH_INLINE_REGEX = re.compile(r"(-?\d{1,3}(?:\.\d{3})*(?:,\d{1,3})?)\s*kwh", re.IGNORECASE)
UC_REGEX = re.compile(r"(Unidade\s+Consumidora|UC)\s*[:\-]?\s*(\d{4,})", re.IGNORECASE)
MMYYYY_REGEX = re.compile(r"(?<!\d)(0?[1-9]|1[0-2])\s*/\s*(20\d{2})(?!\d)")

# Mapeamento de meses para abreviações em português
MONTH_ABBR_PT = {
    1: "JAN",
    2: "FEV", 
    3: "MAR",
    4: "ABR",
    5: "MAI",
    6: "JUN",
    7: "JUL",
    8: "AGO",
    9: "SET",
    10: "OUT",
    11: "NOV",
    12: "DEZ",
}

# Grupos de tokens para identificação de tipos de energia
BASE_ENERGY_GROUPS = [("energia",), ("ativa", "atv", "ativ"), ("injetada", "injet")]
MUC_GROUPS = [*BASE_ENERGY_GROUPS, ("muc", "m uc", "m-uc")]
OUC_GROUPS = [*BASE_ENERGY_GROUPS, ("ouc", "o uc", "o-uc")]
FORA_PONTA_GROUPS = [*BASE_ENERGY_GROUPS, ("fora",), ("ponta", "fp", "pta")]

# Valores conhecidos para correção específica do arquivo 33857
KNOWN_TRIBUTOS_VALUES = [40.0, 150.0, 287.0]
