from typing import Tuple
from colorama import Fore, Style
import psycopg2
from psycopg2 import sql

from homomorphic_polynomial_system.enc_num import serialize, deserialize

VALUE = 1


class DBConn:
    def __init__(self, db_name, user, host, password):
        self.db_name = db_name
        self.user = user
        self.host = host
        self.password = password

        self.cur = None
        try:
            self.conn = psycopg2.connect(f"dbname={self.db_name} "
                                         f"user={self.user} "
                                         f"host={self.host} "
                                         f"password={self.password}")
        except ConnectionError:
            print(f"{Fore.RED}Error while connection establishment{Style.RESET_ALL}")

    def create_user(self, data: list):
        try:
            self.cur = self.conn.cursor()
            user_tokens = sql.SQL(', ').join(sql.Literal(n) for n in data)

            query = sql.SQL("INSERT INTO person (login, name, passwd_hash) VALUES ({values})").format(
                values=user_tokens
            )

            self.cur.execute(query)

        except (ConnectionError, psycopg2.Error) as error:
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

        except (ConnectionError, psycopg2.Error) as error:
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

        except (ConnectionError, psycopg2.Error) as error:
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
            memory_dump = self.cur.fetchall()
            return memory_dump

        except (ConnectionError, psycopg2.Error) as error:
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

        except (ConnectionError, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while getting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def init_new_variable(self, var_data: list):
        try:
            self.cur = self.conn.cursor()
            var_tokens = sql.SQL(', ').join(sql.Literal(n) for n in var_data)

            query = sql.SQL("INSERT INTO memory (var_name, value, login) VALUES ({values})").format(
                values=var_tokens
            )

            self.cur.execute(query)

        except (ConnectionError, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while inserting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def edit_value(self, login: str, var_name: str, value: str):
        try:
            self.cur = self.conn.cursor()
            query = sql.SQL("UPDATE memory SET value = {value} WHERE login = {login} and var_name = {var_name}").format(
                login=sql.Literal(login),
                var_name=sql.Literal(var_name),
                value=sql.Literal(value)
            )

            self.cur.execute(query)

        except (ConnectionError, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while updating data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def delete_variable(self, login: str, var_name: str):
        try:
            self.cur = self.conn.cursor()
            query = sql.SQL("DELETE FROM memory WHERE login = {login} and var_name = {var_name}").format(
                login=sql.Literal(login),
                var_name=sql.Literal(var_name),
            )

            self.cur.execute(query)

        except (ConnectionError, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while deleting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def calc_variables(self, login: str, var_name1: str, var_name2: str, var_name_res: str, op: str) -> str:
        try:
            self.cur = self.conn.cursor()

            variable1 = self.get_variable(login, var_name1)
            variable2 = self.get_variable(login, var_name2)

            enc_value1 = deserialize(variable1[0][VALUE])
            enc_value2 = deserialize(variable2[0][VALUE])

            enc_result = None

            if op == "+":
                enc_result = enc_value1 + enc_value2
            if op == "-":
                enc_result = enc_value1 - enc_value2
            if op == "*":
                enc_result = enc_value1 * enc_value2

            self.edit_value(login, var_name_res, serialize(enc_result))
            return serialize(enc_result)

        except (ConnectionError, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while getting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def div_variables(self, login: str, var_name1: str, var_name2: str) -> \
            Tuple[str, str, str]:
        try:
            self.cur = self.conn.cursor()

            variable1 = self.get_variable(login, var_name1)
            variable2 = self.get_variable(login, var_name2)

            enc_value1 = deserialize(variable1[0][VALUE])
            enc_value2 = deserialize(variable2[0][VALUE])

            enc_whole_part, enc_remains, enc_divider = enc_value1 / enc_value2
            return serialize(enc_whole_part), serialize(enc_remains), serialize(enc_divider)

        except (ConnectionError, psycopg2.Error) as error:
            print(f"{Fore.RED}Error while getting data: {error}{Style.RESET_ALL}")
        finally:
            self.cur.close()
            self.conn.commit()

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
