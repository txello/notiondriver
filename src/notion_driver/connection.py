from notion_client import Client


class NotionConnection:
    def __init__(self, token: str):
        self.__token = token
        
        self.client = Client(auth=token)
    
    def query(self, database_id:str, **filters: dict):
        return self.client.databases.query(database_id=database_id, **filters)