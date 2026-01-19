from main import get_db
TABLES = [
    'ratings',
    'comments',
    'content',
    'users'
]

db = get_db()
cursor = db.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS=0")

for table in TABLES:
    cursor.execute(f"TRUNCATE TABLE {table}")

cursor.execute("SET FOREIGN_KEY_CHECKS=1")

db.commit()
db.close()

print("Database berhasil di-reset")

