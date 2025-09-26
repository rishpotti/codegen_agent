from unittest.mock import MagicMock

class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @classmethod
    def query(cls):
        return MagicMock() # Will be patched

class Notification:
    def __init__(self, id, user_id, message, type, read, timestamp):
        self.id = id
        self.user_id = user_id
        self.message = message
        self.type = type
        self.read = read
        self.timestamp = timestamp

    @classmethod
    def query(cls):
        return MagicMock() # Will be patched

class SQLAlchemy:
    def __init__(self):
        self.session = MagicMock()

db = SQLAlchemy()
