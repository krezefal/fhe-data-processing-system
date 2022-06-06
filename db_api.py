import pickle
from typing import Tuple
from colorama import Fore, Style
import psycopg2
from psycopg2 import sql
import numpy as np

from consts import VALUE


class DBConn:
    def __init__(self, db_name, user, password):
        self.db_name = db_name
        self.user = user
        self.password = password

        self.cur = None
        try:
            self.conn = psycopg2.connect(f"dbname={self.db_name} user={self.user} password={self.password}")
        except ConnectionError:
            print(f"{Fore.RED}Error while connection establishment{Style.RESET_ALL}")

    def create_user(self, data: tuple):
        try:
            self.cur = self.conn.cursor()
            user_tokens = sql.SQL(', ').join(sql.Literal(n) for n in data)

            query = sql.SQL("INSERT INTO person (login, passwd_hash, public_key) VALUES ({values})").format(
                values=user_tokens
            )

            self.cur.execute(query)

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while inserting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def get_user_info(self, login: str):
        try:
            self.cur = self.conn.cursor()
            query = sql.SQL("SELECT * FROM person WHERE login = {login}").format(
                login=sql.Literal(login)
            )

            self.cur.execute(query)
            user_info = self.cur.fetchall()
            return user_info

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while getting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def get_variable(self, login: str, name: str):
        try:
            self.cur = self.conn.cursor()
            query = sql.SQL("SELECT * FROM memory WHERE login = {login} and var_name = {name}").format(
                login=sql.Literal(login),
                name=sql.Literal(name)
            )

            self.cur.execute(query)
            variable_fields = self.cur.fetchall()
            return variable_fields

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while getting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def get_memory(self, login: str):
        try:
            self.cur = self.conn.cursor()
            query = sql.SQL("SELECT * FROM memory WHERE login = {login}").format(
                login=sql.Literal(login),
            )

            self.cur.execute(query)
            dump = self.cur.fetchall()
            return dump

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while getting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def check_variable_exist(self, login: str, name: str) -> bool:
        try:
            self.cur = self.conn.cursor()
            query = sql.SQL("SELECT 1 FROM memory WHERE login = {login} and var_name = {name}").format(
                login=sql.Literal(login),
                name=sql.Literal(name),
            )

            self.cur.execute(query)
            response = self.cur.fetchall()

            return response

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while getting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def init_new_variable(self, var_data: tuple):
        try:
            self.cur = self.conn.cursor()
            var_tokens = sql.SQL(', ').join(sql.Literal(n) for n in var_data)

            query = sql.SQL("INSERT INTO memory (var_name, login, value) VALUES ({values})").format(
                values=var_tokens
            )

            self.cur.execute(query)

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while inserting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def edit_value(self, login: str, name: str, value: bytes):
        try:
            self.cur = self.conn.cursor()
            query = sql.SQL("UPDATE memory SET value = {value} WHERE login = {login} and var_name = {name}").format(
                login=sql.Literal(login),
                name=sql.Literal(name),
                value=sql.Literal(value)
            )

            self.cur.execute(query)

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while updating data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def delete_variable(self, login: str, name: str):
        try:
            self.cur = self.conn.cursor()
            query = sql.SQL("DELETE FROM memory WHERE login = {login} and var_name = {name}").format(
                login=sql.Literal(login),
                name=sql.Literal(name),
            )

            self.cur.execute(query)

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while deleting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def calc_variables(self, login: str, name1: bytes, name2: bytes, op: str) \
            -> Tuple[np.poly1d, np.poly1d, np.poly1d]:
        try:
            self.cur = self.conn.cursor()

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
                    raise Exception(f"{Fore.RED}Zero division{Style.RESET_ALL}")

                enc_q, enc_r = enc_value1 / enc_value2
                return enc_q, enc_r, enc_value2

        except (Exception, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while getting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
