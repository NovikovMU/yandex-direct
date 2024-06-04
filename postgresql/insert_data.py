from create_table import PostgreSQLConnection


with PostgreSQLConnection() as cursor:
    cursor.execute("""
        INSERT INTO testusers (user_id, name, amount) VALUES
        (16, 'Максим', 2),
        (159, 'Артем', 1),
        (3, 'Игорь', 33);
    """)
