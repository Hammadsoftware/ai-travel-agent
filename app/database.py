import os

from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5,
    kwargs={
        "row_factory": dict_row,
    },
)


def get_db():
    return pool.connection()