import json
import re

nb_path = 'notebooks/02_Case_Representation.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_code = r"""def extract_metadata(raw_text):
    meta = {
        "no_perkara": "tidak ditemukan",
        "tanggal": "tidak ditemukan",
        "jenis_perkara": "Cerai Gugat",
        "pihak": "tidak ditemukan",
        "pasal": "tidak ditemukan",
        "amar_putusan": "tidak ditemukan",
        "alasan_perceraian": "tidak ditemukan",
        "ringkasan_fakta": "tidak ditemukan"
    }
    
    import re
    # 1. Nomor Perkara
    match_no = re.search(r'Nomor\s*[:]?\s*(\d+/Pdt\.G/(\d{4})/PA\.[A-Za-z.]+)', raw_text, re.IGNORECASE)
    tahun_perkara = None
    if match_no:
        meta["no_perkara"] = match_no.group(1)
        tahun_perkara = match_no.group(2)
        
    # 2. Tanggal Putusan
    match_tgl_spesifik = re.search(r'(?:diucapkan|diputuskan|dibacakan).*?tanggal\s+(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})', raw_text, re.IGNORECASE | re.DOTALL)
    
    if match_tgl_spesifik:
        meta["tanggal"] = match_tgl_spesifik.group(1)
    else:
        all_dates = re.findall(r'tanggal\s+(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+(\d{4}))', raw_text, re.IGNORECASE)
        if all_dates:
            if tahun_perkara:
                valid_dates = [d for d in all_dates if int(d[1]) >= int(tahun_perkara)]
                if valid_dates:
                    meta["tanggal"] = valid_dates[-1][0]
                else:
                    meta["tanggal"] = all_dates[-1][0]
            else:
                meta["tanggal"] = all_dates[-1][0]
                
    # 3. Pasal
    pasal_matches = re.findall(r'(Pasal\s+\d+[^\n.,]{0,60})', raw_text, re.IGNORECASE)
    if pasal_matches:
        unique_pasal = list(set(pasal_matches))[:3]
        meta["pasal"] = ", ".join(unique_pasal)
        
    # 4. Amar Putusan
    # Ambil kemunculan "MENGADILI" yang terakhir (karena putusan asli ada di bawah)
    matches_amar = re.findall(r'M\s*E\s*N\s*G\s*A\s*D\s*I\s*L\s*I\s*[:;]?(.*?)(?:Demikian|Ketua Majelis|Ditetapkan|Panitera)', raw_text, re.IGNORECASE | re.DOTALL)
    if matches_amar:
        amar = matches_amar[-1].strip()
        amar_clean = re.sub(r'\s+', ' ', amar)
        meta["amar_putusan"] = amar_clean[:1000] + "..." if len(amar_clean) > 1000 else amar_clean
        
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

    # 6. Pihak
    penggugat = None
    tergugat = None

    def clean_name(n):
        if not n: return None
        n = n.replace('\n', ' ')
        n = re.sub(r'(?i)\b(umur|bin\b|binti\b|tempat|agama|pendidikan|pekerjaan|selanjutnya|disebut|sebagai).*', '', n)
        n = re.sub(r'\b[a-zA-Z]\b', '', n)
        n = re.sub(r'\s+', ' ', n)
        n = n.strip(' \n\r\t,;:')
        if len(n) < 3: return None
        return n.upper()

    m2 = re.search(r'antara\s*:\s*(.*?)\s+(?:melawan|lawan)\s+(.*?)(?:\s+sebagai|\n|;)', raw_text, re.IGNORECASE | re.DOTALL)
    if m2:
        penggugat = clean_name(m2.group(1))
        tergugat = clean_name(m2.group(2))

    if not penggugat:
        m3_p = re.search(r'(?:PENGGUGAT|PEMOHON)\s*,\s*(.*?)(?:,)', raw_text, re.IGNORECASE)
        if m3_p: penggugat = clean_name(m3_p.group(1))
    if not tergugat:
        m3_t = re.search(r'(?:TERGUGAT|TERMOHON)\s*,\s*(.*?)(?:,)', raw_text, re.IGNORECASE)
        if m3_t: tergugat = clean_name(m3_t.group(1))

    m1_p = re.search(r'([A-Za-z\s.,]{5,50})\s+sebagai\s+Penggugat', raw_text, re.IGNORECASE)
    m1_t = re.search(r'([A-Za-z\s.,]{5,50})\s+sebagai\s+Tergugat', raw_text, re.IGNORECASE)
    if not penggugat and m1_p:
        penggugat = clean_name(m1_p.group(1))
    if not tergugat and m1_t:
        tergugat = clean_name(m1_t.group(1))

    if penggugat and tergugat:
        meta["pihak"] = f"{penggugat} vs {tergugat}"
    elif penggugat:
        meta["pihak"] = f"{penggugat} vs Tergugat"
    elif tergugat:
        meta["pihak"] = f"Penggugat vs {tergugat}"
    else:
        meta["pihak"] = "tidak ditemukan"

    return meta

def label_amar(text):
    text = str(text).lower()
    # Prioritaskan Ditolak/NO
    if 'tidak dapat diterima' in text or 'tidak diterima' in text or 'menolak gugatan' in text or 'gugatan penggugat ditolak' in text or 'batal' in text:
        return 'ditolak'
    elif 'menolak permohonan' in text or 'menolak eksepsi' in text and 'mengadili sendiri' in text:
        return 'ditolak'
    elif 'sebagian' in text and 'kabul' in text:
        return 'dikabulkan sebagian'
    elif 'kabul' in text or 'mengabulkan' in text:
        return 'dikabulkan'
    elif 'tolak' in text or 'gugur' in text:
        return 'ditolak'
    else:
        # Default fallback tapi coba cek kata NO (Niet Ontvankelijk)
        if 'niet ontvankelijk' in text or 'n.o' in text:
            return 'ditolak'
        return 'dikabulkan'

print("Fungsi Ekstraksi Metadata & Label Siap (IMPROVED AMAR EXTRACTION)!")
"""

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if 'def extract_metadata(raw_text):' in source:
            cell['source'] = [line + '\n' for line in new_code.split('\n')]
            break

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Berhasil mengupdate 02_Case_Representation.ipynb dengan perbaikan ekstrak amar!")
