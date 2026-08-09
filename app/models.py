from app.database import get_db


def create_tables():
    with get_db() as conn:
        with conn.cursor() as cursor:

            # =========================
            # Users
            # =========================

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Add password to an existing users table
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS password VARCHAR(255);
            """)

            # =========================
            # Conversations
            # =========================

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # =========================
            # Messages
            # =========================

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER
                        REFERENCES conversations(id)
                        ON DELETE CASCADE,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        conn.commit()

    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()