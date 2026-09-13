"""
Reviews API — reads from the `reviews` table in store.db and returns
aggregated rating information for products.
"""

import base64
import json
import os
import sqlite3
from typing import Optional, Union

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")


def _search_products(query: str, max_price: Optional[float] = None, is_organic: Optional[Union[bool, str]] = None) -> str:
    """
    Search the product database by keyword (matched against name, description, and category).
    Optionally filter by maximum price and/or organic status.
    Returns a JSON array of matching products, each with: id, name, category, price,
    description, is_organic.
    """
    if isinstance(is_organic, str):
        is_organic = is_organic.strip().lower() in ("true", "1", "yes")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql = "SELECT id, name, category, price, description, is_organic FROM products WHERE 1=1"
    params: list = []

    if query:
        sql += " AND (name LIKE ? OR description LIKE ? OR category LIKE ?)"
        like = f"%{query}%"
        params.extend([like, like, like])

    if max_price is not None:
        sql += " AND price <= ?"
        params.append(max_price)

    if is_organic is not None:
        sql += " AND is_organic = ?"
        params.append(1 if is_organic else 0)

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    products = [
        {
            "id":          row[0],
            "name":        row[1],
            "category":    row[2],
            "price":       row[3],
            "description": row[4],
            "is_organic":  bool(row[5]),
        }
        for row in rows
    ]
    return json.dumps(products)

search_products = tool(_search_products)

if __name__ == "__main__":
    # Single product
    result = _search_products("honey")
    print("Search results for 'honey':")
    print(result)

    # Multiple products
    # print("\nBatch ratings:")
    # results = get_ratings_for_products([1, 3, 5, 7])
    # for r in results:
    #     print(f"  Product {r['product_id']}: {r['average_rating']} stars ({r['review_count']} reviews)")