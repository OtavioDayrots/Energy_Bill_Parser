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
cd "C:\Users\cadastro.tecnico\Documents\economiza COTAA"
python -m venv .venv
./.venv/Scripts/python -m pip install -U pip
./.venv/Scripts/pip install -r requirements.txt
```

### 📁 Estrutura do Projeto

```
economiza COTAA/
├── 📁 faturas/                    # Pasta com faturas PDF para processar
│   ├── 📁 faturas_teste/          # Faturas de teste
│   └── 📁 01-2025/                # Faturas por mês/ano
├── 📁 saidas_excel/               # Pasta onde são salvos os arquivos Excel gerados
├── 📁 scripts/                    # Código fonte do processador
│   ├── 🐍 ler_faturas.py          # Módulo principal (interface completa)
│   ├── 🚀 processar_simples.py    # Script ultra simples (recomendado)
│   ├── ⚙️ processar_faturas.py    # Script interativo
│   ├── 📋 constants.py            # Constantes e expressões regulares
│   ├── 🔤 text_utils.py           # Utilitários de processamento de texto
│   ├── 📄 pdf_extractor.py        # Extração de texto de PDFs
│   ├── 💰 value_extractor.py      # Extração de valores monetários
│   ├── 📐 layout_processor.py     # Processamento baseado em layout
│   ├── ⚙️ config.py               # Configurações do sistema
│   └── 📦 __init__.py             # Pacote Python
├── 📄 requirements.txt            # Dependências Python
├── 📄 README.md                   # Este arquivo

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
./.venv/Scripts/python scripts/processar_simples.py

# Especifica pasta de entrada
./.venv/Scripts/python scripts/processar_simples.py "caminho/para/pasta"
```
- ✅ **Zero configuração** - só executar!
- ✅ Nome do arquivo gerado automaticamente com data/hora
- ✅ Saída sempre na pasta `saidas_excel`

#### ⚙️ **Execução Interativa**
```powershell
./.venv/Scripts/python scripts/processar_faturas.py
```
- ✅ Pergunta pasta de entrada e saída
- ✅ Nome do arquivo gerado com data atual
- ✅ Interface amigável

#### ⚙️ **Execução Personalizada**
```powershell
./.venv/Scripts/python scripts/ler_faturas.py --input "CAMINHO_DOS_PDFS" --output "saida_faturas.xlsx"
```

Exemplos:
```powershell
# Pasta inteira (procura recursivamente por .pdf)
./.venv/Scripts/python scripts/ler_faturas.py --input "." --output "saida_faturas.xlsx"

# Um único arquivo PDF
./.venv/Scripts/python scripts/ler_faturas.py --input "C:\caminho\arquivo.pdf" --output "saida.xlsx"
```

### Observações
- O script busca valores monetários próximos às linhas com os rótulos de "Energia Atv Injetada" (com e sem o símbolo `R$`).
- Caso a data não apareça em `mm/yyyy`, o campo "Data" pode ficar vazio.


