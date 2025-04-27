class DatabaseError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        
class NoSuchTableError(Exception):
    def __init__(self, *args):
        super().__init__(*args)