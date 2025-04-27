from sqlalchemy import exc


class FakeDBAPI:
    paramstyle = "named"

    class Error(Exception):
        pass

    @staticmethod
    def connect(*args, **kwargs):
        return FakeConnection()

class FakeConnection:
    # Простейшее фейковое соединение
    def execute(self, statement, parameters=None):
        # Обрабатываем запросы (например, SELECT)
        if statement.strip().lower().startswith("select"):
            return [{"id": 1, "name": "Test Item"}]
        else:
            raise exc.DatabaseError("Unsupported SQL query")
    
    def close(self):
        pass