@echo off
call "%USERPROFILE%\anaconda3\condabin\conda.bat" activate banking-dashboard
cd /d "%~dp0"
python -m streamlit run app.py
pause