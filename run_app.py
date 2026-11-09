"""Script peluncur otomatis SignDesk (1-click runner).

Fungsi:
1. Memeriksa modul Python yang dibutuhkan (joblib, streamlit, cv2, mediapipe, sklearn, pandas, numpy, dll).
   Jika ada modul yang belum terpasang di komputer ini, otomatis menjalankan pip install.
2. Memeriksa keberadaan model terlatih (models/model_terbaik.joblib).
   Jika belum ada, otomatis melatih model dari data/landmarks/ (src/train.py).
3. Mengatur konfigurasi encoding UTF-8 agar kompatibel dengan terminal Windows.
4. Menjalankan server web Streamlit (app/app.py) pada port 8501.
5. Memantau ketersediaan server dan otomatis membuka browser ke http://localhost:8501
   begitu aplikasi siap digunakan.
"""

import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess
import urllib.request
import importlib.util
from pathlib import Path

# Pastikan encoding UTF-8 di Windows terminal
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

BASE_DIR = Path(__file__).resolve().parent
APP_PATH = BASE_DIR / "app" / "app.py"
MODEL_PATH = BASE_DIR / "models" / "model_terbaik.joblib"
TRAIN_SCRIPT = BASE_DIR / "src" / "train.py"
REQ_FILE = BASE_DIR / "requirements.txt"
DEFAULT_PORT = 8501

# Daftar paket wajib untuk aplikasi SignDesk
MODUL_WAJIB = [
    ("joblib", "joblib"),
    ("streamlit", "streamlit"),
    ("cv2", "opencv-python"),
    ("mediapipe", "mediapipe"),
    ("sklearn", "scikit-learn"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("streamlit_webrtc", "streamlit-webrtc"),
    ("matplotlib", "matplotlib"),
    ("av", "av"),
]


def cek_dan_install_dependensi():
    """Periksa apakah semua pustaka terpasang. Jika ada yang hilang (seperti joblib), pasang otomatis."""
    modul_kurang = []
    pip_kurang = []
    for nama_modul, nama_pip in MODUL_WAJIB:
        if importlib.util.find_spec(nama_modul) is None:
            modul_kurang.append(nama_modul)
            pip_kurang.append(nama_pip)

    if modul_kurang:
        print("=" * 60, flush=True)
        print(f"[INFO] Ditemukan modul yang belum terpasang: {', '.join(modul_kurang)}", flush=True)
        print("[INFO] Sedang memasang paket yang dibutuhkan otomatis via pip...", flush=True)
        print("=" * 60, flush=True)

        if REQ_FILE.exists():
            perintah = [sys.executable, "-m", "pip", "install", "-r", str(REQ_FILE)]
        else:
            perintah = [sys.executable, "-m", "pip", "install"] + pip_kurang

        proses = subprocess.run(perintah, cwd=str(BASE_DIR))
        if proses.returncode != 0:
            print("\n[PERINGATAN] Pemasangan otomatis mengalami kendala.", flush=True)
            print("Silakan jalankan perintah berikut secara manual di Command Prompt:", flush=True)
            print(f"    pip install {' '.join(pip_kurang)}\n", flush=True)
        else:
            print("[OK] Seluruh pustaka berhasil dipasang!\n", flush=True)
    else:
        print("[OK] Semua dependensi Python terpasang lengkap.", flush=True)


def cek_port_tersedia(port):
    """Cek apakah port tertentu sedang kosong atau sudah dipakai."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def tentukan_port():
    """Gunakan port 8501 jika kosong, atau cari port berikutnya jika terpakai."""
    port = DEFAULT_PORT
    while not cek_port_tersedia(port) and port < DEFAULT_PORT + 10:
        port += 1
    return port


def cek_dan_siapkan_model():
    """Pastikan model machine learning sudah tersedia."""
    if not MODEL_PATH.exists():
        print("=" * 60, flush=True)
        print("[INFO] File model belum ditemukan.", flush=True)
        print("[INFO] Melatih model secara otomatis dari data landmarks...", flush=True)
        print("=" * 60, flush=True)
        hasil = subprocess.run([sys.executable, str(TRAIN_SCRIPT)], cwd=str(BASE_DIR))
        if hasil.returncode != 0:
            print("[ERROR] Pelatihan model gagal. Periksa data di folder data/landmarks/.", flush=True)
            sys.exit(hasil.returncode)
        print("[OK] Model berhasil dilatih dan disimpan ke models/model_terbaik.joblib!", flush=True)
    else:
        print("[OK] Model terlatih siap digunakan (models/model_terbaik.joblib).", flush=True)


def buka_browser_otomatis(url):
    """Tunggu hingga localhost aktif, lalu buka di browser default."""
    print(f"[INFO] Menunggu server aktif di {url} ...", flush=True)
    batas_waktu = 40  # detik
    mulai = time.time()
    buka_sukses = False

    while time.time() - mulai < batas_waktu:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    print("\n" + "=" * 60, flush=True)
                    print(" [SUKSES] SignDesk Siap Digunakan!", flush=True)
                    print(f" URL: {url}", flush=True)
                    print(" Membuka browser secara otomatis...", flush=True)
                    print("=" * 60 + "\n", flush=True)
                    webbrowser.open(url)
                    buka_sukses = True
                    break
        except Exception:
            pass
        time.sleep(0.5)

    if not buka_sukses:
        print(f"\n[INFO] Jika browser tidak terbuka otomatis, silakan buka: {url}", flush=True)


def main():
    os.chdir(str(BASE_DIR))
    print("\n" + "=" * 60, flush=True)
    print("      SIGNDESK — PENERJEMAH ALFABET BISINDO (MODE LOKET)", flush=True)
    print("=" * 60, flush=True)

    # 1. Pastikan seluruh dependensi seperti joblib, streamlit, cv2, dll ada
    cek_dan_install_dependensi()

    # 2. Pastikan file model tersedia
    cek_dan_siapkan_model()

    # 3. Tentukan port dan URL
    port = tentukan_port()
    url = f"http://localhost:{port}"

    # 4. Jalankan thread pemantau untuk membuka browser otomatis
    thread_browser = threading.Thread(target=buka_browser_otomatis, args=(url,), daemon=True)
    thread_browser.start()

    # 5. Jalankan Streamlit
    perintah = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_PATH),
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--server.enableCORS",
        "false",
        "--server.enableXsrfProtection",
        "false",
    ]

    try:
        subprocess.run(perintah, cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        print("\n[INFO] Aplikasi SignDesk ditutup. Terima kasih!", flush=True)


if __name__ == "__main__":
    main()
