FROM python:3.10-slim

WORKDIR /app

# Install curl (entrypoint ES health-check) and cron (periodic data sync)
RUN apt-get update && apt-get install -y --no-install-recommends curl cron \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Tải trước model sentence-transformers để tiết kiệm thời gian khi khởi động container
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Install the crontab (runs data sync every 5 minutes)
COPY crontab /etc/cron.d/search-chat
RUN chmod 0644 /etc/cron.d/search-chat && crontab /etc/cron.d/search-chat

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
