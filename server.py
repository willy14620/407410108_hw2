# Import module
import threading
import socket


class ServerSocket(threading.Thread):
    def __init__(self, conn_sc, conn_sockname, server):
        super().__init__()
        self.conn_sc = conn_sc
        self.conn_sockname = conn_sockname
        self.server = server
        self.exitStatus = False

    def run(self):
        while True:
            # Receive message from client
            try:
                clientMessage = self.conn_sc.recv(1024).decode()
                if self.exitStatus:
                    break
            except BrokenPipeError:
                break
            else:
                if 'quit' not in clientMessage:
                    print(f'{self.conn_sockname}: {clientMessage}')

                else:
                    print(f'{self.conn_sockname} has closed the connection.')
                    self.conn_sc.close()
                    self.server.remove_connection(self)
                    return

    def close_connection(self):
        self.exitStatus = True


class Command(threading.Thread):
    def __init__(self, connections, conn_sc_list):
        super().__init__()
        self.command_dict = {'HELP': 'Print all commands.',
                             'PRINT': 'Print all connecting clients.', 'KICK': 'Disconnect someone client.'}
        self.connections = connections
        self.conn_sc_list = conn_sc_list

    def run(self):
        while True:
            command = input()
            if 'HELP' in command:
                for c, d in self.command_dict.items():
                    print(f'{c}: {d}')
                print()

            elif 'PRINT' in command:
                if len(self.conn_sc_list) == 0:
                    print('No connection.')
                    continue
                for i, c in enumerate(self.conn_sc_list, 1):
                    print(f'{i}. {c.getpeername()}')
                print()

            elif 'KICK' in command:
                if len(self.conn_sc_list):
                    try:
                        temp = int(command.split(' ')[1])
                        self.connections[temp-1].close_connection()
                        self.conn_sc_list[temp-1].shutdown(socket.SHUT_RD)
                        # self.conn_sc_list[temp-1].close()
                        self.conn_sc_list.pop(temp-1)
                        self.connections.pop(temp-1)
                    except:
                        print('ERROR')


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.conn_sc_list = []
        self.host = host
        self.port = port

    def run(self):
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sc.bind((self.host, self.port))
        sc.listen(1)
        print('Listening at', sc.getsockname())
        print('\n', '*'*52)
        print(' *You can input command "HELP" to show all commands!*')
        print('', '*'*52, '\n')
        command_handle = Command(self.connections, self.conn_sc_list)
        command_handle.start()

        while True:
            # Accept connection
            conn_sc, conn_sockname = sc.accept()
            print(
                f'Accepted a new connection from {conn_sc.getpeername()} to {conn_sc.getsockname()}')

            # Create new thread
            server_socket = ServerSocket(conn_sc, conn_sockname, self)

            # Start new thread
            server_socket.start()

            # Append to connecting list
            self.connections.append(server_socket)
            self.conn_sc_list.append(conn_sc)
            print('Ready to receive messages from', conn_sc.getpeername())

    def remove_connection(self, conn):
        # Remove connection from connecting list
        self.connections.remove(conn)


HOST = '127.0.0.1'
PORT = 8000

server = Server(HOST, PORT)
server.start()
