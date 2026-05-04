import os
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ES_USER = os.getenv("ELASTICSEARCH_USER", "")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")
INDEX_NAME = "products_index"
MODEL_NAME = "all-MiniLM-L6-v2"

# Lazy loading of model
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def get_es_client():
    if ES_USER and ES_PASSWORD:
        return Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASSWORD))
    return Elasticsearch(ES_HOST)

es = get_es_client()

def format_results(hits):
    results = []
    for hit in hits:
        source = hit["_source"]
        score = hit.get("_score", 0)
        results.append({
            "product_general_id": source.get("product_general_id"),
            "product_name": source.get("product_name"),
            "category_name": source.get("category_name"),
            "min_price": source.get("min_price"),
            "img": source.get("img", ""),
            "product_description": source.get("product_description", ""),
            "score": score
        })
    return results

def search_keyword(query: str, top_k: int = 5):
    """BM25 Content-based search"""
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["product_name^3", "product_description", "tags^2", "category_name"],
                "fuzziness": "AUTO"
            }
        },
        "size": top_k
    }
    response = es.search(index=INDEX_NAME, body=body)
    return format_results(response["hits"]["hits"])

def search_vector(query: str, top_k: int = 5):
    """k-NN Vector search"""
    model = get_model()
    query_vector = model.encode(query).tolist()
    
    body = {
        "knn": {
            "field": "embedding",
            "query_vector": query_vector,
            "k": top_k,
            "num_candidates": 100
        },
        "size": top_k
    }
    response = es.search(index=INDEX_NAME, body=body)
    return format_results(response["hits"]["hits"])

def search_hybrid(query: str, top_k: int = 5):
    """Hybrid search combining BM25 and k-NN"""
    model = get_model()
    query_vector = model.encode(query).tolist()
    
    # In a real hybrid setup, you might want to use Rank Fusion (RRF), 
    # but for simplicity, we combine them in a boolean query or simple script score.
    # Here we use Elasticsearch 8.x KNN search combined with standard query.
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["product_name^3", "product_description", "tags^2", "category_name"],
                "fuzziness": "AUTO",
                "boost": 0.5
            }
        },
        "knn": {
            "field": "embedding",
            "query_vector": query_vector,
            "k": top_k,
            "num_candidates": 100,
            "boost": 0.5
        },
        "size": top_k
    }
    
    response = es.search(index=INDEX_NAME, body=body)
    return format_results(response["hits"]["hits"])
