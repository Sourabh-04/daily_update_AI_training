import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app1 = FastAPI()

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="library_store",
        user="postgres",
        password="Admin@123"
    )

class Book(BaseModel):
    id: int
    name: str
    author: str
    category: str
    pages: int
    price: float

@app1.get("/books")
def read_books():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM books")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app1.post("/books")
def create_book(book: Book):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO books VALUES (%s,%s,%s,%s,%s,%s)",
            (
                book.id,
                book.name,
                book.author,
                book.category,
                book.pages,
                book.price
            )
        )

        conn.commit()
        cur.close()
        conn.close()

        return {
            "message": "Book created successfully",
            "book": book
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app1.get("/books/technology")
def get_technology_books():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM books WHERE category = %s",
        ("Technology",)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


@app1.put("/books/price/{book_id}")
def update_book_price(book_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE books SET price = %s  WHERE book_id = %s",
        (950, book_id)
    )

    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    cur.close()
    conn.close()

    return {
        "message": f"Price updated successfully for book {book_id}"
    }

@app1.put("/books/stock/{book_id}/")
def update_stock(book_id: int, stock: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE books SET stock = %s  WHERE book_id = %s",
        (stock, book_id)
    )
    conn.commit()
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    cur.close()
    conn.close()

    return {
        "message": f"Price updated successfully for book {book_id}"
    }

conn = get_connection()
conn.close()