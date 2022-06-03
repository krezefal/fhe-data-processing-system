from interface import Interface

_interface = Interface()


def begin():
    while True:

        print("'0' -> Exit")
        print("'1' -> Sign in")
        print("'2' -> Sign up")

        choice = int(input("Enter task number: "))

        match choice:
            case 0:
                return
            case 1:
                auth = _interface.sign_in()
                if auth:
                    _interface.operate()
                else:
                    print("Invalid login or password")
            case 2:
                _interface.sign_up()
            case _:
                print("Invalid action")


if __name__ == "__main__":
    begin()
