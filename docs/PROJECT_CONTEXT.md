# Bối cảnh Manga Reader

Ứng dụng cá nhân ngoại tuyến Windows. [Đặc tả đầy đủ](REQUIREMENTS.md) là nguồn yêu cầu; tài liệu này phản ánh mã đã có.

Giai đoạn 1: đã khởi tạo app/tests/scripts/data, đường dẫn tuyệt đối không phụ thuộc cwd và tách resource với dữ liệu user trong bản frozen. Chưa có GUI, scanner, website, build hay shortcut; các phần đó được làm lần lượt giai đoạn 2–6.

Kiến trúc mục tiêu: Manager → worker scanner → atomic library.js → website file://. ID tương đối; tiến độ localStorage trang/tỷ lệ; bốn vùng điều khiển và F; config dùng thực tế. Các phần này chưa triển khai ở giai đoạn 1.

Kiểm chứng giai đoạn 1: `python -m unittest discover -v` đạt 2/2 test; `git diff --check` đạt. Chạy source sẽ dùng `python -m app.manager` sau giai đoạn 2. Build/Search chưa có script ở giai đoạn 1. Quyết định: stdlib runtime, không sửa ảnh, không fetch, không server. Git: mỗi giai đoạn test đạt phải cập nhật hai tài liệu rồi commit; không push, không commit dữ liệu cá nhân/build.
