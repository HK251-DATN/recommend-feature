# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python-based recommendation/search microservice for the e-commerce platform. Exposes a Flask REST API on port 5000. Uses Elasticsearch for product search and Google Gemini for natural language understanding.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask API server
python app.py

# Run CLI chatbot (interactive terminal mode)
python main.py

# Ingest product data from product.csv into Elasticsearch
python ingest_data.py

# Export product data from PostgreSQL to product.csv
python data_cronjob.py
```

**Docker:**

```bash
# Start Elasticsearch + Flask API
docker-compose up -d

# Rebuild after code changes
docker-compose up -d --build api
```

## Architecture

**Data flow:**

1. `data_cronjob.py` — queries the ecommerce PostgreSQL DB and exports `product.csv`
2. `ingest_data.py` — reads `product.csv`, generates 384-dim embeddings via `all-MiniLM-L6-v2`, bulk-indexes into Elasticsearch index `products_index`
3. `search_engine.py` — wraps Elasticsearch queries (BM25 keyword, k-NN vector, hybrid)
4. `chatbot_agent.py` — uses Gemini API (`gemini-1.5-flash`) for keyword extraction and response generation
5. `app.py` — Flask REST API that wires search + chatbot together
6. `main.py` — interactive CLI wrapper (dev/testing only)

**Elasticsearch index `products_index` fields:**

- `product_name` (text, boost 3x), `product_description` (text), `tags` (text, boost 2x), `category_name` (keyword)
- `embedding` — dense_vector, 384 dims, cosine similarity, used for k-NN

**Hybrid search** (`search_hybrid`) combines BM25 multi_match (boost 0.5) and k-NN (boost 0.5) in a single Elasticsearch query body.

## API Endpoints

| Method | Path                                | Description                                                            |
| ------ | ----------------------------------- | ---------------------------------------------------------------------- |
| GET    | `/api/search/keyword?q=...&top_k=5` | BM25 keyword search                                                    |
| GET    | `/api/search/vector?q=...&top_k=5`  | k-NN vector search                                                     |
| GET    | `/api/search/hybrid?q=...&top_k=5`  | Hybrid search (default for chatbot)                                    |
| POST   | `/api/chat`                         | Chatbot: `{"message": "..."}` → keywords + products + natural response |

## Environment Variables

Copy `.env.example` to `.env`:

```
GEMINI_API_KEY=...
ELASTICSEARCH_HOST=http://localhost:9200   # use http://elasticsearch:9200 in Docker
ELASTICSEARCH_USER=                        # leave empty if security disabled
ELASTICSEARCH_PASSWORD=
```

## Key Details

- Elasticsearch runs on port **9250** (host) → 9200 (container) via `docker-compose.yml`. Security (`xpack.security`) is disabled for local dev.
- The SentenceTransformer model (`all-MiniLM-L6-v2`) is lazy-loaded on first vector search call.
- `data_cronjob.py` has hardcoded DB credentials (`localhost:5432`, `ecommercev3`) — update before running against a different environment.
- `ingest_data.py` **deletes and recreates** the index on each run — all existing data is lost.
- The `/api/chat` endpoint always uses hybrid search with `top_k=5`.
