from create_connection import PostgreSQLConnection


def create_table():
    with PostgreSQLConnection() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            name TEXT NOT NULL UNIQUE,
            upper_limit INTEGER,
            demand_time TIMESTAMPTZ,
            is_entered_into_user_list BOOLEAN DEFAULT FALSE,
            is_verified BOOLEAN DEFAULT FALSE,
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                REFERENCES users (telegram_id)
        );
        """)


if __name__ == '__main__':
    create_table()