import psycopg2


class PostgreSQLConnection:
    def __init__(
            self,
            password=None,
            host=None,
            port=None,
            user=None
    ) -> None:
        self.password = password or 'mysecretpassword'
        self.host = host or 'db'
        self.port = port or '5432'
        self.user = user or 'postgres'

    def __enter__(self):
        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password
        )
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
