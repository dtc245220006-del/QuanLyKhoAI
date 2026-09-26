import os

import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "quan_ly_kho"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def search_inventory(intent: dict):
    conn = get_connection()
    try:
        where = []
        params = []

        item_name = intent.get("item_name")
        group_name = intent.get("group_name")
        only_low_stock = bool(intent.get("only_low_stock", False))
        max_results = min(max(int(intent.get("max_results", 10)), 1), 50)

        if item_name:
            where.append("h.ten_hang LIKE %s")
            params.append(f"%{item_name}%")
        if group_name:
            where.append("n.ten_nhom LIKE %s")
            params.append(f"%{group_name}%")
        if only_low_stock:
            where.append("t.so_luong < h.ton_toi_thieu")

        sql = """
            SELECT
                h.id AS ma_hang,
                h.ten_hang,
                n.ten_nhom,
                t.so_luong AS so_luong_ton,
                h.ton_toi_thieu,
                h.gia_nhap,
                h.gia_ban,
                t.ngay_cap_nhat
            FROM ton_kho t
            INNER JOIN hang_hoa h ON h.id = t.ma_hang
            LEFT JOIN nhom_hang n ON n.id = h.ma_nhom
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY t.so_luong ASC LIMIT %s"
        params.append(max_results)

        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()
