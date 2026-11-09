# Bối cảnh Manga Reader

Ứng dụng cá nhân ngoại tuyến Windows. [Đặc tả đầy đủ](REQUIREMENTS.md) là nguồn yêu cầu; tài liệu này phản ánh mã đã có.

Giai đoạn 1–4: đã có đường dẫn tuyệt đối, settings UTF-8 ghi atomic, GUI Tkinter tiếng Việt, chọn/ghi nhớ thư mục, hai nút chính và trạng thái/thống kê. ScanController chạy một daemon worker, queue/after xử lý kết quả trên main thread; chỉ mở trình duyệt sau scan_and_publish thành công, hỗ trợ lỗi/thử lại. Đóng cửa sổ hủy timer. Scanner và website thư viện đã tích hợp; reader/build/shortcut chưa triển khai.

Luồng hiện có: Manager → worker scanner → atomic library.js → browser index.html (website sẽ có ở giai đoạn 4). Scanner schema_version=1, source{name,uri}, scanned_at UTC, stats{stories,chapters,images}, stories[{id,name,cover,chapter_count,chapters:[{id,name,images,image_count}]}]. ID SHA-256 rút gọn từ đường dẫn tương đối. Natural sorting NFKC/casefold/số nguyên với tie-break xác định. Bỏ qua truyện/tập không ảnh. Lỗi đọc hoặc file biến mất hủy toàn scan, không ghi library cũ. Không hỗ trợ symlink/junction; báo lỗi thay vì đi theo liên kết.

File URI từ Path.as_uri (Unicode/#/%/&/khác ổ đĩa). Windows IO dùng prefix mở rộng hỗ trợ đường dẫn dài, URI không có prefix nội bộ. Đọc một byte xác nhận quyền ảnh, không giải mã/đổi ảnh. Ghi JSON escaped, allow_nan=false → temp cùng folder → fsync → os.replace.

Website hiện có: index.html nạp config/library/app bằng script thường, không fetch. Grid dark mode responsive, 20 truyện/trang; tìm live NFD bỏ dấu/đ=d/gom khoảng trắng; clamp và reset trang; detail theo thứ tự scanner, ảnh cover lỗi/empty; hash route story/library, F5/Back/Forward. Tên nhập DOM qua textContent. `config.js` đủ cấu hình yêu cầu; các biến reader sẽ được nối ở giai đoạn 5. Reader/progress/bốn vùng/F chưa có. Root giữ file cấu hình/README; app/web/tests/scripts/docs tách chức năng. Tài nguyên không cần Internet.

Kiểm chứng giai đoạn 4: `python -m unittest discover -v` đạt 25/25 test, 0 lỗi; diff check đạt. Gồm 20 Python/Tk/scanner và 5 browser Chromium thật file://: ảnh C→D, Unicode, cover, tìm không dấu, 20/5 truyện mỗi trang, hash lỗi, F5, Back/Forward, viewport 390px, empty/lỗi bìa. Cài build/test dependency riêng (Playwright/PyInstaller) không dùng runtime. Lỗi hash sai encoding đã sửa và test lại. Chạy source `python -m app.manager` hoặc scripts/start.bat. Build/Search chưa có script. Giới hạn: browser khác và đường dẫn dài browser chưa kiểm. Git: mỗi giai đoạn test đạt cập nhật hai tài liệu rồi commit; không push/commit dữ liệu cá nhân/build.
