## Leitor de Faturas de Energia → Excel

Extrai, a partir de PDFs de faturas de energia, os campos:
- Caminho do PDF
- Data (formato `OUT/24`)
- Unidade Consumidora
- Energia Atv Injetada mUC
- Energia Atv Injetada oUC
- Energia Atv Injetada - Fora Ponta

Gera um arquivo Excel consolidando somente as faturas que possuem pelo menos um dos descontos de "Energia Atv Injetada".

### Requisitos
- Python 3.10+

### Instalação rápida (Windows PowerShell)
```powershell
cd "C:\Users\cadastro.tecnico\Documents\Consumos_Energia_COTAA"
python -m venv .venv2
./.venv2/Scripts/python -m pip install -U pip
./.venv2/Scripts/pip install -r requirements.txt
```

### 📁 Estrutura do Projeto

```
Consumos_Energia_COTAA/
├── 📁 faturas/
│   ├── 📁 01-2025/
│   └── 📁 02-2025/
├── 📁 saidas_excel/
├── 📁 scripts/
│   ├── 📁 executors/
│   │   ├── ler_faturas.py
│   │   ├── processar_faturas.py
│   │   └── processar_simples.py
│   ├── 📁 extractors/
│   │   ├── pdf_extractor.py
│   │   └── value_extractor.py
│   ├── 📁 untils/
│   │   ├── constants.py
│   │   └── text_utils.py
│   ├── layout_processor.py
│   ├── config.py
│   └── __init__.py
├── ui_manager.py                  # Interface Streamlit
├── run_ui.bat                     # Atalho para abrir a interface
├── requirements.txt
└── README.md

```

#### 📋 **Descrição dos Módulos**

| Módulo | Função | Descrição |
|--------|--------|-----------|
| 🚀 `processar_simples.py` | **Script principal** | Execução ultra simples, zero configuração |
| ⚙️ `processar_faturas.py` | **Script interativo** | Pergunta pasta de entrada e saída |
| 🐍 `ler_faturas.py` | **Módulo completo** | Interface de linha de comando avançada |
| 📋 `constants.py` | **Constantes** | Expressões regulares e configurações |
| 🔤 `text_utils.py` | **Utilitários** | Normalização e processamento de texto |
| 📄 `pdf_extractor.py` | **Extração PDF** | Leitura e extração de texto de PDFs |
| 💰 `value_extractor.py` | **Valores** | Extração de valores monetários e numéricos |
| 📐 `layout_processor.py` | **Layout** | Processamento baseado em coordenadas |
| ⚙️ `config.py` | **Configurações** | Caminhos e configurações padrão |

### Uso

#### 🚀 **Execução Ultra Simples** (Recomendado)
```powershell
# Usa pasta padrão
./.venv2/Scripts/python scripts/executors/processar_simples.py

# Especifica pasta de entrada
./.venv2/Scripts/python scripts/executors/processar_simples.py "caminho/para/pasta"
```
- ✅ **Zero configuração** - só executar!
- ✅ Nome do arquivo gerado automaticamente com data/hora
- ✅ Saída sempre na pasta `saidas_excel`

#### ⚙️ **Execução Interativa**
```powershell
./.venv2/Scripts/python scripts/executors/processar_faturas.py
```
- ✅ Pergunta pasta de entrada e saída
- ✅ Nome do arquivo gerado com data atual
- ✅ Interface amigável

#### ⚙️ **Execução Personalizada**
```powershell
./.venv2/Scripts/python scripts/executors/ler_faturas.py --input "CAMINHO_DOS_PDFS" --output "saida_faturas.xlsx"
```

Exemplos:
```powershell
# Pasta inteira (procura recursivamente por .pdf)
./.venv2/Scripts/python scripts/executors/ler_faturas.py --input "." --output "saida_faturas.xlsx"

# Um único arquivo PDF
./.venv2/Scripts/python scripts/executors/ler_faturas.py --input "C:\caminho\arquivo.pdf" --output "saida.xlsx"
```

### Interface (Streamlit)
Opção 1 – via .bat (duplo clique recomendado)
```
run_ui.bat
```
Opção 2 – via PowerShell
```powershell
./.venv2/Scripts/Activate.ps1
streamlit run ui_manager.py
```

### Solução de problemas
- Módulo não encontrado (streamlit): ative a venv correta (`.venv2`) e reinstale `pip install -r requirements.txt`.
- Imports quebrados após mover arquivos: garanta que a estrutura e os imports relativos estão como na seção de estrutura.
- Streamlit abre o código em vez da interface: use `run_ui.bat` ou `streamlit run ui_manager.py`.

### Observações
- O script busca valores monetários próximos às linhas com os rótulos de "Energia Atv Injetada" (com e sem o símbolo `R$`).
- Caso a data não apareça em `mm/yyyy`, o campo "Data" pode ficar vazio.


