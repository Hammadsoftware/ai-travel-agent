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
    max_size=10,

    # Don't wait forever for a connection
    timeout=15,

    # Recycle old connections
    max_lifetime=300,

    # Check connection before using it
    check=ConnectionPool.check_connection,

    kwargs={
        "row_factory": dict_row,
        "connect_timeout": 10,
        "sslmode": "require",
    },

    open=True,
)


def get_db():
    return pool.connection()


def close_db():
    pool.close()