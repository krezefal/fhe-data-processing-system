import getopt
import pickle
import sys
from getpass import getpass
from hashlib import md5
from typing import Tuple

import requests
import yaml
from colorama import Fore, Style

from homomorphic_polynomial_system.enc_num import EncryptedNumber
from homomorphic_polynomial_system.keygen import AbramovPublicKey

NAME = 0
RESULT = 0
WHOLE_PART = 0
VALUE = 1
REMAINS = 1
PASSWORD_HASH = 2
DIVIDER = 2
PUBLIC_KEY = 3


def parse_server_info(argv) -> Tuple[str, str]:
    with open('./clientside/server_info.yaml', 'r') as file:
        config = yaml.safe_load(file)

    ip = None
    port = None

    try:
        opts, args = getopt.getopt(argv, "hip:p:", ["ip=", "port="])
    except getopt.GetoptError:
        print("demo_app.py -ip <ip> -p <port>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("demo_app.py -ip <ip> -p <port>")
            sys.exit()
        elif opt in ("-ip", "--ip"):
            ip = arg
        elif opt in ("-p", "--port"):
            port = arg

    if ip is None:
        ip = config['conn_info']['ip']
    if port is None:
        port = config['conn_info']['port']

    return ip, port


def enter_option(text: str) -> int:
    while True:
        try:
            choice = int(input(text))
            return choice
        except ValueError:
            print(f"{Fore.RED}Number required{Style.RESET_ALL}")


def signup_login(address) -> str:
    while True:
        login = input("Enter login: ")
        response = requests.get(f"{address}/get_user_info?login={login}",
                                verify='./clientside/openssl_cert/cert.pem')
        if len(response.json()) != 0:
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


def response_login(address) -> Tuple[str, any]:
    while True:
        login = input("Login: ")
        response = requests.get(f"{address}/get_user_info?login={login}",
                                verify='./clientside/openssl_cert/cert.pem')
        if len(response.json()) == 0:
            print(f"{Fore.RED}User not found{Style.RESET_ALL}")
        else:
            return login, response.json()


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
                key_path = f"./clientside/keys/{key_type}_key.fhe"

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
