# BÁO CÁO AUDIT PUBLIC API: GITHUB REST API (v3)

---

## I. TỔNG QUAN API

* **Tên Dịch Vụ:** GitHub REST API
* **Phiên bản:** v3
* **Base URL:** `https://api.github.com`
* **Định dạng dữ liệu:** JSON (`application/json`)
* **Cơ chế xác thực:** Token-based (Bearer Token / OAuth2) hoặc Basic Auth (Deprecated)
* **Tài liệu tham khảo:** [GitHub REST API Documentation](https://docs.github.com/en/rest)

---

## II. CHI TIẾT AUDIT 5 ENDPOINTS

### 1. Endpoint: Lấy thông tin người dùng (`Get a user`)

* **URL Path:** `GET /users/{username}`
* **Mục đích:** Truy vấn thông tin hồ sơ công khai của một người dùng dựa trên username.
* **HTTP Method:** `GET`

#### Headers chính:
* **Request Headers:**
  * `Accept: application/vnd.github+json` (Yêu cầu API response theo format định sẵn)
  * `Authorization: Bearer <TOKEN>` *(Optional - giúp tăng Rate Limit)*
  * `If-None-Match: "<etag_value>"` *(Optional - dùng cho Conditional Requests)*
* **Response Headers:**
  * `Content-Type: application/json; charset=utf-8`
  * `ETag: W/"5f82a912..."` *(Dùng cho caching client-side)*
  * `X-RateLimit-Limit: 60` (hoặc `5000` nếu đã xác thực)
  * `X-RateLimit-Remaining: 58`
  * `X-RateLimit-Reset: 1711900000`

#### HTTP Status Codes:
* `200 OK`: Trả về object chi tiết thông tin người dùng.
* `304 Not Modified`: Khi gửi kèm header `If-None-Match` và dữ liệu chưa bị thay đổi.
* `404 Not Found`: Không tìm thấy `username`.

#### Đánh giá tính RESTful:
* **Đạt:** Sử dụng đúng danh từ tài nguyên (`/users`), định danh rõ ràng qua ID/Username. Method `GET` có tính an toàn (Safe) và đẳng idempotent (Idempotent). Caching tốt qua `ETag`.

---

### 2. Endpoint: Danh sách Issue của Repository (`List repository issues`)

* **URL Path:** `GET /repos/{owner}/{repo}/issues`
* **Mục đích:** Lấy danh sách các issue thuộc về một repository cụ thể.
* **HTTP Method:** `GET`

#### Headers chính:
* **Request Headers:**
  * `Accept: application/vnd.github+json`
  * `Authorization: Bearer <TOKEN>`
* **Response Headers:**
  * `Content-Type: application/json; charset=utf-8`
  * `Link: <https://api.github.com/repositories/123/issues?page=2>; rel="next", <https://api.github.com/repositories/123/issues?page=5>; rel="last"` *(Phân trang)*
  * `X-Total-Count: 120` *(Nếu có custom header)*

#### HTTP Status Codes:
* `200 OK`: Trả về danh sách (array) các Issue objects.
* `301 Moved Permanently`: Nếu repository bị đổi tên hoặc chuyển hướng.
* `404 Not Found`: Repository không tồn tại hoặc riêng tư (Private).

#### Đánh giá tính RESTful:
* **Đạt:** Sử dụng mối quan hệ lồng nhau giữa các tài nguyên (`/repos/{owner}/{repo}/issues`). 
* **Điểm sáng:** Phân trang tuân thủ nguyên tắc **HATEOAS**thông qua header `Link` với các quan hệ `rel="next"`, `rel="last"`.

---

### 3. Endpoint: Tạo Issue mới (`Create an issue`)

* **URL Path:** `POST /repos/{owner}/{repo}/issues`
* **Mục đích:** Tạo một issue mới trong repository.
* **HTTP Method:** `POST`

#### Headers chính:
* **Request Headers:**
  * `Content-Type: application/json`
  * `Authorization: Bearer <TOKEN>` *(Bắt buộc)*
  * `Accept: application/vnd.github+json`
* **Response Headers:**
  * `Content-Type: application/json; charset=utf-8`
  * `Location: https://api.github.com/repos/{owner}/{repo}/issues/42` *(URL của tài nguyên vừa tạo)*

#### HTTP Status Codes:
* `201 Created`: Tạo thành công issue. Trả về thông tin issue vừa tạo.
* `400 Bad Request`: Payload JSON thiếu trường bắt buộc (VD: thiếu `title`).
* `401 Unauthorized`: Chưa cung cấp Access Token.
* `403 Forbidden`: Token không đủ quyền ghi (write access) vào repo.
* `422 Unprocessable Entity`: Cấu trúc JSON đúng nhưng dữ liệu không hợp lệ (VD: label không tồn tại).

#### Đánh giá tính RESTful:
* **Đạt:** Trả về `201 Created` kèm theo header `Location` chỉ định URI của tài nguyên mới tạo. Không mang tính idempotent (mỗi lần POST tạo 1 issue mới).

---

### 4. Endpoint: Cập nhật thông tin Issue (`Update an issue`)

* **URL Path:** `PATCH /repos/{owner}/{repo}/issues/{issue_number}`
* **Mục đích:** Chỉnh sửa một số thuộc tính của issue (title, body, state, assignees...).
* **HTTP Method:** `PATCH`

#### Headers chính:
* **Request Headers:**
  * `Content-Type: application/json`
  * `Authorization: Bearer <TOKEN>` *(Bắt buộc)*
* **Response Headers:**
  * `Content-Type: application/json; charset=utf-8`

#### HTTP Status Codes:
* `200 OK`: Cập nhật thành công, trả về object issue đã được sửa.
* `403 Forbidden`: Không có quyền sửa issue.
* `404 Not Found`: Không tìm thấy issue hoặc repo.
* `422 Unprocessable Entity`: Dữ liệu field truyền lên không hợp lệ.

#### Đánh giá tính RESTful:
* **Đạt:** Sử dụng đúng chuẩn `PATCH` cho việc cập nhật một phần (partial update) thay vì `PUT` (thay thế toàn bộ). Xác định đúng tài nguyên bằng URI đầy đủ `/issues/{issue_number}`.

---

### 5. Endpoint: Xóa một Label khỏi Repository (`Delete a label`)

* **URL Path:** `DELETE /repos/{owner}/{repo}/labels/{name}`
* **Mục đích:** Xóa vĩnh viễn một label khỏi repository.
* **HTTP Method:** `DELETE`

#### Headers chính:
* **Request Headers:**
  * `Authorization: Bearer <TOKEN>` *(Bắt buộc)*
* **Response Headers:**
  * `X-RateLimit-Limit: 5000`
  * *(Thường không có Body nên Content-Type không bắt buộc)*

#### HTTP Status Codes:
* `204 No Content`: Xóa thành công, không trả về dữ liệu trong Response Body.
* `404 Not Found`: Label cần xóa không tồn tại.
* `403 Forbidden`: Tài khoản không đủ quyền admin/write.

#### Đánh giá tính RESTful:
* **Đạt:** Sử dụng chuẩn động từ `DELETE`. Chuẩn hóa HTTP Status Code `204 No Content` khi hành động thành công và không cần gửi lại nội dung dữ liệu.

