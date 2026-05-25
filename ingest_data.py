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

def ensure_index(es):
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

    if not es.indices.exists(index=INDEX_NAME):
        print(f"Creating index '{INDEX_NAME}'...")
        es.indices.create(index=INDEX_NAME, body=index_mapping)
        print("Index created successfully.")
    else:
        print(f"Index '{INDEX_NAME}' already exists, skipping creation.")

def get_indexed_ids(es) -> set:
    """Returns all document IDs currently in the index."""
    ids = set()
    resp = helpers.scan(es, index=INDEX_NAME, query={"query": {"match_all": {}}}, _source=False)
    for hit in resp:
        ids.add(hit["_id"])
    return ids

def delete_orphans(es, indexed_ids: set, current_ids: set):
    """Deletes documents whose IDs are no longer in the product catalog."""
    orphan_ids = indexed_ids - current_ids
    if not orphan_ids:
        print("No orphaned documents to delete.")
        return

    deletions = [{"_op_type": "delete", "_index": INDEX_NAME, "_id": oid} for oid in orphan_ids]
    helpers.bulk(es, deletions)
    print(f"Deleted {len(orphan_ids)} orphaned document(s): {orphan_ids}")

def ingest_data():
    es = get_es_client()

    if not es.ping():
        print("Cannot connect to Elasticsearch. Please ensure it is running.")
        return

    ensure_index(es)

    print("Loading Sentence Transformer model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Reading product.csv...")
    df = pd.read_csv("product.csv")
    df = df.fillna("")

    current_ids = set(str(row["product_general_id"]) for _, row in df.iterrows())

    documents = []
    print("Generating embeddings and preparing data for Elasticsearch...")

    for _, row in df.iterrows():
        combined_text = f"{row['product_name']} {row['product_description']} {row['category_name']} {row['tags']}"
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

    print(f"Upserting {len(documents)} products...")
    helpers.bulk(es, documents)
    print("Upsert completed.")

    print("Checking for orphaned documents...")
    indexed_ids = get_indexed_ids(es)
    delete_orphans(es, indexed_ids, current_ids)

    print("Data ingestion completed successfully!")

if __name__ == "__main__":
    ingest_data()
