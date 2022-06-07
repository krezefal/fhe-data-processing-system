from hashlib import md5
from colorama import Fore, Style
import pickle
import yaml

from abramov_system import keygen
from db_api import DBConn
from consts import *
import interface_utils

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

db = DBConn(config['conn_credentials']['dbname'],
            config['conn_credentials']['user'],
            config['conn_credentials']['password'])


class Interface:
    def __init__(self):
        self.login = None
        self.private_key = None
        self.public_key = None

    def __del__(self):
        db.close_connection()

    def sign_up(self):
        print(f"{Fore.CYAN}Signing up: {Fore.WHITE}name{Style.RESET_ALL} -> login -> password")
        login = interface_utils.signup_login(db)

        print(f"{Fore.CYAN}Signing up: {Style.RESET_ALL} name -> {Fore.WHITE}login{Style.RESET_ALL} -> password")
        name = input("Enter name: ")

        print(f"{Fore.CYAN}Signing up: {Style.RESET_ALL} name -> login -> {Fore.WHITE}password{Style.RESET_ALL}")
        password = interface_utils.signup_password()

        print("To use remote secure memory you need private and public keys.")
        print("Both will be generated automatically after you enter the parameters:")

        base, degree = interface_utils.enter_alg_params()
        self.private_key, self.public_key = keygen.generate_abramov_keypair(base, degree)

        db.create_user((login, name, md5(password.encode('utf-8')).hexdigest()))

        with open('keys/private_key.fhe', 'wb') as file_private_key, \
                open('keys/public_key.fhe', 'wb') as file_public_key:
            file_private_key.write(pickle.dumps(self.private_key))
            file_public_key.write(pickle.dumps(self.public_key))

        print(f"{Fore.GREEN}You have successfully registered{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Private and public keys were saved to 'keys' directory{Style.RESET_ALL}")

    def sign_in(self):
        login, resp = interface_utils.response_login(db)

        correct_password = resp[0][PASSWORD_HASH]
        interface_utils.signin_password(correct_password)

        self.login = login
        print(f"{Fore.GREEN}You have successfully authorize{Style.RESET_ALL}")

        self.private_key = interface_utils.enter_key(key_type='private')
        self.public_key = interface_utils.enter_key(key_type='public')

        print(f"{Fore.GREEN}Keys has been added{Style.RESET_ALL}")

    def operate(self):
        while True:

            print()
            print("'0' -> Logout                     '6' -> a + b")
            print("'1' -> Initialize new variable    '7' -> a - b")
            print("'2' -> Get variable list          '8' -> a * b")
            print("'3' -> Get variable               '9' -> a / b")
            print("'4' -> Edit value                 '10' -> Get private key (root)")
            print("'5' -> Delete variable            '11' -> Get public key (polynomial)")
            print()
            print("             '12' -> Update private and public keys")
            print()

            choice = interface_utils.enter_option("Enter operation number: ")
            match choice:

                case 0:
                    self.login = None
                    self.private_key = None
                    self.public_key = None
                    return

                case 1:  # Initialize new variable
                    name = str(input("Enter a variable name: "))
                    exist = db.check_variable_exist(self.login, name)
                    if exist:
                        print(f"{Fore.RED}Error: value '{name}' already initialized{Style.RESET_ALL}")
                        continue

                    enc_value, value = interface_utils.enter_value(self.public_key)
                    db.init_new_variable((name, self.login, pickle.dumps(enc_value)))
                    print(f"{Fore.GREEN}Initialized: {name} = {value}{Style.RESET_ALL}")

                case 2:  # Get variable list
                    dump = db.get_memory(self.login)
                    if len(dump) != 0:
                        for idx, variable in enumerate(dump):
                            name = variable[NAME]
                            value = self.private_key.decrypt(pickle.loads(variable[VALUE]))

                            print(f"{Fore.GREEN}#{idx + 1}: {name} = {value}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}No initialized variables{Style.RESET_ALL}")

                case 3:  # Get variable
                    name = str(input("Enter a variable name: "))
                    variable = db.get_variable(self.login, name)
                    if variable:
                        value = self.private_key.decrypt(pickle.loads(variable[0][VALUE]))
                        print(f"{Fore.GREEN}{name} = {value}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}No variable with name {name}{Style.RESET_ALL}")

                case 4:  # Edit value
                    name = str(input("Enter a variable name: "))
                    exist = db.check_variable_exist(self.login, name)
                    if not exist:
                        print(f"{Fore.RED}No variable with name {name}{Style.RESET_ALL}")
                        continue

                    enc_value, value = interface_utils.enter_value(self.public_key)
                    db.edit_value(self.login, name, pickle.dumps(enc_value))
                    print(f"{Fore.GREEN}Edited: {name} = {value}{Style.RESET_ALL}")

                case 5:  # Delete variable
                    name = str(input("Enter a variable name: "))
                    exist = db.check_variable_exist(self.login, name)
                    if not exist:
                        print(f"{Fore.RED}No variable with name {name}{Style.RESET_ALL}")
                        continue

                    db.delete_variable(self.login, name)
                    print(f"{Fore.GREEN}Variable '{name}' was deleted{Style.RESET_ALL}")

                case 6 | 7 | 8 | 9:  # a +/-/*/'/' b
                    name1 = str(input("Enter 1st variable name: "))
                    name2 = str(input("Enter 2nd variable name: "))
                    res_name = str(input("Enter variable name in which to write the result: "))

                    exist = db.check_variable_exist(self.login, name1)
                    if exist is False:
                        print(f"{Fore.RED}No variable with name {name1}{Style.RESET_ALL}")
                        continue
                    exist = db.check_variable_exist(self.login, name2)
                    if exist is False:
                        print(f"{Fore.RED}No variable with name {name2}{Style.RESET_ALL}")
                        continue
                    exist = db.check_variable_exist(self.login, res_name)
                    if exist is False:
                        print(f"{Fore.RED}No variable with name {res_name}{Style.RESET_ALL}")
                        continue

                    if choice == 6:
                        enc_result, _, _ = db.calc_variables(self.login, name1, name2, op='+')
                        db.edit_value(self.login, res_name, pickle.dumps(enc_result))
                        result = self.private_key.decrypt(enc_result)
                        print(f"{Fore.GREEN}{name1} + {name2} = {result}{Style.RESET_ALL}")

                    if choice == 7:
                        enc_result, _, _ = db.calc_variables(self.login, name1, name2, op='-')
                        db.edit_value(self.login, res_name, pickle.dumps(enc_result))
                        result = self.private_key.decrypt(enc_result)
                        print(f"{Fore.GREEN}{name1} - {name2} = {result}{Style.RESET_ALL}")

                    if choice == 8:
                        enc_result, _, _ = db.calc_variables(self.login, name1, name2, op='*')
                        db.edit_value(self.login, res_name, pickle.dumps(enc_result))
                        result = self.private_key.decrypt(enc_result)
                        print(f"{Fore.GREEN}{name1} * {name2} = {result}{Style.RESET_ALL}")

                    if choice == 9:
                        try:
                            enc_q, enc_r, enc_value2 = db.calc_variables(self.login, name1, name2, op='/')
                            if enc_r is None and enc_value2 is None:
                                result = self.private_key.decrypt(enc_q)
                            else:
                                dec_q = self.private_key.decrypt(enc_q)
                                dec_r = self.private_key.decrypt(enc_r)
                                dec_value2 = self.private_key.decrypt(enc_value2)
                                result = dec_q + dec_r / dec_value2

                            print(f"{Fore.GREEN}{name1} / {name2} = {result}{Style.RESET_ALL}")

                        except ZeroDivisionError:
                            print(f"{Fore.RED}Division by zero{Style.RESET_ALL}")

                case 10:  # Get private key (root)
                    print(self.private_key.get_root())

                case 11:  # Get public key (polynomial)
                    print(self.public_key.get_polynomial())

                case 12:  # Update private and public keys
                    decision = input(f"{Fore.RED}Updating the keys will lead to erase your remote memory."
                                     f" Do you want to continue? [y/n] :{Style.RESET_ALL}")
                    if decision == 'n' or decision == 'no':
                        continue

                    while True:
                        try:
                            base = int(input("Enter number system: "))
                            degree = int(input("Enter degree of the key polynomial: "))
                            break
                        except ValueError:
                            print(f"{Fore.RED}That was no valid number{Style.RESET_ALL}")

                    self.private_key, self.public_key \
                        = keygen.generate_abramov_keypair(base, degree)

                    db.update_user_key(self.login, pickle.dumps(self.public_key))

                    with open('keys/private_key.fhe', 'wb') as file_private_key, \
                            open('keys/public_key.fhe', 'wb') as file_public_key:
                        file_private_key.write(pickle.dumps(self.private_key))
                        file_public_key.write(pickle.dumps(self.public_key))

                    print(f"{Fore.GREEN}Private and public keys were updated "
                          f"and saved to 'keys' directory{Style.RESET_ALL}")

                case _:
                    interface_utils.print_error(f"{Fore.RED}Undefined option{Style.RESET_ALL}")

