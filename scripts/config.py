"""
Configurações padrão para o processador de faturas.
"""
import os

# Configurações padrão
DEFAULT_INPUT = "../faturas"
DEFAULT_OUTPUT = "../saidas_excel"
DEFAULT_WINDOW = 2
DEFAULT_DEBUG = False
DEFAULT_DUMP_DIR = None

# Caminhos relativos ao diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def get_default_paths():
    """Retorna os caminhos padrão baseados na estrutura do projeto."""
    return {
        'input': os.path.join(PROJECT_ROOT, 'faturas'),
        'output': os.path.join(PROJECT_ROOT, 'saidas_excel'),
        'dump_dir': None
    }
