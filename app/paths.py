"""Resolve resources independently of the working directory."""
from dataclasses import dataclass
from pathlib import Path
import os
import sys


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
