# NutriSmart AI

NutriSmart AI adalah project final Data Science untuk melakukan skrining
risiko pola hidup terhadap obesitas berdasarkan pola makan dan aktivitas fisik.

## Fitur rencana

- Perhitungan BMI sebagai informasi kondisi tubuh saat ini
- Prediksi skor risiko pola hidup terhadap obesitas
- Interpretasi hasil berdasarkan BMI dan skor model
- Penyimpanan riwayat skrining
- Grafik perkembangan skor berdasarkan tanggal
- Rekomendasi sederhana terkait pola makan dan aktivitas

## Menjalankan project secara lokal

1. Buka terminal di folder project.
2. Buat virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Aktifkan virtual environment pada Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   Pada Windows Command Prompt:

   ```cmd
   .venv\Scripts\activate.bat
   ```

4. Instal dependency:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Jalankan aplikasi:

   ```bash
   python -m streamlit run streamlit_app.py
   ```

6. Jalankan JupyterLab:

   ```bash
   jupyter lab
   ```

## Catatan

- File rahasia tidak boleh dimasukkan ke GitHub.
- Folder `.venv` tidak boleh diunggah.
- Model hasil training nantinya disimpan di folder `artifacts/`.
