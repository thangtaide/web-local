# Manga Reader

Ứng dụng cá nhân đọc manga ngoại tuyến trên Windows 10/11. Manga Manager dùng Python/Tkinter; website dùng HTML/CSS/JavaScript thuần và mở trực tiếp bằng `file://`. Không server, tài khoản, database hay kết nối Internet khi đọc.

Đang triển khai theo 7 giai đoạn; trạng thái thực tế tại [AI_HANDOFF](docs/AI_HANDOFF.md). Đặc tả đầy đủ tại [REQUIREMENTS](docs/REQUIREMENTS.md).

Yêu cầu chạy source: Python 3.10 trở lên có Tkinter. Mở Manager: `python -m app.manager` hoặc `scripts\start.bat`. Chạy kiểm thử: `python -m unittest discover -v`. Scanner sẽ được nối hoàn chỉnh trong giai đoạn 3.
