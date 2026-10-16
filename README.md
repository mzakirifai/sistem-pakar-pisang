# 🍌 Sistem Pakar Diagnosis Kematangan Pisang Pascapanen

Sistem pakar berbasis web untuk mendiagnosis tingkat kematangan buah pisang pascapanen dari empat ciri fisik: warna kulit, tekstur, aroma, dan bercak cokelat pada kulit. Penalarannya memakai **Forward Chaining 2 lapis** dan **Certainty Factor (CF)** untuk menyatakan tingkat keyakinan hasil diagnosis.

Aplikasi dibuat dengan Python dan Streamlit. Basis pengetahuan (aturan) disimpan di database MySQL.

---

## 🛠️ Fitur Utama

- **Diagnosis 2 lapis.** Lapis 1 menentukan dugaan awal fase (Mentah, Mengkal, atau Matang) dari warna kulit. Lapis 2 menggabungkan dugaan awal itu dengan tekstur, aroma, dan bercak untuk menghasilkan kelas akhir (Mentah, Mengkal, Matang Optimal, atau Terlalu Matang) beserta rekomendasi penanganan.
- **Aturan hanya menyala bila semua kondisinya terpenuhi.** Jika kombinasi ciri tidak ada di basis pengetahuan, aplikasi tidak menebak. Aplikasi menampilkan pesan dan profil ciri khas dari fase yang diduga, supaya pengamatan bisa diperiksa kembali.
- **Transparansi penalaran.** Hasil diagnosis disertai rule yang menyala dan rincian perhitungan CF. Di tab Basis Pengetahuan, tiap rule menampilkan sumber rujukannya.
- **Riwayat diagnosis** Riwayat diagnosis selama sesi (tanpa entri kembar, lengkap dengan rule dan jam) yang bisa diunduh sebagai CSV, tombol contoh kasus untuk mencoba, dan laporan hasil yang bisa diunduh

---

## 🧠 Cara Kerja Inferensi

Rumus CF mengikuti materi kuliah SBP Pertemuan 4 (Inferensi Pengetahuan, UNINDRA):

| Kasus | Rumus |
|---|---|
| Premis tunggal | CF(H,E) = CF(E) × CF(Rule) |
| Premis majemuk (AND) | min(CF premis) × CF(Rule) |
| Kesimpulan serupa dari beberapa rule | CF1 + CF2 × (1 − CF1) |

Ciri hasil pengamatan dianggap ber-CF 1 (aplikasi tidak menanyakan keyakinan pengguna), sehingga:

- Lapis 1: CF dugaan awal = CF rule lapis 1.
- Lapis 2: CF akhir = CF dugaan awal × CF rule lapis 2.

Contoh: Kuning penuh, Agak lunak, Beraroma kuat, bercak Sedikit → rule L3 (0,8) → rule O4 (0,8) → CF akhir 0,64 (64%) dengan kelas Matang Optimal.

Rumus gabungan hanya dipakai bila lebih dari satu rule dengan kesimpulan sama menyala. Pada basis pengetahuan saat ini, satu input paling banyak menyalakan satu rule.

---

## 📚 Basis Pengetahuan

Basis pengetahuan berisi 3 rule lapis 1 (L1–L3) dan 15 rule lapis 2: M1–M3 (Mentah), K1–K3 (Mengkal), O1–O6 (Matang Optimal), dan T1–T3 (Terlalu Matang). Kolom `sumber` pada tabel `rules` memuat rujukan tiap rule.

Profil ciri khas tiap kelas akhir:

| Kelas | Tekstur | Aroma | Bercak |
|---|---|---|---|
| Mentah | Keras | Tidak beraroma | Tidak ada |
| Mengkal | Agak lunak | Beraroma ringan | Tidak ada |
| Matang Optimal | Lunak | Beraroma kuat | Tidak ada atau Sedikit |
| Terlalu Matang | Lunak | Beraroma kuat | Banyak |

CF rule lapis 2 bernilai 1,0 untuk profil khas, dikurangi 0,2 untuk setiap tingkat ciri yang bergeser dari profil khas. Hanya kombinasi dengan penyimpangan paling banyak satu tingkat yang dibuat sebagai rule.

---

## ⚠️ Asumsi Pemodelan dan Batasan

| Bagian yang tertopang sumber | Bagian yang merupakan asumsi tim |
|---|---|
| Kulit berubah dari hijau ke kuning saat matang | Nilai CF pakar tiap rule dan CF rule lapis 1 |
| Kekerasan buah menurun selama pematangan | Pemetaan label (Keras / Agak lunak / Lunak, Tidak / Ringan / Kuat), karena jurnal memakai angka seperti satuan N dan persen senyawa |
| Aroma ester meningkat saat matang | Batas bercak "Sedikit" untuk optimal dan "Banyak" untuk terlalu matang |
| Bercak cokelat muncul pada fase terlalu matang; skala warna 5 layak konsumsi, skala 6–7 lewat masak | Aroma kuat pada fase terlalu matang (belum ada sumbernya) |
| Selisih skala 4 ke 5 sekitar 0,6–2 hari pada sebagian besar perlakuan (Sutowijoyo & Widodo, Tabel 1–2) | CF pengguna dianggap 1 dan hanya rule dengan penyimpangan satu tingkat yang dibuat |

Batasan:

- Hanya 15 dari 81 kombinasi input yang punya rule. Sisanya menghasilkan "tidak ada aturan yang cocok".
- Sumber memakai varietas dan kondisi simpan yang berbeda (Raja Bulu, Kepok, Brazilian, Fenjiao). Kecepatan matang berbeda antar varietas dan suhu, jadi "tunggu 1–2 hari" hanyalah perkiraan.
- Basis pengetahuan belum divalidasi dengan pakar atau data lapangan.

---

## 📂 Struktur Project

```text
.
├── .streamlit/              # Konfigurasi antarmuka Streamlit
├── database/
│   └── sistem_pakar_pisang_v2.sql   # Skema dan isi basis pengetahuan
├── app.py                   # Antarmuka utama aplikasi
├── config.py                # Konfigurasi environment
├── database.py              # Koneksi dan query MySQL
├── inference.py             # Mesin inferensi Forward Chaining dan CF
├── riwayat.py               # Jam WIB dan ekspor riwayat ke CSV
├── test_inference.py        # Uji mesin inferensi (tanpa database)
├── test_koneksi.py          # Uji manual koneksi database dan satu contoh diagnosis
├── test_riwayat.py          # Uji ekspor riwayat
├── .env.example             # Template konfigurasi environment
├── .gitignore
├── requirements.txt         # Dependensi Python
└── README.md
```

---

## 🚀 Cara Menjalankan

### 1. Prasyarat

- Python 3.10 atau lebih baru
- MySQL atau MariaDB (misalnya lewat XAMPP)

### 2. Persiapan database

1. Buka phpMyAdmin atau klien MySQL pilihanmu.
2. Buat database baru bernama `sistem_pakar_pisang`.
3. Import file `database/sistem_pakar_pisang_v2.sql` ke database tersebut.

File SQL ini menghapus dan membuat ulang keempat tabel (`DROP TABLE`), jadi jangan diimpor ke database yang berisi data lain.

### 3. Konfigurasi environment

Salin `.env.example` menjadi `.env`, lalu sesuaikan isinya:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=sistem_pakar_pisang
DB_PORT=3306
```

### 4. Instal dependensi

```bash
pip install -r requirements.txt
```

### 5. Jalankan aplikasi

```bash
streamlit run app.py
```

### 6. Jalankan uji

```bash
pip install pytest
python -m pytest test_inference.py test_riwayat.py    # tanpa database
python test_koneksi.py                # perlu database yang sudah diimpor
```

---

## ☁️ Deployment (Streamlit Community Cloud)

Isi *Secrets* aplikasi dengan:

```toml
DB_HOST = "alamat-host-database"
DB_USER = "pengguna"
DB_PASSWORD = "kata-sandi"
DB_NAME = "nama-database"
DB_PORT = 4000
```

Aplikasi memakai `st.secrets` bila tersedia, dan memakai `.env` bila tidak. Data aturan di-cache selama 10 menit, jadi perubahan isi database baru terlihat setelah cache habis atau aplikasi dijalankan ulang.

---

## 📖 Referensi

1. Sutowijoyo, D., & Widodo, W. D. (2013). Kriteria Kematangan Pascapanen Pisang Raja Bulu dan Pisang Kepok. *Prosiding Seminar Ilmiah PERHORTI*. IPB.
2. Sularida, N., Sari, J. Y., & Purnama, I. P. N. (2018). Identifikasi Tingkat Kematangan Buah Pisang Menggunakan Metode Ekstraksi Ciri Statistik pada Warna Kulit Buah. *ULTIMATICS*, Vol. X, No. 2, 98–102.
3. Zhu, X., Li, Q., Li, J., Luo, J., Chen, W., & Li, X. (2018). Comparative Study of Volatile Compounds in the Fruit of Two Banana Cultivars at Different Ripening Stages. *Molecules*, 23(10), 2456.
4. Maduwanthi, S. D. T., & Marapana, R. A. U. J. (2017). Biochemical changes during ripening of banana: A review. *International Journal of Food Science and Nutrition*, 2(5), 166–169.
5. Maduwanthi, S. D. T., & Marapana, R. A. U. J. (2019). Induced Ripening Agents and Their Effect on Fruit Quality of Banana. *International Journal of Food Science*, 2019, Article 2520179.
6. Kosasih, R. (2021). Klasifikasi Tingkat Kematangan Pisang Berdasarkan Ekstraksi Fitur Tekstur dan Algoritme KNN. *Jurnal Nasional Teknik Elektro dan Teknologi Informasi*, 10(4), 383–388.
7. Dayan, D. R., Anggalana, M. G., Fahrezi, M. F., Sujono, N. M., Hannover, R., Giri, E. P., & Mindara, G. P. (2026). Penerapan Metode Image Processing Berbasis Histogram Warna untuk Identifikasi dan Penentuan Tingkat Kematangan Buah Pisang. *JATI (Jurnal Mahasiswa Teknik Informatika)*, 10(3), 5450–5456.
8. Materi kuliah Sistem Berbasis Pengetahuan, Pertemuan 4: Inferensi Pengetahuan. Teknik Informatika, UNINDRA, 2026.

---

## 👥 Tim Penyusun

Kelompok 1, tugas mata kuliah Sistem Berbasis Pengetahuan, Teknik Informatika, Universitas Indraprasta PGRI.

Anggota:
1. Muhammad Zaki Rifai
2. Bayu Muhamad Rizki
3. Parkah Nurhidayat
4. Madya Ratri Prasetyo
5. Muhardika