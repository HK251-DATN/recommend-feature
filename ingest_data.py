import os
import pandas as pd
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Configuration
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ES_USER = os.getenv("ELASTICSEARCH_USER", "")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")

INDEX_NAME = "products_index"
# all-MiniLM-L6-v2 outputs 384-dimensional vectors
MODEL_NAME = "all-MiniLM-L6-v2" 

def get_es_client():
    if ES_USER and ES_PASSWORD:
        return Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASSWORD))
    return Elasticsearch(ES_HOST)

def create_index(es):
    index_mapping = {
        "mappings": {
            "properties": {
                "product_general_id": {"type": "integer"},
                "product_name": {"type": "text"},
                "product_description": {"type": "text"},
                "tags": {"type": "text"},
                "category_name": {"type": "keyword"},
                "min_price": {"type": "float"},
                "img": {"type": "keyword"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }
    
    if es.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting it to recreate...")
        es.indices.delete(index=INDEX_NAME)
        
    print(f"Creating index '{INDEX_NAME}'...")
    es.indices.create(index=INDEX_NAME, body=index_mapping)
    print("Index created successfully.")

def ingest_data():
    es = get_es_client()
    
    # Ensure Elasticsearch is connected
    if not es.ping():
        print("Cannot connect to Elasticsearch. Please ensure it is running.")
        return

    create_index(es)
    
    print("Loading Sentence Transformer model...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Reading product.csv...")
    df = pd.read_csv("product.csv")
    
    # Fill NaN values
    df = df.fillna("")
    
    documents = []
    print("Generating embeddings and preparing data for Elasticsearch...")
    
    for index, row in df.iterrows():
        # Combine text for vectorization
        combined_text = f"{row['product_name']} {row['product_description']} {row['category_name']} {row['tags']}"
        
        # Generate embedding
        embedding = model.encode(combined_text).tolist()
        
        doc = {
            "_index": INDEX_NAME,
            "_id": row["product_general_id"],
            "_source": {
                "product_general_id": row["product_general_id"],
                "product_name": row["product_name"],
                "product_description": row["product_description"],
                "tags": row["tags"],
                "category_name": row["category_name"],
                "min_price": float(row["min_price"]) if row["min_price"] else 0.0,
                "img": row["img"],
                "embedding": embedding
            }
        }
        documents.append(doc)
        
    print(f"Bulk indexing {len(documents)} products...")
    helpers.bulk(es, documents)
    print("Data ingestion completed successfully!")

if __name__ == "__main__":
    ingest_data()
