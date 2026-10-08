"""Build an isolated administrator-only WordPress trial from the current preview."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'wordpress' / 'vivies-preview'
OUTPUT = ROOT / 'wordpress' / 'vivies-preview.zip'
template = (ROOT / 'index.html').read_text()
template = template.replace('styles.css?v=refinement-3', '{{styles.css}}')
template = template.replace('preview.js?v=refinement-3', '{{preview.js}}')
template = template.replace('src="Vivies.png"', 'src="{{Vivies.png}}"')
assert template.count('{{Vivies.png}}') == 2
assert '{{styles.css}}' in template and '{{preview.js}}' in template

with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in ('vivies-preview.php', 'readme.txt'):
        archive.write(SOURCE / name, 'vivies-preview/' + name)
    archive.writestr('vivies-preview/preview.html', template)
    for name in ('styles.css', 'preview.js', 'Vivies.png'):
        archive.write(ROOT / name, 'vivies-preview/assets/' + name)

with zipfile.ZipFile(OUTPUT) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == 6
    assert archive.read('vivies-preview/assets/Vivies.png') == (ROOT / 'Vivies.png').read_bytes()
print(f'Built {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} bytes)')
print('SHA256:', hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
