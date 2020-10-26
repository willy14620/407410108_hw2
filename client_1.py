import socket
import threading
import sys
import os


class Send(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        while True:
            print('{}: '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            if message:
                self.sock.sendall('{}: {}'.format(
                    self.name, message).encode('utf-8'))

        # print('\nQuitting...')
        # self.sock.close()
        # os._exit(0)


class Receive(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
            except ConnectionResetError:
                sys.exit(1)

            if message:
                print('{}: {}: '.format(self.name, message), end='')

            else:
                print('\nOh no, we have lost connection to the server!')
                print('Quitting...')
                self.sock.close()
                os._exit(0)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):

        print('Trying to connect to {}:{}...'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))
        print('Successfully connected to {}:{}'.format(self.host, self.port))

        self.name = input('Your name: ')

        print('Hi, {}! Getting ready to send and receive messages.'.format(self.name))

        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name)

        send.start()
        receive.start()

        self.sock.sendall('Server: {} has joined the chat. Say hi!'.format(
            self.name).encode('utf-8'))

        # print("OK! Leave chatroom by typing QUIT")
        # print('{}: '.format(self.name), end='')

        return receive


HOST = '127.0.0.1'
PORT = 8000

client = Client(HOST, PORT)
receive = client.start()
