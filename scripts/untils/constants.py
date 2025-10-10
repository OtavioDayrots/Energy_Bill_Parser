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
# Mês por extenso, com ou sem barra antes do ano: "Outubro / 2024" ou "Outubro 2024"
FULL_MONTH_YEAR_REGEX = re.compile(
    r"\b(janeiro|fevereiro|marc[oó]|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b\s*/?\s*(20\d{2})",
    re.IGNORECASE,
)
# Padrão comum na linha de matrícula: ...-YYYY-MM-...
MATRICULA_CYCLE_REGEX = re.compile(r"-(20\d{2})-(0[1-9]|1[0-2])-")

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

# Mapeamento de nome do mês (pt-BR) para número
MONTH_NAME_TO_NUM = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

# Grupos de tokens para identificação de tipos de energia
BASE_ENERGY_GROUPS = [("energia",), ("ativa", "atv", "ativ"), ("injetada", "injet")]
MTC_GROUPS = [("Consumo"), ("em"), ("kWh")]
MUC_GROUPS = [*BASE_ENERGY_GROUPS, ("muc", "m uc", "m-uc")]
OUC_GROUPS = [*BASE_ENERGY_GROUPS, ("ouc", "o uc", "o-uc")]
FORA_PONTA_GROUPS = [*BASE_ENERGY_GROUPS, ("fora",), ("ponta", "fp", "pta")]

# Valores conhecidos para correção específica do arquivo 33857
KNOWN_TRIBUTOS_VALUES = [40.0, 150.0, 287.0]

# Expressões regulares para novos dados - múltiplas variações
# Lista de regex para classificação (tenta diferentes formatos)
CLASSIFICACAO_REGEXES = [
    re.compile(r"Classificação:\s*([A-Z]+-[A-Z\s\.]+?)\s*/\s*[A-Z0-9]+", re.IGNORECASE),  # Formato padrão
    re.compile(r"Classificação:\s*([^/]+)", re.IGNORECASE),  # Tudo até a barra /
]

# Lista de regex para tipo de serviço
TIPO_SERVICO_REGEXES = [
    re.compile(r"Classificação:\s*[A-Z]+-[A-Z\s\.]+?\s*/\s*([A-Z0-9]+)\s+SERVIÇO", re.IGNORECASE),  # Com SERVIÇO completo
    re.compile(r"Classificação:\s*[^/]+/\s*([A-Z0-9]+)\s+SERVIÇO", re.IGNORECASE),  # Mais flexível para classificação
    re.compile(r"Classificação:\s*[^/]+/\s*([A-Z0-9]+)\s+", re.IGNORECASE),  # Qualquer coisa após tipo
    re.compile(r"Classificação:\s*[^/]+/\s*([A-Z0-9]+)", re.IGNORECASE),  # Só o tipo
]

# Lista de regex para limites de tensão
LIM_MIN_REGEXES = [
    re.compile(r"Lim\.\s*Min\.\s*:\s*(\d+)(?:\s|$)", re.IGNORECASE),  # Lim. Min.: 12345
    re.compile(r"Limite\s*Mínimo\s*:\s*(\d+)(?:\s|$)", re.IGNORECASE),  # Limite Mínimo: 12345
]

LIM_MAX_REGEXES = [
    re.compile(r"Lim\.\s*Max\.\s*:\s*(\d+)(?:\s|$)", re.IGNORECASE),  # Lim. Max.: 12345
    re.compile(r"Limite\s*Máximo\s*:\s*(\d+)(?:\s|$)", re.IGNORECASE),  # Limite Máximo: 12345
]