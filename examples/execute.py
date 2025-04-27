import os
from notion_driver import NotionDriver

driver = NotionDriver(
    token=os.environ.get("NOTION_TOKEN"),
    #default_database_id=os.environ.get("DATABASE_ID") - Добавляем БД-one-access-only.
    default_database_id=None
)
result = driver.execute("SELECT Value FROM test1 WHERE number.Integer = 14")
print(result)