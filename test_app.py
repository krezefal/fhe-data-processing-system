import sys

from interface_utils import parse_db_creds, enter_option, print_error
from interface import Interface


def main(argv):
    db_creds = parse_db_creds(argv)
    _interface = Interface(*db_creds)

    while True:

        print("'0' -> Exit")
        print("'1' -> Sign in")
        print("'2' -> Sign up")

        choice = enter_option("Enter task number: ")

        match choice:
            case 0:
                del _interface
                return
            case 1:
                _interface.sign_in()
                _interface.operate()
            case 2:
                _interface.sign_up()
            case _:
                print_error("Invalid action")


if __name__ == "__main__":
    main(sys.argv[1:])
