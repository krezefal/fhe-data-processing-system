import pickle
from typing import Tuple

import psycopg2
from psycopg2 import sql
import numpy as np

from consts import VALUE


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

    def create_user(self, data: tuple):
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

    def get_user_info(self, login: str):
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

    def get_variable(self, login: str, name: bytes):
        try:
            query = sql.SQL("SELECT * FROM memory WHERE login = {login} and name = {name}").format(
                login=sql.Identifier(login),
                name=sql.Identifier(name),
            )

            self.cur.execute(query)
            variable_fields = self.cur.fetchall()
            return variable_fields

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    def get_memory(self, login: str):
        try:
            query = sql.SQL("SELECT * FROM memory WHERE login = {login}").format(
                login=sql.Identifier(login),
            )

            self.cur.execute(query)
            dump = self.cur.fetchall()
            return dump

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    def check_variable_exist(self, login: str, name: bytes) -> bool:
        try:
            query = sql.SQL("SELECT 1 FROM memory WHERE login = {login} and name = {name}").format(
                login=sql.Identifier(login),
                name=sql.Identifier(name),
            )

            self.cur.execute(query)
            response = self.cur.fetchall()

            if response is None:
                return False
            return True

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    def init_new_variable(self, var_data: tuple):
        try:
            # data = tuple(data.values())
            var_tokens = sql.SQL(', ').join(sql.Literal(n) for n in var_data)

            query = sql.SQL("INSERT INTO memory (var_name, login, value) VALUES ({var_tokens})").format(
                values=var_tokens
            )

            self.cur.execute(query)

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    def edit_value(self, login: str, name: bytes, value: bytes):
        try:

            query = sql.SQL("UPDATE memory SET value = {value} WHERE login = {login} and name = {name}").format(
                login=sql.Identifier(login),
                name=sql.Identifier(name),
                value=sql.Identifier(value)
            )

            self.cur.execute(query)

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    def delete_variable(self, login: str, name: bytes):
        try:

            query = sql.SQL("DELETE FROM memory WHERE login = {login} and name = {name}").format(
                login=sql.Identifier(login),
                name=sql.Identifier(name),
            )

            self.cur.execute(query)

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    def calc_variables(self, login: str, name1: bytes, name2: bytes, op: str) -> Tuple[np.poly1d, np.poly1d, np.poly1d]:
        try:
            variable1 = self.get_variable(login, name1)
            variable2 = self.get_variable(login, name2)

            enc_value1 = pickle.loads(variable1[VALUE])
            enc_value2 = pickle.loads(variable2[VALUE])

            if op == "+":
                return enc_value1 + enc_value2, None, None
            if op == "-":
                return enc_value1 - enc_value2, None, None
            if op == "*":
                return enc_value1 * enc_value2, None, None
            if op == "/":
                if enc_value2 == 0:
                    raise Exception('Zero division')

                enc_q, enc_r = enc_value1 / enc_value2
                return enc_q, enc_r, enc_value2

        except Exception:
            print("[DBConn]: An error occurred during query execution")
        finally:
            self.cur.close()
            self.conn.commit()

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
