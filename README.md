# CBR Hukum: Sistem Case-Based Reasoning untuk Putusan Pengadilan Agama

Proyek ini merupakan implementasi utuh dari sistem **Case-Based Reasoning (CBR)** berbasis *Machine Learning* dan *Natural Language Processing* (NLP) untuk menganalisis dan mengklasifikasikan dokumen hukum perdata agama di Indonesia (khususnya putusan **Cerai Gugat**).

Sistem ini dirancang secara sistematis ke dalam 5 tahapan untuk mencocokkan kasus hukum baru (*query*) dengan perpustakaan kasus terdahulu (*case base*) menggunakan pendekatan tekstual, lalu memberikan prediksi putusan secara otomatis.

---

## 🚀 Pendekatan & Algoritma Utama
Sistem ini beroperasi dengan ekosistem algoritma yang sangat efisien dan ringan (*lightweight*):
- **TF-IDF Vectorization:** Untuk membobotkan dan mengekstrak kosa kata legal (seperti "nafkah", "KDRT", "ekonomi") menjadi representasi ruang vektor (*Vector Space*).
- **Cosine Similarity:** Digunakan sebagai pengukur kemiripan (*distance metric*) pada fase *Retrieval* guna menemukan top-K kasus terdahulu yang secara esensial sama dengan masalah baru.
- **Support Vector Machine (LinearSVC):** Digunakan untuk klasifikasi pola dokumen serta mendukung hibridisasi prediksi.
- **Weighted Similarity Voting:** Mekanisme *Reuse* yang memberikan prediksi akhir berdasarkan mayoritas label berbobot tingkat kemiripan dari hasil *Retrieval*.

---

## 📂 Struktur Direktori Proyek

```text
CBR_Hukum/
│
├── data/
│   ├── raw/          # Berkas putusan PDF asli dan ekstraksi teks kasar
│   ├── processed/    # Teks bersih (_clean.txt) dan Metadata Utama (cases.csv)
│   ├── eval/         # Data uji (queries.json) dan hasil metrik evaluasi (.csv)
│   └── results/      # Hasil output (predictions.csv)
│
├── notebooks/        # Jupyter Notebook eksekusi utama sistem (Tahap 1 - 5)
├── models/           # Ekspor *Persistence Model* (tfidf_vectorizer.pkl & svm_classifier.pkl)
├── logs/             # Catatan *error handling* dan ekstraksi
│
├── requirements.txt  # Daftar dependensi modul Python
└── README.md         # Dokumentasi utama proyek (berkas ini)
```

---

## 📚 Tahapan Eksekusi (Pipeline)

Sistem telah dipecah secara rapi ke dalam 5 buah *Jupyter Notebook* untuk kemudahan *testing* dan evaluasi akademis. Eksekusi program harus dilakukan secara berurutan:

### 1. `01_extract.ipynb` (Tahap 1: Membangun Case Base)
Fokus pada ekstraksi teks dari PDF menggunakan `pdfplumber` dan membersihkan tanda baca hukum, *stopword* (serta kustom stopword pengadilan), hingga *stemming* (menggunakan `Sastrawi`).

### 2. `02_Case_Representation.ipynb` (Tahap 2: Representasi Kasus)
Menjalankan *RegEx* canggih untuk membedah dokumen PDF menjadi Metadata yang berguna: *Nomor Perkara*, *Tanggal*, *Pihak*, *Amar Putusan*, dan mengekstrak otomatis alasan/faktor perceraian. Hasilnya digabung ke dalam master dataset `cases.csv`.

### 3. `03_retrieval.ipynb` (Tahap 3: Case Retrieval)
Membentuk Model **TF-IDF** dan **SVM**. Mengonversi seluruh `cases.csv` menjadi dimensi vektor, lalu membangun fungsi *Retrieval* Cosine Similarity untuk menghasilkan fungsi komputasi kedekatan antar teks. Model ini kemudian diekspor ke folder `/models/`.

### 4. `04_predict.ipynb` (Tahap 4: Case Solution Reuse)
Sistem penalaran CBR sejati. Fungsi ini menerima *"kueri"* permasalahan rumah tangga (contoh: *"suami selingkuh dan sering memukul"*), mencari dokumen historis terkait (dari Tahap 3), dan menggunakan **Weighted Similarity Voting** untuk meramalkan nasib amar putusannya (misal: *'Dikabulkan'*).

### 5. `05_evaluation.ipynb` (Tahap 5: Model Evaluation)
Analisis kuantitatif secara mendalam. Modul ini menghitung performa Mesin Pencari (*Top-K Accuracy, Precision@K*) dan Klasifikasi Prediksi (*Accuracy, Precision, Recall, F1-Score*). Lengkap dengan visualisasi *Confusion Matrix* dan draf Akademis (*Error Analysis*) siap lampir ke laporan.

---

## 🛠️ Instalasi & Persiapan Lingkungan

1. **Persyaratan Sistem:**
   * Python 3.8 ke atas (Direkomendasikan Python 3.10+)
   * Lingkungan *Jupyter Notebook* (Google Colab / VS Code)

2. **Instalasi Dependensi:**
   Instal seluruh pustaka yang dipersyaratkan:
   ```bash
   pip install -r requirements.txt
   ```

3. **Cara Menjalankan:**
   Arahkan kursor Anda ke dalam direktori `notebooks/`, lalu mulailah mengeksekusi dari modul `01_extract.ipynb` ke tahapan berikutnya secara *Run All Cells*.
