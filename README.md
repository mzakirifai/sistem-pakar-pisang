# 🍌 Sistem Pakar Diagnosis Kematangan Pisang Pascapanen

Sistem pakar berbasis web ini dibangun untuk mendiagnosis tingkat kematangan buah pisang pascaproduksi/pascapanen berdasarkan 4 indikator fisik utama: warna kulit, tekstur, aroma, dan bercak cokelat pada kulit. 

Aplikasi ini menggunakan metode **Forward Chaining 2 Lapis** yang digabungkan dengan **Certainty Factor (CF)** untuk mengukur tingkat kepastian/keyakinan diagnosis[cite: 7].

---

## 🛠️ Fitur Utama

- **Diagnosis 2 Lapis (Forward Chaining):**
  - **Lapis 1:** Menganalisis warna kulit untuk menentukan dugaan awal tingkat kematangan[cite: 7].
  - **Lapis 2:** Menggabungkan dugaan awal dengan indikator fisik lainnya (tekstur, aroma, bercak) untuk menghasilkan kesimpulan akhir dan rekomendasi penanganan[cite: 7].
- **Perhitungan Certainty Factor (CF):** Menghitung persentase keyakinan hasil diagnosis secara objektif dan menangani kondisi *partial match* jika ciri fisik pengguna bertentangan[cite: 7].
- **Explainable AI (Transparansi Penalaran):** Menampilkan detail rule dan rumus matematika di balik hasil diagnosis[cite: 7].
- **Riwayat Diagnosis:** Menyimpan catatan hasil pengujian selama sesi berjalan[cite: 7].

---

## 📂 Struktur Project

```text
.
├── .streamlit/          # Konfigurasi antarmuka Streamlit
├── app.py               # Antarmuka utama aplikasi (UI/UX)
├── config.py            # Konfigurasi environment & variabel
├── database.py          # Modul koneksi & query MySQL
├── inference.py         # Mesin inferensi Forward Chaining & CF
├── test_koneksi.py      # Script pengujian koneksi database
├── .env.example         # Template konfigurasi environment
├── .gitignore           # Daftar berkas yang diabaikan Git
├── requirements.txt     # Daftar dependensi Python
└── README.md            # Dokumentasi project

🚀 Cara Menjalankan Project
1. Prasyarat
- Python 3.10 atau versi lebih baru
- MySQL Server / XAMPP

2. Persiapan Database
- Buka phpMyAdmin atau MySQL Client pilihan kamu.
- Buat database baru bernama sistem_pakar_pisang.   
- Import file sistem_pakar_pisang.sql ke dalam database tersebut.   

3. Konfigurasi Environment
- Salin file .env.example menjadi .env:
    cp .env.example .env
- Sesuaikan kredensial database di dalam file .env:
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=
    DB_NAME=sistem_pakar_pisang

4. Instalasi Dependensi
Buka terminal/command prompt di direktori project, lalu jalankan:
    pip install -r requirements.txt

5. Jalankan Aplikasi
Jalankan perintah berikut untuk membuka aplikasi di browser:
    streamlit run app.py
    
👥 Tim PenyusunKelompok 1 — Tugas Mata Kuliah Sistem Berbasis Pengetahuan