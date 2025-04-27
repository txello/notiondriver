from sqlalchemy.engine import default
from sqlalchemy import exc

from notion_driver.ext.sqlalchemy.connection import NotionConnection
from notion_driver.ext.sqlalchemy.fake_dbapi import FakeDBAPI

from notion_driver.driver import NotionDriver

class NotionDialect(default.DefaultDialect):
    name = "notion"
    driver = "notion"
    supports_statement_cache = False  # Не поддерживаем кэширование запросов для этого диалекта

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None

    @classmethod
    def import_dbapi(cls):
        # Возвращаем фейковый DBAPI для SQLAlchemy
        return FakeDBAPI()

    def create_connect_args(self, url):
        #print(url.username, url.password, url.host, url.port, url.database)
        
        # Извлекаем параметры из URL
        token = url.username or url.password or url.host  # Используем хост для хранения токена
        if url.host == token:
            database_id = None
        else:
            database_id = url.host if url.host else None
        
        return ([], {"token": token, "database_id": database_id})

    def connect(self, *args, **kwargs):
        """
        Устанавливаем соединение с API Notion, используя переданные аргументы.
        """
        token = kwargs.get('token')
        database_id = kwargs.get('database_id')
        
        if not token:
            raise ValueError("Token must be provided")
        
        # Инициализация клиента Notion
        self.client = NotionDriver(token=token, default_database_id=database_id)
        self.database_id = database_id
        
        return NotionConnection(self.client, self.database_id)

    def get_database(self):
        # Используем client для получения базы данных Notion
        return self.client.get_collection_view(self.database_id)

    # Метод для выполнения SQL-запросов
    def execute(self, conn, statement, parameters, context=None):
        """
        Реализуем обработку запросов через Notion API.
        """
        # В данном примере просто делаем запрос к базе данных Notion
        # Пример запроса: SELECT * FROM users
        # В Notion нет прямого SQL, поэтому запрос нужно преобразовывать в API-запрос
        
        if statement.strip().lower().startswith("select"):
            response = self.client.databases.query(self.database_id)
            # Преобразуем ответ в формат, который можно вернуть как результат
            return response["results"]
        else:
            raise exc.DatabaseError("Unsupported SQL query type")

    def create(self, record_data):
        # Создаем новую запись в базе данных Notion
        database = self.get_database()
        new_record = database.collection.add_row()
        for key, value in record_data.items():
            setattr(new_record, key, value)

    def update(self, record_id, updated_data):
        # Обновляем существующую запись в базе данных Notion
        database = self.client.get_collection_view(self.database_id)
        record = database.collection.get_rows(query={"id": record_id})[0]
        for key, value in updated_data.items():
            setattr(record, key, value)