# 📋 API Testing Checklist & Quality Assurance

Checklist kiểm thử luồng chính trên Swagger UI / Postman cho hệ thống Quản lý Câu lạc bộ (Bao gồm Happy Path và Error Cases).

---

## 1. Module Xác thực (Authentication)

| Test ID | Endpoint | Method | Loại Test | Kịch bản Test | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Output) |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **AUTH_01** | `/auth/register` | `POST` | **Case Đúng** | Đăng ký tài khoản mới hợp lệ | Email mới, mật khẩu đúng chuẩn, họ tên | `201 Created` - Đăng ký thành công |
| **AUTH_02** | `/auth/register` | `POST` | **Case Lỗi** | Đăng ký email đã tồn tại | Email đã có trong hệ thống | `400 Bad Request` / `409 Conflict` |
| **AUTH_03** | `/auth/login` | `POST` | **Case Đúng** | Đăng nhập tài khoản chính xác | Email và mật khẩu đúng | `200 OK` - Trả về Access & Refresh Token |
| **AUTH_04** | `/auth/login` | `POST` | **Case Lỗi** | Đăng nhập sai mật khẩu | Email đúng, mật khẩu sai | `400 Bad Request` / `401 Unauthorized` |
| **AUTH_05** | `/auth/login` | `POST` | **Case Lỗi** | Đăng nhập vượt quá giới hạn Rate Limit | Gửi request liên tục > 5 lần/phút | `429 Too Many Requests` |
| **AUTH_06** | `/auth/Refresh_token` | `POST` | **Case Đúng** | Cấp lại Access Token mới | Refresh Token hợp lệ và còn hạn | `200 OK` - Trả về Access Token mới |

---

## 2. Module Câu lạc bộ & Thành viên (Club & Member Management)

| Test ID | Endpoint | Method | Loại Test | Kịch bản Test | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Output) |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **CLUB_01** | `/clubs` | `POST` | **Case Đúng** | Tạo mới một câu lạc bộ | Tên CLB, mô tả, user đăng nhập | `201 Created` - Tự động set làm Chủ nhiệm (Owner) |
| **CLUB_02** | `/clubs` | `GET` | **Case Đúng** | Lấy danh sách CLB có tìm kiếm | `club_name="IT"` | `200 OK` - Danh sách câu lạc bộ khớp tìm kiếm |
| **CLUB_03** | `/clubs/{id}` | `GET` | **Case Lỗi** | Xem chi tiết CLB khi chưa tham gia | User ngoài CLB | `403 Forbidden` - Không có quyền xem |
| **CLUB_04** | `/clubs/{id}` | `GET` | **Case Đúng** | Xem chi tiết CLB khi là thành viên | User đã tham gia CLB | `200 OK` - Chi tiết thông tin CLB |
| **CLUB_05** | `/clubs/{id}` | `PUT`/`PATCH` | **Case Lỗi** | Thành viên thường cố sửa thông tin CLB | User có `role != owner` | `403 Forbidden` |
| **CLUB_06** | `/clubs/{id}` | `DELETE` | **Case Lỗi** | Thành viên thường cố xóa CLB | User có `role != owner` | `403 Forbidden` |
| **CLUB_07** | `/clubs/{id}` | `DELETE` | **Case Đúng** | Chủ nhiệm thực hiện xóa CLB | User là Chủ nhiệm (Owner) | `200 OK` - Xóa thành công (Soft Delete) |
| **CLUB_08** | `/clubs/{id}/members` | `POST` | **Case Đúng** | Thêm thành viên vào CLB | `user_id` hợp lệ, role mong muốn | `201 Created` - Thêm thành viên thành công |
| **CLUB_09** | `/clubs/{id}/members/{user_id}` | `DELETE` | **Case Đúng** | Xóa thành viên khỏi CLB | `user_id` thành viên cần xóa | `200 OK` - Xóa thành viên thành công |

---



## 3. Module Hoạt động & Minh chứng (Club Activities & Attachments)

| Test ID | Endpoint | Method | Loại Test | Kịch bản Test | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Output) |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **ACT_01** | `/clubs/{id}/activities` | `POST` | **Case Đúng** | Tạo hoạt động mới cho CLB | Title chưa tồn tại, deadline hợp lệ | `201 Created` - Tạo task mới thành công |
| **ACT_02** | `/clubs/{id}/activities` | `POST` | **Case Lỗi** | Tạo hoạt động bị trùng tiêu đề trong CLB | Title đã tồn tại trong CLB | `400 Bad Request` / `409 Conflict` |
| **ACT_03** | `/clubs/{id}/activities` | `GET` | **Case Đúng** | Lọc và phân trang danh sách task | `status=TODO&priority=HIGH&page=1` | `200 OK` - Trả về `items` và `pagination` |
| **ACT_04** | `/clubs/activities/{id}` | `PATCH` | **Case Đúng** | Assignee cập nhật trạng thái hoạt động | Gửi `status: IN_PROGRESS` | `200 OK` - Cập nhật trạng thái thành công |
| **ACT_05** | `/clubs/activities/{id}` | `PATCH` | **Case Lỗi** | Assignee cố tình đổi tên/mô tả task | Gửi body kèm `title` mới | `403 Forbidden` |
| **ACT_06** | `/clubs/activities/{id}` | `PATCH` | **Case Lỗi** | Chuyển sai quy trình trạng thái (Workflow) | Nhảy cóc `TODO` -> `DONE` | `400 Bad Request` |
| **ACT_07** | `/clubs/activities/{id}` | `DELETE` | **Case Lỗi** | Assignee hoặc Member cố xóa hoạt động | User có `role_id != 1` | `403 Forbidden` |
| **ACT_08** | `/clubs/activities/{id}` | `DELETE` | **Case Đúng** | Chủ nhiệm CLB thực hiện xóa task | User có `role_id == 1` (Owner) | `200 OK` - Xóa hoạt động thành công |
| **ACT_09** | `/clubs/activities/{id}/attachments` | `POST` | **Case Lỗi** | Upload file sai định dạng cho phép | File đuôi `.exe`, `.zip`, `.bat` | `400 Bad Request` - Sai định dạng |
| **ACT_10** | `/clubs/activities/{id}/attachments` | `POST` | **Case Lỗi** | Upload file có dung lượng vượt giới hạn | File có kích thước > 5MB | `400 Bad Request` - File quá 5MB |
| **ACT_11** | `/clubs/activities/{id}/attachments` | `POST` | **Case Đúng** | Upload file ảnh/PDF minh chứng hợp lệ | File `.png`/`.pdf` < 5MB | `201 Created` - Lưu file vật lý và lưu JSON |
| **ACT_12** | `/clubs/activities/{id}/comments` | `POST` | **Case Đúng** | Thêm bình luận/trao đổi nội bộ | Nội dung chuỗi văn bản | `201 Created` - Thêm comment thành công |

