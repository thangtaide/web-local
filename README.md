# Manga Reader

Một thư viện truyện của riêng bạn trên Windows 10/11. Manga Manager dùng Tkinter; website HTML/CSS/JavaScript thuần mở trực tiếp bằng `file://`. Không server, localhost, tài khoản, database, CDN hay Internet khi đọc. Ảnh gốc được giữ nguyên.

## Sửa giữ Space cuộn chậm — 12/11/2026

Nhấn Space một lần vẫn cuộn 80% màn hình; giữ Space cuộn liên tục, thả để dừng.
Giữ Shift để cuộn lên, có thể đổi hướng khi vẫn giữ Space. Không phụ thuộc tốc
độ lặp phím của Windows. Đổi tab, mất focus, focus ô nhập hoặc chuyển tập sẽ
dừng cuộn, không tự chuyển tập ở cuối ảnh.

Đã cập nhật tài nguyên web runtime hiện có; **F5 tab đang đọc** để nhận sửa đổi.
Nếu mở Manager, dùng bản EXE mới tại
`dist/MangaReader/MangaReader.exe`, giữ `_internal` bên cạnh. Theo yêu cầu mới,
build dùng đường dẫn cố định này và tái tạo toàn bộ nội dung bên trong;
không tạo thêm thư mục dist riêng theo timestamp.
64 test source và 10 kiểm tra EXE/tài nguyên đóng gói PASS. Không xóa tiến độ,
library, settings hoặc phiên bản web cũ. Chi tiết ở [VALIDATION](docs/VALIDATION.md).

## Giao diện AMOLED Dark Purple

Manager và website dùng nền gần đen `#09090B`, panel `#141419`, chữ trắng dịu và điểm nhấn tím `#8B5CF6`. Nút chính dùng tông tím điều chỉnh nhẹ `#8754EF` để chữ trắng có tương phản tốt hơn; hover/focus và trạng thái disabled rõ ràng. Manager có trạng thái kèm nội dung và màu, chọn/sao chép đường dẫn Unicode, hỗ trợ Tab; bố cục được đo theo font/DPI. Không thêm thư viện GUI.

Website giữ bố cục, tìm kiếm, phím tắt, tiến độ và chế độ F. `DARK_MODE=false` vẫn bật giao diện sáng cho thư viện; reader giữ nền tối như trước. Nâng cấp EXE cập nhật CSS theo hash tại cùng địa chỉ runtime, không xóa settings, library.js hoặc tiến độ browser. Ảnh so sánh bằng fixture nằm trong `test-results/theme-before/` và `test-results/theme-after/` của workspace kiểm thử, không nằm trong Git/bản phát hành.

## Dùng bản EXE

Mở `dist\MangaReader\MangaReader.exe`. Bản này có sẵn Python/Tkinter; máy người dùng không cần cài Python. Mang **toàn bộ thư mục MangaReader**, gồm `_internal`, khi sao chép; không chỉ một file EXE. Giữ ứng dụng ở vị trí ổn định trước khi cài shortcut.

1. Bấm **Chọn thư mục**, chọn thư mục cha chứa các truyện.
2. Xem đường dẫn trong ô đường dẫn (dùng Home/End/mũi tên nếu đường dẫn quá dài).
3. Bấm **Mở Web Đọc Truyện**. Mỗi lần đều quét lại toàn bộ thư viện; cửa sổ vẫn đáp ứng.
4. Chờ quét/ghi dữ liệu thành công rồi website tự mở. Nếu lỗi, xem thông báo và thử lại; library hợp lệ cũ được giữ nguyên.

Settings và website runtime của EXE nằm tại `%LOCALAPPDATA%\MangaReader\`. Website là file thật, vẫn dùng được sau khi đóng Manager; không cần Administrator. Không đặt truyện cá nhân trong build/dist.

## Windows Search

Từ root repository chạy:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_shortcut.ps1
```

Hoặc chạy `install_shortcut.ps1` trong thư mục bản phát hành, giữ `shortcut_native.ps1` cạnh nó. Có thể chỉ định EXE khác:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_shortcut.ps1 -ExePath "C:\Apps\MangaReader\MangaReader.exe"
```

Nhấn **Windows**, gõ **Manga Reader**, Enter để mở. Script tạo một shortcut của user hiện tại trong Start Menu Programs với target/working directory/icon đúng. Chạy lại cập nhật cùng shortcut; nếu di chuyển ứng dụng phải tạo lại shortcut. Windows Search có thể cần thời gian cập nhật chỉ mục.

Gỡ shortcut bằng:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\uninstall_shortcut.ps1
```

Chỉ shortcut Manga Reader bị gỡ, không xóa EXE/settings/tiến độ/truyện. Không sửa PATH/Registry. `Bypass` chỉ áp dụng cho tiến trình PowerShell vừa chạy, không sửa policy hệ thống. Build và unit test không đăng ký shortcut vào Start Menu thật.

## Chạy từ source

Cần **Python 3.10+ có Tkinter**, không dependency runtime ngoài Standard Library. Từ root repository:

```powershell
python -m app.manager
```

Hoặc mở `scripts\start.bat` từ bất kỳ thư mục hiện hành nào. Chọn thư viện/mở web như trên. Source lưu `data\settings.json`, sinh `web\js\library.js`, mở `web\index.html`. Không cần tự mở HTML trước lần quét đầu.

## Thư viện và cách đọc

```text
Thư viện/
  One Piece/
    Tập 1/
      1.jpg
      2.jpg
      10.png
    Tập 2/
      001.webp
  Truyện tiếng Việt/
    Chương 01/
      1.avif
```

Ảnh trực tiếp trong folder tập: jpg/jpeg/png/webp/gif/avif, không phân biệt hoa thường. Truyện/tập/ảnh sắp tự nhiên 1, 2, 10. Bìa là ảnh đầu tiên của tập có ảnh đầu tiên; bỏ qua truyện/tập rỗng. Hỗ trợ Unicode, dấu cách, `#`, `%`, `&`, thư viện ngoài project/khác ổ đĩa. Symlink/junction bị từ chối có thông báo.

Tìm real-time: `truyen dac biet` tìm được **Truyện Đặc Biệt**. Mặc định 20 truyện/trang. Chọn truyện và tập hoặc **Đọc tiếp**; **Đọc từ đầu** bắt đầu lại tập đầu. **Đọc gần đây** có tối đa 10 truyện duy nhất.

Ảnh dọc liên tục, không crop/méo, mặc định tối đa 900px và không vượt màn hình. Bốn vùng trên/dưới/trái/phải có nút chuột và nhãn phím. Cuối tập có **Đọc tập tiếp theo**, không tự chuyển khi cuộn.

| Phím | Hành vi |
|---|---|
| Space / Shift + Space | Nhấn: xuống/lên 80% màn hình; giữ: cuộn liên tục, thả để dừng |
| ← / → | Tập trước / tập sau |
| Home / End | Đầu / cuối tập |
| F | Ẩn/hiện toàn bộ giao diện bao quanh truyện |
| + / - | Tăng/giảm 100px, trong khoảng 400–1600px |
| Esc | Danh sách tập |
| F5 | Reload trình duyệt, khôi phục tiến độ nếu lưu được |

F không fullscreen, không tự hiện theo chuột; nhấn F lần nữa để trở lại. Reader mới/F5 hiện điều khiển. Phím riêng bỏ qua input và Ctrl/Alt/Meta. Tiến độ lưu từng truyện/tập theo **ảnh + tỷ lệ trong ảnh**, có tên ảnh để tìm lại khi ảnh phía trước bị xóa. Tập mất thì về tập đầu còn lại. localStorage bị chặn vẫn đọc được và có thông báo. Source/EXE có file URL khác nhau nên có thể có vùng lưu trữ khác nhau.

## Cấu hình

Chỉnh `web\js\config.js` rồi F5 source. Mọi cấu hình có tác dụng: số truyện/trang, width mặc định/min/max/step, khoảng ảnh, tỷ lệ/hiệu ứng cuộn, live search/bỏ dấu, lazy loading, lưu tiến độ, dark mode, số truyện gần đây. Width user đã lưu hợp lệ ưu tiên hơn mặc định.

Với EXE, chỉnh source rồi build lại. Runtime dùng asset theo hash nội dung, đồng bộ tài nguyên ứng dụng và giữ dữ liệu riêng. Không sửa `web\versions` runtime; các file ứng dụng có thể được đồng bộ lại. Không tự xóa phiên bản cũ/file user.

## Build EXE Windows

```powershell
python -m pip install pyinstaller
.\scripts\build_exe.bat
```

Cần Python 3.10+/Tkinter. PyInstaller chỉ dùng build; script xác định root của chính nó, chạy mọi cwd. Kết quả `dist\MangaReader\MangaReader.exe`, `_internal`, README, docs và script shortcut. Build onedir, không console, có icon sách, không đóng gói library.js/settings/ảnh cá nhân. Đóng EXE trước build lại; build thay sản phẩm cũ. dist/build không commit. Tái tạo icon: `python scripts/create_icon.py` (stdlib).

Thiết kế tham chiếu [runtime PyInstaller](https://pyinstaller.org/en/stable/runtime-information.html) và [spec files](https://pyinstaller.org/en/stable/spec-files.html).

## Kiểm thử

```powershell
python -m pip install playwright
python -m playwright install chromium
python -m unittest discover -v
```

Thiếu Playwright thì browser test báo skip, không được hiểu là đã kiểm chứng web. Test chạy **file:// thật**, không server, fixture tự sinh. Tk tests cần Tk khả dụng. Test shortcut chỉ tạo .lnk dưới APPDATA tạm, không chạm Start Menu thật. Bộ hiện có 55 test thường (32 Python/Tk và 23 browser); xem [biên bản kiểm thử](docs/VALIDATION.md).

Muốn chạy 23 test browser với Chrome đã cài trên máy, đặt biến môi trường `MANGA_BROWSER_CHANNEL=chrome`, rồi chạy `python -m unittest tests.test_web tests.test_reader -v`; với Edge là `msedge`. Mặc định dùng Chromium do Playwright cung cấp. Chrome đã đạt; Edge trên máy QA trước đây thoát trước khi kết nối DevTools, nên chưa xác minh được Edge.

Sau build, chạy riêng:

```powershell
python -m unittest tests.exe_smoke -v
```

Smoke kiểm tra binary tạo cửa sổ/đóng/mở lại với LOCALAPPDATA tạm và PATH không có Python; `PrintWindow`/GDI đọc pixel thật để xác minh nền AMOLED, ô đường dẫn tối và nút tím trong EXE. Smoke thứ hai dùng Manager bằng interpreter với resource bundle, nâng cấp CSS tại cùng file URL và kiểm tra settings/file riêng/localStorage/đọc tiếp còn nguyên; không được diễn giải thành đã bấm folder native/mở default browser trong tiến trình EXE.

Nghiệm thu thủ công còn lại: EXE → chọn folder native → mở web → xem ảnh → đóng/mở lại và kiểm tra folder; cài shortcut → Windows Search → Enter. Giao diện EXE mới đã được chụp/xác minh bằng PrintWindow không cần foreground. Môi trường vẫn từ chối SetForegroundWindow, nên chưa xác minh các thao tác tương tác này. Title bar native yêu cầu dark mode khi Windows hỗ trợ; native dialog/title bar vẫn tùy phiên bản và thiết lập Windows. Xem [AI_HANDOFF](docs/AI_HANDOFF.md) cho kết quả chính xác.

## Giới hạn và xử lý lỗi

- `file://`/localStorage khác nhau theo browser/profile/riêng tư; không bảo đảm lưu trên mọi browser. Không tự đồng bộ/backup giữa máy. Chromium và Chrome đã kiểm thử; Edge chưa xác minh vì không khởi động được trong tự động hóa.
- Chưa hỗ trợ ZIP/RAR/CBZ/PDF hoặc tải truyện.
- Ảnh lỗi: kiểm tra file gốc và browser hỗ trợ AVIF/WebP, rồi bấm **Mở Web Đọc Truyện** để quét lại. Không sửa ảnh gốc, không thêm server.
- Folder/file không đọc được khiến toàn lượt quét thất bại và giữ library cũ; sửa quyền/đóng chương trình khóa file rồi thử lại.
- Scanner hỗ trợ IO đường dẫn dài Windows; giới hạn tên file/ổ đĩa/browser mở URI vẫn phụ thuộc môi trường.
- Header kích thước best effort, không kiểm tra ảnh hỏng; ảnh chưa nhận diện có thể tải trước khi khôi phục, timeout 8s/ảnh. Metadata bất thường có thể đổi bố cục lần đầu.
- Build chưa ký số; Windows có thể hiện thông báo nhà phát hành chưa xác thực.

## Cấu trúc và bàn giao

| Thư mục | Vai trò |
|---|---|
| app/ | Tk Manager, scanner/header ảnh, settings, atomic write, paths/runtime |
| web/ | Website thuần, config, reader |
| data/ | Settings source, không commit |
| tests/ | Python/Tk/Chromium file://, runtime, shortcut, EXE smoke |
| scripts/ | Chạy/build/icon/cài/gỡ shortcut |
| assets/, packaging/ | Icon, entry, spec, version |
| docs/ | Đặc tả/bối cảnh/bàn giao |
| dist/, build/, test-results/ | Sản phẩm phát sinh, không commit |

Đọc [PROJECT_CONTEXT](docs/PROJECT_CONTEXT.md), [AI_HANDOFF](docs/AI_HANDOFF.md), [đặc tả đầy đủ](docs/REQUIREMENTS.md) trước khi tiếp tục. Commit theo giai đoạn test đạt, không tự push; không commit truyện/đường dẫn riêng/settings/library.js sinh.
