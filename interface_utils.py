import pickle
from getpass import getpass
from hashlib import md5
from typing import Tuple
from colorama import Fore, Style

from homomorphic_polynomial_system.enc_num import EncryptedNumber
from homomorphic_polynomial_system.keygen import AbramovPublicKey
from db_api import DBConn


def enter_option(text: str) -> int:
    while True:
        try:
            choice = int(input(text))
            return choice
        except ValueError:
            print(f"{Fore.RED}Number required{Style.RESET_ALL}")


def signup_login(db: DBConn) -> str:
    while True:
        login = input("Enter login: ")
        response = db.get_user_info(login)
        if response:
            print(f"{Fore.RED}User with this login already exists. Try another{Style.RESET_ALL}")
        else:
            return login


def signup_password() -> str:
    while True:
        password = getpass("Enter password: ")
        confirm = getpass("Confirm password: ")
        if password != confirm:
            print(f"{Fore.RED}Passwords are not the same{Style.RESET_ALL}")
        else:
            return password


def enter_alg_params() -> Tuple[int, int]:
    while True:
        try:
            base = int(input("Number system: "))
            degree = int(input("Degree of the key polynomial: "))
            return base, degree
        except ValueError:
            print(f"{Fore.RED}That was no valid number{Style.RESET_ALL}")


def response_login(db: DBConn) -> Tuple[str, any]:
    while True:
        login = input("Login: ")
        response = db.get_user_info(login)
        if not response:
            print(f"{Fore.RED}User not found{Style.RESET_ALL}")
        else:
            return login, response


def signin_password(correct_password):
    while True:
        password = getpass("Password: ")
        if correct_password != md5(password.encode("utf-8")).hexdigest():
            print(f"{Fore.RED}Wrong password{Style.RESET_ALL}")
        else:
            return


def enter_key(key_type: str):
    while True:
        try:
            key_path = str(input(f"Specify the path to {key_type} key file or "
                                 f"press {Fore.CYAN}enter{Style.RESET_ALL} to use default location: "))
            if key_path == "":
                key_path = f"./keys/{key_type}_key.fhe"

            with open(key_path, 'rb') as key_file:
                key = pickle.loads(key_file.read())
                return key

        except OSError as error:
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")


def enter_value(public_key: AbramovPublicKey) -> Tuple[EncryptedNumber, int]:
    while True:
        try:
            value = int(input("Enter a value: "))
            enc_value = public_key.encrypt(value)
            return enc_value, value
        except ValueError:
            print(f"{Fore.RED}It is only possible to enter a number{Style.RESET_ALL}")


def print_error(text: str):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")

# def encode(string) -> int:
#     bit_arr = bitarray.bitarray()
#     bit_arr.frombytes(string.encode('utf-8'))
#     int_value = int(bit_arr.to01(), 2)
#     return int_value

# bits_arr = []
# for c in string:
#     bits = bin(ord(c))[2:]
#     bits = '00000000'[len(bits):] + bits
#     bits_arr.extend([int(b) for b in bits])
# return bits_arr


# def decode(bits_arr):
#     chars = []
#     for b in range(len(bits_arr) // 8):
#         byte = bits_arr[b * 8:(b + 1) * 8]
#         chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
#     return ''.join(chars)
