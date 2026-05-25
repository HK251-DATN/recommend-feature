import os
import psycopg2
import pandas as pd

# ====== DB CONFIG ======
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("SEARCH_CHAT_DB_NAME", "ecommerce_db"),
    "user": os.getenv("DB_USERNAME", "khoidev"),
    "password": os.getenv("DB_PASSWORD", "khoicktv"),
}

# ====== SQL QUERY ======
QUERY = """
SELECT 
    p.product_general_id,
    p.name AS product_name,
    p.description AS product_description,
    p.unit,
    p.unit_quantity,
    p.tags,
    p.img,
    p.created_at,

    c.category_id,
    c.category_name,
    c.description AS category_description,

    p.product_general_id,
    MIN(b.price) AS min_price    
FROM product_general p
LEFT JOIN category c 
    ON p.category_id = c.category_id
RIGHT JOIN batch_detail b
    ON p.product_general_id = b.product_general_id
GROUP BY p.product_general_id, c.category_id;
"""

def main():
    conn = None
    try:
        # 1. CONNECT DB
        conn = psycopg2.connect(**DB_CONFIG)

        # 2. QUERY → DATAFRAME
        df = pd.read_sql(QUERY, conn)

        # 3. CLEAN DATA (optional nhưng nên làm)
        # convert array tags -> string
        if 'tags' in df.columns:
            df['tags'] = df['tags'].apply(
                lambda x: ",".join(x) if isinstance(x, list) else ""
            )

        # 4. EXPORT CSV
        df.to_csv("product.csv", index=False, encoding="utf-8-sig")

        print("Export thành công → product.csv")

    except Exception as e:
        print("Lỗi:", e)

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()