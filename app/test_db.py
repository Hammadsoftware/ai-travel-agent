
from app.database import get_db


def test_connection():
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:

                cursor.execute("SELECT version();")

                result = cursor.fetchone()

                print("Database connected successfully!")
                print(result)

    except Exception as e:
        print("Database connection failed!")
        print(e)


if __name__ == "__main__":
    test_connection()