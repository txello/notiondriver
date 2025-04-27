import os
import sqlalchemy as sa

TOKEN=os.environ.get("NOTION_TOKEN")
# DATABASE_ID=os.environ.get("DATABASE_ID") - Добавляем БД-one-access-only.

# notion://{TOKEN} - Все БД от Токена
# notion://{TOKEN}@ - то же самое
# notion://{TOKEN}@{DATABASE_ID} - Определенная БД от Токена. Попытка доступа к другим через FROM вызовет ошибку `DatabaseError`

url = f"notion://{TOKEN}"

engine = sa.create_engine(url)
conn = engine.connect()

result = conn.execute(sa.text("SELECT ID, Value FROM test1 ORDER BY ID DESC"))
print(result.all())