# Notion-Driver

`Notion-Driver` — это Python-драйвер для работы с базами данных `Notion`, предоставляющий SQL-подобный интерфейс для взаимодействия с данными в Notion. Он позволяет выполнять запросы, используя конструкции SQL, и взаимодействовать с данными в вашей базе Notion.

## Особенности:
* Выполнение SQL-подобных запросов: `SELECT`, `FROM`, `WHERE`, `ORDER BY`.
* Поддержка сортировки данных по столбцам.
* Легкая интеграция с API Notion для выполнения запросов.
* Преобразование результатов запросов в формат, удобный для дальнейшей обработки.
* Поддержка SQLAlchemy

## Установка

Для установки и использования `notion-driver`, необходимо сначала установить его через pip:
```bash
pip install .
```
Затем создайте свой API-ключ для доступа к Notion и получите database_id для вашей базы данных.
```
DATABASE_ID - Ссылка из URL: https://www.notion.so/DATABASE_ID?v=.....
```
## Использование

1. Инициализация драйвера: Чтобы начать работу с Notion, создайте объект драйвера, передав свой API-ключ и идентификатор базы данных (по умолчанию будет использоваться база данных, указанная в настройках):
```py
from notion_driver import NotionDriver

# Создайте драйвер, передав свой API-ключ и database_id
driver = NotionDriver(token="your_notion_api_token", default_database_id="your_database_id")
```
2. Выполнение запросов: Для выполнения SQL-подобных запросов используйте метод execute:
```py
# Выполнение запроса
results = driver.execute("SELECT * FROM test1 WHERE title.ID = 1 ORDER BY Value DESC")

# Вывод результатов
print(results)
```

В данном примере будет выполнен запрос, который выберет все записи из базы данных test1, где столбец ID является типом title и равен 1, и отсортирует их по столбцу Value в порядке убывания.

3. Методы курсора: Полученные данные можно обрабатывать с использованием методов курсора:
```py
cursor = driver.execute("SELECT * FROM test1 ORDER BY ID DESC")
```

4. Подключение через URL и SQLAlchemy

Вы можете подключиться к Notion через SQLAlchemy с использованием URL-формата:
```py
import os
import sqlalchemy as sa

TOKEN = os.environ.get("NOTION_TOKEN")
# DATABASE_ID = os.environ.get("DATABASE_ID")  # Добавляем БД-one-access-only.

# notion://{TOKEN} - Все БД от Токена
# notion://{TOKEN}@ - То же самое
# notion://{TOKEN}@{DATABASE_ID} - Определённая БД от Токена. Попытка доступа к другим через FROM вызовет ошибку `DatabaseError`

url = f"notion://{TOKEN}"

engine = sa.create_engine(url)
conn = engine.connect()

# Выполнение SQL-запроса через SQLAlchemy
result = conn.execute(sa.text("SELECT ID, Value FROM test1 ORDER BY ID DESC"))
print(result.all())  # Печатает все результаты
```
