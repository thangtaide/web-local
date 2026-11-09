# Bối cảnh Manga Reader

Ứng dụng cá nhân ngoại tuyến Windows. [Đặc tả đầy đủ](REQUIREMENTS.md) là nguồn yêu cầu; tài liệu này phản ánh mã đã có.

Giai đoạn 1–3: đã có đường dẫn tuyệt đối, settings UTF-8 ghi atomic, GUI Tkinter tiếng Việt, chọn/ghi nhớ thư mục, hai nút chính và trạng thái/thống kê. ScanController chạy một daemon worker, queue/after xử lý kết quả trên main thread; chỉ mở trình duyệt sau scan_and_publish thành công, hỗ trợ lỗi/thử lại. Đóng cửa sổ hủy timer. Scanner đã tích hợp; website/build/shortcut chưa triển khai.

Luồng hiện có: Manager → worker scanner → atomic library.js → browser index.html (website sẽ có ở giai đoạn 4). Scanner schema_version=1, source{name,uri}, scanned_at UTC, stats{stories,chapters,images}, stories[{id,name,cover,chapter_count,chapters:[{id,name,images,image_count}]}]. ID SHA-256 rút gọn từ đường dẫn tương đối. Natural sorting NFKC/casefold/số nguyên với tie-break xác định. Bỏ qua truyện/tập không ảnh. Lỗi đọc hoặc file biến mất hủy toàn scan, không ghi library cũ. Không hỗ trợ symlink/junction; báo lỗi thay vì đi theo liên kết.

File URI từ Path.as_uri (Unicode/#/%/&/khác ổ đĩa). Windows IO dùng prefix mở rộng hỗ trợ đường dẫn dài, URI không có prefix nội bộ. Đọc một byte xác nhận quyền ảnh, không giải mã/đổi ảnh. Ghi JSON escaped, allow_nan=false → temp cùng folder → fsync → os.replace. Tiến độ/phím tắt/bốn vùng/F/config sẽ có ở giai đoạn 5.

Kiểm chứng giai đoạn 3: `python -m unittest discover -v` đạt 20/20 test; `git diff --check` đạt. Tk thật ẩn: chọn/khôi phục và heartbeat. Scanner thật: Unicode/ký tự đặc biệt, 1.000 ảnh, root ngoài project khác ổ đĩa C so với D, đường dẫn >260 ký tự, ID di chuyển, rollback và ảnh không thay đổi. Lỗi quyền/xóa giữa scan mô phỏng xác định. Chạy source: `python -m app.manager` hoặc scripts/start.bat; chưa có trang để đọc đến giai đoạn 4. Build/Search chưa có script. Quyết định: stdlib runtime, không sửa ảnh, không fetch, không server. Git: mỗi giai đoạn test đạt cập nhật hai tài liệu rồi commit; không push/commit dữ liệu cá nhân/build. Browser có thể giới hạn đường dẫn dài riêng dù scanner đọc được.
