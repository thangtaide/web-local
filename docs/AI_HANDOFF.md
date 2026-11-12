# Bàn giao AI

## Build tại đường dẫn cố định — 12/11/2026

Theo yêu cầu người dùng, đã tái tạo `dist/MangaReader` bằng
`scripts/build_exe.bat`. PyInstaller xác nhận xóa thư mục output cũ rồi COLLECT
lại toàn bộ; không tạo thêm dist theo timestamp. EXE hiện dùng:
`dist/MangaReader/MangaReader.exe`, chứa sửa Space hold. Không xóa các thư mục
dist khác hoặc dữ liệu đọc trong AppData. Các đường dẫn build riêng ở phần
lịch sử dưới đây không phải bản cần mở hiện tại.

## Sửa Space hold — 12/11/2026

Đã sửa `web/js/reader.js` để nhấn lẻ vẫn cuộn một trang, giữ phím cuộn RAF liên
tục không retarget native smooth theo repeat; nhả phím/mất focus/ẩn tab/đổi
route/ô nhập/wheel dừng an toàn. Không đổi scanner/manager/theme/schema hoặc
storage. `tests/test_space_scroll.py` thêm 9 ca browser trung tính thật; trước
sửa 7 lỗi, sau sửa PASS. Full source 64 PASS, bundle/native EXE 10 PASS.

EXE mới: `dist/space-scroll-20261112T024813Z/MangaReader/MangaReader.exe`.
Đã đồng bộ asset web runtime hiện có ở cùng URL bằng prepare_web; người dùng
F5 trang đang mở. Giữ `_internal`; không mở bản EXE cũ để tránh hạ asset.
Không đổi shortcut hiện có, settings/library/progress hoặc xóa bản cũ.
Evidence `test-results/space-scroll-20261112T024813Z/`, các log
`test-results/space-scroll-{before,after,full,bundle,build}.log`.
Playwright 1.65.1 chỉ ở .venv QA, dùng Chrome cài sẵn, không tải browser.
Không git add/commit/push/tag/reset/clean. Tài liệu tự commit theo Stage bên
dưới là lịch sử workflow cũ; lượt sửa này không tạo Stage/commit mới.

Đọc [đặc tả chuẩn hóa đầy đủ](REQUIREMENTS.md); không cần lịch sử hội thoại. Mục tiêu gốc là Manager Windows + website file://, EXE và Start Menu. Yêu cầu bổ sung sau `87718df`: nâng cấp AMOLED Dark Purple đồng nhất cho Tkinter và website, giữ kiến trúc/chức năng/dữ liệu, chạy baseline/hồi quy, build lại, kiểm chứng upgrade runtime và commit riêng. Palette và quyết định đầy đủ ở PROJECT_CONTEXT.

Bất biến: stdlib/Tkinter và JS thuần, không server/Internet/database/npm, không sửa ảnh gốc, không push/đổi remote/reset hard, không dữ liệu cá nhân. Auto commit sau mỗi giai đoạn test đạt và cập nhật cả hai tài liệu trước commit.

Trạng thái: 1–7 giữ nguyên, bản nâng cấp AMOLED Dark Purple đã hoàn tất triển khai/kiểm thử/build trong phạm vi môi trường. Commit gần nhất trước bản cập nhật này: `87718df test: complete integration and regression validation`. Commit bàn giao chứa nâng cấp và tài liệu này: `style: apply amoled dark purple theme to manga reader`; lấy hash bằng `git log -1 --oneline` sau commit. Native dialog/default browser/Windows Search tương tác còn pending; giao diện EXE mới đã được xác minh qua PrintWindow/GDI.

## Nâng cấp AMOLED Dark Purple

Baseline thực chạy lại trước sửa: 50/50 unittest,2/2 smoke,21/21 Chrome; working tree sạch. Sau sửa: 55/55 unittest (32 Python/Tk +23 Chromium),2/2 smoke tăng cường và23/23 Chrome, 0 lỗi/skip. Build scripts/build_exe.bat thành công, output dist/MangaReader/MangaReader.exe. Đã chụp và xem trước/sau: library/detail/reader/focus desktop1440x900 và mobile390x844; Manager scaling Tk100/125/150%; screenshot native EXE. Các ảnh là fixture-only tại test-results/theme-before và theme-after, ignore, không dùng ảnh riêng. Pixel EXE thật xác nhận background09090B, surface141419 và nút8754EF, không cần SetForegroundWindow.

File sản phẩm thay đổi: app/theme.py mới (palette/clam/ttk states/DWM native fallback); app/manager.py (layout compact/DPI, style/semantic status, giữ readonly path/Tab/disabled, nhả GUI callbacks khi dispose); web/css/style.css (tokens AMOLED/card/input/control/hover/focus, light override, không đổi geometry reader). Không sửa scanner/ID/schema/file URI/settings/paths/HTML/JS/localStorage/config/icon/spec/scripts/shortcut.

File kiểm thử: tests/test_theme.py mới (DPI/layout/copy binding/Tab/status/màu), tests/windows_capture.py mới (Win32/GDI chỉ stdlib), test_manager.py thêm state assertions, test_web.py và test_reader.py thêm theme/hover/focus/light/không trang trí ảnh; exe_smoke.py xác minh pixel native và nâng cấp CSS cùng URL, giữ settings/file riêng/progress/width/đọc tiếp. Copy test stub clipboard bên trong Tcl interpreter, không thay clipboard hệ thống.

Một lượt phát triển lộ destructor Tk trên worker do view còn trong closure/callback; đã nhả callback lúc dispose và capture AppPaths thay vì view trong job mặc định; chạy lại sạch cảnh báo. Review cuối thêm test tái hiện rule nút chung ghi đè nền hover của nút cuối tập; đã tăng specificity của primary hover để chữ tối luôn đi cùng nền tím sáng. Không thay scan/worker/queue/after hay luồng mở browser. Primary #8754EF hơi tối hơn accent #8B5CF6 để chữ #FFFFFF đạt khoảng4,62:1; hover dùng chữ tối trên tím sáng, active dùng chữ trắng trên tím đậm. Giữ `DARK_MODE=false` cho library; reader luôn dark như trước.

Upgrade: test dùng resource bundle thật và legacy CSS mô phỏng; cùng index file URL chuyển sang hash CSS mới, localStorage giữ nguyên byte rồi Đọc tiếp giữ trang/tỷ lệ/width1000. Runtime thật hiện hữu cũng đã gọi prepare_web sau build, so hash settings.json/library.js trước-sau bằng nhau và CSS version cũ còn nguyên; không quét truyện cá nhân hoặc đọc/reset storage browser cá nhân. Đọc lại shortcut hiện hữu: target/working directory/icon đúng, không tạo lại link. Cơ chế hash và path dữ liệu giữ nguyên.

Bốn tài liệu README/PROJECT_CONTEXT/AI_HANDOFF/VALIDATION được cập nhật; giữ lịch sử7 giai đoạn phía dưới. Lần tiếp nhận sau đọc kết quả hiện hành tại đây và VALIDATION trước những số liệu lịch sử. Muốn truy xuất commit nâng cấp dùng `git log -1` hoặc tìm đúng message, không đoán hash.

Kết quả lịch sử mốc7: 50/50 test thường (29 Python/Tk/header/scanner/runtime/shortcut +21 Chromium file://),2/2 EXE smoke,21/21 Chrome; 0 lỗi/skip. Build native Windows11 Pro x64 build26200/Python3.10.9/PyInstaller6.22.3 đạt từ cwd ngoài repo. EXE tạo cửa sổ/đóng/mở lại, dữ liệu tạm/PATH không Python; integration interpreter/resource bundle không đồng nghĩa native EXE end-to-end. [VALIDATION](VALIDATION.md) có kết quả mới nhất và lịch sử.

Đã cài Start Menu shortcut thật bằng bước riêng và đọc lại IShellLinkW xác nhận đích/working dir/icon đúng EXE vừa build. Unit tests chỉ tạo shortcut dưới APPDATA tạm, không đăng ký thật. Môi trường chặn SetForegroundWindow; không điều khiển được native dialog/Search thực tế. Các phần này cần thủ công theo README. WScript.Shell TargetPath Unicode thất bại thật; đã thay bằng IShellLinkW, test Unicode/idempotency/gỡ an toàn đạt. Sửa CRLF batch + UTF8 BOM PS, build lại đạt. Có pywinauto cài cho thử nghiệm foreground nhưng mã/test dự án không phụ thuộc nó.

Giai đoạn 7 đã thêm corruption/quota/getItem bị chặn, config, rapid keys/BackForward, ảnh trễ chưa có size, hủy restore, mobile320, 10.000 ảnh và extended root URI. Đã sửa symlink bị bỏ qua, main GUI hiển thị thống kê trước khi mở browser, path dài ở validation GUI, lỗi phím dispatch từ window, storage notice dịch vị trí, native scroll-restoration tranh vị trí, load ảnh cùng tỷ lệ cắt cuộn mượt. Build sao chép thêm docs vào bản phát hành để README không có liên kết tài liệu bị thiếu. Xem screenshot library/reader, kiểm tra gitignore và file theo dõi không có dữ liệu riêng. Không còn lỗi sản phẩm được biết qua test cuối.

Edge đã thử qua channel msedge nhưng process thoát trước DevTools nên không có test nào chạy; test harness đã sửa cleanup khi browser launch thất bại. Chrome channel đạt21. Chưa xác minh Edge/Firefox, URI cực dài trong browser, máy Windows10 thật hoặc máy sạch chưa cài Python (smoke chỉ loại Python khỏi PATH). Junction không hỗ trợ; header best effort/restore timeout8s. Không ghi Windows Search hoặc native EXE end-to-end PASS khi chưa chạy.

## Bảy giai đoạn và kết quả trước commit

| Giai đoạn | Commit | Kết quả đã chạy |
|---|---|---|
| 1 Khởi tạo | 86c238f chore: initialize manga reader project | 2/2 |
| 2 Manager | ff9343f feat: add manga manager desktop interface | 10/10 gồm Tk thật ẩn |
| 3 Scanner | 6c393a5 feat: implement safe manga library scanner | 20/20 |
| 4 Web thư viện | 7b66f64 feat: build offline manga library website | 25/25 gồm 5 Chromium file:// |
| 5 Reader | 75a588d feat: implement manga reader and reading progress | 36/36 gồm 14 Chromium file:// |
| 6 EXE/Search | a73cac0 build: add windows executable and start menu integration | 40/40 + 2/2 smoke; build đạt; shortcut thật đã tạo/đọc lại |
| 7 Tổng thể | 87718df test: complete integration and regression validation | 50/50 + 2/2 smoke + 21/21 Chrome; build đạt |

## Việc còn lại và cách tiếp tục

Không còn giai đoạn lập trình bắt buộc chưa làm. Nghiệm thu thủ công trên desktop tương tác: chạy dist/MangaReader/MangaReader.exe, chọn folder native, bấm mở, xem ảnh trong default browser, đóng/mở lại xem đường dẫn được nhớ; Windows Search gõ Manga Reader, Enter và kiểm tra GUI. Shortcut đã cài thật, không cần tạo lại trừ khi di chuyển ứng dụng. Ghi rõ OS/browser/test thực sự chạy và cập nhật VALIDATION/PROJECT_CONTEXT/AI_HANDOFF sau nghiệm thu. Không được sửa kiểm thử để che lỗi khởi động browser.

Nếu tiếp tục sửa mã: chạy `python -m unittest discover -v`; build bằng scripts/build_exe.bat; chạy `python -m unittest tests.exe_smoke -v`; khi thay frontend, test channel Chrome nếu khả dụng. Không cần pywinauto để chạy dự án. Browser tests thiếu Playwright báo skip rõ, không tính là PASS đầy đủ. Không đẩy artifacts hay nguồn truyện lên Git. Muốn thay đổi ngoài phạm vi phải có yêu cầu mới; không tự thêm server để chữa storage.

Sau commit nâng cấp giao diện, kiểm tra `git status --short` sạch; luôn kiểm tra lại khi tiếp nhận. Artifacts ignore dist/build/test-results vẫn tồn tại để dùng/QA, không phải dữ liệu tracked. Tài liệu không tự nhúng hash commit chứa nó; lấy HEAD từ Git. Giới hạn mới: đã mô phỏng Tk100/125/150% và xem ảnh, chưa đổi Windows monitor DPI/per-monitor trên thiết bị thật; title bar native/dialog còn tùy OS và system theme. Edge/Firefox/máy Windows10 sạch chưa kiểm lại; giữ nguyên các giới hạn trước.

Quy trình tiếp nhận: đọc README → PROJECT_CONTEXT → AI_HANDOFF → REQUIREMENTS; kiểm tra git log/status; đọc source; chạy test; xác định phần chưa làm; triển khai theo thứ tự; test; cập nhật tài liệu; tự commit khi hoàn tất giai đoạn. Áp dụng được cho mọi nền tảng AI.
