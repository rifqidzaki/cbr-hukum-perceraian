import nbformat
import sys
import os

nb_path = "notebooks/05_evaluation.ipynb"
try:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
except Exception as e:
    print(f"Error reading notebook: {e}")
    sys.exit(1)

new_cells = []

# 1. Markdown: Error Analysis
md_error_analysis = """## 6. Error Analysis (Analisis Kesalahan Akademik)

Dalam konteks *Case-Based Reasoning* pada domain hukum, evaluasi tidak hanya sebatas akurasi numerik, namun juga pemahaman *mengapa* sebuah retrieval atau prediksi bisa gagal. Berikut adalah beberapa faktor utama yang diidentifikasi:

### A. Retrieval Failures (Kegagalan Pencarian Kasus Serupa)
1. **Keyword Mismatch & Out-of-Vocabulary (OOV)**: Karena menggunakan TF-IDF (Bag-of-Words), sistem kesulitan jika *query* menggunakan sinonim yang tidak ada di *Case Base*. Misalnya, query menggunakan kata "KDRT", sedangkan putusan lama menggunakan kata "dipukul" atau "dianiaya". *Cosine Similarity* akan merespon dengan nilai kedekatan yang rendah.
2. **Dokumen Terlalu Mirip (Boilerplate Overlap)**: Teks hukum sangat *repetitif*. Frasa seperti "MENGADILI", "Menimbang bahwa", "Berdasarkan Pasal..." mendominasi *vector space* jika tidak ditangani dengan *stopwords* yang sangat agresif, menyebabkan kasus yang substansinya berbeda terlihat "mirip" secara matematis.

### B. Prediction Failures (Kegagalan Prediksi Solusi)
1. **Noise OCR (Optical Character Recognition)**: Dokumen hukum di Indonesia (terutama PDF lama) sering berupa hasil *scan* yang buram, menyebabkan *watermark* atau huruf terpecah (misal: "S e k r e t a r i s"). Hal ini merusak proses tokenisasi dan *stemming*.
2. **Imbalanced Dataset & Label Bias**: Kasus Perdata Agama (Cerai Gugat) memiliki probabilitas tinggi untuk "Dikabulkan". Model SVM dan sistem *Majority Voting* cenderung bias ke kelas mayoritas. Kasus yang unik (dimana gugatan "Ditolak") sangat jarang masuk ke Top-K *Retrieval*, sehingga menyulitkan prediksi yang bersifat anomali.
"""
new_cells.append(nbformat.v4.new_markdown_cell(md_error_analysis))


# 2. Code: Similarity Distribution & Top TF-IDF Features
code_sim_tfidf = """# --- TAMBAHAN VISUALISASI ---
# 1. Distribusi Cosine Similarity (Keseluruhan Dataset)
similarity_matrix = cosine_similarity(X_all_tfidf)
sim_scores = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]

plt.figure(figsize=(10, 5))
sns.histplot(sim_scores, bins=50, kde=True, color='teal')
plt.title('Distribusi Cosine Similarity Antar Dokumen (Keseluruhan Case Base)', fontsize=14)
plt.xlabel('Cosine Similarity Score', fontsize=12)
plt.ylabel('Frekuensi', fontsize=12)
plt.axvline(np.mean(sim_scores), color='red', linestyle='dashed', linewidth=2, label=f'Mean: {np.mean(sim_scores):.2f}')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(eval_dir, 'similarity_distribution.png'), dpi=150)
plt.show()

# 2. Top-20 TF-IDF Features (Kata yang Paling Berpengaruh dalam Penentuan Kemiripan)
feature_names = tfidf_vectorizer.get_feature_names_out()
avg_tfidf_scores = np.asarray(X_all_tfidf.mean(axis=0)).ravel()
top_idx = avg_tfidf_scores.argsort()[-20:]
top_features = [feature_names[i] for i in top_idx]
top_scores = avg_tfidf_scores[top_idx]

plt.figure(figsize=(12, 8))
sns.barplot(x=top_scores, y=top_features, palette='viridis')
plt.title('Top 20 Fitur/Kata Berdasarkan Rata-Rata Bobot TF-IDF', fontsize=15)
plt.xlabel('Rata-Rata Bobot TF-IDF', fontsize=12)
plt.ylabel('Token (Kata)', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(eval_dir, 'top_tfidf_features.png'), dpi=150)
plt.show()
"""
new_cells.append(nbformat.v4.new_code_cell(code_sim_tfidf))

# 3. Markdown: Kelebihan dan Kekurangan
md_pros_cons = """## 7. Analisis Kelebihan dan Kekurangan (Pros & Cons)

### ✅ Kelebihan (Pros)
* **Sangat Ringan dan Cepat (Lightweight)**: Tidak membutuhkan *hardware accelerator* seperti GPU. Cocok untuk *deployment* di server dengan *resource* rendah.
* **Stabilitas Tinggi pada Data Repetitif (Boilerplate)**: TF-IDF justru diuntungkan pada domain hukum karena kosakata (leksikon) hukum bersifat formal dan konsisten.
* **Explainability (Bisa Dijelaskan)**: Dalam Legal-Tech, keputusan AI harus bisa dijelaskan (*Explainable AI*). Dengan TF-IDF, kita bisa melacak tepat kata apa yang membuat dua dokumen dianggap "mirip". Hal ini sulit dilakukan jika menggunakan *Large Language Models (LLM)*.

### ❌ Kekurangan (Cons)
* **Keterbatasan Semantic Understanding (Lexical Gap)**: *Retrieval* murni berbasis *keyword* eksak. Model tidak memahami bahwa "selingkuh", "wanita idaman lain", dan "WIL" merujuk pada konsep yang sama jika tidak diakali pada fase *preprocessing*.
* **Sensitivitas Tinggi terhadap Preprocessing**: Satu tahap pembersihan (misal: *stopwords removal*) yang terlewat dapat merusak seluruh matriks vektor dan menjatuhkan akurasi *retrieval* secara drastis.
"""
new_cells.append(nbformat.v4.new_markdown_cell(md_pros_cons))

# Cek apakah sudah ditambahkan sebelumnya (menghindari duplikasi)
has_added = False
for cell in nb['cells']:
    if cell['cell_type'] == 'markdown' and '## 6. Error Analysis' in cell['source']:
        has_added = True
        break

if not has_added:
    nb['cells'].extend(new_cells)
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print("Successfully added Analysis and Visualization to 05_evaluation.ipynb")
else:
    print("Cells already exist in 05_evaluation.ipynb, skipping to avoid duplication.")
