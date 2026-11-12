"""Tkinter UI. Workers communicate only through a queue, never through Tk."""
import queue
from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser

from app.paths import get_paths, io_path
from app.settings import load_settings, save_settings, SettingsError
from app.theme import apply_theme, request_dark_titlebar


def scan_and_publish(folder, paths):
    # Deferred import keeps the GUI independently testable.
    from app.scanner import scan_library, write_library
    from app.paths import prepare_web
    library = scan_library(folder)
    prepare_web(paths)
    write_library(paths.library, library)
    return library['stats']


class ScanController:
    """One job at a time. Only poll() may open the browser (on the caller thread)."""
    def __init__(self, job, index, opener=webbrowser.open, on_success=None):
        self.job, self.index, self.opener = job, Path(index), opener
        self.results = queue.Queue()
        self.busy = False
        self.on_success = on_success

    def start(self, folder):
        if self.busy:
            return False
        if not folder:
            raise ValueError('Hãy chọn thư mục thư viện trước.')
        if not io_path(Path(folder).expanduser().absolute()).is_dir():
            raise ValueError('Thư mục không tồn tại hoặc không thể truy cập. Hãy chọn lại.')
        self.busy = True
        try:
            threading.Thread(target=self._run, args=(folder,), daemon=True).start()
        except Exception:
            self.busy = False
            raise
        return True

    def _run(self, folder):
        try:
            result = (True, self.job(folder))
        except Exception as exc:
            result = (False, str(exc) or type(exc).__name__)
        self.results.put(result)

    def poll(self):
        try:
            success, value = self.results.get_nowait()
        except queue.Empty:
            return None
        try:
            if success and self.on_success:
                self.on_success(value)
            if success and not self.opener(self.index.resolve().as_uri() + '#/library'):
                return False, 'Đã ghi thư viện nhưng không mở được trình duyệt. Hãy mở index.html thủ công.'
            return success, value
        except Exception as exc:
            return False, 'Không mở được trình duyệt: ' + str(exc)
        finally:
            self.busy = False


class MangaManager:
    def __init__(self, root, paths=None, job=None, opener=webbrowser.open):
        self.root = root
        self.paths = paths or get_paths()
        self.controller = ScanController(job or (lambda folder, paths=self.paths: scan_and_publish(folder, paths)),
                                         self.paths.web / 'index.html', opener, self._show_stats)
        root.title('Manga Reader')
        self.style, px = apply_theme(root)
        icon = self.paths.resources / 'assets/app.ico'
        if icon.exists():
            try:
                root.iconbitmap(str(icon))
            except tk.TclError:
                pass
        frame = ttk.Frame(root, padding=px(24), style='Manga.TFrame')
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text='Manga Reader', style='Title.Manga.TLabel').grid(row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(frame, text='Thư viện truyện cá nhân · Offline', style='Secondary.Manga.TLabel').grid(row=1, column=0, columnspan=2, sticky='w', pady=(px(3), px(22)))
        ttk.Label(frame, text='THƯ MỤC TRUYỆN', style='Section.Manga.TLabel').grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, px(8)))
        self.folder = tk.StringVar()
        self.status = tk.StringVar(value='Chọn thư mục cha chứa các truyện để bắt đầu.')
        self.stats = tk.StringVar()
        initial_status_kind = 'Ready'
        try:
            self.folder.set(load_settings(self.paths.settings))
            if self.folder.get():
                available = io_path(Path(self.folder.get()).expanduser().absolute()).is_dir()
                self.status.set('Sẵn sàng.' if available else 'Thư mục đã lưu không còn tồn tại. Hãy chọn lại.')
                initial_status_kind = 'Ready' if available else 'Error'
        except SettingsError as exc:
            self.status.set(str(exc))
            initial_status_kind = 'Error'
        self.path_entry = ttk.Entry(frame, textvariable=self.folder, state='readonly', style='Path.Manga.TEntry', font=('Segoe UI', 10), takefocus=True)
        self.path_entry.grid(row=3, column=0, sticky='ew', padx=(0, px(10)))
        self.choose_button = ttk.Button(frame, text='Chọn thư mục', command=self.choose_folder, style='Secondary.Manga.TButton')
        self.choose_button.grid(row=3, column=1)
        self.open_button = ttk.Button(frame, text='Mở Web Đọc Truyện', command=self.open_web, style='Primary.Manga.TButton')
        self.open_button.grid(row=4, column=0, columnspan=2, sticky='w', pady=(px(20), px(15)))
        status_frame = ttk.Frame(frame, style='Manga.TFrame')
        status_frame.grid(row=5, column=0, columnspan=2, sticky='ew')
        status_frame.columnconfigure(1, weight=1)
        status_frame.rowconfigure(0, minsize=px(42))
        self.status_dot = ttk.Label(status_frame, text='●', style='Ready.Manga.TLabel')
        self.status_dot.grid(row=0, column=0, sticky='nw', padx=(0, px(9)))
        self.status_label = ttk.Label(status_frame, textvariable=self.status, style='Ready.Manga.TLabel', wraplength=px(560), justify='left')
        self.status_label.grid(row=0, column=1, sticky='nw')
        self.stats_label = ttk.Label(frame, textvariable=self.stats, style='Secondary.Manga.TLabel')
        self.stats_label.grid(row=6, column=0, columnspan=2, sticky='w', pady=(px(5), 0))
        self._set_status(self.status.get(), initial_status_kind)
        # Let Tk measure point fonts at the current DPI instead of fixing a pixel height.
        root.update_idletasks()
        min_height = frame.winfo_reqheight()
        root.minsize(px(640), min_height)
        root.geometry(f'{px(760)}x{min_height}')
        self.path_entry.bind('<Configure>', lambda event, label=self.status_label: label.configure(wraplength=max(px(280), event.width)))
        request_dark_titlebar(root)
        self.timer = self.root.after(75, self._poll)
        self.root.protocol('WM_DELETE_WINDOW', self.close)

    def dispose(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        # A finished/closing worker must not retain a destroyed Tk view through its callback.
        self.controller.on_success = None

    def close(self):
        self.dispose()
        self.root.destroy()

    def _set_status(self, text, kind='Ready'):
        self.status.set(text)
        self.status_label.configure(style=kind + '.Manga.TLabel')
        self.status_dot.configure(style=kind + '.Manga.TLabel')

    def choose_folder(self):
        if self.controller.busy:
            return
        folder = filedialog.askdirectory(parent=self.root, title='Chọn thư mục cha chứa truyện', mustexist=True)
        if not folder:
            return
        self.folder.set(folder)
        try:
            save_settings(self.paths.settings, folder)
            self._set_status('Đã lưu thư mục. Nhấn Mở Web Đọc Truyện để quét và đọc.')
        except OSError as exc:
            self._set_status('Đã chọn thư mục nhưng không lưu được cấu hình.', 'Error')
            messagebox.showerror('Lỗi lưu cấu hình', str(exc), parent=self.root)

    def open_web(self):
        try:
            if not self.controller.start(self.folder.get()):
                return
        except (ValueError, OSError, RuntimeError) as exc:
            self._set_status(str(exc), 'Error')
            messagebox.showerror('Không thể mở thư viện', str(exc), parent=self.root)
            return
        self.open_button.state(['disabled'])
        self.choose_button.state(['disabled'])
        self._set_status('Đang quét toàn bộ thư viện… Bạn có thể tiếp tục di chuyển cửa sổ.', 'Scanning')

    def _show_stats(self, value):
        self.stats.set(f"{value['stories']} truyện · {value['chapters']} tập · {value['images']} ảnh")
        self._set_status('Đã quét và ghi dữ liệu thành công. Đang mở trình duyệt…', 'Success')
        self.root.update_idletasks()

    def _poll(self):
        result = self.controller.poll()
        if result is not None:
            success, value = result
            self.open_button.state(['!disabled'])
            self.choose_button.state(['!disabled'])
            if success:
                self._set_status('Đã quét và ghi dữ liệu thành công. Đã mở trình duyệt.', 'Success')
            else:
                self._set_status('Không hoàn tất. Có thể chọn lại thư mục và thử lại.', 'Error')
                messagebox.showerror('Không thể mở thư viện', value, parent=self.root)
        self.timer = self.root.after(75, self._poll)


def main():
    root = tk.Tk()
    MangaManager(root)
    root.mainloop()


if __name__ == '__main__':
    main()
