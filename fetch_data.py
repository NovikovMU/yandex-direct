import redis
import json

from create_connection import PostgreSQLConnection


redis_connection = redis.Redis(host='localhost', port=6379, db=0)


def fetch_data():
    with PostgreSQLConnection() as cursor:
        cached_data = redis_connection.get('accounts_list')
        if cached_data:
            result = json.loads(cached_data)
        else:
            cursor.execute(
                """
                SELECT name, upper_limit, user_id
                FROM accounts a
                INNER JOIN users u
                ON a.user_id = u.telegram_id
                where u.is_verified = TRUE;
                """
            )
            result = cursor.fetchall()
            redis_connection.set('accounts_list', json.dumps(result))
    return result
