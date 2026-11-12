# IShellLinkW preserves Unicode paths even when WScript.Shell uses a legacy code page.
if (-not ('MangaShortcut' -as [type])) {
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
[ComImport, Guid("000214F9-0000-0000-C000-000000000046"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMangaShellLinkW {
    void GetPath([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder path, int size, IntPtr data, uint flags);
    void GetIDList(out IntPtr pidl);
    void SetIDList(IntPtr pidl);
    void GetDescription([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder text, int size);
    void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string text);
    void GetWorkingDirectory([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder path, int size);
    void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string path);
    void GetArguments([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder text, int size);
    void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string text);
    void GetHotkey(out short key);
    void SetHotkey(short key);
    void GetShowCmd(out int command);
    void SetShowCmd(int command);
    void GetIconLocation([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder path, int size, out int index);
    void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string path, int index);
    void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string path, uint reserved);
    void Resolve(IntPtr window, uint flags);
    void SetPath([MarshalAs(UnmanagedType.LPWStr)] string path);
}
public static class MangaShortcut {
    static object NewLink() { return Activator.CreateInstance(Type.GetTypeFromCLSID(new Guid("00021401-0000-0000-C000-000000000046"))); }
    public static void Create(string path, string target, string directory) {
        object obj = NewLink();
        try {
            var link = (IMangaShellLinkW)obj;
            link.SetPath(target); link.SetWorkingDirectory(directory);
            link.SetIconLocation(target, 0); link.SetDescription("Manga Reader - Doc truyen ngoai tuyen");
            link.SetShowCmd(1); ((IPersistFile)obj).Save(path, true);
        } finally { Marshal.FinalReleaseComObject(obj); }
    }
    public static string[] Read(string path) {
        object obj = NewLink();
        try {
            ((IPersistFile)obj).Load(path, 0);
            var link = (IMangaShellLinkW)obj;
            var target = new StringBuilder(32768); var directory = new StringBuilder(32768); var icon = new StringBuilder(32768); int index;
            link.GetPath(target, target.Capacity, IntPtr.Zero, 4);
            link.GetWorkingDirectory(directory, directory.Capacity); link.GetIconLocation(icon, icon.Capacity, out index);
            return new [] { target.ToString(), directory.ToString(), icon.ToString() + "," + index };
        } finally { Marshal.FinalReleaseComObject(obj); }
    }
}
'@
}
