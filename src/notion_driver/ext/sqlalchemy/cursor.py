from sqlalchemy import exc

from notion_driver.driver import NotionDriver

class NotionCursor:
    def __init__(self, driver, **kwargs):
        self.driver: NotionDriver = driver
        self._results = []
        self._table_cache = {}
        
        self.description = []  # Атрибут для хранения информации о столбцах
        
        self._current_index = 0  # Индекс для fetchmany() и fetchone()

    def execute(self, statement, parameters=None):
        results = self.driver.execute(statement=statement, parameters=parameters)
        self._results.extend(results)
        self._current_index = 0  # Сброс индекса после выполнения запроса
        
        if self._results:
            first_row = self._results[0]
            self.description = [(key, None, None, None, None, None, None) for key in first_row.keys()]
        return self._results

    def all(self):
        """Вернуть все результаты как список кортежей (значение столбца)"""
        return [tuple(row.values()) for row in self._results]

    def one(self):
        """Вернуть одну запись как кортеж (значение столбца) или ошибку"""
        if not self._results:
            raise exc.DatabaseError("No results found")
        if len(self._results) > 1:
            raise exc.DatabaseError("Multiple results found when exactly one was expected")
        return tuple(self._results[0].values())

    def first(self):
        """Вернуть первую запись как кортеж (значение столбца) или None"""
        if not self._results:
            return None
        return tuple(self._results[0].values())

    def fetchall(self):
        """Вернуть все результаты как список кортежей (значение столбца)"""
        return [tuple(row.values()) for row in self._results]

    def fetchone(self):
        """Вернуть одну запись как кортеж (значение столбца) или None"""
        if self._current_index < len(self._results):
            row = self._results[self._current_index]
            self._current_index += 1
            return tuple(row.values())
        return None

    def fetchmany(self, size=1):
        """Вернуть несколько записей как кортежи (значение столбца)"""
        end_index = self._current_index + size
        results = self._results[self._current_index:end_index]
        self._current_index = end_index
        return [tuple(row.values()) for row in results]

    def __iter__(self):
        """Поддержка итерации по результатам"""
        return iter(self._results)

    def close(self):
        pass