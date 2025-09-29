# ui_manager.py
import streamlit as st
import traceback
from pathlib import Path
from datetime import datetime
import os
import sys
import subprocess

# Importa o entrypoint que aceita argv
try:
    PROJECT_ROOT = Path(__file__).resolve().parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
except Exception:
    pass

from scripts.executors.ler_faturas import main as ler_main

st.set_page_config(page_title="Processar Faturas", layout="centered")

st.title("Processamento de Faturas")

if "input_dir" not in st.session_state:
    st.session_state["input_dir"] = "faturas/02-2025"
if "output_dir" not in st.session_state:
    st.session_state["output_dir"] = "saidas_excel"
if "gerar_nome" not in st.session_state:
    st.session_state["gerar_nome"] = f"faturas_processadas_{datetime.now():%Y%m%d_%H%M}"
if "input_dir_field" not in st.session_state:
    st.session_state["input_dir_field"] = st.session_state["input_dir"]
if "output_dir_field" not in st.session_state:
    st.session_state["output_dir_field"] = st.session_state["output_dir"]

def _choose_dir_windows(title: str) -> str | None:
    """Abre seletor nativo de pastas via subprocess para máxima compatibilidade.
    Retorna caminho ou None.
    """
    try:
        code = (
            "import tkinter as tk; from tkinter import filedialog; "
            "root=tk.Tk(); root.withdraw(); "
            f"p=filedialog.askdirectory(title={title!r}); "
            "print(p or '')"
        )
        res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        if res.returncode == 0:
            path = (res.stdout or "").strip()
            return path or None
        return None
    except Exception:
        return None

def _list_subdirs(base: str) -> list[str]:
    try:
        p = Path(base)
        if not p.exists():
            return []
        return [str(d) for d in p.iterdir() if d.is_dir()]
    except Exception:
        return []

cols1 = st.columns([4,1])
with cols1[1]:
    st.markdown('<div style="height: 28px"></div>', unsafe_allow_html=True)
    if st.button("Selecionar", use_container_width=True, key="btn_sel_input"):
        chosen = _choose_dir_windows("Selecione a pasta de faturas")
        if chosen:
            st.session_state["input_dir"] = chosen
            st.session_state["input_dir_field"] = chosen
            st.rerun()
with cols1[0]:
    input_dir = st.text_input("Pasta de faturas (ex: faturas/02-2025)", key="input_dir_field")

cols2 = st.columns([4,1])
with cols2[1]:
    st.markdown('<div style=\"height: 28px\"></div>', unsafe_allow_html=True)
    if st.button("Selecionar ", use_container_width=True, key="btn_sel_output"):
        chosen = _choose_dir_windows("Selecione a pasta de saída")
        if chosen:
            st.session_state["output_dir"] = chosen
            st.session_state["output_dir_field"] = chosen
            st.rerun()
with cols2[0]:
    output_dir = st.text_input("Pasta de saída (ex: saidas_excel)", key="output_dir_field")

with st.form("form_processamento"):
    gerar_nome = st.text_input("Nome do arquivo de saída (sem extensão)", key="gerar_nome")
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