import interface_utils
from interface import Interface


def begin():
    _interface = Interface()

    while True:

        print("'0' -> Exit")
        print("'1' -> Sign in")
        print("'2' -> Sign up")

        choice = interface_utils.enter_option("Enter task number: ")

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
                interface_utils.print_error("Invalid action")


if __name__ == "__main__":
    begin()
