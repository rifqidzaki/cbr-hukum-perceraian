import nbformat
import sys

nb_path = "notebooks/02_Case_Representation.ipynb"

try:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
except Exception as e:
    print(f"Error reading notebook: {e}")
    sys.exit(1)

new_cell_content = """def extract_metadata(raw_text):
    meta = {
        "no_perkara": "tidak ditemukan",
        "tanggal": "tidak ditemukan",
        "jenis_perkara": "Cerai Gugat",
        "pihak": "Penggugat vs Tergugat",
        "pasal": "tidak ditemukan",
        "amar_putusan": "tidak ditemukan",
        "alasan_perceraian": "tidak ditemukan",
        "ringkasan_fakta": "tidak ditemukan"
    }
    
    import re
    # 1. Nomor Perkara
    match_no = re.search(r'Nomor\\s*[:]?\\s*(\\d+/Pdt\\.G/(\\d{4})/PA\\.[A-Za-z.]+)', raw_text, re.IGNORECASE)
    tahun_perkara = None
    if match_no:
        meta["no_perkara"] = match_no.group(1)
        tahun_perkara = match_no.group(2)
        
    # 2. Tanggal Putusan (IMPROVED)
    # Cari pola tanggal putusan spesifik (di bagian akhir dokumen)
    match_tgl_spesifik = re.search(r'(?:diucapkan|diputuskan|dibacakan).*?tanggal\\s+(\\d{1,2}\\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\\s+\\d{4})', raw_text, re.IGNORECASE | re.DOTALL)
    
    if match_tgl_spesifik:
        meta["tanggal"] = match_tgl_spesifik.group(1)
    else:
        # Fallback: ambil semua tanggal
        all_dates = re.findall(r'tanggal\\s+(\\d{1,2}\\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\\s+(\\d{4}))', raw_text, re.IGNORECASE)
        if all_dates:
            if tahun_perkara:
                # Prioritaskan tanggal dengan tahun yang sama/lebih baru dari tahun perkara
                valid_dates = [d for d in all_dates if int(d[1]) >= int(tahun_perkara)]
                if valid_dates:
                    meta["tanggal"] = valid_dates[-1][0] # Ambil yang terakhir (biasanya putusan)
                else:
                    meta["tanggal"] = all_dates[-1][0]
            else:
                meta["tanggal"] = all_dates[-1][0]
                
    # 3. Pasal
    pasal_matches = re.findall(r'(Pasal\\s+\\d+[^\\n.,]{0,60})', raw_text, re.IGNORECASE)
    if pasal_matches:
        unique_pasal = list(set(pasal_matches))[:3]
        meta["pasal"] = ", ".join(unique_pasal)
        
    # 4. Amar Putusan (setelah MENGADILI)
    match_amar = re.search(r'M\\s*E\\s*N\\s*G\\s*A\\s*D\\s*I\\s*L\\s*I(.*?)(?:Demikian|Ketua Majelis|yang menjatuhkan)', raw_text, re.IGNORECASE | re.DOTALL)
    if match_amar:
        amar = match_amar.group(1).strip()
        amar_clean = re.sub(r'\\s+', ' ', amar)
        meta["amar_putusan"] = amar_clean[:500] + "..." if len(amar_clean) > 500 else amar_clean
        
    # 5. Alasan Perceraian
    alasan_keywords = {
        "pertengkaran": ["pertengkaran", "perselisihan", "cekcok", "bertengkar", "tidak harmonis"],
        "ekonomi": ["ekonomi", "nafkah", "tidak memberi", "tidak mampu"],
        "meninggalkan": ["meninggalkan", "pergi", "pulang"],
        "kekerasan": ["kekerasan", "kdrt", "memukul", "menganiaya", "dipukul"],
        "selingkuh": ["selingkuh", "wanita lain", "pria lain", "berselingkuh", "zina"],
        "mabuk": ["mabuk", "minum-minuman", "minuman keras", "miras"],
        "judi": ["judi", "berjudi", "perjudian"]
    }
    
    raw_lower = raw_text.lower()
    alasan_ditemukan = []
    for kategori, keywords in alasan_keywords.items():
        for kw in keywords:
            if kw in raw_lower:
                alasan_ditemukan.append(kategori)
                break
    
    if alasan_ditemukan:
        meta["alasan_perceraian"] = ", ".join(alasan_ditemukan)
        meta["ringkasan_fakta"] = f"Perceraian didasari oleh faktor: {', '.join(alasan_ditemukan)}."
    else:
        meta["alasan_perceraian"] = "Perselisihan/Tidak diketahui"
        meta["ringkasan_fakta"] = "Gugatan cerai diajukan atas dasar ketidakharmonisan rumah tangga."

    return meta

def label_amar(text):
    \"\"\"Mengklasifikasikan teks amar putusan menjadi label kategorikal.\"\"\"
    text = str(text).lower()
    if 'sebagian' in text and 'kabul' in text:
        return 'dikabulkan sebagian'
    elif 'kabul' in text:
        return 'dikabulkan'
    elif 'tolak' in text or 'gugur' in text or 'tidak dapat diterima' in text or 'batal' in text:
        return 'ditolak'
    else:
        return 'dikabulkan'  # Default: mayoritas cerai gugat dikabulkan

print("Fungsi Ekstraksi Metadata & Label Siap (IMPROVED)!")
"""

# Find the cell containing extract_metadata and replace it
found = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'def extract_metadata' in ''.join(cell['source']):
        cell['source'] = new_cell_content
        found = True
        break

if found:
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print("Successfully updated extract_metadata function in 02_Case_Representation.ipynb")
else:
    print("Could not find the extract_metadata function in the notebook!")
    sys.exit(1)
