from create_connection import PostgreSQLConnection


with PostgreSQLConnection() as cursor:
    cursor.execute("""
    DROP TABLE IF EXISTS users, accounts CASCADE
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        just_registered BOOLEAN DEFAULT TRUE,
        is_verified BOOLEAN DEFAULT FALSE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        upper_limit INTEGER,
        demand_time TIMESTAMPTZ,
        user_id INTEGER,
        CONSTRAINT fk_user
            FOREIGN KEY (user_id)
            REFERENCES users (telegram_id)
    );
    """)
