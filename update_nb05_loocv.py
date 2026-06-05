import json
import os

nb_path = r'd:\SEMESTER 6\Penalaran Komputer\sistem Case-Based Reasoning -\CBR_Hukum\notebooks\05_evaluation.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Evaluasi Realistis dengan LOOCV (Leave-One-Out Cross-Validation)\n",
            "\n",
            "Mengevaluasi model pada dataset berukuran kecil (62 kasus) dengan metode pembagian *Train-Test Split* konvensional (misal 80:20) akan sangat rawan mengalami **In-Sample Bias** dan **Overfitting**. Hal ini terbukti dari akurasi pengujian sebelumnya yang mencapai 100% karena model SVM menghafal seluruh data latih, dan data uji terlalu sedikit (hanya 12 kasus).\n",
            "\n",
            "Untuk mengukur performa prediksi **CBR Retrieval** yang sesungguhnya di dunia nyata, kita menerapkan **LOOCV**. Pada metode ini, kita melakukan simulasi sebanyak 62 iterasi. Di setiap iterasi:\n",
            "- $1$ kasus dikeluarkan dan diperlakukan sebagai **Query (Kasus Baru)**.\n",
            "- $61$ kasus sisanya menjadi **Knowledge Base (Kasus Terdahulu)**.\n",
            "- Kita mencari Top-5 kasus paling mirip dari 61 kasus tersebut menggunakan *Cosine Similarity*.\n",
            "- Sistem memprediksi label query tersebut menggunakan **Weighted Majority Voting**, lalu membandingkannya dengan label aslinya (*Ground Truth*)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from sklearn.metrics.pairwise import cosine_similarity\n",
            "import numpy as np\n",
            "\n",
            "loocv_results = []\n",
            "\n",
            "print(\"Memulai proses Leave-One-Out Cross Validation (LOOCV) untuk CBR Retrieval...\")\n",
            "for i in tqdm(range(len(df_cases)), desc=\"LOOCV Iterations\"):\n",
            "    # Ambil 1 kasus sebagai query test\n",
            "    query_index = i\n",
            "    query_case = df_cases.iloc[query_index]\n",
            "    query_tfidf = X_all_tfidf[query_index]\n",
            "    true_label = query_case['label']\n",
            "    \n",
            "    # Pisahkan sisa 61 kasus sebagai base knowledge\n",
            "    base_indices = [idx for idx in range(len(df_cases)) if idx != query_index]\n",
            "    base_cases = df_cases.iloc[base_indices].reset_index(drop=True)\n",
            "    base_tfidf = X_all_tfidf[base_indices]\n",
            "    \n",
            "    # Hitung Cosine Similarity\n",
            "    sim_scores = cosine_similarity(query_tfidf, base_tfidf).flatten()\n",
            "    \n",
            "    # Ambil Top-5\n",
            "    top_k = 5\n",
            "    top_indices = sim_scores.argsort()[::-1][:top_k]\n",
            "    \n",
            "    top_similarities = sim_scores[top_indices]\n",
            "    top_labels = base_cases.iloc[top_indices]['label'].values\n",
            "    top_case_ids = base_cases.iloc[top_indices]['case_id'].values\n",
            "    \n",
            "    # Prediksi dengan Weighted Majority Voting\n",
            "    score_dikabulkan = 0\n",
            "    score_ditolak = 0\n",
            "    \n",
            "    for j in range(top_k):\n",
            "        if top_labels[j] == 'dikabulkan':\n",
            "            score_dikabulkan += top_similarities[j]\n",
            "        else:\n",
            "            score_ditolak += top_similarities[j]\n",
            "            \n",
            "    pred_label = 'dikabulkan' if score_dikabulkan > score_ditolak else 'ditolak'\n",
            "    \n",
            "    loocv_results.append({\n",
            "        'case_id': query_case['case_id'],\n",
            "        'true_label': true_label,\n",
            "        'predicted_label': pred_label,\n",
            "        'correct': true_label == pred_label,\n",
            "        'top1_case_id': top_case_ids[0],\n",
            "        'top1_similarity': top_similarities[0],\n",
            "        'top_k_labels': list(top_labels)\n",
            "    })\n",
            "\n",
            "df_loocv = pd.DataFrame(loocv_results)\n",
            "print(\"LOOCV Selesai!\")"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Hitung Metrik LOOCV\n",
            "y_true_loocv = df_loocv['true_label']\n",
            "y_pred_loocv = df_loocv['predicted_label']\n",
            "\n",
            "acc_loocv = accuracy_score(y_true_loocv, y_pred_loocv)\n",
            "prec_loocv = precision_score(y_true_loocv, y_pred_loocv, average='macro', zero_division=0)\n",
            "rec_loocv = recall_score(y_true_loocv, y_pred_loocv, average='macro', zero_division=0)\n",
            "f1_loocv = f1_score(y_true_loocv, y_pred_loocv, average='macro', zero_division=0)\n",
            "\n",
            "# Hitung Top-K Retrieval Accuracy\n",
            "def top_k_accuracy(k):\n",
            "    correct = 0\n",
            "    for idx, row in df_loocv.iterrows():\n",
            "        if row['true_label'] in row['top_k_labels'][:k]:\n",
            "            correct += 1\n",
            "    return correct / len(df_loocv)\n",
            "\n",
            "top1_acc = top_k_accuracy(1)\n",
            "top3_acc = top_k_accuracy(3)\n",
            "top5_acc = top_k_accuracy(5)\n",
            "\n",
            "print(\"=== HASIL EVALUASI CBR RETRIEVAL (LOOCV) ===\")\n",
            "print(f\"Accuracy : {acc_loocv*100:.2f}%\")\n",
            "print(f\"Precision (macro): {prec_loocv:.4f}\")\n",
            "print(f\"Recall (macro)   : {rec_loocv:.4f}\")\n",
            "print(f\"F1-Score (macro) : {f1_loocv:.4f}\")\n",
            "print(\"-\" * 40)\n",
            "print(f\"Top-1 Retrieval Accuracy: {top1_acc*100:.2f}%\")\n",
            "print(f\"Top-3 Retrieval Accuracy: {top3_acc*100:.2f}%\")\n",
            "print(f\"Top-5 Retrieval Accuracy: {top5_acc*100:.2f}%\")\n",
            "print(\"\\nClassification Report:\")\n",
            "print(classification_report(y_true_loocv, y_pred_loocv, zero_division=0))"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Visualisasi: Confusion Matrix LOOCV\n",
            "cm_loocv = confusion_matrix(y_true_loocv, y_pred_loocv, labels=svm_model.classes_)\n",
            "plt.figure(figsize=(8, 6))\n",
            "sns.heatmap(cm_loocv, annot=True, fmt='d', cmap='OrRd', \n",
            "            xticklabels=svm_model.classes_, yticklabels=svm_model.classes_,\n",
            "            linewidths=.5, cbar_kws={\"shrink\": .8})\n",
            "plt.title(\"Confusion Matrix - CBR Retrieval (LOOCV)\", fontsize=16, pad=15)\n",
            "plt.ylabel('Actual Solutions (Ground Truth)', fontsize=12)\n",
            "plt.xlabel('Predicted Solutions', fontsize=12)\n",
            "plt.xticks(rotation=45, ha='right')\n",
            "plt.tight_layout()\n",
            "plt.savefig(os.path.join(eval_dir, 'loocv_confusion_matrix.png'), dpi=150)\n",
            "plt.show()\n",
            "\n",
            "# Visualisasi: LOOCV vs In-Sample\n",
            "metrics_comp = {\n",
            "    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],\n",
            "    'In-Sample (SVM)': [prediction_metrics[\"Accuracy\"], prediction_metrics[\"Precision\"], prediction_metrics[\"Recall\"], prediction_metrics[\"F1-Score\"]],\n",
            "    'Real-World (LOOCV)': [acc_loocv, prec_loocv, rec_loocv, f1_loocv]\n",
            "}\n",
            "df_comp = pd.DataFrame(metrics_comp)\n",
            "df_comp_melted = df_comp.melt(id_vars='Metric', var_name='Evaluation Method', value_name='Score')\n",
            "\n",
            "plt.figure(figsize=(10, 6))\n",
            "ax = sns.barplot(x='Metric', y='Score', hue='Evaluation Method', data=df_comp_melted, palette='viridis')\n",
            "plt.ylim(0, 1.1)\n",
            "for p in ax.patches:\n",
            "    ax.annotate(f\"{p.get_height():.2f}\", (p.get_x() + p.get_width() / 2., p.get_height()), \n",
            "                ha='center', va='bottom', fontsize=10, xytext=(0, 5), textcoords='offset points')\n",
            "plt.title(\"Perbandingan Metrik: In-Sample vs Real-World (LOOCV)\", fontsize=16)\n",
            "plt.tight_layout()\n",
            "plt.savefig(os.path.join(eval_dir, 'loocv_vs_insample.png'), dpi=150)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Simpan Hasil Metrik dan Detail LOOCV\n",
            "df_comp.to_csv(os.path.join(eval_dir, 'loocv_metrics.csv'), index=False)\n",
            "\n",
            "df_loocv_save = df_loocv.drop(columns=['top_k_labels']) # drop list column for cleaner CSV\n",
            "df_loocv_save.to_csv(os.path.join(eval_dir, 'loocv_detail.csv'), index=False)\n",
            "\n",
            "print(\"File visualisasi dan metrik LOOCV telah berhasil disimpan ke folder 'data/eval/'\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. Analisis Diskusi LOOCV & Error Analysis\n",
            "\n",
            "### Kenapa LOOCV?\n",
            "Berdasarkan grafik batang di atas, terlihat perbedaan antara metrik pengujian *In-Sample* dengan hasil LOOCV. Hasil *In-Sample* cenderung mengarah pada angka sempurna (1.0) karena model telah menghafal seluruh pola dari data yang sama. Skor **Real-World (LOOCV)** adalah ukuran yang jauh lebih jujur untuk menggambarkan bagaimana sistem CBR kita akan merespons kasus baru yang benar-benar belum pernah dilihatnya.\n",
            "\n",
            "### Error Analysis (Penyebab Prediksi Meleset)\n",
            "Sistem CBR berbasis teks (NLP Tradisional TF-IDF) memiliki sensitivitas tinggi terhadap *vocabulary overlap*. Jika suatu gugatan yang aslinya \"ditolak\" (misal *case_id* X) memiliki banyak kata repetitif yang menyerupai gugatan yang \"dikabulkan\" (seperti uraian mahar, pekerjaan, alamat), maka *Cosine Similarity* akan menganggap kasus tersebut mirip dengan kasus \"dikabulkan\", sehingga sistem tertipu dalam tahap *Weighted Majority Voting*.\n",
            "\n",
            "### Bias pada Kelas Minoritas\n",
            "Mengingat dataset hukum kita sangat *imbalanced* (46 Dikabulkan vs 16 Ditolak), kemungkinan besar persentase salah tebak pada kelas \"ditolak\" (*false positives*) lebih tinggi. Ini membuktikan bahwa menambah variasi putusan NO/Ditolak secara berkala adalah kunci utama untuk membuat *Knowledge Base* CBR kita semakin kebal terhadap *Imbalanced Data Bias*."
        ]
    }
]

nb['cells'].extend(new_cells)

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Berhasil menginjeksi kode LOOCV ke 05_evaluation.ipynb!")
