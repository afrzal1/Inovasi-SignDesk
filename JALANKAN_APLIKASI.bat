@echo off
title SignDesk - Penerjemah Alfabet BISINDO (Mode Loket)
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo ============================================================
echo        SIGNDESK - PENERJEMAH ALFABET BISINDO (MODE LOKET)
echo ============================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=python
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set PY_CMD=py
    ) else (
        echo [ERROR] Python tidak terdeteksi di komputer ini.
        echo Silakan pasang Python dari https://www.python.org/ (versi 3.10 atau 3.11 disarankan)
        echo dan pastikan centang opsi "Add Python to PATH" saat instalasi.
        echo.
        pause
        exit /b 1
    )
)

echo Sedang memeriksa modul (joblib, streamlit, dll), model, dan menyalakan server...
echo Jika ada modul yang belum terpasang, sistem akan memasangnya otomatis.
echo Begitu siap, browser akan langsung otomatis terbuka ke http://localhost:8501
echo.
echo Tekan [Ctrl + C] di jendela ini jika ingin menutup aplikasi.
echo ============================================================
echo.

%PY_CMD% -u run_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo Terjadi kendala saat menjalankan aplikasi.
    echo Pastikan komputer terhubung ke internet jika membutuhkan unduhan modul awal,
    echo atau jalankan perintah ini manual di Command Prompt / Terminal:
    echo     pip install -r requirements.txt
    echo ============================================================
    echo.
    pause
)
