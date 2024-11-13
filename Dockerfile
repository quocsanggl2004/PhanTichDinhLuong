# Sử dụng hình ảnh Python chính thức phiên bản 3.9
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ nội dung từ thư mục hiện tại vào thư mục /app trong container
COPY . /app

# Cài đặt các phụ thuộc liệt kê trong requirements.txt 
# Đảm bảo Scrapy được liệt kê trong đó
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir scrapy --upgrade

# Đảm bảo quyền cho các script hoặc tệp cần thiết khác
# RUN chmod +x some_script.sh

# Chạy lệnh Scrapy để bắt đầu crawl
CMD ["scrapy", "crawl", "Telephone"]