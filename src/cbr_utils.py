from pathlib import Path
from bs4 import BeautifulSoup
import re, json

MONTHS = {
    'januari':'01','februari':'02','maret':'03','april':'04','mei':'05','juni':'06',
    'juli':'07','agustus':'08','september':'09','oktober':'10','november':'11','desember':'12'
}
LABELS = {'Nomor','Tingkat Proses','Klasifikasi','Kata Kunci','Tahun','Tanggal Register','Lembaga Peradilan',
          'Jenis Lembaga Peradilan','Hakim Ketua','Hakim Anggota','Panitera','Amar','Amar Lainnya',
          'Catatan Amar','Tanggal Musyawarah','Tanggal Dibacakan','Kaidah','Abstrak','Lampiran'}
STOP_AFTER = {'Kaidah','Abstrak','Lampiran','Putusan Terkait','Statistik','Kirim Masukan','Publikasi Dokumen Elektronik'}

def norm_space(s: str) -> str:
    s = str(s).replace('\xa0', ' ')
    s = re.sub(r'[\r\t]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def html_to_lines(path: Path):
    html = path.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r'saved from url=\(\d+\)([^\s]+)', html)
    source_url = m.group(1) if m else ''
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'svg']):
        tag.decompose()
    lines = [norm_space(x) for x in soup.get_text('\n').splitlines()]
    return [x for x in lines if x], source_url

def parse_date(s: str) -> str:
    s = s.replace('Tanggal', '').replace('—', '').strip()
    m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', s, re.I)
    if m:
        dd, mon, yyyy = m.groups()
        return f'{yyyy}-{MONTHS.get(mon.lower(), "01")}-{int(dd):02d}'
    return s

def get_after(lines, label, default=''):
    try:
        i = lines.index(label)
        for j in range(i + 1, min(i + 5, len(lines))):
            if lines[j] and lines[j] not in LABELS:
                return lines[j]
    except ValueError:
        pass
    return default

def get_title_date(lines):
    for l in lines:
        if l.startswith('Tanggal ') and '—' in l:
            return parse_date(l)
    return parse_date(get_after(lines, 'Tanggal Dibacakan') or get_after(lines, 'Tanggal Musyawarah'))

def content_lines(lines):
    start = 0
    for i, l in enumerate(lines):
        if l == 'Beranda' and i + 3 < len(lines) and 'PN MALANG' in lines[i+2:i+6]:
            start = i
            break
    end = len(lines)
    for i, l in enumerate(lines[start:], start):
        if l in STOP_AFTER:
            end = i
            break
    return lines[start:end]

def get_block(lines, start_label, stop_labels=None):
    if stop_labels is None:
        stop_labels = STOP_AFTER
    try:
        start = lines.index(start_label) + 1
    except ValueError:
        return ''
    block = []
    for l in lines[start:]:
        if l in stop_labels:
            break
        block.append(l)
    return norm_space(' '.join(block))

def extract_pasals(text: str) -> str:
    pattern = re.compile(r'Pasal\s+\d+[A-Za-z]*(?:\s*ayat\s*\(?\d+\)?)?(?:\s*huruf\s*[a-z])?(?:\s*(?:jo\.?|Jo\.)\s*Pasal\s+\d+[A-Za-z]*(?:\s*ayat\s*\(?\d+\)?)?)?(?:\s+(?:Undang-Undang|UU|KUHP)[^.;]*)?', re.I)
    found = []
    for m in pattern.finditer(text):
        pasal = norm_space(m.group(0).strip(' ,;'))
        if len(pasal) > 220:
            pasal = pasal[:220].rsplit(' ', 1)[0]
        if pasal not in found:
            found.append(pasal)
    return '; '.join(found)

def pasal_utama(pasal: str) -> str:
    if not pasal:
        return ''
    m = re.search(r'Pasal\s+\d+[A-Za-z]*(?:\s*ayat\s*\(?\d+\)?)?(?:\s*huruf\s*[a-z])?', pasal, re.I)
    return norm_space(m.group(0)) if m else pasal.split(';')[0]

def extract_dakwaan(text: str) -> str:
    sents = re.split(r'(?<=[.;])\s+|(?=Menjatuhkan pidana)|(?=Menetapkan)', text)
    chosen = []
    for s in sents:
        sl = s.lower()
        if 'tindak pidana' in sl or 'dakwaan' in sl or 'pasal' in sl:
            chosen.append(norm_space(s))
        if len(chosen) >= 3:
            break
    return norm_space(' '.join(chosen))[:1000]

def extract_barang_bukti(text: str) -> str:
    m = re.search(r'(?:Menetapkan|Memerintahkan)\s+barang\s+bukti\s+berupa\s*:?(.+?)(?:Membebankan|Membebani|Tanggal\s+Musyawarah|Tanggal\s+Dibacakan|\bKaidah\b|$)', text, re.I | re.S)
    if not m:
        m = re.search(r'barang\s+bukti\s+berupa\s*:?(.+?)(?:Membebankan|Membebani|Tanggal|$)', text, re.I | re.S)
    return norm_space(m.group(1))[:1800] if m else ''

def extract_pidana_phrase(text: str) -> str:
    patterns = [
        r'pidana\s+penjara\s+selama\s+(.+?)(?:dan\s+pidana\s+denda|serta\s+pidana\s+denda|dan\s+denda|,\s*dengan|;|\.)',
        r'berupa\s+pidana\s+penjara\s+selama\s+(.+?)(?:dan\s+pidana\s+denda|serta\s+pidana\s+denda|dan\s+denda|,\s*dengan|;|\.)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I | re.S)
        if m:
            return norm_space(m.group(1))[:180]
    return ''

def extract_denda(text: str):
    m = re.search(r'denda\s+(?:sejumlah|sebesar)?\s*Rp\.?\s*([0-9\.]+(?:,[0-9]{2})?)', text, re.I)
    if not m:
        m = re.search(r'denda\s+Rp\s*([0-9\.]+(?:,[0-9]{2})?)', text, re.I)
    if not m:
        return '', None
    digits = re.sub(r'[^0-9]', '', m.group(1).split(',')[0])
    return norm_space(m.group(0)), int(digits) if digits else None

def summarize(text: str, nwords=70) -> str:
    words = text.split()
    return ' '.join(words[:nwords]) + ('...' if len(words) > nwords else '')

def jenis_narkotika(text: str) -> str:
    tl = text.lower()
    jenis = []
    for kw in ['sabu', 'ganja', 'ekstasi', 'dobel l', 'obat keras', 'narkotika']:
        if kw in tl:
            jenis.append(kw)
    return '; '.join(jenis) if jenis else 'narkotika'

def label_perbuatan(text: str) -> str:
    tl = text.lower()
    if 'menjual' in tl or 'jual beli' in tl or 'perantara' in tl or 'menawarkan untuk dijual' in tl:
        return 'jual_beli_perantara'
    if 'memiliki' in tl or 'menyimpan' in tl or 'menguasai' in tl or 'menyediakan' in tl:
        return 'memiliki_menyimpan_menguasai'
    return 'lainnya'
