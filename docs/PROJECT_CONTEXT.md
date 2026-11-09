# Bối cảnh Manga Reader

Ứng dụng cá nhân ngoại tuyến Windows. [Đặc tả đầy đủ](REQUIREMENTS.md) là nguồn yêu cầu; tài liệu này phản ánh mã đã có.

Giai đoạn 1–2: đã có đường dẫn tuyệt đối, settings UTF-8 ghi atomic, GUI Tkinter tiếng Việt, chọn/ghi nhớ thư mục, hai nút chính và trạng thái/thống kê. ScanController chạy một daemon worker, queue/after xử lý kết quả trên main thread; chỉ mở trình duyệt sau job thành công, hỗ trợ lỗi/thử lại. Đóng cửa sổ hủy timer. Scanner/website/build/shortcut chưa triển khai; giao diện gọi interface scan_and_publish với import trì hoãn.

Kiến trúc mục tiêu: Manager → worker scanner → atomic library.js → website file://. ID tương đối; tiến độ localStorage trang/tỷ lệ; bốn vùng điều khiển và F; config dùng thực tế. Các phần này chưa triển khai ở giai đoạn 1.

Kiểm chứng giai đoạn 2: `python -m unittest discover -v` đạt 10/10 test; `git diff --check` đạt. Đã chạy Tk thật (cửa sổ ẩn) để chọn/khôi phục folder và xác nhận heartbeat GUI trong lúc worker chờ. Chạy source: `python -m app.manager` hoặc scripts/start.bat; việc quét sẽ hoạt động sau giai đoạn 3. Build/Search chưa có script. Quyết định: stdlib runtime, không sửa ảnh, không fetch, không server. Git: mỗi giai đoạn test đạt phải cập nhật hai tài liệu rồi commit; không push, không commit dữ liệu cá nhân/build.
