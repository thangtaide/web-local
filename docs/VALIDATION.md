# Biên bản kiểm thử và giới hạn nghiệm thu

## Rebuild tại dist/MangaReader — 12/11/2026

Theo quyền xóa/build rõ ràng của người dùng, đã chạy script build chuẩn và
tái tạo toàn bộ `dist/MangaReader`. Log `test-results/rebuild-fixed.log` có
`Removing dir .../dist/MangaReader` rồi COLLECT hoàn tất, không tạo thư mục
dist timestamp mới. Lệnh xóa PowerShell thủ công ban đầu bị kiểm tra tự động
chặn; việc dọn output do bước đóng gói chuẩn của PyInstaller thực hiện.

EXE: `dist/MangaReader/MangaReader.exe`. Đã kiểm tra lại native GUI mở/đóng
hai lần và 9 ca giữ Space bằng web assets lấy từ chính bundle: **10 PASS,
0 FAIL, 0 SKIP**, 14,472 giây. JS đóng gói khớp source. Đây là kiểm tra mới;
64 test source ở phần trước không chạy lại vì không sửa code sản phẩm.

Log `test-results/rebuild-fixed-tests.log`; summary trong thư mục
`test-results/fixed-build-check-…/`. Không xóa settings/library/progress trong
AppData, không xóa thư mục dist khác hoặc đăng ký lại shortcut. Giữ `_internal`
bên cạnh EXE; cập nhật README/docs phát hành theo đường dẫn cố định.

## Sửa Space cuộn chậm — 12/11/2026

Root từ workspace hiện tại; sửa JS reader, thêm test và cập nhật tài liệu.
Chrome thật mở file:// với ảnh PNG trung tính tự sinh, không dùng truyện cá nhân
hoặc Internet. Playwright 1.65.1 cài riêng vào .venv QA, Chrome có sẵn.

| Kiểm tra | Kết quả |
| --- | --- |
| 9 ca Space mới trên code cũ | 7 FAIL / 2 PASS, tái hiện giữ/repeat/dừng/Shift lỗi |
| Reader/web/Space sau sửa | 32 PASS / 0 FAIL / 0 SKIP |
| unittest discover toàn project | 64 PASS / 0 FAIL / 0 SKIP, 40,335 s |
| Native EXE mới + 9 ca trên web đóng gói | 10 PASS / 0 FAIL / 0 SKIP |
| Build PyInstaller spec hiện có, thư mục mới riêng | PASS |
| Runtime user | App assets cập nhật tại URL cũ; settings/library/EXE cũ nguyên SHA-256 |

Ca mới: tap đúng 80%, hold không có repeat vẫn liên tục, repeat không restart
smooth, thả dừng, Shift đổi hướng khi đang giữ, Home dừng và repeat còn giữ
không bật lại, blur/tab ẩn không chờ keyup, chuyển route, không auto next,
input focus không chiếm gõ chữ, SMOOTH_SCROLL=false vẫn giữ bước nhấn lẻ.
Các test cũ tiếp tục phủ F, +/-/width, Home/End, progress/reload/storage/ảnh
trễ và navigation. Trước sửa giữ không repeat chỉ đi 720 px; phát 40 repeat
30 ms chỉ đi 813 px, dưới ngưỡng 1.200 px; sau sửa vượt ngưỡng và dừng trong
sai số 2 px khi nhả phím. Không dùng số PASS thay cho kiểm tra browser.

Native smoke mở/đóng EXE mới hai lần bằng LOCALAPPDATA tạm, xác minh cửa sổ
và pixel theme; 9 ca hold dùng đúng JS lấy từ bundle với Chrome. Không tự
bấm folder native/default browser hoặc đăng ký lại shortcut thật.

EXE: `dist/space-scroll-20261112T024813Z/MangaReader/MangaReader.exe`.
Giữ `_internal`, README/docs/script đi kèm. Build dùng spec hiện có với
distpath/workpath riêng, không dùng --clean hoặc thay dist/MangaReader cũ.
Code deploy runtime dùng prepare_web, chỉ index/versioned app assets; không
đụng browser profile/localStorage. F5 tab đang mở để nạp JS mới.

Evidence: `test-results/space-scroll-20261112T024813Z/`; logs
`test-results/space-scroll-before.log`, `space-scroll-after.log`,
`space-scroll-full.log`, `space-scroll-bundle.log`, `space-scroll-build.log`.
Git baseline/index/HEAD và bảo toàn dữ liệu nằm trong baseline/audit của evidence.
Không thực hiện commit/push/tag hoặc Git phá hủy.

Ngày 10/11/2026. Máy QA Windows 11 Pro 64-bit, version10.0.26200; Python3.10.9, Tcl/Tk8.6; PyInstaller6.22.3, Playwright1.64.1. Tài nguyên test do dự án sinh, không dùng manga cá nhân. Không có server HTTP và không gửi dữ liệu lên dịch vụ bên ngoài.

## Nâng cấp AMOLED Dark Purple sau mốc87718df

Working tree trước sửa sạch, HEAD87718df. Baseline chạy lại thực tế: `python -m unittest discover -v` **PASS50/50**, `python -m unittest tests.exe_smoke -v` **PASS2/2**, channel Chrome với `python -m unittest tests.test_web tests.test_reader -v` **PASS21/21**, không skip. Không dùng báo cáo cũ thay cho baseline.

| Kiểm chứng sau nâng cấp | Trạng thái | Kết quả thực chạy |
|---|---|---|
| `python -m unittest discover -v` | PASS | 55/55,0 lỗi,0 skip;32 Python/Tk +23 Chromium file:// |
| `python -m unittest tests.exe_smoke -v` sau build | PASS | 2/2,0 lỗi,0 skip; pixel native EXE và migration runtime tăng cường |
| `$env:MANGA_BROWSER_CHANNEL='chrome'`; `python -m unittest tests.test_web tests.test_reader -v` | PASS | 23/23,0 lỗi,0 skip; biến môi trường được dọn sau chạy |
| `scripts/build_exe.bat` | PASS | Build lại Windows x64 onedir đúng dist/MangaReader/MangaReader.exe, bundle app/theme.py tự động qua import; không đổi spec |
| Manager dark/path/button/hover/focus/disabled/status | PASS | ttk clam màu mới, trạng thái có chữ và dấu chấm, actual worker test disable/reenable và success/error style đúng |
| Unicode path copy binding và Tab navigation | PASS | readonly path giữ Unicode; copy binding qua clipboard stub trong Tcl, không đổi clipboard hệ thống; Tab entry→choose→open→entry |
| Tk scaling100/125/150% | PASS | Mô phỏng tỷ lệ font/pixel, kiểm tra minsize/text không cắt và chụp ảnh; không đổi DPI của Windows |
| Native EXE theme | PASS | PrintWindow/GDI stdlib đọc pixel từ PID EXE thật: nền09090B, entry141419, action8754EF; đóng/mở lại sạch; đã xem screenshot EXE |
| Website desktop/mobile/hover/focus/light config | PASS | 1440x900 và390x844; palette, input/card/current page, dark reader, light library còn hoạt động |
| Reader/F/images/progress/navigation | PASS | Bộ cũ chạy lại đạt; thêm ảnh không padding/border/radius/shadow, gap0, F không chừa padding; không sửa JS/schema/storage |
| Upgrade runtime và storage trong fixture | PASS | Bundle thực→legacy CSS mô phỏng→CSS mới, cùng index file URL; settings/file riêng giữ nguyên; localStorage progress/width không đổi trước mở đọc tiếp; restore đúng ảnh1 zero-based/tỷ lệ0,4/width1000 |
| Runtime đang có của user | PASS | Đồng bộ chỉ app assets sau build bằng prepare_web; settings.json và library.js so SHA-256 trước/sau giữ nguyên; CSS cũ vẫn tồn tại, CSS được index tham chiếu khớp bundle mới |
| Shortcut thật hiện hữu | PASS | Đọc IShellLinkW: target/working dir/icon đều đúng EXE cùng vị trí; giữ nguyên shortcut, không đăng ký lại |
| Compileall/diff/bundle/phạm vi | PASS | Python compileall và diff check đạt; web/docs khớp source; bundle không có settings/library sinh; scanner/settings/paths/HTML/JS/spec/icon/scripts không đổi so với87718df |
| Native folder picker/default browser/Windows Search tương tác | NOT TESTED | Vẫn thiếu foreground automation; không dùng pixel screenshot để tuyên bố đã click dialog/Search |
| Windows monitor125/150%/per-monitor DPI thật | NOT TESTED | Chỉ mô phỏng scaling Tk; chưa thay đổi cấu hình màn hình người dùng |
| Windows10 thật/Edge/Firefox/máy không cài Python | NOT TESTED | Giữ giới hạn mốc trước; không coi PATH không Python là máy sạch |

Không có FAIL còn tồn tại trong những lượt cuối. Có một lượt phát triển báo destructor Tk trên worker, đã sửa giữ AppPaths thay vì view và nhả callback khi dispose. Review cuối có test tái hiện rule nút chung ghi đè hover nền nút tiếp theo cuối tập; sửa specificity primary hover và kiểm thử lại. Không thay đổi thuật toán hoặc schema scanner/reader. Nút action8754EF là điều chỉnh nhỏ so với accent8B5CF6 để white text đạt khoảng4,62:1; hover tím sáng chuyển chữ tối, không white-on-light hoặc chữ tối trên nền tím tối.

Ảnh trước/sau bằng fixture: test-results/theme-before và theme-after, gồm library/detail/reader/focus desktop/mobile, manager100/125/150; native EXE mới tại theme-after/exe-manager.png. Đã xem các ảnh Manager100/150, detail, mobile reader và EXE; screenshot được ignore, không chứa truyện riêng/không commit. Theme native title bar yêu cầu DWM dark hỗ trợ; màu cuối vẫn theo Windows. Không có gradient/glow hoặc reader/focus animation.

## Kết quả lịch sử tại mốc87718df

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
