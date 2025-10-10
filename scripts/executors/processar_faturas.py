#!/usr/bin/env python3
"""
Script super simples para processar faturas.
Uso: python processar_faturas.py [pasta_entrada] [pasta_saida]
"""
import os
import sys
from datetime import datetime
from ..config import get_default_paths

# Adiciona o diretório atual ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .ler_faturas import main

def processar():
    """Processa faturas com configurações personalizáveis."""
    print("Processador de Faturas de Energia")
    print("=" * 40)
    
    # Obtém o diretório do projeto (pai do diretório scripts)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Verifica argumentos da linha de comando
    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        input_path = input("Digite o caminho da pasta com os PDFs (ou Enter para usar padrão): ").strip()
        if not input_path:
            default_paths = get_default_paths()
            input_path = default_paths['input']  # Padrão
    
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        output_dir = input("Digite o diretório de saída (ou Enter para usar padrão): ").strip()
        if not output_dir:
            # usa diretório padrão centralizado
            output_dir = get_default_paths()['output']
    
    # Cria a pasta se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Gera nome do arquivo com data atual
    data_atual = datetime.now().strftime("%Y%m%d_%H%M")
    output_filename = f"faturas_processadas_{data_atual}.xlsx"
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"Processando: {input_path}")
    print(f"Saída: {output_path}")
    print("-" * 40)
    
    # Simula argumentos da linha de comando
    sys.argv = [
        'processar_faturas.py',
        '--input', input_path,
        '--output', output_path
    ]
    
    # Executa
    return main()

if __name__ == "__main__":
    try:
        exit_code = processar()
        if exit_code == 0:
            print("\nProcessamento concluído com sucesso!")
        else:
            print(f"\nProcessamento falhou com código: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nProcessamento interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        sys.exit(1)
