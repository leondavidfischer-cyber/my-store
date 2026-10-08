"""Package only the standalone preview and its user instructions."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root / 'artifacts' / 'vivies-preview.zip'
output.parent.mkdir(exist_ok=True)
files = ['index.html', 'styles.css', 'preview.js', 'Vivies.png', 'OPEN-PREVIEW.txt', 'docs/architecture.md']
with ZipFile(output, 'w', ZIP_DEFLATED) as package:
    for name in files:
        package.write(root / name, 'vivies-preview/' + name)
with ZipFile(output) as package:
    assert package.testzip() is None
    assert len(package.namelist()) == len(files)
print(output)
