# checkout a procuct using the product id and quantity and store the order in the database
import base64
import json
import os
import sqlite3
from typing import Optional

from langchain_core.tools import tool
DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")

def _checkout_product(product_id: int) -> str:
    """
    Place an order for the given product ID. Saves the order to the database and returns
    a confirmation message with the order ID, product name, and price.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return f"Error: product with ID {product_id} not found."

    name, price = row
    cursor.execute(
        "INSERT INTO orders (product_id, product_name, price) VALUES (?, ?, ?)",
        (product_id, name, price),
    )
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return (
        f"Order #{order_id} confirmed! '{name}' has been successfully ordered for ${price:.2f}. "
        f"Your order will arrive in 3-5 business days. Thank you for shopping with us!"
    )

checkout_product = tool(_checkout_product)

if __name__ == "__main__":
    # Single product
    result = _checkout_product(2)
    print("Checkout result:")
    print(result)