import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()


class Product(BaseModel):
    id: int
    name: str
    price: float


products = []


@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/products")
def get_products():
    return products


@app.post("/products")
def add_product(product: Product):
    products.append(product)
    return {
        "message": "Product added",
        "products": products
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product.id == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")


@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: Product):
    for index, product in enumerate(products):
        if product.id == product_id:
            products[index] = updated_product
            return updated_product

    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for index, product in enumerate(products):
        if product.id == product_id:
            deleted = products.pop(index)

            return {
                "message": "Product deleted",
                "products": deleted
            }
    raise HTTPException(status_code=404, detail="Product not found")


def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="fastapi_store",
        user="postgres",
        password="Admin@123"
    )

    print("Connected to PostgreSQL successfully")
    return conn


@app.get('/products')
def get_product():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


@app.post('/products')
def add_product(product: Product):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products VALUES (%s, %s,%s)",
        (product.id,product.name,product.price))
    conn.commit()
    conn.close()
    return {
        "message": "Product added",
        "products": product
    }



@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE products
        SET name = %s,
            price = %s
        WHERE id = %s
        """,
        (product.name, product.price, product_id)
    )

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Product updated successfully"
    }



conn = get_connection()
conn.close()