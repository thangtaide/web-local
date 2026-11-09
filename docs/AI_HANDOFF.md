# Bàn giao AI

Đọc [đặc tả chuẩn hóa đầy đủ](REQUIREMENTS.md); không cần lịch sử hội thoại. Mục tiêu là Manager Windows + website file:// hoàn chỉnh, đóng gói EXE và Start Menu. Không có yêu cầu bổ sung ngoài đặc tả.

Bất biến: stdlib/Tkinter và JS thuần, không server/Internet/database/npm, không sửa ảnh gốc, không push/đổi remote/reset hard, không dữ liệu cá nhân. Auto commit sau mỗi giai đoạn test đạt và cập nhật cả hai tài liệu trước commit.

Trạng thái: 1–5 hoàn tất, 6–7 chưa thực hiện. Giai đoạn hiện tại: kết thúc 5. Commit gần nhất trước cập nhật: `7b66f64 feat: build offline manga library website`; commit hiện tại dự kiến `feat: implement manga reader and reading progress`.

Kết quả gần nhất: 36/36 unittest đạt, 0 lỗi/skip; diff check đạt Windows/Python 3.10.9. 14 test Chromium file:// (web D, ảnh đặc biệt C); 22 Python/Tk/header/scanner. Reader đủ controls/F/shortcuts/width/progress/recent10; test ảnh trễ 350ms, reload/resize/width, ảnh/tập mất, storage bị chặn. Screenshot reader đã xem. Test route từng nhận nhầm DOM cũ, đã chờ data-route/aria-busy và chạy lại toàn bộ đạt. Chưa EXE/Search. Playwright 1.64.1/Chromium, PyInstaller 6.22.3 cài chỉ test/build. Giai đoạn 6 thêm frozen prepare_web versioned, icon/spec/build/shortcuts, chạy EXE Windows thật. Giai đoạn 7 regression/docs và bổ sung corruption/config/slow unknown-size nếu cần. Giới hạn: browser khác/đường dẫn rất dài browser chưa kiểm; junction bị từ chối; metadata best effort, timeout restore 8s/ảnh. Không được ghi test chưa chạy là PASS.

Quy trình tiếp nhận: đọc README → PROJECT_CONTEXT → AI_HANDOFF → REQUIREMENTS; kiểm tra git log/status; đọc source; chạy test; xác định phần chưa làm; triển khai theo thứ tự; test; cập nhật tài liệu; tự commit khi hoàn tất giai đoạn. Áp dụng được cho mọi nền tảng AI.
