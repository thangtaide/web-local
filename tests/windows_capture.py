"""Capture a native window offscreen with standard-library Win32/GDI calls."""
import ctypes
from ctypes import wintypes
import struct


def window_pixels(handle):
    """Return width, height, top-down BGRX pixels without stealing foreground focus."""
    user = ctypes.WinDLL('user32', use_last_error=True)
    gdi = ctypes.WinDLL('gdi32', use_last_error=True)
    declarations = [
        (user.GetWindowRect, [wintypes.HWND, ctypes.POINTER(wintypes.RECT)], wintypes.BOOL),
        (user.GetWindowDC, [wintypes.HWND], wintypes.HDC),
        (user.ReleaseDC, [wintypes.HWND, wintypes.HDC], ctypes.c_int),
        (user.PrintWindow, [wintypes.HWND, wintypes.HDC, wintypes.UINT], wintypes.BOOL),
        (gdi.CreateCompatibleDC, [wintypes.HDC], wintypes.HDC),
        (gdi.CreateCompatibleBitmap, [wintypes.HDC, ctypes.c_int, ctypes.c_int], wintypes.HBITMAP),
        (gdi.SelectObject, [wintypes.HDC, wintypes.HANDLE], wintypes.HANDLE),
        (gdi.DeleteObject, [wintypes.HANDLE], wintypes.BOOL),
        (gdi.DeleteDC, [wintypes.HDC], wintypes.BOOL),
        (gdi.GetDIBits, [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT], ctypes.c_int),
    ]
    for function, args, result in declarations:
        function.argtypes, function.restype = args, result
    rect = wintypes.RECT()
    if not user.GetWindowRect(handle, ctypes.byref(rect)):
        raise ctypes.WinError(ctypes.get_last_error())
    width, height = rect.right - rect.left, rect.bottom - rect.top
    source = user.GetWindowDC(handle)
    memory = gdi.CreateCompatibleDC(source)
    bitmap = gdi.CreateCompatibleBitmap(source, width, height)
    previous = gdi.SelectObject(memory, bitmap)
    try:
        if not user.PrintWindow(handle, memory, 2):
            raise ctypes.WinError(ctypes.get_last_error())
        gdi.SelectObject(memory, previous)
        header = ctypes.create_string_buffer(struct.pack('<IiiHHIIiiII', 40, width, -height, 1, 32, 0, width*height*4, 0, 0, 0, 0))
        pixels = ctypes.create_string_buffer(width * height * 4)
        if gdi.GetDIBits(memory, bitmap, 0, height, pixels, header, 0) != height:
            raise ctypes.WinError(ctypes.get_last_error())
        return width, height, pixels.raw
    finally:
        gdi.SelectObject(memory, previous)
        gdi.DeleteObject(bitmap); gdi.DeleteDC(memory); user.ReleaseDC(handle, source)
