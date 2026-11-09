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
echo Sedang memeriksa dan menyalakan aplikasi SignDesk...
echo Begitu siap, browser akan langsung otomatis terbuka.
echo.
echo Tekan [Ctrl + C] di jendela hitam ini jika ingin menutup aplikasi.
echo ============================================================
echo.

python -u run_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Terjadi kendala saat menjalankan aplikasi.
    pause
)
