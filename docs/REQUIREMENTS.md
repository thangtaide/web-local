# Đặc tả chuẩn hóa Manga Reader

Tài liệu này là nguồn yêu cầu độc lập với lịch sử hội thoại và nền tảng AI.

## Sản phẩm và ràng buộc

Xây dựng hoàn chỉnh ứng dụng đọc manga cá nhân cho Windows 10/11: Manga Manager Tkinter chọn thư viện, ghi nhớ lựa chọn, quét mỗi lần bấm **Mở Web Đọc Truyện**, ghi dữ liệu an toàn rồi mới mở trình duyệt mặc định. Website tĩnh mở `file://`, không backend, localhost, HTTP server, database, tài khoản, Internet, CDN, font từ xa, React/Vue/Angular/Electron/Node/npm. Python Standard Library và Vanilla HTML/CSS/JS; dependency chỉ dùng khi cần build/test. Không tải truyện, không sửa/di chuyển/xóa/nén ảnh gốc. Giao diện, README, tài liệu, báo cáo tiếng Việt; mã/commit có thể tiếng Anh.

## Repository

Tách `app/` (manager/scanner/settings/paths), `web/` (index/css/js/config), `data/` runtime source, `docs/`, `tests/`, `scripts/`, `assets/`, `packaging/`, `dist/` không commit. Không tạo placeholder vô ích. Không ghi đè dữ liệu có sẵn không liên quan. `.gitignore` loại ảnh cá nhân, thư viện, settings runtime, library.js sinh, cache, temp, bytecode, log nhạy cảm, build/dist. Fixture tự sinh vô hại, không hardcode đường dẫn cá nhân; cấu hình mẫu có hậu tố example.

## Thư viện và scanner

Thư mục cha tùy chọn → cấp 1 truyện → cấp 2 tập → ảnh trực tiếp trong tập. Hỗ trợ jpg/jpeg/png/webp/gif/avif không phân biệt hoa thường; chưa hỗ trợ zip/rar/cbz/pdf. Natural sorting ổn định Unicode, nhiều số, khóa tương đương có tie-break xác định, cho truyện/tập/ảnh. Bìa là ảnh đầu tiên của tập đầu tiên có ảnh; truyện/tập rỗng xử lý nhất quán và test.

Scanner độc lập GUI. Schema có version, nguồn, thời điểm, thống kê, truyện {id,name,cover,chapters,chapter_count}, tập {id,name,images,image_count}. ID từ đường dẫn tương đối trong thư viện, không từ root tuyệt đối hoặc chỉ số mảng; di chuyển root giữ ID, đổi tên có thể đổi ID và reader phải fallback. URL ảnh dùng Path.as_uri chuẩn, Unicode/dấu cách/#/%/&/ngoài project/khác ổ đĩa/đường dẫn dài. Không nối chuỗi URL tùy tiện. Không fetch JSON; sinh `window.MANGA_LIBRARY = ...;` qua script thường. Serialize an toàn trước, ghi temp, flush, atomic replace, lỗi giữ nguyên dữ liệu hợp lệ cũ. Xử lý thư viện rỗng, file không ảnh, ảnh xóa giữa scan, folder mất quyền, file ảnh không đọc được, hàng chục nghìn ảnh; không âm thầm bỏ qua lỗi nghiêm trọng. Không cần giải mã ảnh, browser xử lý ảnh hỏng.

## Manager

Tiêu đề Manga Reader/Manager; đường dẫn đầy đủ, **Chọn thư mục**, **Mở Web Đọc Truyện**, trạng thái và số truyện/tập/ảnh. Không có nút scan/reload/refresh/update riêng. askdirectory, Unicode, lưu settings.json, khôi phục và báo folder đã mất. Mỗi lần mở: kiểm tra lựa chọn/tồn tại/quyền đọc → khóa nút → báo quét → worker scan toàn bộ → ghi dữ liệu → thống kê → mở web → mở khóa. Scan/write lỗi không mở web, không crash, giữ library cũ và thử lại được. Một worker mỗi cửa sổ; Tk chỉ cập nhật từ main thread qua queue/after; GUI không treo.

## Website thư viện và điều hướng

Hash routes `#/library`, `#/story/<id>`, `#/read/<story>/<chapter>` mã hóa/giải mã ID an toàn; F5, Back, Forward, direct route, tránh reload toàn trang. Dark mode, grid responsive cover không méo + placeholder lỗi, empty state. 20 truyện/trang, chỉ render trang hiện tại, clamp trang hợp lệ. Search live không Enter, case-insensitive, Unicode bỏ dấu, đ=d, gom khoảng trắng, search đổi về trang 1, no results. Đọc gần đây tối đa 10 truyện không trùng, bìa/tên/tập/tiến độ/Đọc tiếp, ẩn hoặc trạng thái phù hợp khi trống. Chi tiết có bìa/tên/số tập/danh sách natural order/đọc từ đầu/đọc tiếp/về thư viện. Chưa đọc mở tập có ảnh đầu tiên; tập mất/đổi tên fallback an toàn.

## Reader

Ảnh dọc căn giữa, mặc định max-width 900px luôn <= viewport, giữ tỷ lệ, không crop/méo, gap 0, lazy load, lỗi hiển thị rõ, tránh nhảy bố cục. +/- bước 100px trong 400..1600 lưu localStorage an toàn. Thanh trên cố định (về tập/tên truyện/tập/F/nút tập trung), thanh dưới cố định (Space/Shift Space/Home/End/-+/Esc/tiến độ và nút chuột), trái tập trước, phải tập sau. Biên tập disable/ẩn. Không xen thanh giữa ảnh; desktop đủ chỗ không che ảnh, mobile thu gọn. F ẩn đồng thời cả bốn vùng và mọi nhãn, không chừa khoảng trống, chỉ ảnh nền tối; F lần nữa khôi phục, không mất điểm đọc, không fullscreen, không hiện theo chuột, mọi shortcut vẫn chạy. Không để người dùng mắc kẹt trong focus.

Phím chính thức: nhấn Space xuống 0.8 viewport; Shift+Space lên 0.8; giữ Space cuộn liên tục, thả dừng, Shift đổi hướng; không phụ thuộc key repeat. Mất focus/tab ẩn/đổi route hoặc nhập văn bản phải hủy giữ phím. ArrowLeft/Right tập trước/sau; Home/End đầu/cuối; F toggle controls; + tăng width; - giảm; Escape về tập; F5 do browser. Prevent default khi cần, không chiếm input/textarea/contenteditable hoặc Ctrl/Alt/Meta, hỗ trợ các cách gõ + thông dụng, không chuyển vượt biên, nhấn nhanh không hỏng trạng thái. Cuối tập có nút **Đọc tập tiếp theo** kèm tên nếu còn, cuối truyện báo hết; không tự chuyển khi cuộn; giữ tiến độ cũ; có thể về tập.

## Tiến độ và cấu hình

Lưu riêng từng truyện và từng tập: storyId/chapterId, chỉ số trang, vị trí tương đối trong ảnh, last-read, thông tin cần thiết để khôi phục; không chỉ scrollY. Đọc tiếp chờ bố cục liên quan ổn định rồi về ảnh/tỷ lệ, tránh nhảy do lazy loading. Test tải chậm, đổi viewport/width, F5, ảnh mất, tập đổi tên/mất. localStorage probe và try/catch mọi thao tác, lỗi vẫn đọc được; không bảo đảm storage file:// trên mọi browser, không thêm server để chữa.

`web/js/config.js` khai báo và dùng thật mọi giá trị: STORIES_PER_PAGE=20; READER_IMAGE_WIDTH=900; MIN_READER_IMAGE_WIDTH=400; MAX_READER_IMAGE_WIDTH=1600; IMAGE_WIDTH_STEP=100; IMAGE_GAP=0; SPACE_SCROLL_RATIO=0.8; SMOOTH_SCROLL=true; LIVE_SEARCH=true; SEARCH_IGNORE_ACCENTS=true; LAZY_LOAD_IMAGES=true; SAVE_READING_POSITION=true; DARK_MODE=true; RECENT_STORIES_LIMIT=10. Width đã lưu có thể override default với kiểm tra hợp lệ.

## EXE và Windows Search

Bắt buộc PyInstaller ưu tiên onedir `MangaReader.exe`, hiển thị Manga Reader, icon; không cần Python runtime bên ngoài. Đóng gói Tk/web/icon; không phụ thuộc cwd, source index hay temp giải nén. Resources chỉ đọc tách dữ liệu ghi. Frozen data `%LOCALAPPDATA%/MangaReader/`, web runtime bền vững `/web/` có index/css/js/library.js đúng chỗ, đồng bộ version an toàn không xóa dữ liệu người dùng; chỉ mở sau scan/write thành công, không cần admin. `scripts/build_exe.bat` chạy mọi cwd, root xác định, check dependency, build vào dist, thông báo lỗi; PyInstaller chỉ build dependency.

`install_shortcut.ps1` và `uninstall_shortcut.ps1` tạo/gỡ đúng shortcut **Manga Reader** ở Start Menu Programs user hiện tại, target EXE đúng, working dir/icon hợp lệ, idempotent, không admin/PATH/Registry, không xóa dữ liệu. Build/test không tự cài shortcut. Đăng ký là thao tác riêng, README giải thích Windows Search phụ thuộc index và di chuyển EXE cần cài lại shortcut.

## Kiểm thử và nghiệm thu

unittest Python: scanner valid/empty stories/chapters/natural sort/formats/upper extensions/Unicode/spaces/special paths/outside project/cross-drive nếu được/ID/atomic rollback/source immutable/permission/deletion/large libraries. Manager chọn/lưu/khôi phục/missing/no folder/scan lỗi/thành công/write before open/no overlap/responsive/main-thread updates. Website library/cover/20 per page/live accent search/pagination/detail/order/hash/direct/F5/Back/Forward/responsive/lazy/errors/shortcuts/chapter controls/end button/width/focus cả bốn vùng/F restore/continue/recent/progress. Test trực tiếp file://, library.js và ảnh ngoài project Unicode, reload/hash/storage khi browser cho phép; HTTP không thay thế file test. Thực sự chạy test, sửa rồi chạy lại, không tự nhận PASS chưa chạy.

Windows phù hợp phải build/chạy EXE/GUI/chọn/quét/web/ảnh/đóng mở/settings/shortcut; Search thực tế nếu môi trường hỗ trợ. Thiếu môi trường báo chính xác, không gọi Windows PASS nếu chưa kiểm. Không bỏ qua test fail nghiêm trọng hay commit có nghĩa hoàn tất khi chưa đạt. Nếu chỉ thiếu xác minh môi trường có thể commit phần đã đạt với giới hạn rõ. Nghiệm thu toàn bộ gồm repository sạch, tính năng nêu trên, EXE, Start Menu/Search, tài liệu, test, bảy commit và không dữ liệu riêng/push.

## Quy trình bảy giai đoạn và Git

1 khởi tạo cấu trúc/gitignore/README/docs/config/test; 2 Tk manager/settings/thread/interface scanner; 3 scanner an toàn và tích hợp; 4 web library/search/pagination/detail/hash; 5 reader/controls/focus/keyboard/progress/recent; 6 icon/EXE/runtime/build/shortcuts/docs; 7 integration/regression/fixes/final docs/status. Mỗi giai đoạn: triển khai → test → sửa → test lại → cập nhật PROJECT_CONTEXT và AI_HANDOFF → xem git diff → TỰ COMMIT → xác minh hash. Không xin xác nhận commit. Không push/force push/reset --hard/xóa lịch sử/đổi remote. Không xóa file không liên quan. YOLO cho phép cài build/test tools và sửa repository. Ưu tiên thực thi đến hoàn tất, không dừng ở skeleton/kế hoạch.

## Tài liệu và bàn giao

PROJECT_CONTEXT phản ánh code thật: giới thiệu/mục tiêu/chức năng đã thống nhất/chưa làm/kiến trúc/cấu trúc/luồng/schema/file URI/progress/shortcuts/four controls/F/config/source/build/Search/tests/quyết định/giới hạn/Git và an toàn dữ liệu. AI_HANDOFF chứa mục tiêu/yêu cầu bổ sung/bất biến/trạng thái 7 giai đoạn/giai đoạn hiện tại/đã xong/commit gần nhất/kết quả test/chưa chạy/lỗi/việc còn lại/hướng dẫn tiếp tục/quy tắc commit và cập nhật docs/link đặc tả này. AI mới: đọc README → PROJECT_CONTEXT → AI_HANDOFF → git log/status → source → test → xác định thiếu → phát triển → test → docs → auto commit giai đoạn. README tiếng Việt đủ source/Python/test/build EXE/location/run/Search install/remove/move/folder structure/search/continue/shortcuts/F/width/broken images/file storage/archive limitations/no sync/no Internet. Báo cáo cuối tiếng Việt đủ tổng quan/cấu trúc/lệnh và số test pass fail pending/GUI/file/EXE/Search/bảy hashes và kết quả trước commit/cách chạy/bàn giao/docs/clean tree/hạn chế/bước còn lại. Không báo thành công giả.
