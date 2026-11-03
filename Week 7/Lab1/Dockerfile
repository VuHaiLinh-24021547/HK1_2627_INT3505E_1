FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Ngăn Python tạo file .pyc và bật log trực tiếp ra console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cài đặt các thư viện cần thiết
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Coppy toàn bộ mã nguồn vào container
COPY . .

# Tạo sẵn thư mục instance cho SQLite (nếu chưa có)
RUN mkdir -p instance

# Mở cổng 5000
EXPOSE 5000

# Chạy ứng dụng
CMD ["python", "run.py"]