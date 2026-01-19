import pymysql

DB_NAME = "gallery_creative"

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    autocommit=True
)

cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.close()
conn.close()

print(f"Database '{DB_NAME}' berhasil dibuat / sudah ada")
