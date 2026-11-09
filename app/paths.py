"""Resolve resources independently of the working directory."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import os
import sys
from app.storage import atomic_write

WEB_FILES = ('index.html', 'css/style.css', 'js/config.js', 'js/app.js', 'js/reader.js')


def io_path(path):
    """Extended Windows paths for IO only; never use the prefix in a public URI."""
    value = str(path)
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        if value.startswith('\\\\'):
            return Path('\\\\?\\UNC\\' + value[2:])
        if Path(value).is_absolute():
            return Path('\\\\?\\' + value)
    return Path(value)


@dataclass(frozen=True)
class AppPaths:
    resources: Path
    data: Path
    web: Path

    @property
    def settings(self):
        return self.data / "settings.json"

    @property
    def library(self):
        return self.web / "js" / "library.js"


def get_paths():
    if getattr(sys, "frozen", False):
        resources = Path(sys._MEIPASS)
        data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "MangaReader"
        return AppPaths(resources, data, data / "web")
    root = Path(__file__).resolve().parent.parent
    return AppPaths(root, root / "data", root / "web")


def prepare_web(paths):
    """Deploy immutable, content-versioned assets before publishing the stable index.

    Only application-owned files are written. Never remove versions or user files.
    library.js remains at a stable URL and is excluded from bundled resources.
    """
    paths.web.mkdir(parents=True, exist_ok=True)
    source = paths.resources / 'web'
    if source.resolve() == paths.web.resolve():
        return
    content = {name: (source / name).read_text(encoding='utf-8') for name in WEB_FILES}
    digest = hashlib.sha256()
    for name, value in content.items():
        digest.update(name.encode() + b'\0' + value.encode('utf-8'))
    version = 'versions/' + digest.hexdigest()[:20]
    for name, value in content.items():
        if name == 'index.html':
            continue
        target = paths.web / version / name
        if not target.exists() or target.read_text(encoding='utf-8') != value:
            atomic_write(target, value)
    index = content['index.html'].replace('href="css/', f'href="{version}/css/')
    for script in ('config.js', 'app.js', 'reader.js'):
        index = index.replace(f'src="js/{script}"', f'src="{version}/js/{script}"')
    target = paths.web / 'index.html'
    if not target.exists() or target.read_text(encoding='utf-8') != index:
        atomic_write(target, index)
