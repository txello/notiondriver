from notion_driver.base import NotionDriverBase
from notion_driver.errors.database import DatabaseError
from notion_driver.utils.parse import NotionParse



class NotionDriver(NotionDriverBase):
    def __init__(self, token, default_database_id = None):
        super().__init__(token, default_database_id)
        
    def execute(self, statement: str, parameters=None):
        results = []
        statement = statement.strip()
        
        if not statement.lower().startswith("select"):
            raise DatabaseError("Only SELECT statements are supported.")
        
        parsed = NotionParse.parse(statement)
        for table in parsed.FROM:
            database_id = self._resolve_database_id(table)
            
            notion_filter = self._build_notion_filter(parsed.WHERE)
            response = self.connection.query(database_id=database_id, **notion_filter)
            results.extend(response.get("results", []))
        
        results = self._format_results(results, selected_columns=self._selected_columns(parsed.SELECT))
        
        if parsed.ORDER_BY:
            results = self._apply_order_by(results=results, order_by=parsed.ORDER_BY)
        
        return results