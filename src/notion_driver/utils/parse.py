from dataclasses import dataclass, field
from typing import Any
import mo_sql_parsing as mosp

from notion_driver.enums.operator import OperatorEnum


@dataclass
class SQLParse:
    SELECT: list[str] = field(default_factory=list)
    FROM: list[str] = field(default_factory=list)
    WHERE: list[OperatorEnum, list[str, Any]] = field(default_factory=list)
    
    ORDER_BY: list[str] = field(default_factory=list)


class NotionParse:
    @classmethod
    def parse(cls, statement: str):
        query = mosp.parse(statement)
        
        return SQLParse(
            SELECT=cls._select(query),
            FROM=cls._from(query),
            WHERE=cls._where(query),
            ORDER_BY=cls._order_by(query)
        )
        
        
    @classmethod
    def _select(cls, query: dict|list):
        select_fields = []
        if "select" in query:
            select_arr = query["select"] if isinstance(query["select"], list) else [query["select"]]
            for arr in select_arr:
                for key, item in arr.items():
                    if isinstance(item, dict):
                        item = item.get("value") or item.get("name") or str(item)
                    
                    if key == "all_columns": item = "*"
                    select_fields.append(item)

        return select_fields
    
    @classmethod
    def _from(cls, query: str):
        from_fields = []
        if "from" in query:
            if isinstance(query["from"], list):
                for item in query["from"]:
                    if isinstance(item, dict):
                        from_fields.append(item.get("value") or item.get("name") or str(item))
                    else:
                        from_fields.append(str(item))
            else:
                from_fields.append(query["from"])
        return from_fields
    
    @classmethod
    def _where(cls, query: str):
        conditions = []
        if "where" in query:
            query = query["where"]
            for op, condition in query.items():
                if op in {"and", "or", "not"}:
                    sub_conditions = []
                    for sub in (condition if isinstance(condition, list) else [condition]):
                        sub_conditions.extend(cls._where(sub))
                    conditions.append((OperatorEnum(op), sub_conditions))
                else:
                    cond_list = []
                    for c in condition:
                        if isinstance(c, dict):
                            if "column" in c:
                                cond_list.append(c["column"])
                            elif "literal" in c:
                                cond_list.append(c["literal"])
                            else:
                                cond_list.append(c)
                        else:
                            cond_list.append(c)
                    conditions.append((OperatorEnum(op), cond_list))
        return conditions
    
    @classmethod
    def _order_by(cls, query: dict | list):
        """Извлекает ORDER BY из запроса"""
        order_by = []
        if "orderby" in query:
            order_by_arr = query["orderby"] if isinstance(query["orderby"], list) else [query["orderby"]]
            for arr in order_by_arr:
                # Если это строка, то сортируем по этому полю
                if isinstance(arr, str):
                    order_by.append((arr, "asc"))  # Сортировка по возрастанию по умолчанию
                elif isinstance(arr, dict):
                    # Если это словарь, извлекаем столбец и направление
                    column = arr.get("value") or arr.get("column")
                    direction = arr.get("sort", "asc").lower()  # По умолчанию "asc"
                    order_by.append((column, direction))

        return order_by
    
    @classmethod
    def urlparse_where(cls, where):
        if not where:
            return {}

        if len(where) == 1:
            return {"filter": cls._parse_condition(where[0])}
        
        return {
            "filter": {
                "and": [cls._parse_condition(cond) for cond in where]
            }
        }
    
    @classmethod
    def _parse_condition(cls, condition):
        op, values = condition
        
        if op == OperatorEnum.AND:
            return {
                "and": [cls._parse_condition(sub) for sub in values]
            }
        elif op == OperatorEnum.OR:
            return {
                "or": [cls._parse_condition(sub) for sub in values]
            }
        elif op == OperatorEnum.NOT:
            return {
                "not": cls._parse_condition(values[0])
            }
        else:
            column, value = values

            # !!! Новое: Разбиваем type и имя поля
            if "." in column:
                property_type, column_name = column.split(".", 1)
            else:
                # Если нет типа - дефолт на rich_text
                property_type, column_name = "rich_text", column
            
            property_type = property_type.lower()

            notion_operator = {
                OperatorEnum.EQ: {"equals": value},
                OperatorEnum.NEQ: {"does_not_equal": value},
                OperatorEnum.GT: {"greater_than": value},
                OperatorEnum.GTE: {"greater_than_or_equal_to": value},
                OperatorEnum.LT: {"less_than": value},
                OperatorEnum.LTE: {"less_than_or_equal_to": value},
            }[op]

            return {
                "property": column_name,
                property_type: notion_operator
            }