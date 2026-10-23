import psycopg2

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="product_store",
        user="postgres",
        password="Admin@123"
    )

connection = get_connection()
cursor = connection.cursor()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/products")
def get_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, price, image
    FROM products
    ORDER BY id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": float(row[2]),
            "image": row[3]
        })
    return products

@app.post("/products")

def post_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name, price, image
    FROM products ORDER BY id"""
                   )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.put("/products/{id}")
def put_product(id: int, name: str, price: float, image: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO products (id, name, price, image)
    VALUES (%s, %s, %s, %s)
    """, (id, name, price, image)
                   )


