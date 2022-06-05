from getpass import getpass
from hashlib import md5
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

    def sign_up(self):
        try:
            while True:
                login = input("Login: ")
                response = db.get_user_info(login)
                if response is not None:
                    print("User with this login already exists. Try another")
                else:
                    break

            while True:
                password = getpass("Password: ")
                confirm = getpass("Confirm Password: ")
                if password != confirm:
                    print("Passwords are not the same")
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
                    print("That was no valid number")

            self.private_key, self.public_key \
                = keygen.generate_abramov_keypair(base, degree)

            # db.create_user({"login": login,
            #                 "password": md5(password.encode('utf-8')).hexdigest(),
            #                 "public_key": pickle.dumps(self.public_key)})

            db.create_user((login, md5(password.encode('utf-8')).hexdigest(), pickle.dumps(self.public_key)))

            with open('keys/private_key.fhe', 'wb') as file_private_key, \
                    open('keys/public_key.fhe', 'wb') as file_public_key:
                file_private_key.write(pickle.dumps(self.private_key))
                file_public_key.write(pickle.dumps(self.public_key))

            print("You have successfully registered")
            print("Private and public keys were saved to 'keys' directory")

        finally:
            db.close_connection()

    def sign_in(self) -> bool:
        try:
            login = input("Login: ")
            response = db.get_user_info(login)
            if response is None:
                print("User not found")
                return False

            correct_password = response[0][PASSWORD_HASH]
            password = getpass("Password: ")
            if correct_password != md5(password.encode("utf-8")).hexdigest():
                print("Wrong password")
                return False

            self.login = login
            print("You have successfully authorize")

            file_path = str(input("Specify the path to private key file: "))
            with open(file_path, 'rb') as file_private_key:
                self.private_key = pickle.load(file_private_key.read())
            self.public_key = response[0][PUBLIC_KEY]

            return True

        finally:
            db.close_connection()

    def operate(self):
        try:
            while True:

                print("'0' -> Exit")
                print("'1' -> Initialize new variable")
                print("'2' -> Get variable list")
                print("'3' -> Get variable")
                print("'4' -> Edit value")
                print("'5' -> Delete variable")
                print("'6' -> a + b")
                print("'7' -> a + b with vars")
                print("'8' -> a - b")
                print("'9' -> a - b with vars")
                print("'10' -> a * b")
                print("'11' -> a * b with vars")
                print("'12' -> a / b")
                print("'13' -> a / b with vars")

                choice = int(input("Enter operation number: "))

                match choice:

                    case 0:
                        return

                    case 1:  # Initialize new variable
                        enc_name, name = utils.enter_name(self.public_key)
                        exist = db.check_variable_exist(self.login, pickle.dumps(enc_name))
                        if exist is True:
                            print(f"Error: value '{name}' already initialized")
                            break

                        enc_value, value = utils.enter_value(self.public_key)
                        db.init_new_variable((pickle.dumps(enc_name), self.login, pickle.dumps(enc_value)))
                        print(f"Initialized: {name} = {value}")

                    case 2:  # Get variable list
                        dump = db.get_memory(self.login)
                        if len(dump) != 0:
                            for idx, variable in enumerate(dump):
                                name = self.private_key.decrypt(pickle.loads(variable[NAME]))
                                value = self.private_key.decrypt(pickle.loads(variable[VALUE]))

                                print(f"#{idx + 1}: {name} = {value}")
                        else:
                            print("No initialized variables")

                    case 3:  # Get variable
                        enc_name, name = utils.enter_name(self.public_key)
                        variable = db.get_variable(self.login, pickle.dumps(enc_name))
                        if variable is not None:
                            value = self.private_key.decrypt(pickle.loads(variable[VALUE]))
                            print(f"{name} = {value}")
                        else:
                            print(f"No variable with name {name}")

                    case 4:  # Edit value
                        enc_name, name = utils.enter_name(self.public_key)
                        exist = db.check_variable_exist(self.login, pickle.dumps(enc_name))
                        if exist is False:
                            print(f"No variable with name {name}")
                            break

                        enc_value, value = utils.enter_value(self.public_key)
                        db.edit_value(self.login, pickle.dumps(enc_name), pickle.dumps(enc_value))
                        print(f"Edited: {name} = {value}")

                    case 5:  # Delete variable
                        enc_name, name = utils.enter_name(self.public_key)
                        exist = db.check_variable_exist(self.login, pickle.dumps(enc_name))
                        if exist is False:
                            print(f"No variable with name {name}")
                            break

                        db.delete_variable(self.login, pickle.dumps(enc_name))
                        print(f"Variable '{name}' was deleted")

                    case 6 | 7 | 8 | 9:  # a + b
                        enc_name1, name1 = utils.enter_name(self.public_key)
                        enc_name2, name2 = utils.enter_name(self.public_key)

                        exist = db.check_variable_exist(self.login, pickle.dumps(enc_name1))
                        if exist is False:
                            print(f"No variable with name {enc_name1}")
                            break
                        exist = db.check_variable_exist(self.login, pickle.dumps(enc_name2))
                        if exist is False:
                            print(f"No variable with name {enc_name2}")
                            break

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

                        print(f"{name1} + {name2} = {result}")

                    case _:
                        print("Undefined option")
        finally:
            db.close_connection()
