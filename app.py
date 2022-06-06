from colorama import Fore, Style

from interface import Interface


def begin():
    _interface = Interface()

    while True:

        print("'0' -> Exit")
        print("'1' -> Sign in")
        print("'2' -> Sign up")

        while True:
            try:
                choice = int(input("Enter task number: "))
                break
            except ValueError:
                print(f"{Fore.RED}Number required{Style.RESET_ALL}")

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
                print(f"{Fore.RED}Invalid action{Style.RESET_ALL}")


if __name__ == "__main__":
    begin()
