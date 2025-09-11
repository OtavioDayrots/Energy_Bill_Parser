"""
Configurações padrão para o processador de faturas.
"""
import os

# Configurações padrão
DEFAULT_INPUT = "../faturas/faturas_teste"
DEFAULT_OUTPUT = "../saida_faturas.xlsx"
DEFAULT_WINDOW = 2
DEFAULT_DEBUG = False
DEFAULT_DUMP_DIR = None

# Caminhos relativos ao diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def get_default_paths():
    """Retorna os caminhos padrão baseados na estrutura do projeto."""
    return {
        'input': os.path.join(PROJECT_ROOT, 'faturas', 'faturas_teste'),
        'output': os.path.join(PROJECT_ROOT, 'saidas_excel', 'saida_faturas.xlsx'),
        'dump_dir': None
    }
