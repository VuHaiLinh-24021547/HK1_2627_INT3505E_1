# Security Audit Report - Social Network API

Các điểm nguy cơ có thể gây rò rỉ thông tin bảo mật trên hệ thống API Social Network.

---

### 1. Lộ Access/Refresh Token qua hệ thống Logging (Logging Leakage)
* **Mô tả:** Các hệ thống Reverse Proxy (Nginx, HAProxy) hoặc thư viện Application Logging vô tình ghi lại toàn bộ HTTP Header (`Authorization: Bearer <token>`) hoặc Request Body của `/auth/login` vào file log.
* **Nguy cơ:** Khi file log bị truy cập trái phép hoặc gửi sang dịch vụ bên thứ ba (ELK, Datadog), kẻ tấn công có thể chiếm đoạt token hoặc mật khẩu thô của người dùng.

### 2. Vi phạm kiểm tra quyền cấp đối tượng (BOLA / IDOR) trên Endpoint `GET /posts/{id}`
* **Mô tả:** Hệ thống chỉ kiểm tra token có scope `posts:read` hay chưa, nhưng bỏ qua bước kiểm tra bài viết đó có thuộc chế độ "Riêng tư" (Private) hoặc thuộc về người dùng khác hay không.
* **Nguy cơ:** Kẻ tấn công có thể thay đổi tham số `{id}` trên URL để đọc trái phép các bài viết riêng tư của bất kỳ người dùng nào trong hệ thống.

### 3. Thông báo lỗi quá chi tiết tại Endpoint `/auth/login` (User Enumeration)
* **Mô tả:** Trả về thông báo chi tiết dạng `"Email không tồn tại"` thay vì thông báo chung `"Email hoặc mật khẩu không chính xác"`.
* **Nguy cơ:** Kẻ tấn công có thể lợi dụng điều này để dò quét (enumerate) xem những email nào đã đăng ký tài khoản trên hệ thống.

### 4. Lộ dữ liệu nhạy cảm trong JWT Payload (Unencrypted Claims)
* **Mô tả:** Đưa các dữ liệu nhạy cảm của người dùng (như `email`, `phone_number`, `role`, `internal_user_id`) vào phần Payload của JWT mà không mã hóa.
* **Nguy cơ:** Bản chất JWT Payload chỉ được mã hóa dạng Base64URL chứ không phải mã hóa mật mã (encryption). Bất kỳ ai bắt được token đều có thể decode và đọc toàn bộ dữ liệu này.

### 5. Lưu trữ Token không an toàn phía Client (Client-Side Storage Leakage)
* **Mô tả:** Phía Web Client lưu trữ `access_token` hoặc `refresh_token` trong `localStorage` hoặc `sessionStorage`.
* **Nguy cơ:** Nếu trang web dính lỗi XSS (Cross-Site Scripting), mã độc của kẻ tấn công có thể dễ dàng đọc toàn bộ `localStorage` và đánh cắp token. *(Khuyến nghị: Dùng HttpOnly, Secure Cookie cho Refresh Token)*.

### 6. Lộ thông tin hệ thống qua Verbose Error Messages (Stack Trace Leakage)
* **Mô tả:** Khi xảy ra lỗi 500 Internal Server Error hoặc 400 Bad Request, API trả về chi tiết Stack Trace của Python, phiên bản SQLite/PostgreSQL, hoặc tên các thư viện nội bộ.
* **Nguy cơ:** Giúp kẻ tấn công nắm được kiến trúc hạ tầng và các thư viện hệ thống đang dùng để tìm kiếm các lỗ hổng zero-day tương ứng.