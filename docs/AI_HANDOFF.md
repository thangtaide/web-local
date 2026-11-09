# Bàn giao AI

Đọc [đặc tả chuẩn hóa đầy đủ](REQUIREMENTS.md); không cần lịch sử hội thoại. Mục tiêu là Manager Windows + website file:// hoàn chỉnh, đóng gói EXE và Start Menu. Không có yêu cầu bổ sung ngoài đặc tả.

Bất biến: stdlib/Tkinter và JS thuần, không server/Internet/database/npm, không sửa ảnh gốc, không push/đổi remote/reset hard, không dữ liệu cá nhân. Auto commit sau mỗi giai đoạn test đạt và cập nhật cả hai tài liệu trước commit.

Trạng thái: 1–7 đã triển khai và đạt test khả dụng. Giai đoạn hiện tại: kết thúc 7, bàn giao. Commit gần nhất tại thời điểm cập nhật: `a73cac0 build: add windows executable and start menu integration`; bản cập nhật này thuộc commit `test: complete integration and regression validation` (lấy hash bằng `git log -1` sau commit). Native tương tác/Windows Search vẫn pending, không được gọi PASS hoặc tuyên bố nghiệm thu 100%.

Kết quả cuối: 50/50 test thường (29 Python/Tk/header/scanner/runtime/shortcut + 21 Chromium file://), 2/2 EXE smoke, thêm 21/21 browser với Chrome cài sẵn; 0 lỗi/skip trong các lượt này. Build native Windows11 Pro x64 build26200/Python3.10.9/PyInstaller6.22.3 đạt từ cwd ngoài repo. EXE thật tạo cửa sổ, đóng sạch/mở lại hai lần, dữ liệu tạm và PATH không Python. Integration còn lại dùng interpreter với resource bundle để Tk quét/ghi/runtime/Chromium ảnh; không diễn giải thành click native folder/default browser trong EXE. Compileall/diff check đạt. [VALIDATION](VALIDATION.md) ghi lệnh và phạm vi bằng chứng.

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
| 7 Tổng thể | commit chứa tài liệu này: test: complete integration and regression validation | 50/50 + 2/2 smoke + 21/21 Chrome; build cuối đạt |

## Việc còn lại và cách tiếp tục

Không còn giai đoạn lập trình bắt buộc chưa làm. Nghiệm thu thủ công trên desktop tương tác: chạy dist/MangaReader/MangaReader.exe, chọn folder native, bấm mở, xem ảnh trong default browser, đóng/mở lại xem đường dẫn được nhớ; Windows Search gõ Manga Reader, Enter và kiểm tra GUI. Shortcut đã cài thật, không cần tạo lại trừ khi di chuyển ứng dụng. Ghi rõ OS/browser/test thực sự chạy và cập nhật VALIDATION/PROJECT_CONTEXT/AI_HANDOFF sau nghiệm thu. Không được sửa kiểm thử để che lỗi khởi động browser.

Nếu tiếp tục sửa mã: chạy `python -m unittest discover -v`; build bằng scripts/build_exe.bat; chạy `python -m unittest tests.exe_smoke -v`; khi thay frontend, test channel Chrome nếu khả dụng. Không cần pywinauto để chạy dự án. Browser tests thiếu Playwright báo skip rõ, không tính là PASS đầy đủ. Không đẩy artifacts hay nguồn truyện lên Git. Muốn thay đổi ngoài phạm vi phải có yêu cầu mới; không tự thêm server để chữa storage.

Sau commit giai đoạn7, working tree dự kiến sạch; luôn tự kiểm tra `git status --short` khi tiếp nhận. Các artifact ignore trong dist/build/test-results vẫn tồn tại để dùng và kiểm tra, không phải dữ liệu tracked. Tài liệu không tự nhúng hash commit chứa nó (tránh tự tham chiếu); lấy HEAD từ Git.

Quy trình tiếp nhận: đọc README → PROJECT_CONTEXT → AI_HANDOFF → REQUIREMENTS; kiểm tra git log/status; đọc source; chạy test; xác định phần chưa làm; triển khai theo thứ tự; test; cập nhật tài liệu; tự commit khi hoàn tất giai đoạn. Áp dụng được cho mọi nền tảng AI.
