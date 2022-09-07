import numpy as np

from homomorphic_polynomial_system import keygen
from homomorphic_polynomial_system.utils import ROUND_TO_INT, ROUND_TO_REAL_NUMBERS
from homomorphic_polynomial_system.enc_num import serialize, deserialize

from .client_utils import *


class ClientConn:
    def __init__(self, ip: str, port: str):
        self.address = f"https://{ip}:{port}"

        self.login = None
        self.private_key = None
        self.public_key = None

    def sign_up(self):
        print(f"{Fore.CYAN}Signing up:{Style.RESET_ALL} "
              f"name{Fore.LIGHTBLACK_EX} -> login -> password{Style.RESET_ALL}")
        name = input("Enter name: ")

        print(f"{Fore.CYAN}Signing up:{Fore.LIGHTBLACK_EX} "
              f"name -> {Style.RESET_ALL}login{Fore.LIGHTBLACK_EX} -> password{Style.RESET_ALL}")
        login = signup_login(self.address)

        print(f"{Fore.CYAN}Signing up:{Fore.LIGHTBLACK_EX} "
              f"name -> login -> {Style.RESET_ALL}password")
        password = signup_password()

        print("To use remote secure memory you need private and public keys.")
        print("Both will be generated automatically after you enter the parameters:")

        base, degree = enter_alg_params()
        self.private_key, self.public_key = keygen.generate_abramov_keypair(base, degree)

        user_data = {"login": login,
                     "name": name,
                     "passwd_hash": md5(password.encode('utf-8')).hexdigest()}

        requests.post(f"{self.address}/create_user", json=user_data,
                      verify='./clientside/openssl_cert/cert.pem')

        with open('./clientside/keys/private_key.fhe', 'wb') as file_private_key, \
                open('./clientside/keys/public_key.fhe', 'wb') as file_public_key:
            file_private_key.write(pickle.dumps(self.private_key))
            file_public_key.write(pickle.dumps(self.public_key))

        print(f"{Fore.GREEN}You have successfully registered{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Private and public keys were saved to 'keys' directory{Style.RESET_ALL}")

    def sign_in(self):
        login, resp = response_login(self.address)

        correct_password = resp[0][PASSWORD_HASH]
        signin_password(correct_password)

        self.login = login
        print(f"{Fore.GREEN}You have successfully authorize{Style.RESET_ALL}")

        self.private_key = enter_key(key_type='private')
        self.public_key = enter_key(key_type='public')

        print(f"{Fore.GREEN}Keys has been added{Style.RESET_ALL}")

    def sign_out(self):
        self.login = None
        self.private_key = None
        self.public_key = None

    def init_new_variable(self):
        var_name = str(input("Enter a variable name: "))
        exist = requests.get(f"{self.address}/check_variable_exist?login={self.login}&var_name={var_name}",
                             verify='./clientside/openssl_cert/cert.pem')

        if len(exist.json()) != 0:
            print(f"{Fore.RED}Value '{var_name}' already initialized{Style.RESET_ALL}")
            return

        enc_value, value = enter_value(self.public_key)
        serialized_oj = serialize(enc_value)
        variable = {"var_name": var_name,
                    "value": serialized_oj,
                    "login": self.login}

        requests.post(f"{self.address}/init_new_variable", json=variable,
                      verify='./clientside/openssl_cert/cert.pem')

        print(f"{Fore.GREEN}Initialized: {var_name} = {value}{Style.RESET_ALL}")

    def get_memory(self):
        response = requests.get(f"{self.address}/get_memory?login={self.login}",
                                verify='./clientside/openssl_cert/cert.pem')

        memory_dump = response.json()
        if len(memory_dump) != 0:
            for idx, variable in enumerate(memory_dump):
                var_name = variable[NAME]
                serialized_obj = variable[VALUE]
                enc_value = deserialize(serialized_obj)
                value = self.private_key.decrypt(enc_value)
                print(f"{Fore.GREEN}#{idx + 1}: {var_name} = {value}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}No initialized variables{Style.RESET_ALL}")

    def get_variable(self):
        var_name = str(input("Enter a variable name: "))
        response = requests.get(f"{self.address}/get_variable?login={self.login}&var_name={var_name}",
                                verify='./clientside/openssl_cert/cert.pem')

        if len(response.json()) != 0:
            serialized_obj = response.json()[0][VALUE]
            enc_value = deserialize(serialized_obj)
            value = self.private_key.decrypt(enc_value)
            print(f"{Fore.GREEN}{var_name} = {value}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}No variable with name '{var_name}'{Style.RESET_ALL}")

    def edit_value(self):
        var_name = str(input("Enter a variable name: "))
        exist = requests.get(f"{self.address}/check_variable_exist?login={self.login}&var_name={var_name}",
                             verify='./clientside/openssl_cert/cert.pem')

        if len(exist.json()) == 0:
            print(f"{Fore.RED}No variable with name '{var_name}'{Style.RESET_ALL}")
            return

        enc_value, value = enter_value(self.public_key)
        serialized_oj = serialize(enc_value)

        variable = {"var_name": var_name,
                    "value": serialized_oj,
                    "login": self.login}

        requests.post(f"{self.address}/edit_value", json=variable,
                      verify='./clientside/openssl_cert/cert.pem')

        print(f"{Fore.GREEN}Edited: {var_name} = {value}{Style.RESET_ALL}")

    def delete_variable(self):
        var_name = str(input("Enter a variable name: "))
        exist = requests.get(f"{self.address}/check_variable_exist?login={self.login}&var_name={var_name}",
                             verify='./clientside/openssl_cert/cert.pem')

        if len(exist.json()) == 0:
            print(f"{Fore.RED}No variable with name '{var_name}'{Style.RESET_ALL}")
            return

        requests.get(f"{self.address}/delete_variable?login={self.login}&var_name={var_name}",
                     verify='./clientside/openssl_cert/cert.pem')

        print(f"{Fore.GREEN}Variable '{var_name}' was deleted{Style.RESET_ALL}")

    def calc_variables(self, op):
        var_name1 = str(input("Enter 1st variable name: "))
        exist = requests.get(f"{self.address}/check_variable_exist?login={self.login}&var_name={var_name1}",
                             verify='./clientside/openssl_cert/cert.pem')

        if len(exist.json()) == 0:
            print(f"{Fore.RED}No variable with name '{var_name1}'{Style.RESET_ALL}")
            return

        var_name2 = str(input("Enter 2nd variable name: "))
        exist = requests.get(f"{self.address}/check_variable_exist?login={self.login}&var_name={var_name2}",
                             verify='./clientside/openssl_cert/cert.pem')

        if len(exist.json()) == 0:
            print(f"{Fore.RED}No variable with name '{var_name2}'{Style.RESET_ALL}")
            return

        var_name_res = str(input("Enter variable name in which to write the result: "))
        exist = requests.get(f"{self.address}/check_variable_exist?login={self.login}&var_name={var_name_res}",
                             verify='./clientside/openssl_cert/cert.pem')

        if len(exist.json()) == 0:
            print(f"{Fore.RED}No variable with name '{var_name_res}'{Style.RESET_ALL}")
            return

        if op == "+":
            calc_data = {"login": self.login,
                         "var_name1": var_name1,
                         "var_name2": var_name2,
                         "var_name_res": var_name_res,
                         "op": "+"}

            response = requests.post(f"{self.address}/calc_variables", json=calc_data,
                                     verify='./clientside/openssl_cert/cert.pem')
            serialized_obj = response.json()
            enc_result = deserialize(serialized_obj)
            result = self.private_key.decrypt(enc_result)
            rounded_result = np.round(result, ROUND_TO_INT)
            print(f"{Fore.GREEN}{var_name1} + {var_name2} = {rounded_result}{Style.RESET_ALL}")

        if op == "-":
            calc_data = {"login": self.login,
                         "var_name1": var_name1,
                         "var_name2": var_name2,
                         "var_name_res": var_name_res,
                         "op": "-"}

            response = requests.post(f"{self.address}/calc_variables", json=calc_data,
                                     verify='./clientside/openssl_cert/cert.pem')
            serialized_obj = response.json()
            enc_result = deserialize(serialized_obj)
            result = self.private_key.decrypt(enc_result)
            rounded_result = np.round(result, ROUND_TO_INT)
            print(f"{Fore.GREEN}{var_name1} - {var_name2} = {rounded_result}{Style.RESET_ALL}")

        if op == "*":
            calc_data = {"login": self.login,
                         "var_name1": var_name1,
                         "var_name2": var_name2,
                         "var_name_res": var_name_res,
                         "op": "*"}

            response = requests.post(f"{self.address}/calc_variables", json=calc_data,
                                     verify='./clientside/openssl_cert/cert.pem')
            serialized_obj = response.json()
            enc_result = deserialize(serialized_obj)
            result = self.private_key.decrypt(enc_result)
            rounded_result = np.round(result, ROUND_TO_INT)
            print(f"{Fore.GREEN}{var_name1} * {var_name2} = {rounded_result}{Style.RESET_ALL}")

        # DIVISION IS DIFFERENT FROM OTHER OPERATIONS
        if op == "/":
            try:
                calc_data = {"login": self.login,
                             "var_name1": var_name1,
                             "var_name2": var_name2}

                response = requests.post(f"{self.address}/div_variables", json=calc_data,
                                         verify='./clientside/openssl_cert/cert.pem')

                response_result = response.json()
                enc_whole_part, enc_remains, enc_divider = \
                    deserialize(response_result[WHOLE_PART]), \
                    deserialize(response_result[REMAINS]), \
                    deserialize(response_result[DIVIDER])

                whole_part = self.private_key.decrypt(enc_whole_part)
                remains = self.private_key.decrypt(enc_remains)
                divider = self.private_key.decrypt(enc_divider)

                result = whole_part + remains / divider
                rounded_result = np.round(result, ROUND_TO_REAL_NUMBERS)
                print(f"{Fore.GREEN}{var_name1} / {var_name2} = {rounded_result}{Style.RESET_ALL}")

                rounded_result_to_int = np.round(result, ROUND_TO_INT)
                print(f"{Fore.RED}Attention! Cryptosystem doesn't allow to encrypt floats. "
                      f"So calculated value will be stored as rounded: "
                      f"({rounded_result_to_int}){Style.RESET_ALL}")
                enc_rounded_result = self.public_key.encrypt(rounded_result_to_int)
                serialized_obj = serialize(enc_rounded_result)

                variable = {"var_name": var_name_res,
                            "value": serialized_obj,
                            "login": self.login}

                requests.post(f"{self.address}/edit_value", json=variable,
                              verify='./clientside/openssl_cert/cert.pem')

            except ZeroDivisionError:
                print(f"{Fore.RED}Division by zero{Style.RESET_ALL}")

    def get_key(self, key):
        if key == "private":
            print(self.private_key.get_root())
        if key == "public":
            print(self.public_key.get_polynomial())

    def update_keys(self):
        pass
        decision = input(f"{Fore.RED}Updating the keys will lead to temporarily downloading the entire "
                         f"remote memory on local host to perform the re-encryption operation with new keys."
                         f" Do you want to continue? [y/n] :{Style.RESET_ALL}")

        if decision == 'n' or decision == 'no':
            return

        base, degree = enter_alg_params()
        new_private_key, new_public_key \
            = keygen.generate_abramov_keypair(base, degree)

        response = requests.get(f"{self.address}/get_memory?login={self.login}",
                                verify='./clientside/openssl_cert/cert.pem')

        memory_dump = response.json()
        if len(memory_dump) != 0:
            for idx, variable in enumerate(memory_dump):
                var_name = variable[NAME]
                serialized_obj = variable[VALUE]
                enc_value = deserialize(serialized_obj)
                value = self.private_key.decrypt(enc_value)
                new_enc_value = new_public_key.encrypt(value)
                serialized_obj = serialize(new_enc_value)

                variable = {"var_name": var_name,
                            "value": serialized_obj,
                            "login": self.login}

                requests.post(f"{self.address}/edit_value", json=variable,
                              verify='./clientside/openssl_cert/cert.pem')

        self.private_key, self.public_key \
            = new_private_key, new_public_key

        with open('./clientside/keys/private_key.fhe', 'wb') as file_private_key, \
                open('./clientside/keys/public_key.fhe', 'wb') as file_public_key:
            file_private_key.write(pickle.dumps(self.private_key))
            file_public_key.write(pickle.dumps(self.public_key))

        print(f"{Fore.GREEN}Private and public keys were updated "
              f"and saved to 'keys' directory{Style.RESET_ALL}")
