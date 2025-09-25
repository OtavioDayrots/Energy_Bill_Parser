@echo off
cd /d %~dp0
call .venv2\Scripts\activate.bat
streamlit run ui_manager.py