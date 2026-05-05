### create .env file in root folder

Copy file .env.example thành file .env, rồi thêm các biến môi trường vào file .env

```sh
# Environment Variables
# ask chatGPT how to get gemini api key
GEMINI_API_KEY=""
ELASTICSEARCH_HOST="http://localhost:9200"
ELASTICSEARCH_USER="admin"
ELASTICSEARCH_PASSWORD="admin"
```

### cách chạy service

```sh
# set up all environment 1 times
pip install -r requirements.txt

# chạy job collect data
python data_cronjob.py

# chạy docker compose
docker-compose up -- build -d

# chạy ingest data
python ingest_data.py

# query bằng 4 api
http://localhost:5000/api/search/keyword?q=banh&top_k=5
http://localhost:5000/api/search/vector?q=banh&top_k=5
http://localhost:5000/api/search/hybrid?q=banh&top_k=5
http://localhost:5000/api/chat
```
