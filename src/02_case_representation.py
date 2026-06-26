from pathlib import Path
import json
import pandas as pd
from cbr_utils import *

PROJECT = Path(__file__).resolve().parents[1]
RAW_HTML = PROJECT / 'data' / 'raw_html'
PROCESSED = PROJECT / 'data' / 'processed'
PROCESSED.mkdir(parents=True, exist_ok=True)

rows = []
for idx, p in enumerate(sorted(RAW_HTML.glob('case_*.html')), start=1):
    case_id = f'case_{idx:03d}'
    lines, source_url = html_to_lines(p)
    full_clean = norm_space(' '.join(content_lines(lines)))
    catatan = get_block(lines, 'Catatan Amar')
    pasal = extract_pasals(catatan)
    denda_text, denda_val = extract_denda(catatan)
    penuntut = ''
    terdakwa = ''
    for i, l in enumerate(lines):
        if l.startswith('Penuntut Umum') and i + 1 < len(lines):
            penuntut = lines[i + 1]
        if l.startswith('Terdakwa') and i + 1 < len(lines):
            terdakwa = lines[i + 1]
    row = {
        'case_id': case_id,
        'file_name': f'{case_id}.html',
        'source_url': source_url,
        'no_perkara': get_after(lines, 'Nomor'),
        'tanggal_putus': get_title_date(lines),
        'tanggal_register': parse_date(get_after(lines, 'Tanggal Register')),
        'tahun': get_after(lines, 'Tahun'),
        'pengadilan': get_after(lines, 'Lembaga Peradilan'),
        'jenis_perkara': get_after(lines, 'Klasifikasi'),
        'kategori': 'Narkotika dan Psikotropika',
        'kata_kunci': get_after(lines, 'Kata Kunci'),
        'terdakwa': terdakwa,
        'terdakwa_anon': f'Terdakwa_{idx:03d}',
        'penuntut_umum': penuntut,
        'hakim_ketua': get_after(lines, 'Hakim Ketua'),
        'hakim_anggota': get_after(lines, 'Hakim Anggota'),
        'panitera': get_after(lines, 'Panitera'),
        'pasal': pasal,
        'pasal_utama': pasal_utama(pasal),
        'jenis_narkotika': jenis_narkotika(catatan),
        'label_perbuatan': label_perbuatan(catatan),
        'dakwaan': extract_dakwaan(catatan),
        'barang_bukti': extract_barang_bukti(catatan),
        'amar': get_after(lines, 'Amar'),
        'amar_lainnya': get_after(lines, 'Amar Lainnya'),
        'amar_putusan': catatan,
        'pidana_penjara': extract_pidana_phrase(catatan),
        'denda': denda_text,
        'denda_rupiah': denda_val,
        'ringkasan_fakta': summarize(catatan, 80),
        'argumen_hukum_utama': extract_dakwaan(catatan) or summarize(catatan, 45),
        'length_words': len(full_clean.split()),
        'text_full': full_clean,
    }
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(PROCESSED / 'cases.csv', index=False, encoding='utf-8-sig')
with open(PROCESSED / 'cases.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
solutions = {r['case_id']: {'no_perkara': r['no_perkara'], 'amar_putusan': r['amar_putusan'], 'pidana_penjara': r['pidana_penjara'], 'denda': r['denda'], 'pasal_utama': r['pasal_utama']} for r in rows}
with open(PROCESSED / 'case_solutions.json', 'w', encoding='utf-8') as f:
    json.dump(solutions, f, ensure_ascii=False, indent=2)
print(f'Selesai representasi {len(df)} kasus. Output: data/processed/cases.csv, cases.json, case_solutions.json')
