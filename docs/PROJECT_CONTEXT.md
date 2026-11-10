# Bối cảnh Manga Reader

Ứng dụng cá nhân ngoại tuyến Windows: tìm Manga Reader trong Start Menu/Search, chọn thư viện, quét và đọc trong trình duyệt. [Đặc tả đầy đủ](REQUIREMENTS.md) là nguồn yêu cầu; tài liệu này phản ánh mã đã có. [Biên bản kiểm thử](VALIDATION.md) phân biệt kết quả đã chạy với nghiệm thu tương tác còn chờ.

## Hệ thống thiết kế AMOLED Dark Purple

Sau mốc `87718df`, nâng cấp giao diện trong phạm vi `app/manager.py`, module `app/theme.py` và `web/css/style.css`. Scanner, schema/ID/URI, paths/runtime, settings, HTML, JavaScript, localStorage, cấu hình, icon/spec/build/shortcut không thay đổi. Reader vẫn giữ nguyên geometry, ảnh không thêm padding/border/shadow/radius, gap theo config, phím F không có animation. Cover bỏ zoom nhẹ khi hover, dùng border tím để phản hồi mà không phủ ảnh.

| Vai trò | Màu |
|---|---|
| Background / phụ | #09090B / #101014 |
| Surface / hover / border | #141419 / #1C1C24 / #292932 |
| Text primary / secondary / muted | #F4F4F5 / #A1A1AA / #71717A |
| Purple / hover / active / subtle | #8B5CF6 / #A78BFA / #7C3AED / #211632 |
| Success / error / warning | #34D399 / #FB7185 / #FBBF24 |
| Nút chính / chữ trên nút | #8754EF / #FFFFFF |

Nút chính dùng tím hơi tối hơn accent chính để chữ trắng cỡ thường đạt tương phản khoảng4,62:1. Hover sáng chuyển chữ sang gần đen; pressed dùng purple active và chữ trắng. Muted chỉ dùng trang trí/disabled, thông tin bình thường dùng secondary. Không gradient/glow hoặc animation cho reader/focus.

Tkinter: `theme.py` chứa COLORS và `ttk.Style` dựa trên theme `clam` đi kèm Tk, vì theme native Windows bỏ qua một số thuộc tính màu. Style có tên riêng cho frame/label/entry/buttons và các trạng thái Ready/Scanning/Success/Error. Giữ native ttk widgets, readonly entry/copy, Tab, file dialog và disabled trong khi scan. Font Segoe UI, padding theo tỷ lệ DPI, chiều cao/minsize đo từ requested size thay vì hardcode. Đã mô phỏng scaling Tk100/125/150%; không thay đổi DPI hệ thống. Khi dispose, hủy timer và nhả callback kết quả; job mặc định chỉ giữ AppPaths, tránh Tk view bị giữ đến lúc GC trên worker. Không đổi quy trình worker/queue/after.

Title bar vẫn native; `ctypes` yêu cầu `DWMWA_USE_IMMERSIVE_DARK_MODE=20` và fallback an toàn nếu hệ điều hành không hỗ trợ. Thiết kế theo [Microsoft DWM attributes](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute); màu title bar/dialog tùy Windows/system theme. Không dùng borderless.

CSS: palette nằm trong một block `:root,.reading` dùng các token `--bg-primary`, `--bg-secondary`, `--surface`, `--surface-hover`, `--border`, `--text-*`, `--accent*`, `--success/--error/--warning`, `--on-accent` và `--action-bg`. Không tạo alias màu cũ. `.light` override token cho library khi DARK_MODE=false; reader vẫn dark như trước. Tất cả màu controls/card/input/placeholder/notice dùng token; không thay đổi chiều cao hay khoảng ảnh của reader. Phân trang hiện tại có nền tím subtle.

Kết quả nâng cấp: baseline thực chạy 50/50 +2/2 smoke +21/21 Chrome; sau sửa 55/55 (32 Python/Tk,23 Chromium) +2/2 smoke tăng cường +23/23 Chrome, không lỗi/skip. EXE build lại đạt, pixel thật và screenshot EXE xác minh AMOLED/path tối/nút tím. Test upgrade cùng URL giữ settings/file riêng/progress/width và đọc tiếp đúng ảnh/tỷ lệ. Runtime người dùng đang tồn tại đã đồng bộ asset mới bằng prepare_web; hash settings/library trước-sau giữ nguyên, asset cũ vẫn tồn tại. Không thay paths/runtime hay xóa user data. Shortcut hiện hữu được đọc lại target/working directory/icon đúng, không đăng ký lại. Biên bản chi tiết và giới hạn ở VALIDATION.

Giai đoạn 1–7 đã triển khai và kiểm thử trong phạm vi môi trường: đường dẫn tuyệt đối, settings UTF-8 atomic, GUI tiếng Việt, chọn/ghi nhớ thư mục, hai nút và trạng thái/thống kê. ScanController chạy một daemon worker, queue/after xử lý trên main thread. Quét/ghi xong → cập nhật thống kê và vẽ lại → mở browser; lỗi không mở, hỗ trợ thử lại. Đóng cửa sổ hủy timer. Scanner, thư viện web, reader, EXE và shortcut đã có. Không có chức năng quản lý truyện phức tạp hoặc nút reload riêng. Còn xác minh native dialog/default browser trong EXE và giao diện Windows Search do foreground bị môi trường từ chối.

Luồng: Manager → worker scanner → prepare_web nếu frozen → atomic library.js → main thread thống kê → browser index.html. Schema_version=1, source{name,uri}, scanned_at UTC, stats{stories,chapters,images}, stories[{id,name,cover,chapter_count,chapters:[{id,name,images,image_sizes,image_count}]}]. ID SHA-256 rút gọn từ đường dẫn tương đối, không đổi khi di chuyển root; đổi tên story/chapter có thể đổi ID, reader fallback an toàn. Natural sorting NFKC/casefold/số nguyên với tie-break xác định. Bỏ qua truyện/tập không ảnh. Lỗi đọc/file biến mất hủy scan và giữ library cũ. Symlink/junction bị báo lỗi, không âm thầm bỏ qua hay đi theo liên kết.

File URI từ Path.as_uri (Unicode/#/%/&/khác ổ đĩa). Windows IO dùng prefix mở rộng hỗ trợ đường dẫn dài, URI không có prefix nội bộ. Đọc header ảnh xác nhận quyền và lấy kích thước tốt nhất có thể, không giải mã/đổi ảnh. `image_meta.py` nhận diện PNG/GIF/JPEG/WebP/AVIF, giới hạn header tối đa 256KiB; kích thước chưa biết là null. Tập có thêm image_sizes song song images. Ghi JSON escaped, allow_nan=false → temp cùng folder → fsync → os.replace.

Website hiện có: index.html nạp config/library/app/reader bằng script thường, không fetch. Grid dark mode responsive, 20 truyện/trang; tìm live NFD bỏ dấu/đ=d/gom khoảng trắng; clamp và reset trang; detail theo thứ tự scanner, ảnh cover lỗi/empty; hash library/story/read, F5/Back/Forward. Tên nhập DOM qua textContent. Root giữ file cấu hình/README; app/web/tests/scripts/docs tách chức năng. Tài nguyên không cần Internet.

Kiểm chứng lịch sử tại mốc87718df: `python -m unittest discover -v` 50/50 đạt (29 Python/Tk và21 Chromium file://), 0 lỗi/skip; EXE smoke2/2; Chrome21/21. Build Windows native từ cwd ngoài repo đạt; HWND/đóng/mở lại với LOCALAPPDATA tạm/PATH không Python, integration bundle/runtime/ảnh đạt. Không gọi đó là đã chọn native folder/mở default browser trực tiếp trong EXE. Scanner đã kiểm tra10.000 ảnh. Kết quả nâng cấp mới hơn ở mục hệ thống thiết kế/VALIDATION.

Đã cài shortcut Start Menu thật như bước riêng; IShellLinkW xác minh target/working dir/icon đúng dist/MangaReader. Search tương tác chưa kiểm. SetForegroundWindow bị từ chối; native dialog/default browser từ EXE cần thủ công. Edge thử chạy nhưng thoát trước DevTools, không test nào chạy trên Edge; Chromium/Chrome đạt. URI quá dài browser chưa kiểm. `.gitattributes` ép CRLF batch/PS; PS UTF-8 BOM cho Windows PowerShell 5, batch codepage65001. Git: cập nhật hai tài liệu trước mỗi commit giai đoạn; không push/commit dữ liệu riêng/build.

## Reader, tiến độ và cấu hình thực tế

`reader.js` hiển thị ảnh dọc bằng wrapper aspect-ratio, ảnh object-fit contain, gap theo config mặc định 0; kích thước header giữ chỗ cho lazy loading, ảnh lỗi giữ chỗ và thông báo. Kích thước header không biết được cập nhật khi load, giữ anchor đang xem; khôi phục chỉ probe ảnh trước target chưa có size, concurrency 4, timeout mỗi ảnh 8 giây. Không đảm bảo mọi ảnh hỏng/metadata xoay đều giữ tỷ lệ header chính xác trước khi browser giải mã.

Bốn vùng cố định: trên tên/trở về/F; dưới cuộn/Home/End/width/Esc/tiến độ; trái/phải tập trước/sau disable tại biên. Desktop có lề tránh che ảnh; mobile nút bên xuống gần thanh dưới. F ẩn toàn bộ `.reader-control` cả thông báo và vùng cuối, padding về 0; giữ anchor trang/tỷ lệ, không fullscreen và không hiện theo chuột. F5/mở reader mới luôn có UI để tránh mắc kẹt. Cuối tập có nút tiếp theo, không tự chuyển.

Phím: Space ±80% viewport (Shift để lên), ←/→ tập, Home/End đầu/cuối, F ẩn/hiện, +/-100px (400..1600), Esc danh sách tập. Bỏ qua input/textarea/select/contenteditable, Ctrl/Alt/Meta; xử lý Equal/NumpadAdd/Subtract. F5 do browser.

Storage probe/try-catch, JSON hỏng fallback, quyền đọc/ghi/quota lỗi vẫn đọc được. Hiện thông báo giữ anchor không dịch điểm đọc. Key `manga-reader.progress.v1`: map story ID → {chapterId,time,chapters:{chapterId:{page,ratio,imageName,time}}}; page zero-based, ratio 0..1, imageName là tên URI giúp tìm trang khi ảnh trước bị xóa. `manga-reader.width.v1` lưu width. Lưu debounce180ms, rời route/pagehide/ẩn tab. Đọc tiếp tập còn tồn tại hoặc tập đầu; trang mất clamp index. Recent10 duy nhất theo time. Không đồng bộ giữa browser/máy; storage file:// phụ thuộc browser. `?start=1` reset một lần, replaceState chỉ hash để F5 resume; scrollRestoration=manual tránh browser tranh điểm đọc. Người dùng wheel/touch/phím đọc sẽ hủy restore đang chờ; Home/End tức thì, Space dùng hiệu ứng theo config. Không cần server fallback.

Mọi config có hiệu lực: STORIES_PER_PAGE grid; READER_IMAGE_WIDTH/MIN/MAX/STEP width; IMAGE_GAP khoảng ảnh; SPACE_SCROLL_RATIO/SMOOTH_SCROLL cuộn; LIVE_SEARCH input hay change; SEARCH_IGNORE_ACCENTS normalization; LAZY_LOAD_IMAGES loading; SAVE_READING_POSITION progress/recent; DARK_MODE màu; RECENT_STORIES_LIMIT lịch sử. Width user hợp lệ override default. Chỉnh `web/js/config.js` khi chạy source; EXE cần build lại sau khi đổi config source.

## Đóng gói và Windows Search

`packaging/entry.py` gọi app.manager; spec onedir liệt kê từng file web và icon, loại hoàn toàn library/settings runtime. Không console, embedded icon nhiều kích thước và version 1.0.0. Icon tái tạo bằng scripts/create_icon.py (stdlib). Runtime không có dependency ngoài Standard Library; build dùng PyInstaller 6.22.3, QA dùng Playwright. Tài nguyên bundle `_internal` chỉ đọc; dữ liệu `%LOCALAPPDATA%/MangaReader` có settings và web bền vững. get_paths không dựa cwd.

prepare_web đọc toàn bộ tài nguyên cần trước, tính SHA-256 nội dung, ghi từng asset atomic dưới `web/versions/<hash>/`, cuối cùng publish index.html ổn định atomic. Index tham chiếu asset version nhưng vẫn nạp `js/library.js` ổn định; không xóa version cũ/file user, không đóng gói hoặc ghi dữ liệu vào bundle. Lỗi resource không publish index mới. Sau prepare_web, scanner ghi library atomic rồi controller mở index runtime. Website hoạt động khi Manager đã đóng.

Build `scripts/build_exe.bat` (mọi cwd) → dist/MangaReader/MangaReader.exe cùng _internal/README/scripts/docs để các liên kết tài liệu trong README dùng được khi sao chép bản phát hành. Đóng ứng dụng trước build; sao chép cả onedir. Cài `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install_shortcut.ps1 [-ExePath ...]`; gỡ bằng uninstall_shortcut.ps1. Cài/gỡ độc lập, không tự chạy khi build/test. Đăng ký user Programs/Manga Reader.lnk idempotent, không admin/PATH/Registry. Helper shortcut_native.ps1 dùng IShellLinkW vì WScript.Shell từ chối TargetPath Unicode trên máy QA; Add-Type chỉ dùng Windows .NET sẵn có. Script gỡ chỉ xóa đúng shortcut, không xóa dữ liệu. Di chuyển ứng dụng phải cài lại shortcut; Search phụ thuộc index.

## Cấu trúc, cách chạy và giới hạn

`app/manager.py` GUI/controller; theme.py palette/ttk/DWM; scanner.py scan/URI/ID; image_meta.py header; settings.py cấu hình; storage.py atomic; paths.py source/frozen/runtime. `web/index.html`, css/style.css và js/config/app/reader.js là web; library.js sinh được ignore. `tests/` unit/browser/integration và windows_capture.py helper GDI stdlib chỉ cho QA; `scripts/` chạy/build/shortcut/icon; `packaging/` entry/spec/version; `assets/` icon; `data/` settings source; `docs/` đặc tả/bàn giao; build/dist/test-results là artifact ignore.

Source Python3.10+/Tkinter: từ root `python -m app.manager`, hoặc scripts/start.bat mọi cwd. Build cài PyInstaller rồi chạy scripts/build_exe.bat. Test cài Playwright và Chromium (`python -m playwright install chromium`), dùng các lệnh ở trên; smoke EXE chạy riêng sau build. Không cài dependency frontend/runtime. Quyết định kiến trúc: stdlib dễ bảo trì, script JS tránh fetch/CORS file://, hash routing tránh server fallback, ID tương đối giữ cơ hội khôi phục khi di chuyển, atomic writes bảo vệ dữ liệu và content hash bảo vệ phiên bản web.

Chức năng chưa triển khai ngoài phạm vi bản này: archive ZIP/RAR/CBZ/PDF, tải truyện, sync/backup nhiều máy. Mọi chức năng trong phạm vi đã có mã; không còn lỗi sản phẩm được biết từ test cuối. Còn nghiệm thu môi trường nêu trên. Header ảnh best effort, ảnh lỗi/metadata bất thường có thể thay đổi bố cục ban đầu; browser có giới hạn URI/định dạng riêng. EXE x64 chưa ký số; Windows 10 thật chưa thử (máy QA là Windows 11 Pro build26200). Không cam kết storage trên mọi browser.

Không sửa/di chuyển/xóa/nén ảnh gốc. Không đưa thư viện/settings/library.js/cache/temp/log riêng/build vào Git; fixtures tự sinh. Không push, thay remote, force push, reset hard hoặc xóa dữ liệu không liên quan. Lịch sử bảy giai đoạn và giới hạn nghiệm thu ở AI_HANDOFF/VALIDATION.
