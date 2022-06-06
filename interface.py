from getpass import getpass
from hashlib import md5
from colorama import Fore, Style
import pickle
import yaml

from abramov_system import keygen
from db_api import DBConn
from consts import *
import utils

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
        while True:
            login = input("Login: ")
            response = db.get_user_info(login)
            if response:
                print(f"{Fore.RED}User with this login already exists. Try another{Style.RESET_ALL}")
            else:
                break

        while True:
            password = getpass("Password: ")
            confirm = getpass("Confirm Password: ")
            if password != confirm:
                print(f"{Fore.RED}Passwords are not the same{Style.RESET_ALL}")
            else:
                break

        print("To use remote secure memory you need private and public keys.")
        print("Both will be generated automatically after you enter the parameters:")

        while True:
            try:
                base = int(input("Number system: "))
                degree = int(input("Degree of the key polynomial: "))
                break
            except ValueError:
                print(f"{Fore.RED}That was no valid number{Style.RESET_ALL}")

        self.private_key, self.public_key \
            = keygen.generate_abramov_keypair(base, degree)

        # db.create_user({"login": login,
        #                 "passwd_hash": md5(password.encode('utf-8')).hexdigest(),
        #                 "public_key": pickle.dumps(self.public_key)})

        db.create_user((login, md5(password.encode('utf-8')).hexdigest(), pickle.dumps(self.public_key)))

        with open('keys/private_key.fhe', 'wb') as file_private_key, \
                open('keys/public_key.fhe', 'wb') as file_public_key:
            file_private_key.write(pickle.dumps(self.private_key))
            file_public_key.write(pickle.dumps(self.public_key))

        print(f"{Fore.GREEN}You have successfully registered{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Private and public keys were saved to 'keys' directory{Style.RESET_ALL}")

    def sign_in(self):
        while True:
            login = input("Login: ")
            response = db.get_user_info(login)
            if not response:
                print(f"{Fore.RED}User not found{Style.RESET_ALL}")
            else:
                break

        correct_password = response[0][PASSWORD_HASH]
        while True:
            password = getpass("Password: ")
            if correct_password != md5(password.encode("utf-8")).hexdigest():
                print(f"{Fore.RED}Wrong password{Style.RESET_ALL}")
            else:
                break

        self.login = login
        print(f"{Fore.GREEN}You have successfully authorize{Style.RESET_ALL}")

        while True:
            try:
                file_path = str(input("Specify the path to private key file: "))
                with open(file_path, 'rb') as file_private_key:
                    self.private_key = pickle.loads(file_private_key.read())
                break
            except OSError as error:
                print(f"{Fore.RED}{error}{Style.RESET_ALL}")

        self.public_key = pickle.loads(response[0][PUBLIC_KEY])

        # print(self.private_key.get_root())          debug
        # print(self.public_key.get_polynomial())

        print(f"{Fore.GREEN}Private key has been added{Style.RESET_ALL}")

    def operate(self):
        while True:

            print()
            print("'0' -> Logout                     '7' -> a + b")
            print("'1' -> Initialize new variable    '8' -> a - b")
            print("'2' -> Get variable list          '9' -> a * b")
            print("'3' -> Get variable               '10' -> a / b")
            print("'4' -> Edit value")
            print("'5' -> Delete variable")
            print()

            while True:
                try:
                    choice = int(input("Enter operation number: "))
                    break
                except ValueError:
                    print(f"{Fore.RED}Number required{Style.RESET_ALL}")

            match choice:

                case 0:
                    self.login = None
                    self.private_key = None
                    self.public_key = None
                    return

                case 1:  # Initialize new variable
                    name = utils.enter_name(self.public_key)
                    exist = db.check_variable_exist(self.login, name)
                    if exist:
                        print(f"{Fore.RED}Error: value '{name}' already initialized{Style.RESET_ALL}")
                        continue

                    enc_value, value = utils.enter_value(self.public_key)
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
                    name = utils.enter_name(self.public_key)
                    variable = db.get_variable(self.login, name)
                    if variable:
                        value = self.private_key.decrypt(pickle.loads(variable[0][VALUE]))
                        print(f"{Fore.GREEN}{name} = {value}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}No variable with name {name}{Style.RESET_ALL}")

                case 4:  # Edit value
                    name = utils.enter_name(self.public_key)
                    exist = db.check_variable_exist(self.login, name)
                    if not exist:
                        print(f"{Fore.RED}No variable with name {name}{Style.RESET_ALL}")
                        continue

                    enc_value, value = utils.enter_value(self.public_key)
                    db.edit_value(self.login, name, pickle.dumps(enc_value))
                    print(f"{Fore.GREEN}Edited: {name} = {value}{Style.RESET_ALL}")

                case 5:  # Delete variable
                    name = utils.enter_name(self.public_key)
                    exist = db.check_variable_exist(self.login, name)
                    if not exist:
                        print(f"{Fore.RED}No variable with name {name}{Style.RESET_ALL}")
                        continue

                    db.delete_variable(self.login, name)
                    print(f"{Fore.GREEN}Variable '{name}' was deleted{Style.RESET_ALL}")

                case 6 | 7 | 8 | 9:  # a + b
                    enc_name1, name1 = utils.enter_name(self.public_key)
                    enc_name2, name2 = utils.enter_name(self.public_key)

                    exist = db.check_variable_exist(self.login, name1)
                    if exist is False:
                        print(f"{Fore.RED}No variable with name {enc_name1}{Style.RESET_ALL}")
                        continue
                    exist = db.check_variable_exist(self.login, name2)
                    if exist is False:
                        print(f"{Fore.RED}No variable with name {enc_name2}{Style.RESET_ALL}")
                        continue

                    result = None
                    if choice == 6:
                        enc_result, _, _ = db.calc_variables(self.login, pickle.dumps(enc_name1),
                                                             pickle.dumps(enc_name2), op='+')
                        result = self.private_key.decrypt(enc_result)

                    if choice == 7:
                        enc_result, _, _ = db.calc_variables(self.login, pickle.dumps(enc_name1),
                                                             pickle.dumps(enc_name2), op='-')
                        result = self.private_key.decrypt(enc_result)

                    if choice == 8:
                        enc_result, _, _ = db.calc_variables(self.login, pickle.dumps(enc_name1),
                                                             pickle.dumps(enc_name2), op='*')
                        result = self.private_key.decrypt(enc_result)

                    if choice == 9:
                        enc_q, enc_r, enc_value2 = db.calc_variables(self.login, pickle.dumps(enc_name1),
                                                                     pickle.dumps(enc_name2), op='/')
                        dec_q = self.private_key.decrypt(enc_q)
                        dec_r = self.private_key.decrypt(enc_r)
                        dec_value2 = self.private_key.decrypt(enc_value2)

                        result = dec_q + dec_r / dec_value2

                    print(f"{Fore.GREEN}{name1} + {name2} = {result}{Style.RESET_ALL}")

                case _:
                    print(f"{Fore.RED}Undefined option{Style.RESET_ALL}")
