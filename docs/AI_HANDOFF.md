# Bàn giao AI

Đọc [đặc tả chuẩn hóa đầy đủ](REQUIREMENTS.md); không cần lịch sử hội thoại. Mục tiêu là Manager Windows + website file:// hoàn chỉnh, đóng gói EXE và Start Menu. Không có yêu cầu bổ sung ngoài đặc tả.

Bất biến: stdlib/Tkinter và JS thuần, không server/Internet/database/npm, không sửa ảnh gốc, không push/đổi remote/reset hard, không dữ liệu cá nhân. Auto commit sau mỗi giai đoạn test đạt và cập nhật cả hai tài liệu trước commit.

Trạng thái: 1–2 hoàn tất, 3–7 chưa thực hiện. Giai đoạn hiện tại: kết thúc 2. Commit gần nhất trước cập nhật: `86c238f chore: initialize manga reader project`; commit hiện tại dự kiến `feat: add manga manager desktop interface`.

Kết quả test gần nhất: 10/10 unittest đạt, 0 lỗi; diff check đạt trên Windows/Python 3.10.9. Có Tk GUI thật ẩn: chọn, settings, worker/heartbeat/queue. Đã sửa timer còn treo sau destroy trong test và chạy lại sạch lỗi Tcl. Chưa chạy file URL/EXE/Search; chưa có các thành phần này. Tiếp tục giai đoạn 3: scanner + prepare_web interface trong paths, tích hợp scan_and_publish. Giai đoạn 4–7 theo đặc tả.

Quy trình tiếp nhận: đọc README → PROJECT_CONTEXT → AI_HANDOFF → REQUIREMENTS; kiểm tra git log/status; đọc source; chạy test; xác định phần chưa làm; triển khai theo thứ tự; test; cập nhật tài liệu; tự commit khi hoàn tất giai đoạn. Áp dụng được cho mọi nền tảng AI.
