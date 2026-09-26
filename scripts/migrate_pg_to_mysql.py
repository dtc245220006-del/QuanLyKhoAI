"""One-time migration helper.

Set SOURCE_DATABASE_URL to the existing PostgreSQL URL and DATABASE_URL to the
new MySQL URL before running. This script copies rows in dependency order.
"""
import os
from sqlalchemy import create_engine, MetaData, select, insert

SOURCE_DATABASE_URL = os.environ.get("SOURCE_DATABASE_URL")
TARGET_DATABASE_URL = os.environ.get("DATABASE_URL")

if not SOURCE_DATABASE_URL or not TARGET_DATABASE_URL:
    raise SystemExit("Cần SOURCE_DATABASE_URL và DATABASE_URL")

source = create_engine(SOURCE_DATABASE_URL)
target = create_engine(TARGET_DATABASE_URL)

tables = [
    "users", "nhom_hang", "hang_hoa", "nha_cung_cap",
    "phieu_nhap", "chi_tiet_phieu_nhap", "ton_kho", "lich_su_kho",
    "phieu_xuat", "chi_tiet_phieu_xuat", "de_xuat_ai", "chi_tiet_de_xuat_ai",
]

src_meta = MetaData()
tgt_meta = MetaData()
src_meta.reflect(bind=source, only=tables)
tgt_meta.reflect(bind=target, only=tables)

with source.connect() as src, target.begin() as dst:
    for name in tables:
        src_table = src_meta.tables[name]
        tgt_table = tgt_meta.tables[name]
        rows = [dict(row._mapping) for row in src.execute(select(src_table))]
        if rows:
            dst.execute(insert(tgt_table), rows)
        print(f"{name}: {len(rows)} rows")

print("Migration hoàn tất.")
