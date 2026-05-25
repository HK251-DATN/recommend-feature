#!/bin/sh
set -e

echo "Waiting for Elasticsearch..."
until curl -sf "${ELASTICSEARCH_HOST:-http://elasticsearch:9200}/_cluster/health" > /dev/null 2>&1; do
  sleep 3
done

echo "Initial data load (PostgreSQL -> Elasticsearch)..."
python data_cronjob.py
python ingest_data.py

echo "Starting cron daemon (data sync every 5 minutes)..."
cron

echo "Starting Flask API..."
exec python app.py
