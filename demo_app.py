import sys

from clientside.client_utils import parse_server_info, enter_option, print_error
from clientside.client import ClientConn


def main(argv):
    ip, port = parse_server_info(argv)
    _client = ClientConn(ip, port)

    while True:

        print("'0' -> Exit")
        print("'1' -> Sign in")
        print("'2' -> Sign up")

        sign_choice = enter_option("Enter task number: ")

        match sign_choice:
            case 0:
                del _client
                return
            case 1:
                _client.sign_in()
                while True:

                    print()
                    print("'0' -> Sign out                   '6' -> a + b")
                    print("'1' -> Initialize new variable    '7' -> a - b")
                    print("'2' -> Get variable list          '8' -> a * b")
                    print("'3' -> Get variable               '9' -> a / b")
                    print("'4' -> Edit value                 '10' -> Get private key (root)")
                    print("'5' -> Delete variable            '11' -> Get public key (polynomial)")
                    print()
                    print("             '12' -> Update private and public keys")
                    print()

                    opt_choice = enter_option("Enter operation number: ")
                    match opt_choice:
                        case 0:
                            _client.sign_out()
                            break
                        case 1:
                            _client.init_new_variable()
                        case 2:
                            _client.get_memory()
                        case 3:
                            _client.get_variable()
                        case 4:
                            _client.edit_value()
                        case 5:
                            _client.delete_variable()
                        case 6:
                            _client.calc_variables("+")
                        case 7:
                            _client.calc_variables("-")
                        case 8:
                            _client.calc_variables("*")
                        case 9:
                            _client.calc_variables("/")
                        case 10:
                            _client.get_key("private")
                        case 11:
                            _client.get_key("public")
                        case 12:
                            _client.update_keys()
                        case _:
                            print_error("Undefined option")
            case 2:
                _client.sign_up()
            case _:
                print_error("Invalid action")


if __name__ == "__main__":
    main(sys.argv[1:])
