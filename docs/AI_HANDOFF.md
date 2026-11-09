# Bàn giao AI

Đọc [đặc tả chuẩn hóa đầy đủ](REQUIREMENTS.md); không cần lịch sử hội thoại. Mục tiêu là Manager Windows + website file:// hoàn chỉnh, đóng gói EXE và Start Menu. Không có yêu cầu bổ sung ngoài đặc tả.

Bất biến: stdlib/Tkinter và JS thuần, không server/Internet/database/npm, không sửa ảnh gốc, không push/đổi remote/reset hard, không dữ liệu cá nhân. Auto commit sau mỗi giai đoạn test đạt và cập nhật cả hai tài liệu trước commit.

Trạng thái: 1–4 hoàn tất, 5–7 chưa thực hiện. Giai đoạn hiện tại: kết thúc 4. Commit gần nhất trước cập nhật: `6c393a5 feat: implement safe manga library scanner`; commit hiện tại dự kiến `feat: build offline manga library website`.

Kết quả gần nhất: 25/25 unittest đạt, 0 lỗi, không skip; diff check đạt Windows/Python 3.10.9. 5 test Playwright/Chromium thật file:// (web D, ảnh Unicode đặc biệt C) bao gồm cover/pagination/search/hash/F5/Back/Forward/mobile/empty. Có Tk GUI thật ẩn. Đã sửa hash encoding sai bị render library. Chưa reader/EXE/Search. Playwright 1.64.1/Chromium và PyInstaller 6.22.3 đã cài chỉ cho test/build. Tiếp tục giai đoạn 5 reader/progress/recent; mọi config phải dùng thật khi xong. Giai đoạn 6 thêm frozen prepare_web versioned, icon/spec/build/shortcuts. Giai đoạn 7 regression/docs. Giới hạn browser khác và đường dẫn rất dài browser chưa kiểm; junction bị từ chối có thông báo.

Quy trình tiếp nhận: đọc README → PROJECT_CONTEXT → AI_HANDOFF → REQUIREMENTS; kiểm tra git log/status; đọc source; chạy test; xác định phần chưa làm; triển khai theo thứ tự; test; cập nhật tài liệu; tự commit khi hoàn tất giai đoạn. Áp dụng được cho mọi nền tảng AI.
