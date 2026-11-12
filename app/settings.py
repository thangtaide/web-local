"""User-selected library location; invalid files are never silently overwritten."""
import json
from pathlib import Path
from app.storage import atomic_write


class SettingsError(Exception):
    pass


def load_settings(path):
    try:
        content = json.loads(Path(path).read_text(encoding='utf-8'))
        if not isinstance(content, dict) or not isinstance(content.get('library_folder', ''), str):
            raise ValueError('sai định dạng')
        return content.get('library_folder', '')
    except FileNotFoundError:
        return ''
    except (OSError, ValueError) as exc:
        raise SettingsError('Không đọc được cấu hình. Hãy chọn lại thư mục để lưu cấu hình mới.') from exc


def save_settings(path, folder):
    atomic_write(path, json.dumps({'library_folder': str(folder)}, ensure_ascii=False, indent=2) + '\n')
