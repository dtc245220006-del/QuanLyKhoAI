# Migration PostgreSQL → MySQL

Nếu cần giữ dữ liệu cũ, trước tiên tạo MySQL schema rồi đặt biến môi trường:

```powershell
$env:SOURCE_DATABASE_URL="postgresql+pg8000://USER:PASSWORD@localhost:5432/quan_ly_kho"
$env:DATABASE_URL="mysql+pymysql://root:PASSWORD@localhost:3306/quan_ly_kho"
python scripts/migrate_pg_to_mysql.py
```

Chạy một lần sau khi database MySQL đã có schema và chưa chứa cùng dữ liệu.
