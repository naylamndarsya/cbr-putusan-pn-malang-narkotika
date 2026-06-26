# Laporan Project CBR Putusan PN Malang Narkotika dan Psikotropika

## 1. Deskripsi Proyek

Project ini membangun sistem **Case-Based Reasoning (CBR)** sederhana berbasis Python untuk mendukung analisis putusan pengadilan. Data yang digunakan adalah **40 putusan pidana khusus narkotika dan psikotropika dari Pengadilan Negeri Malang**. Sistem ini bekerja dengan cara menyimpan putusan lama sebagai case base, lalu mencari kasus lama yang paling mirip ketika ada query kasus baru.

## 2. Tujuan

Tujuan utama project ini adalah:

1. Membangun case base dari 40 putusan PN Malang kategori narkotika dan psikotropika.
2. Membersihkan teks putusan agar siap diproses oleh model.
3. Mengekstrak metadata penting seperti nomor perkara, tanggal putus, terdakwa, penuntut umum, pasal, barang bukti, amar putusan, pidana penjara, dan denda.
4. Membangun fungsi retrieval untuk mencari top-5 putusan yang paling mirip dengan query kasus baru.
5. Mengambil amar putusan dari kasus termirip sebagai solusi awal.
6. Mengevaluasi hasil retrieval menggunakan metrik Top-1 Accuracy, Hit@5, Precision@5, Recall@5, dan F1@5.

## 3. Dataset

Dataset diperoleh dari Direktori Putusan Mahkamah Agung Republik Indonesia dengan filter:

- Pengadilan: PN Malang
- Klasifikasi: Pidana Khusus
- Kategori: Narkotika dan Psikotropika
- Jumlah data: 40 putusan
- Format awal: HTML
- Format hasil preprocessing: TXT, CSV, JSON

Ringkasan data:

| Indikator | Nilai |
|---|---:|
| Jumlah dokumen HTML | 40 |
| Jumlah teks bersih | 40 |
| Jumlah baris cases.csv | 40 |
| Rata-rata panjang teks | 361.12 kata |
| Putusan dengan pasal eksplisit | 4 |
| Putusan dengan denda terekstrak | 38 |

## 4. Tahap 1: Membangun Case Base

Pada tahap ini, 40 file HTML putusan dimasukkan ke folder `data/raw_html/`. Setelah itu, script `01_prepare_case_base.py` digunakan untuk mengubah HTML menjadi teks bersih dan menyimpannya ke folder `data/raw/`.

Preprocessing yang dilakukan:

1. Menghapus elemen non-teks seperti script, style, dan elemen tampilan web.
2. Mengambil bagian isi putusan dari halaman detail.
3. Menghapus footer, navigasi, statistik, dan bagian lain yang tidak dibutuhkan.
4. Melakukan normalisasi spasi dan karakter.
5. Menyimpan hasil sebagai `case_001.txt` sampai `case_040.txt`.

Output tahap ini:

- `data/raw_html/*.html`
- `data/raw/*.txt`
- `logs/cleaning.log`

## 5. Tahap 2: Case Representation

Setiap putusan direpresentasikan menjadi baris data terstruktur dalam `cases.csv`. Kolom yang digunakan meliputi:

- `case_id`
- `no_perkara`
- `tanggal_putus`
- `pengadilan`
- `jenis_perkara`
- `kategori`
- `terdakwa`
- `terdakwa_anon`
- `penuntut_umum`
- `pasal`
- `pasal_utama`
- `jenis_narkotika`
- `label_perbuatan`
- `dakwaan`
- `barang_bukti`
- `amar_putusan`
- `pidana_penjara`
- `denda`
- `ringkasan_fakta`
- `argumen_hukum_utama`
- `length_words`
- `text_full`

Output tahap ini:

- `data/processed/cases.csv`
- `data/processed/cases.json`
- `data/processed/case_solutions.json`

## 6. Tahap 3: Case Retrieval

Metode retrieval yang digunakan adalah **TF-IDF + Cosine Similarity**.

Alasan memilih TF-IDF:

1. Dataset hanya berjumlah 40 putusan sehingga TF-IDF cukup ringan dan efektif.
2. Teks putusan memiliki kata kunci hukum yang kuat, seperti pasal, narkotika, sabu, ganja, dakwaan, dan pidana penjara.
3. TF-IDF mudah dijelaskan dalam laporan dan sesuai dengan instruksi tugas.
4. Cosine similarity cocok untuk mengukur kemiripan antar dokumen teks.

Fungsi utama:

```python
def retrieve(query: str, k: int = 5):
    # preprocess query
    # ubah query menjadi vektor TF-IDF
    # hitung cosine similarity dengan seluruh case base
    # kembalikan top-k kasus paling mirip
```

Output tahap ini:

- `src/03_retrieval.py`
- Top-5 kasus termirip untuk setiap query

## 7. Tahap 4: Case/Solution Reuse

Pada tahap reuse, sistem mengambil solusi dari kasus lama yang paling mirip. Solusi yang digunakan adalah **amar putusan** dan informasi hukuman seperti pidana penjara dan denda.

Strategi reuse:

- Sistem mengambil top-5 kasus termirip.
- Kasus dengan skor similarity tertinggi dijadikan solusi utama.
- Amar putusan dari kasus tersebut digunakan sebagai rekomendasi solusi awal.

Output tahap ini:

- `src/04_predict.py`
- `data/results/predictions.csv`

## 8. Tahap 5: Evaluasi Model

Evaluasi dilakukan menggunakan query uji pada `data/eval/queries.json`. Setiap query memiliki ground truth case_id. Sistem dinilai berdasarkan apakah kasus yang benar muncul pada hasil retrieval.

Hasil evaluasi awal:

| Metrik | Nilai |
|---|---:|
| Jumlah query | 10 |
| Top-1 Accuracy | 1.00 |
| Hit@5 Accuracy | 1.00 |
| Macro Precision@5 | 0.20 |
| Macro Recall@5 | 1.00 |
| Macro F1@5 | 0.33 |

## 9. Analisis Kegagalan Model

Potensi kegagalan model dapat terjadi karena:

1. Banyak putusan memiliki kosakata yang sangat mirip karena berada pada domain narkotika yang sama.
2. Beberapa halaman HTML hanya memuat metadata dan catatan amar, bukan seluruh naskah putusan lengkap.
3. Beberapa pasal tidak selalu tertulis eksplisit dalam metadata, sehingga ekstraksi pasal bergantung pada isi catatan amar.
4. Nama barang bukti seperti sabu, ganja, ekstasi, dan obat keras dapat muncul pada beberapa kasus sekaligus sehingga model sulit membedakan kasus jika query terlalu umum.
5. TF-IDF belum memahami makna konteks secara mendalam seperti model embedding BERT.

## 10. Rekomendasi Perbaikan

Rekomendasi perbaikan:

1. Menggunakan PDF putusan lengkap jika tersedia agar bagian fakta hukum dan pertimbangan hakim lebih lengkap.
2. Menambahkan ekstraksi pasal berbasis regex yang lebih detail.
3. Menambahkan model embedding seperti IndoBERT untuk membandingkan performa dengan TF-IDF.
4. Membuat query uji yang lebih bervariasi dan divalidasi secara manual.
5. Menambahkan fitur khusus hukum seperti berat barang bukti, jenis narkotika, peran terdakwa, dan lama hukuman.

## 11. Kesimpulan

Project ini berhasil membangun sistem CBR sederhana untuk 40 putusan narkotika dan psikotropika PN Malang. Sistem telah mencakup tahapan case base, preprocessing, case representation, retrieval, solution reuse, dan evaluasi. Model TF-IDF + Cosine Similarity dapat digunakan untuk menemukan putusan lama yang mirip dengan query kasus baru dan mengambil amar putusan sebagai solusi awal.
