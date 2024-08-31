from app.database.abstraction import StorageProvider
from app.database.redis import RedisCache
from app.database.sqlite import SqliteDatabase

Database = SqliteDatabase
