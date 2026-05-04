FROM python:3.10-slim

WORKDIR /app

# Cài đặt các system dependencies nếu cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Tải trước model sentence-transformers để tiết kiệm thời gian khi khởi động container
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 5000

# Khởi chạy Flask app
CMD ["python", "app.py"]
