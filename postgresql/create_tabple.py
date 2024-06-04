from create_connection import PostgreSQLConnection


with PostgreSQLConnection() as cursor:

        cursor.execute("""
        DROP TABLE IF EXISTS users, accounts, users_accounts CASCADE
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );

        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_accounts (
            user_id INTEGER,
            account_id INTEGER,
            just_registered BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            amount NUMERIC NOT NULL,
            demand_time TIMESTAMPTZ,
            PRIMARY KEY (user_id, account_id),
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                REFERENCES users (telegram_id),
            CONSTRAINT fk_account
                FOREIGN KEY (account_id)
                REFERENCES accounts (id)
        );
        """)
