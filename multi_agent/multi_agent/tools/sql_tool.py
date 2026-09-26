import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "multi_agent_shop"),
    )


def search_products(intent):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT *
        FROM products
        WHERE category = %s
    """

    cursor.execute(query, (intent["category"],))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows