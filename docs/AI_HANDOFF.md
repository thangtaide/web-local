# Bàn giao AI

Đọc [đặc tả chuẩn hóa đầy đủ](REQUIREMENTS.md); không cần lịch sử hội thoại. Mục tiêu là Manager Windows + website file:// hoàn chỉnh, đóng gói EXE và Start Menu. Không có yêu cầu bổ sung ngoài đặc tả.

Bất biến: stdlib/Tkinter và JS thuần, không server/Internet/database/npm, không sửa ảnh gốc, không push/đổi remote/reset hard, không dữ liệu cá nhân. Auto commit sau mỗi giai đoạn test đạt và cập nhật cả hai tài liệu trước commit.

Trạng thái: 1–3 hoàn tất, 4–7 chưa thực hiện. Giai đoạn hiện tại: kết thúc 3. Commit gần nhất trước cập nhật: `ff9343f feat: add manga manager desktop interface`; commit hiện tại dự kiến `feat: implement safe manga library scanner`.

Kết quả gần nhất: 20/20 unittest đạt, 0 lỗi; diff check đạt Windows/Python 3.10.9. Có Tk GUI thật ẩn; scanner/integration đã chạy C→D, >260 ký tự và 1.000 ảnh; quyền/xóa/atomic replace lỗi dùng mock. Đã sửa fixture tên không hợp lệ Windows và cleanup đường dẫn dài, chạy lại đạt. Chưa chạy browser file://, EXE/Search. Đang cài Playwright và PyInstaller chỉ cho kiểm thử/build. Tiếp tục giai đoạn 4 website thuần file://; giai đoạn 5 reader, 6 frozen prepare_web triển khai versioned runtime, 7 regression. Giới hạn: browser đường dẫn dài chưa kiểm, junction bị từ chối có thông báo.

Quy trình tiếp nhận: đọc README → PROJECT_CONTEXT → AI_HANDOFF → REQUIREMENTS; kiểm tra git log/status; đọc source; chạy test; xác định phần chưa làm; triển khai theo thứ tự; test; cập nhật tài liệu; tự commit khi hoàn tất giai đoạn. Áp dụng được cho mọi nền tảng AI.
