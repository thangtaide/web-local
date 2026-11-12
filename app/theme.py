"""AMOLED palette and ttk styling; no application state or persistence lives here."""
import sys
from tkinter import ttk

COLORS = {
    'background': '#09090B', 'background_secondary': '#101014',
    'surface': '#141419', 'surface_hover': '#1C1C24', 'border': '#292932',
    'text': '#F4F4F5', 'secondary': '#A1A1AA', 'muted': '#71717A',
    'accent': '#8B5CF6', 'accent_hover': '#A78BFA', 'accent_active': '#7C3AED',
    'accent_subtle': '#211632', 'success': '#34D399', 'error': '#FB7185',
    'warning': '#FBBF24',
    # Slightly darker than the accent: white button text exceeds 4.5:1 contrast.
    'action': '#8754EF', 'on_accent': '#FFFFFF',
}


def apply_theme(root):
    style = ttk.Style(root)
    # Native Windows themes ignore several ttk color settings; clam is bundled with Tk.
    style.theme_use('clam')
    scale = root.winfo_fpixels('1i') / 96
    px = lambda value: max(1, round(value * scale))
    c = COLORS
    root.configure(background=c['background'])
    style.configure('Manga.TFrame', background=c['background'])
    style.configure('Manga.TLabel', background=c['background'], foreground=c['text'], font=('Segoe UI', 10))
    style.configure('Title.Manga.TLabel', font=('Segoe UI', 21, 'bold'))
    style.configure('Secondary.Manga.TLabel', foreground=c['secondary'])
    style.configure('Section.Manga.TLabel', foreground=c['secondary'], font=('Segoe UI', 9, 'bold'))
    for kind, color in [('Ready', 'accent_hover'), ('Scanning', 'warning'), ('Success', 'success'), ('Error', 'error')]:
        style.configure(kind + '.Manga.TLabel', foreground=c[color])
    style.configure('Path.Manga.TEntry', fieldbackground=c['surface'], foreground=c['text'],
                    insertcolor=c['text'], bordercolor=c['border'], lightcolor=c['surface'],
                    darkcolor=c['surface'], padding=(px(10), px(9)), borderwidth=1,
                    selectbackground=c['accent_active'], selectforeground=c['on_accent'], font=('Segoe UI', 10))
    style.map('Path.Manga.TEntry', fieldbackground=[('readonly', c['surface']), ('disabled', c['background_secondary'])],
              foreground=[('disabled', c['muted']), ('readonly', c['text'])],
              bordercolor=[('focus', c['accent_hover'])])
    for name, primary in [('Secondary', False), ('Primary', True)]:
        key = name + '.Manga.TButton'
        style.configure(key, background=c['action'] if primary else c['surface'],
                        foreground=c['on_accent'] if primary else c['text'],
                        bordercolor=c['action'] if primary else c['accent_subtle'],
                        lightcolor=c['surface'], darkcolor=c['surface'],
                        focuscolor=c['accent_hover'], focusthickness=1, borderwidth=1,
                        relief='flat', anchor='center',
                        font=('Segoe UI', 11 if primary else 10, 'bold' if primary else 'normal'),
                        padding=(px(18 if primary else 13), px(10 if primary else 9)))
        style.map(key,
                  background=[('disabled', c['surface_hover']), ('pressed', c['accent_active']),
                              ('active', c['accent_hover'] if primary else c['accent_subtle'])],
                  foreground=[('disabled', c['secondary']), ('pressed', c['on_accent']),
                              ('active', c['background'] if primary else c['text'])],
                  bordercolor=[('disabled', c['border']), ('focus', c['accent_hover']), ('active', c['accent_hover'])])
    return style, px


def request_dark_titlebar(root):
    """Honor Windows dark mode on a native title bar; older systems safely ignore it."""
    if sys.platform != 'win32':
        return False
    try:
        import ctypes
        from ctypes import wintypes
        ancestor = ctypes.windll.user32.GetAncestor
        ancestor.argtypes = (wintypes.HWND, wintypes.UINT)
        ancestor.restype = wintypes.HWND
        handle = ancestor(root.winfo_id(), 2)
        setter = ctypes.windll.dwmapi.DwmSetWindowAttribute
        setter.argtypes = (wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD)
        setter.restype = ctypes.c_long
        enabled = wintypes.BOOL(True)
        return setter(handle, 20, ctypes.byref(enabled), ctypes.sizeof(enabled)) == 0
    except (OSError, AttributeError):
        return False
