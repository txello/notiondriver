from notion_driver.ext.sqlalchemy.cursor import NotionCursor


class NotionConnection:
    def __init__(self, driver, databases_id=None):
        self.driver = driver
        self.database_id = databases_id

    def execute(self, statement, parameters=None):
        pass

    def close(self):
        pass

    def rollback(self):
        # Notion не поддерживает транзакции — метод-заглушка
        pass

    def commit(self):
        # Notion не поддерживает транзакции — метод-заглушка
        pass

    def begin(self):
        # Также может ожидаться SQLAlchemy — метод-заглушка
        pass

    def cursor(self):
        return NotionCursor(self.driver, databases_id=self.database_id)
