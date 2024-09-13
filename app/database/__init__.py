# from app.database.deprecated_redis import RedisCache
from app.database.sqlite import SqliteDatabase
# from app.database.postgres import PostgresDatabase
# from app.database.mongodb import MongoDB
# from app.database.mysql import MySQLDatabase

Database = SqliteDatabase
