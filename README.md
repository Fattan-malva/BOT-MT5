# MT5 Python Autobot (MACD + Bollinger)

**PENTING**: Ini adalah contoh bot edukasional. Selalu uji di akun demo sebelum live. Anda bertanggung jawab penuh atas penggunaan kode ini.

## Ringkasan
Bot ini menggunakan library resmi `MetaTrader5` (Python package) untuk berinteraksi langsung dengan terminal MetaTrader 5 yang terinstal secara lokal. Strategi contoh menggunakan kombinasi **MACD** + **Bollinger Bands**. Manajemen risiko dasar (ukuran lot dinamis, trailing stop, batas kerugian harian) sudah disertakan — tapi perlu penyesuaian ke spesifikasi broker/instrument.

## Apa yang disertakan
- `src/` berisi modul modular:
  - `connector.py` - koneksi MT5 & helper
  - `strategy.py` - perhitungan indikator & sinyal entry
  - `trader.py` - eksekusi order (open/close/modify)
  - `risk_manager.py` - perhitungan lot & pembatas risiko
  - `monitor.py` - loop utama & fetching candles
  - `notifier.py` - output/console notifications
  - `utils.py` - helper umum
  - `main.py` - entry point orchestrator
- `.env.example` - variabel lingkungan
- `requirements.txt` - paket Python yang dibutuhkan

## Prasyarat
1. Python 3.8 - 3.11 (beberapa versi PyPI MetaTrader5 belum mendukung Python 3.12+). Lakukan `python --version`.
2. Terminal **MetaTrader 5** terinstal di komputer dan Anda sudah login ke akun Exness di terminal (Demo atau Live).
3. Pasang package resmi MetaTrader5 via pip:
   ```bash
   pip install MetaTrader5 pandas numpy python-dotenv
   ```
   Dokumentasi resmi dan halaman PyPI: https://pypi.org/project/MetaTrader5/ and https://www.mql5.com/en/docs/integration/python_metatrader5. citeturn0search0turn0search3

## Penting - konfigurasi MT5 sebelum menjalankan
- Pastikan terminal MT5 **sudah dibuka** dan **login** ke akun Exness Anda terlebih dahulu. Package Python berkomunikasi dengan terminal lokal. mt5.initialize() biasanya menemukan terminal yang berjalan. citeturn0search1turn0search5
- Aktifkan **Allow automated trading / Algo trading** di MT5 > Tools > Options > Expert Advisors, jika ingin membuka posisi lewat script. citeturn1search7
- Linux/Mac: bisa berjalan dengan Wine / lingkungan yang kompatibel; dokumentasi MetaTrader5 menyebut dukungan Wine (butuh konfigurasi tambahan). citeturn0search15turn0search6

## Instalasi
1. Clone atau ekstrak zip ini.
2. Buat virtualenv (opsional) dan aktifkan.
3. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Salin `.env.example` menjadi `.env` dan isi variabel (login, password, server, simbol, dsb.).
5. Jalankan MT5 terminal dan pastikan Anda login ke akun Exness.
6. Jalankan bot:
   ```bash
   python src/main.py
   ```

## Catatan penting
- Perhitungan ukuran lot mencoba menggunakan properti symbol_info dari MT5, tetapi **harus** Anda verifikasi untuk instrumen tertentu. Jika hitungan lot menghasilkan error "Invalid volume", sesuaikan parameter minimal/maksimal lot pada `risk_manager.py`.
- Trailing stop dan modifikasi SL/TP menggunakan `TRADE_ACTION_SLTP` via `mt5.order_send()` — ini bergantung pada izin terminal & status posisi.
- Selalu uji di akun demo terlebih dahulu.

Referensi dokumentasi MetaTrader5 (initialize/login/order_send/symbol_info): https://www.mql5.com/en/docs/integration/python_metatrader5. citeturn0search1turn0search5turn1search1
