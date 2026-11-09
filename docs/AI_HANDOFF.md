# Bàn giao AI

Đọc [đặc tả chuẩn hóa đầy đủ](REQUIREMENTS.md); không cần lịch sử hội thoại. Mục tiêu là Manager Windows + website file:// hoàn chỉnh, đóng gói EXE và Start Menu. Không có yêu cầu bổ sung ngoài đặc tả.

Bất biến: stdlib/Tkinter và JS thuần, không server/Internet/database/npm, không sửa ảnh gốc, không push/đổi remote/reset hard, không dữ liệu cá nhân. Auto commit sau mỗi giai đoạn test đạt và cập nhật cả hai tài liệu trước commit.

Trạng thái: 1–6 đã triển khai và đạt test khả dụng; 7 chưa thực hiện. Giai đoạn hiện tại: kết thúc 6. Commit gần nhất trước cập nhật: `75a588d feat: implement manga reader and reading progress`; commit hiện tại dự kiến `build: add windows executable and start menu integration`. Native tương tác/Windows Search vẫn pending, không được gọi PASS.

Kết quả gần nhất: 40/40 test thường + 2/2 EXE smoke đạt, 0 lỗi/skip; diff check đạt. Build native Windows/Python 3.10.9/PyInstaller 6.22.3 thành công từ cwd ngoài repo. 14 test Chromium file://; 26 Python/Tk/header/scanner/runtime/shortcut. EXE thật tạo cửa sổ, đóng sạch/mở lại hai lần, môi trường dữ liệu tạm và PATH không có Python. Test integration còn lại dùng interpreter với resource bundle thật để Tk quét/ghi/runtime/Chromium ảnh. Không được diễn giải thành đã click native folder và default browser trực tiếp từ EXE.

Đã cài Start Menu shortcut thật bằng bước riêng và đọc lại IShellLinkW xác nhận đích/working dir/icon đúng EXE vừa build. Unit tests chỉ tạo shortcut dưới APPDATA tạm, không đăng ký thật. Môi trường chặn SetForegroundWindow; không điều khiển được native dialog/Search thực tế. Các phần này cần thủ công theo README. WScript.Shell TargetPath Unicode thất bại thật; đã thay bằng IShellLinkW, test Unicode/idempotency/gỡ an toàn đạt. Sửa CRLF batch + UTF8 BOM PS, build lại đạt. Có pywinauto cài cho thử nghiệm foreground nhưng mã/test dự án không phụ thuộc nó.

Còn lại giai đoạn 7: thêm corruption/config/rapid navigation/unknown-size delayed tests, integration/regression, kiểm tra ignore và dữ liệu nhạy cảm, tài liệu cuối và commit. Có thể test browser Edge/Chrome cài trên máy. Giới hạn: đường dẫn quá dài browser chưa kiểm; junction không hỗ trợ; header best effort/restore timeout 8s. Đặc biệt không ghi Windows Search tương tác hoặc native EXE end-to-end là PASS khi chưa thực hiện được.

Quy trình tiếp nhận: đọc README → PROJECT_CONTEXT → AI_HANDOFF → REQUIREMENTS; kiểm tra git log/status; đọc source; chạy test; xác định phần chưa làm; triển khai theo thứ tự; test; cập nhật tài liệu; tự commit khi hoàn tất giai đoạn. Áp dụng được cho mọi nền tảng AI.
