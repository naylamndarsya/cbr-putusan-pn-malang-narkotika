from pathlib import Path
import shutil
from cbr_utils import html_to_lines, content_lines, norm_space

PROJECT = Path(__file__).resolve().parents[1]
RAW_HTML = PROJECT / 'data' / 'raw_html'
RAW_TXT = PROJECT / 'data' / 'raw'
LOGS = PROJECT / 'logs'

RAW_TXT.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

log = []
html_files = sorted(RAW_HTML.glob('case_*.html'))
if len(html_files) < 30:
    raise ValueError(f'Dokumen kurang dari 30. Saat ini hanya {len(html_files)} HTML.')

for p in html_files:
    lines, _ = html_to_lines(p)
    text = norm_space(' '.join(content_lines(lines)))
    out_path = RAW_TXT / f'{p.stem}.txt'
    out_path.write_text(text, encoding='utf-8')
    log.append(f'{p.stem}: {len(text.split())} kata -> {out_path.name}')

(LOGS / 'cleaning.log').write_text('\n'.join(log), encoding='utf-8')
print(f'Selesai preprocessing {len(html_files)} dokumen. Output: data/raw/*.txt dan logs/cleaning.log')
