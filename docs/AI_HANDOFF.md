# Bàn giao AI

Đọc [đặc tả chuẩn hóa đầy đủ](REQUIREMENTS.md); không cần lịch sử hội thoại. Mục tiêu là Manager Windows + website file:// hoàn chỉnh, đóng gói EXE và Start Menu. Không có yêu cầu bổ sung ngoài đặc tả.

Bất biến: stdlib/Tkinter và JS thuần, không server/Internet/database/npm, không sửa ảnh gốc, không push/đổi remote/reset hard, không dữ liệu cá nhân. Auto commit sau mỗi giai đoạn test đạt và cập nhật cả hai tài liệu trước commit.

Trạng thái: 1 hoàn tất, 2–7 chưa thực hiện. Giai đoạn hiện tại: kết thúc 1. Chưa có commit trước đó (repository mới); commit này là `chore: initialize manga reader project`.

Kết quả test gần nhất: 2/2 unittest đạt, 0 lỗi; diff check đạt trên Windows/Python 3.10.9. Chưa chạy GUI/file URL/EXE/Search; những thành phần này chưa có. Chưa ghi nhận lỗi. Tiếp tục giai đoạn 2 sau commit giai đoạn 1.

Quy trình tiếp nhận: đọc README → PROJECT_CONTEXT → AI_HANDOFF → REQUIREMENTS; kiểm tra git log/status; đọc source; chạy test; xác định phần chưa làm; triển khai theo thứ tự; test; cập nhật tài liệu; tự commit khi hoàn tất giai đoạn. Áp dụng được cho mọi nền tảng AI.
