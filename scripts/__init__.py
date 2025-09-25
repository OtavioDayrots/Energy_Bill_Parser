"""
Pacote para processamento de faturas de energia.
Contém módulos para extração, parsing e processamento de dados de PDFs.

Módulos principais:
- ler_faturas: Módulo principal com interface de linha de comando
- processar_simples: Script ultra simples (recomendado)
- processar_faturas: Script interativo para execução personalizada
- constants: Constantes e expressões regulares
- text_utils: Utilitários de processamento de texto
- pdf_extractor: Extração de texto de PDFs
- value_extractor: Extração de valores monetários
- layout_processor: Processamento baseado em layout

Formas de execução:
1. Ultra simples: python processar_simples.py [pasta_entrada]
2. Interativo: python processar_faturas.py
3. Completa: python ler_faturas.py --input pasta --output arquivo.xlsx
"""
__version__ = "2.0.0"
__author__ = "Sistema de Processamento de Faturas"
__description__ = "Sistema modular para extrair dados de energia injetada de faturas PDF"

# Imports principais para facilitar uso
from .executors.ler_faturas import main, process_pdf, Row
from .untils.constants import MUC_GROUPS, OUC_GROUPS, FORA_PONTA_GROUPS

__all__ = [
    'main',
    'process_pdf', 
    'Row',
    'MUC_GROUPS',
    'OUC_GROUPS', 
    'FORA_PONTA_GROUPS'
]

