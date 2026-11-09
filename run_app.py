"""Script peluncur otomatis SignDesk (1-click runner).

Fungsi:
1. Memeriksa keberadaan model terlatih (models/model_terbaik.joblib).
   Jika belum ada, otomatis melatih model dari data/landmarks/ (src/train.py).
2. Mengatur konfigurasi encoding UTF-8 agar kompatibel dengan terminal Windows.
3. Menjalankan server web Streamlit (app/app.py) pada port 8501.
4. Memantau ketersediaan server dan otomatis membuka browser ke http://localhost:8501
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
from pathlib import Path

# Pastikan encoding UTF-8 di Windows terminal
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

BASE_DIR = Path(__file__).resolve().parent
APP_PATH = BASE_DIR / "app" / "app.py"
MODEL_PATH = BASE_DIR / "models" / "model_terbaik.joblib"
TRAIN_SCRIPT = BASE_DIR / "src" / "train.py"
DEFAULT_PORT = 8501


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
    batas_waktu = 35  # detik
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

    cek_dan_siapkan_model()

    port = tentukan_port()
    url = f"http://localhost:{port}"

    # Jalankan thread pemantau untuk membuka browser otomatis
    thread_browser = threading.Thread(target=buka_browser_otomatis, args=(url,), daemon=True)
    thread_browser.start()

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
