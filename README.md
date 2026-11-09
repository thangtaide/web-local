# Manga Reader

Ứng dụng cá nhân đọc manga ngoại tuyến trên Windows 10/11. Manga Manager dùng Python/Tkinter; website dùng HTML/CSS/JavaScript thuần và mở trực tiếp bằng `file://`. Không server, tài khoản, database hay kết nối Internet khi đọc.

Đang triển khai theo 7 giai đoạn; trạng thái thực tế tại [AI_HANDOFF](docs/AI_HANDOFF.md). Đặc tả đầy đủ tại [REQUIREMENTS](docs/REQUIREMENTS.md).

Yêu cầu chạy source: Python 3.10 trở lên có Tkinter. Mở Manager: `python -m app.manager` hoặc `scripts\start.bat`. Chọn thư mục cha theo cấu trúc `Thư viện/Truyện/Tập/ảnh.jpg`, bấm **Mở Web Đọc Truyện** để quét và mở thư viện. Website có tìm kiếm không dấu, 20 truyện/trang và danh sách tập; reader được bổ sung ở giai đoạn 5.

Chạy kiểm thử: `python -m unittest discover -v`. Test trình duyệt dùng `python -m pip install playwright` rồi `python -m playwright install chromium`. Test chạy trực tiếp `file://`, không server; thiếu Playwright sẽ báo skip rõ ràng.
