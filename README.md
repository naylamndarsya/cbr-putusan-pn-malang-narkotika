# Case-Based Reasoning untuk Putusan PN Malang: Narkotika dan Psikotropika

Project ini dibuat untuk tugas SubCPMK-3 Penalaran Komputer. Sistem menerapkan siklus **Case-Based Reasoning (CBR)** untuk mendukung analisis 40 putusan pidana khusus narkotika dan psikotropika dari Pengadilan Negeri Malang.

## Ringkasan Project

- Domain hukum: Pidana Khusus Narkotika dan Psikotropika
- Pengadilan: PN Malang
- Jumlah dokumen: 40 HTML putusan
- Representasi dokumen: TF-IDF
- Retrieval: Cosine Similarity
- Reuse solusi: Weighted similarity dari kasus paling mirip
- Evaluasi: Top-1 Accuracy, Hit@5, Precision@5, Recall@5, F1@5

## Struktur Folder

```text
/data/
  /raw_html/       # 40 file HTML putusan asli
  /raw/            # hasil konversi HTML menjadi teks bersih
  /processed/      # cases.csv, cases.json, case_solutions.json
  /eval/           # queries.json, retrieval_metrics.csv, prediction_metrics.csv
  /results/        # predictions.csv
/src/              # script per tahap CBR
/notebooks/        # notebook demo project
/docs/             # laporan ringkas
/logs/             # cleaning.log
requirements.txt
README.md
```

## Cara Install

```bash
pip install -r requirements.txt
```

## Cara Menjalankan Pipeline End-to-End

Jalankan dari folder utama repository:

```bash
python src/01_prepare_case_base.py
python src/02_case_representation.py
python src/03_retrieval.py --query "terdakwa menguasai sabu dan didakwa narkotika" --k 5
python src/04_predict.py --query "terdakwa menjadi perantara jual beli sabu" --k 5
python src/05_evaluation.py
```

## Output Utama

1. `data/raw/*.txt` berisi teks bersih dari setiap putusan.
2. `data/processed/cases.csv` berisi metadata dan fitur teks dari 40 putusan.
3. `data/processed/case_solutions.json` berisi mapping solusi/amar putusan.
4. `data/results/predictions.csv` berisi hasil prediksi solusi dari query uji.
5. `data/eval/retrieval_metrics.csv` dan `data/eval/prediction_metrics.csv` berisi hasil evaluasi.

## Tahapan CBR

### 1. Membangun Case Base
40 putusan HTML dikumpulkan dari Direktori Putusan MA kategori PN Malang - Narkotika dan Psikotropika, lalu dikonversi menjadi teks bersih.

### 2. Case Representation
Setiap putusan direpresentasikan menjadi struktur data dengan metadata seperti nomor perkara, tanggal putus, pengadilan, terdakwa, penuntut umum, pasal, barang bukti, amar putusan, pidana penjara, denda, ringkasan fakta, dan teks penuh.

### 3. Case Retrieval
Sistem menggunakan TF-IDF untuk mengubah teks menjadi vektor, lalu menghitung cosine similarity antara query kasus baru dan seluruh case base.

### 4. Case/Solution Reuse
Dari top-5 kasus termirip, sistem mengambil amar putusan dari kasus dengan skor similarity tertinggi sebagai solusi awal.

### 5. Model Evaluation
Evaluasi dilakukan menggunakan query uji pada `data/eval/queries.json`. Metrik yang digunakan adalah Top-1 Accuracy, Hit@5, Precision@5, Recall@5, dan F1@5.

## Catatan Etika Data

Nama terdakwa berasal dari dokumen publik. Untuk laporan dan presentasi, disarankan menggunakan kolom `terdakwa_anon` agar analisis tetap berfokus pada pola putusan, bukan identitas personal.
