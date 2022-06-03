import psycopg2
from psycopg2 import sql

USER_CREDENTIALS_TABLE_NAME = "user_credentials"
MESSAGES_TABLE_NAME = "messages"


class DBConn:
    def __init__(self, db_name, user, password):
        self.db_name = db_name
        self.user = user
        self.password = password

        try:
            self.conn = psycopg2.connect(f"dbname={self.db_name} user={self.user} password={self.password}")
            self.cur = self.conn.cursor()
        except ConnectionError:
            print("[DBConn]: Some error occurred during connection establishment")

    def create_user(self, data):
        try:
            # data = tuple(data.values())
            user_tokens = sql.SQL(', ').join(sql.Literal(n) for n in data)

            query = sql.SQL("INSERT INTO person (login, password, public_key) VALUES ({values})").format(
                values=user_tokens
            )

            self.cur.execute(query)

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    def get_user_info(self, login):
        try:
            query = sql.SQL("SELECT * FROM person WHERE login = {login}").format(
                login=sql.Identifier(login),
            )

            self.cur.execute(query)
            user_info = self.cur.fetchall()
            return user_info

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    # TOTALLY TODO

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
