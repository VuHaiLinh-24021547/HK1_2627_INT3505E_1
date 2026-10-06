# Báo Cáo Đánh Giá (Review) Spotify Web API
> **Đơn vị đánh giá:** API Review Team  
> **Đối tượng:** Spotify Web API (`https://api.spotify.com/v1`)  
> **Khung tham chiếu:** API Review Checklist (9 tiêu chuẩn thiết kế RESTful API)

---

## 1. Tổng quan Đánh giá (Executive Summary)

Spotify Web API là một trong những hệ thống Web API phổ biến và rộng lớn nhất hiện nay. Nhìn chung, Spotify áp dụng tương đối chuẩn chỉnh các nguyên tắc RESTful API, đảm bảo tính nhất quán cao, bảo mật chặt chẽ và trải nghiệm nhà phát triển (Developer Experience - DX) tốt.

### Bảng tổng hợp kết quả (Scorecard)

| STT | Tiêu chí | Trạng thái | Điểm đánh giá | Ghi chú ngắn |
| :--- | :--- | :---: | :---: | :--- |
| **01** | Tài nguyên là danh từ | ⚠️ Đạt một phần | 8/10 | RESTful cho các tài nguyên chính, dùng RPC-style (động từ) cho Player controls. |
| **02** | Naming nhất quán | ✅ Đạt | 10/10 | Tuân thủ tuyệt đối: `kebab-case` cho URL, `snake_case` cho Query/Body. |
| **03** | Status code đúng nghĩa | ✅ Đạt | 10/10 | Sử dụng đúng chuẩn HTTP Status Codes, không trả lời `200 OK` kèm body lỗi. |
| **04** | Idempotency rõ ràng | ✅ Đạt | 8.5/10 | GET, PUT, DELETE chuẩn idempotent; POST không hỗ trợ `Idempotency-Key` header. |
| **05** | Error response có cấu trúc | ⚠️ Cần cải thiện | 7/10 | Có cấu trúc nhất quán nhưng chưa áp dụng chuẩn **RFC 7807** (`problem+json`). |
| **06** | Pagination rõ ràng | ✅ Đạt | 10/10 | Hỗ trợ cả Offset-based và Cursor-based, giới hạn `limit` rõ ràng. |
| **07** | Filter/Sort đa dạng | ✅ Đạt | 9.5/10 | Tìm kiếm nâng cao, hỗ trợ Sparse Fieldsets qua tham số `fields`. |
| **08** | Authentication & Security | ✅ Đạt xuất sắc | 10/10 | OAuth 2.0 + PKCE, Token ở Header, xử lý Rate Limit với `Retry-After`. |
| **09** | Versioning + Deprecation | ✅ Đạt | 9/10 | Sử dụng URL Prefix (`/v1`), lộ trình Deprecation thông báo rõ ràng. |

---

## 2. Phân tích Chi tiết Theo Checklist

### 01. Tài nguyên là danh từ (Noun-based Resources)
* **Yêu cầu:** URLs chỉ chứa danh từ, không dùng động từ. HTTP Method thể hiện hành động.
* **Đánh giá Spotify API:**
  * **Điểm tốt:** Hầu hết các endpoint chính đều sử dụng danh từ số nhiều và định danh tài nguyên chuẩn REST:
    * `GET /v1/tracks/{id}`
    * `GET /v1/albums/{id}/tracks`
    * `POST /v1/users/{user_id}/playlists`
  * **Hạn chế:** Đối với tính năng điều khiển trình phát nhạc (Player API), Spotify chuyển sang dạng **RPC-style** chứa động từ trong URL:
    * `POST /v1/me/player/next`
    * `POST /v1/me/player/previous`
    * `PUT /v1/me/player/pause`
    * `PUT /v1/me/player/play`
  * *Nhận xét:* Dù vi phạm nguyên tắc "URL thuần danh từ", đây là đánh đổi thực tế (pragmatic design) chấp nhận được đối với các lệnh điều khiển media thời gian thực.

---

### 02. Naming nhất quán (Consistent Naming Conventions)
* **Yêu cầu:** Path dùng `lowercase` + `kebab-case`, query parameter dùng `snake_case`, dùng danh từ số nhiều cho collection.
* **Đánh giá Spotify API:**
  * **URL Path:** Hoàn toàn dùng `kebab-case` và số nhiều:
    * `/v1/audio-features`
    * `/v1/recommendations`
    * `/v1/browse/categories`
  * **Query Parameters & Request/Response Body:** Đồng nhất dùng `snake_case`:
    * Query: `?client_id=...&redirect_uri=...&include_groups=album`
    * Body JSON: `"duration_ms": 200040`, `"external_urls": {...}`, `"release_date_precision": "day"`
  * *Nhận xét:* Tuyệt đối tuân thủ quy tắc đặt tên xuyên suốt toàn bộ API ecosystem.

---

### 03. Status code đúng nghĩa (Proper Status Codes)
* **Yêu cầu:** Mỗi response dùng code phù hợp. Tuyệt đối không trả `200 OK` đi kèm thông báo lỗi trong body.
* **Đánh giá Spotify API:**
  * Spotify tuân thủ nghiêm ngặt các chuẩn mã trạng thái HTTP:
    * `200 OK`: Truy vấn / cập nhật thành công.
    * `201 Created`: Tạo tài nguyên thành công (VD: tạo playlist mới).
    * `204 No Content`: Thao tác thành công nhưng không có dữ liệu trả về (VD: `PUT /v1/me/player/play`).
    * `304 Not Modified`: Hỗ trợ caching hiệu quả.
    * `400 Bad Request`: Payload hoặc tham số không hợp lệ.
    * `401 Unauthorized`: Token hết hạn hoặc không hợp lệ.
    * `403 Forbidden`: Token không đủ Scope truy cập.
    * `404 Not Found`: Không tìm thấy tài nguyên.
    * `429 Too Many Requests`: Vượt quá Rate Limit.

---

### 04. Idempotency rõ ràng (Clear Idempotency)
* **Yêu cầu:** POST cần cơ chế `Idempotency-Key` (nếu có); PUT/DELETE phải đảm bảo tính Idempotent; tài liệu hóa rõ ràng.
* **Đánh giá Spotify API:**
  * Các phương thức `GET`, `PUT`, `DELETE` tuân thủ đúng tính chất Idempotent. Ví dụ: gọi `PUT /v1/me/player/play` nhiều lần vẫn giữ nguyên trạng thái "đang phát".
  * **Hạn chế:** Spotify API không chính thức hỗ trợ Header `Idempotency-Key` cho các lệnh `POST` tạo dữ liệu (như thêm bài hát vào playlist hay tạo playlist) để chống trùng lặp dữ liệu do Retry mạng.

---

### 05. Error response có cấu trúc (Structured Error Response)
* **Yêu cầu:** Theo chuẩn RFC 7807 (`application/problem+json`) nhất quán, có `type`, `title`, `detail`, `instance`.
* **Đánh giá Spotify API:**
  * Spotify sử dụng cấu trúc error JSON đồng nhất nhưng **theo chuẩn riêng**, chưa áp dụng chuẩn **RFC 7807**:
    ```json
    {
      "error": {
        "status": 401,
        "message": "Invalid access token"
      }
    }
    ```
  * Một số lỗi Authentication trả về theo chuẩn OAuth 2.0:
    ```json
    {
      "error": "invalid_grant",
      "error_description": "Refresh token revoked"
    }
    ```
  * *Đánh giá:* Dễ hiểu và đồng nhất, tuy nhiên nếu nâng cấp lên RFC 7807 sẽ giúp các công cụ client tự động hóa việc xử lý lỗi tốt hơn.

---

### 06. Pagination rõ ràng (Clear Pagination)
* **Yêu cầu:** Collection nào cũng có phân trang (cursor hoặc offset), có giới hạn trên (`limit`).
* **Đánh giá Spotify API:**
  * **Offset-based Pagination (Paging Object):** Áp dụng cho phần lớn collection (`limit`, `offset`, `total`, `next`, `previous`, `href`, `items`).
    ```json
    {
      "href": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
      "items": [ ... ],
      "limit": 1,
      "next": "https://api.spotify.com/v1/me/shows?offset=2&limit=1",
      "offset": 1,
      "previous": "https://api.spotify.com/v1/me/shows?offset=0&limit=1",
      "total": 4
    }
    ```
  * **Cursor-based Pagination (Cursor Paging Object):** Áp dụng cho danh sách động/mới nhất (VD: `GET /v1/me/following?type=artist`).
  * **Giới hạn:** Mọi endpoint đều có quy định `limit` mặc định (thường là 20) và tối đa (thường là 50).

---

### 07. Filter/Sort đa dạng (Rich Filter & Sort Features)
* **Yêu cầu:** Hỗ trợ lọc theo field chính, sort đa field, hỗ trợ **Sparse Fieldsets** (chọn field cần trả về).
* **Đánh giá Spotify API:**
  * **Lọc tìm kiếm (Filtering):** Endpoint `/v1/search` cực kỳ mạnh mẽ, hỗ trợ cú pháp lọc sâu theo từng thuộc tính:  
    `q=album:gold%20artist:abba&type=album`
  * **Sparse Fieldsets:** Spotify hỗ trợ tham số `fields` rất ấn tượng trên các tài nguyên lớn (như Playlist), cho phép client chỉ lấy đúng các trường mong muốn nhằm giảm dung lượng truyền tải:  
    `GET /v1/playlists/{playlist_id}?fields=name,tracks.items(track(name,href))`

---

### 08. Authentication & Security
* **Yêu cầu:** Token ở Header, không lộ qua URL. Có cơ chế Rate Limit rõ ràng.
* **Đánh giá Spotify API:**
  * **Chuẩn Xác thực:** Sử dụng OAuth 2.0 đầy đủ các flows (Authorization Code Flow with PKCE, Client Credentials Flow).
  * **Truyền Token:** Token bắt buộc phải gửi qua Header `Authorization: Bearer <token>`. Tuyệt đối không chấp nhận token qua Query Parameter trên URL.
  * **Rate Limiting:** Khi vi phạm giới hạn tần suất gọi, API trả về HTTP `429 Too Many Requests` đi kèm Response Header `Retry-After: <số_giây>` để thông báo thời gian client cần chờ trước khi thử lại.

---

### 09. Versioning + Deprecation
* **Yêu cầu:** Có version prefix trên URL ngay từ đầu. Có lộ trình ngừng hỗ trợ (Deprecation) rõ ràng.
* **Đánh giá Spotify API:**
  * **Versioning:** Sử dụng URL Path Prefix `/v1/` thống nhất từ khi ra mắt.
  * **Deprecation Policy:** Spotify thông báo các chính sách thay đổi API qua **Developer Dashboard**, **Changelog**, và gửi email trực tiếp cho các app đã đăng ký. Họ đưa ra khoảng thời gian chuyển tiếp (Grace Period) hợp lý trước khi chính thức tắt (sunset) các endpoint cũ.

---

## 3. Kết luận & Bài học kinh nghiệm (Takeaways)

Spotify Web API là một hình mẫu tuyệt vời về thiết kế **Pragmatic RESTful API** dành cho các hệ thống quy mô lớn. 

### Điểm sáng đáng học hỏi:
1. **Trải nghiệm Developer tuyệt vời:** Naming convention đồng nhất 100%, hỗ trợ Sparse Fieldsets (`fields`) giúp tối ưu hiệu năng mobile client.
2. **Quản lý Rate Limit thông minh:** Dùng header `Retry-After` tiêu chuẩn giúp client xây dựng cơ chế Retry (Exponential Backoff) dễ dàng.
3. **Bảo mật tiêu chuẩn cao:** Tắt hoàn toàn việc nhận Token qua URL, áp dụng OAuth 2.0 + PKCE triệt để.

### Điểm có thể cải thiện:
1. Chuẩn hóa error payload theo **RFC 7807** (`application/problem+json`).
2. Bổ sung header `Idempotency-Key` cho các tác vụ `POST` quan trọng nhằm tránh duplicate dữ liệu khi gặp sự cố mạng.