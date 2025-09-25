# ui_manager.py
import streamlit as st
import traceback
from pathlib import Path
from datetime import datetime

# Importa o entrypoint que aceita argv
from scripts.executors.ler_faturas import main as ler_main

st.set_page_config(page_title="Processar Faturas", layout="centered")

st.title("Processamento de Faturas")
st.caption("Interface simples para usuários leigos")

with st.form("form_processamento"):
    input_dir = st.text_input("Pasta de faturas (ex: faturas/02-2025)", value="faturas/02-2025")
    output_dir = st.text_input("Pasta de saída (ex: saidas_excel)", value="saidas_excel")
    gerar_nome = st.text_input("Nome do arquivo de saída (sem extensão)", value=f"faturas_processadas_{datetime.now():%Y%m%d_%H%M}")
    submitted = st.form_submit_button("Processar")

log_box = st.empty()
progress = st.empty()
result_box = st.empty()

if "logs" not in st.session_state:
    st.session_state["logs"] = ""

def log(msg: str):
    st.session_state["logs"] += (msg + "\n")

# render único dos logs
log_box.text_area("Logs", value=st.session_state["logs"], height=300, key="logs_area", disabled=True)

if submitted:
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        out_file = output_path / f"{gerar_nome}.xlsx"

        if not input_path.exists():
            st.error("Pasta de faturas não encontrada.")
        else:
            log("Iniciando processamento...")
            progress.progress(10)

            # Chama o executor principal passando argv explicitamente
            argv = [
                "--input", str(input_path),
                "--output", str(out_file)
            ]
            exit_code = ler_main(argv)
            if exit_code != 0:
                st.warning(f"Processamento retornou código {exit_code}. Verifique os logs.")

            progress.progress(90)
            log(f"Processamento concluído.")
            progress.progress(100)

            if out_file.exists():
                result_box.success(f"Arquivo gerado: {out_file}")
                st.download_button("Baixar Excel", data=out_file.read_bytes(), file_name=out_file.name)
            else:
                st.warning("Arquivo de saída não encontrado. Verifique logs e caminhos.")
    except Exception as e:
        st.error("Erro durante o processamento.")
        log(traceback.format_exc())