# Biên bản kiểm thử và giới hạn nghiệm thu

Ngày 10/11/2026. Máy QA Windows 11 Pro 64-bit, version10.0.26200; Python3.10.9, Tcl/Tk8.6; PyInstaller6.22.3, Playwright1.64.1. Tài nguyên test do dự án sinh, không dùng manga cá nhân. Không có server HTTP và không gửi dữ liệu lên dịch vụ bên ngoài.

## Kết quả cuối đã chạy

| Lệnh/thao tác | Kết quả | Phạm vi |
|---|---|---|
| `python -m unittest discover -v` | 50 đạt, 0 lỗi, 0 skip | 29 Python/Tk + 21 Chromium file://; lượt cuối 23,392s |
| `python -m unittest tests.exe_smoke -v` | 2 đạt, 0 lỗi, 0 skip | Native EXE launch/close/relaunch và integration bundle-resource/runtime/file://; lượt cuối 1,859s |
| `MANGA_BROWSER_CHANNEL=chrome`, rồi `python -m unittest tests.test_web tests.test_reader -v` | 21 đạt, 0 lỗi, 0 skip | Google Chrome đã cài, file://; 14,234s |
| `scripts/build_exe.bat` gọi bằng đường dẫn tuyệt đối từ cwd ngoài repo | Đạt | Windows x64 onedir dist/MangaReader/MangaReader.exe; build cuối khoảng4s |
| `python -m compileall -q app tests scripts/create_icon.py packaging/entry.py` | Đạt | Biên dịch cú pháp Python |
| `git diff --check`, `git diff --cached --check` trước commit | Đạt | Whitespace/patch |
| `git check-ignore` settings/library/dist/build/test-results | Đạt | Runtime/artifacts không được commit |
| Cài shortcut thật bằng install_shortcut.ps1, sau đó đọc IShellLinkW | Đạt | Start Menu user hiện tại, tên Manga Reader, target/working dir/icon đúng binary dist |

21 test browser mặc định và21 test Chrome là cùng bộ tình huống trên hai browser, không phải42 bài kiểm thử khác nhau. Hai smoke test chạy riêng, không tự build/cài shortcut thật khi discover. Tests shortcut chỉ làm việc trong APPDATA tạm; việc cài thật là bước thiết lập độc lập sau build/tests.

## Bằng chứng theo thành phần

Scanner: fixture hợp lệ/rỗng, bỏ truyện/tập rỗng, sáu extension và chữ hoa, nhiều số/natural tie-break, Unicode/dấu cách/#/%/&, thư viện bên ngoài repo ở ổ C trong khi web/repo ở D, đường dẫn hơn260 ký tự, extended-prefix root vẫn sinh URI chuẩn, ID di chuyển/root khác và chèn truyện, serialize tên đặc biệt, lỗi quyền/xóa giữa quét, atomic rollback/temp cleanup, hash/mtime ảnh gốc không đổi, 10.000 ảnh. Lỗi quyền/race dùng mock để tạo tình huống xác định; dữ liệu quét/ghi và path dài/cross-drive là thao tác filesystem thật. Symlink được mô phỏng DirEntry để chứng minh không bị âm thầm bỏ qua. Header PNG/GIF/JPEG/WebP/AVIF và header hỏng có test stdlib; không chứng minh mọi biến thể codec đều giải mã được trong browser.

Manager: Tk thật trong tiến trình Python, cửa sổ ẩn, gọi chọn folder qua mock filedialog để điều khiển fixture; lưu/khôi phục settings, không chọn/folder mất, lỗi scan, thử lại, disable/re-enable nút, heartbeat mainloop, worker khác thread, queue về main thread. Thứ tự được xác minh write → thống kê trên main thread → opener trên main thread. Browser opener trong test Manager được thay callback để không mở tab trên desktop người dùng.

Website: Playwright mở `index.html` bằng file URL. Script library.js và ảnh Unicode ngoài project/cross-drive tải thật, kiểm tra naturalWidth. Có library/cover/empty/broken cover/20+5 pagination/live search không dấu/đ=d, details/natural chapter order/hash lỗi/F5 reload/BackForward/direct reader. Reader có tỷ lệ/zero gap/responsive320–1440/lazy/error/width persistence/bounds, Space/Shift/Home/End/arrows/Esc/F/+/-/Numpad/modifier/input/F5 không bị chặn, bốn vùng ẩn/hiện và anchor, mouse không tự hiện, nút tiếp theo, no auto chapter, progress riêng từng tập/resume/reload/resize/width/recent10 và config3, deleted images/tập fallback, storage không khả dụng/JSON hỏng/get bị chặn/quota. Ảnh trễ300–350ms bằng trì hoãn gán src trong browser, có cả unknown sizes; đọc chủ động hủy restore. Config mặc định và thay đổi đều có test; không có HTTP(S) request từ trang trong test; lỗi JS chưa xử lý làm test fail. Screenshot library/reader đã xem, chỉ lưu artifact ignore.

EXE: binary thực sự khởi động từ cwd tạm, môi trường LOCALAPPDATA tạm/PATH không Python. EnumWindows tìm đúng cửa sổ Manga Reader thuộc PID, WM_CLOSE đóng process mã0; lặp lại hai lần, file settings được giữ. Resource bundle `_internal/web` được Manager trong interpreter dùng thật để quét/ghi runtime, rồi Chromium mở runtime và xem ảnh. Điều này xác minh resource/runtime/integration, **không chứng minh người dùng đã bấm folder native và mở trình duyệt mặc định trực tiếp trong tiến trình EXE**. Máy QA vẫn cài Python; chưa thử máy Windows sạch.

Shortcut: installer/gỡ lặp lại, Unicode EXE, kiểm tra đường dẫn/working dir/icon bằng IShellLinkW, missing EXE không tạo link, dữ liệu/file không liên quan giữ nguyên. WScript.Shell từ chối Unicode TargetPath trên QA nên dùng helper Unicode native. Start Menu thật đã có link hợp lệ tới bản build hiện tại; build lại cùng đường dẫn không cần cài lại.

## Chưa thể kiểm chứng / giới hạn môi trường

| Mục | Trạng thái và bước tiếp theo |
|---|---|
| Native folder dialog và mở default browser bằng nút trong EXE thật | Pending. Môi trường từ chối SetForegroundWindow, không thực hiện được điều khiển foreground. Mở EXE thủ công, chọn folder, bấm mở, kiểm tra ảnh/settings sau khởi động lại. |
| Windows Search hiển thị và Enter mở ứng dụng | Pending. Link Start Menu đã xác minh, chưa điều khiển được giao diện Search/chỉ mục. Nhấn Windows, gõ Manga Reader, đợi index nếu cần và Enter. |
| Microsoft Edge | Chưa xác minh. Thử channel msedge nhưng browser process thoát mã0 trước khi DevTools kết nối, lỗi setup; 0 test tình huống được chạy trên Edge. Không đổi sang HTTP hoặc coi Edge là PASS. |
| Firefox/browser khác, mọi chế độ storage file:// | Chưa kiểm. Chromium/Chrome với profile test mới đã đạt, không bảo đảm mọi browser/profile. |
| Windows10 thật, máy không cài Python | Chưa kiểm. Build có Python DLL/Tk riêng và launch với PATH không Python đạt trên Windows11, chưa thay thế kiểm thử máy sạch. |
| Browser mở URI cực dài, metadata/codec ảnh thực tế mọi biến thể | Chưa kiểm toàn diện. Scanner path>260 và header synthetic đạt; browser có giới hạn riêng, ảnh lỗi có UI xử lý. |

Không còn test bắt buộc thất bại trong phạm vi môi trường đã chạy. Các lỗi phát hiện trong phát triển đã sửa và chạy lại đạt. Lần thử Edge là giới hạn khởi động browser bổ sung, không được tính vào số test chính đã đạt. Chưa tuyên bố nghiệm thu toàn bộ luồng tương tác Windows cho đến khi hoàn tất các mục pending.

## Git và bảo vệ dữ liệu

Bảy giai đoạn có commit riêng; xem bảng AI_HANDOFF và `git log --oneline --reverse`. Hai tài liệu bàn giao được cập nhật trước từng commit. Chỉ code/README/spec/icon/tests sinh dữ liệu được theo dõi. Không commit settings.json, library.js sinh, ảnh truyện, dữ liệu riêng, dist/build/cache/log hoặc screenshot. Không push/đổi remote/xóa lịch sử. Sau commit cuối kiểm tra git status sạch; artifact ignore vẫn giữ để chạy EXE ngay.
