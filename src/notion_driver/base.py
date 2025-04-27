from notion_driver.connection import NotionConnection
from notion_driver.errors.database import DatabaseError, NoSuchTableError
from notion_driver.utils.parse import NotionParse, SQLParse


class NotionDriverBase:
    def __init__(self, token: str, default_database_id: str|None = None):
        self.__token = token
        self.default_database_id = default_database_id
        
        self.connection = NotionConnection(token=token)\
            
        self._database_cache = {}
        
    def _resolve_database_id(self, table_name: str) -> str:
        """Определить database_id по имени таблицы и проверке ограничений."""
        # Если есть жестко заданный database_id
        if self.default_database_id:
            # Проверим имя этой базы
            database = self._get_database(self.default_database_id)
            if not self._table_name_matches(database, table_name):
                raise DatabaseError(
                    f"Access to database '{table_name}' is restricted. "
                    f"Only '{self.default_database_id}' is allowed by connection."
                )
            return self.default_database_id

        # Иначе искать по имени базы
        database_id = self._find_database_id_by_name(table_name)
        if not database_id:
            raise NoSuchTableError(f"Table '{table_name}' not found in Notion workspace.")
        return database_id
    
    def _get_database(self, database_id: str):
        """Получить описание базы данных (с кэшированием)."""
        if database_id not in self._database_cache:
            self._database_cache[database_id] = self.connection.client.databases.retrieve(database_id=database_id)
        return self._database_cache[database_id]

    def _find_database_id_by_name(self, table_name: str):
        """Искать database_id по названию таблицы."""
        response = self.connection.client.search(filter={"property": "object", "value": "database"})
        for result in response.get("results", []):
            title = "".join(t.get("plain_text", "") for t in result.get("title", []))
            if title.lower() == table_name.lower():
                return result["id"]
        return None

    def _table_name_matches(self, database, table_name):
        """Проверка совпадения названия базы данных."""
        title = database.get("title", [])
        if not title:
            return False
        return any(t.get("plain_text", "").lower() == table_name.lower() for t in title)
    
    def _format_results(self, results, selected_columns=None):
        """Преобразовать результаты запроса в список словарей, с учётом нужных колонок."""
        formatted = []
        select_all = (not selected_columns) or ("*" in selected_columns)

        for row in results:
            props = row.get("properties", {})
            item = {}
            for key, value in props.items():
                if select_all or (key in selected_columns):
                    item[key] = self._extract_value(value)
            formatted.append(item)
        return formatted
    
    def _selected_columns(self, query_select):
        selected_columns = None
        if query_select != '*':
            selected_columns = [
                col['value'] if isinstance(col, dict) else col
                for col in query_select
            ]
        
        return selected_columns
    
    def _extract_value(self, prop):
        """Извлечь значение из поля Notion."""
        if prop.get("type") == "title":
            return "".join([t.get("plain_text", "") for t in prop.get("title", [])])
        if prop.get("type") == "rich_text":
            return "".join([t.get("plain_text", "") for t in prop.get("rich_text", [])])
        if prop.get("type") == "number":
            return prop.get("number")
        if prop.get("type") == "checkbox":
            return prop.get("checkbox")
        # Можно добавить поддержку других типов
        return None
    
    def _build_notion_filter(self, query_where: str):
        return NotionParse.urlparse_where(query_where)
    
    def _apply_order_by(self, results, order_by):
        """Применяет сортировку по указанным полям, учитывая возможные значения None."""
        if not order_by:
            return results

        # Для каждого столбца и направления сортировки
        for column, direction in order_by:
            # Сортируем результаты по значению в указанном столбце
            results = sorted(
                results,
                key=lambda x: x.get(column, 0),  # Сортируем по значению столбца, по умолчанию 0 для None
                reverse=(direction == 'desc')    # Сортировка по убыванию, если направление 'desc'
            )
        
        return results