import socket
from threading import Thread
from time import sleep
import datetime


class Log:
    def __init__(self, name: str):
        self.name = name
        try:
            self.file = open(name, "a")
        except FileNotFoundError:
            self.file = open(name, "w")
        self.save_data("Log started at " + str(datetime.datetime.now()))
        self.file.close()

    def save_data(self, data: str):
        self.file = open(self.name, "a")
        self.file.write("{}\n".format(data))
        self.file.close()

    @staticmethod
    def read_and_return_list(name: str):
        try:
            file = open(name, "r")
        except FileNotFoundError:
            return []
        data = file.read()
        return data.split("\n")

    def kill_log(self):
        self.file = open(self.name, "a")
        self.save_data("Log stopped at {}\n".format(datetime.datetime.now()))
        self.file.close()


class P2P:
    def __init__(self, port: int, max_clients: int = 1):
        self.running = True
        self.port = port
        self.max_clients = max_clients
        self.clients_ip = ["" for i in range(self.max_clients)]
        self.incoming_requests = {}
        self.clients_logs = [Log for i in range(self.max_clients)]
        self.client_sockets = [socket.socket()
                               for i in range(self.max_clients)]
        for i in self.client_sockets:
            i.settimeout(0.2)
        #self.keys = [rsa.key.PublicKey for i in range(self.max_clients)]
        #self.my_keys = [rsa.key.PrivateKey for i in range(self.max_clients)]
        self.socket_busy = [False for i in range(self.max_clients)]
        self.blacklist = ["127.0.0.1"] + \
            Log.read_and_return_list("blacklist.txt")
        self.server_socket = socket.socket()
        self.server_socket.settimeout(0.2)
        self.server_socket.bind(('localhost', port))
        self.server_socket.listen(self.max_clients)
        self.log = Log("server.log")
        self.log.save_data("Server initialized")

    # Create session with specific user
    def create_session(self, address: str):
        self.log.save_data(f"Creating session with {address}")
        ind = self.get_free_socket()
        if address in self.blacklist:
            self.log.save_data(f"{address} in blacklist")
            return
        if ind is None:
            self.log.save_data(f"All sockets are buse, can't connect \
            to {address}")
            return
        try:
            self.add_user(address)
            thread = Thread(target=self.connect, args=(address, 1))
            thread.start()
            thread.join(0)
            connection, address = self.server_socket.accept()
            connection.settimeout(0.2)
        except OSError:
            self.log.save_data(f"Failed to create session with {address}")
            self.del_user(address)
        #my_key = rsa.newkeys(512)
        #self.was_send(address, my_key[0].save_pkcs1())
        #key = connection.recv(162).decode()
        #self.clients_logs[ind].save_data(f"from {address}: {key}")
        #key = rsa.PublicKey.load_pkcs1(key)
        #self.add_keys(address, key, my_key[1])
        while self.running and self.socket_busy[ind]:
            try:
                data = connection.recv(2048)
            except socket.timeout:
                continue
            except OSError:
                self.close_connection(address)
                return
            if data:
                # data = rsa.decrypt(data, self.my_keys[ind])
                self.add_request(address, data)

        try:
            self.close_connection(address)
        except TypeError or KeyError:
            pass

    def connect(self, address: str, *args):
        ind = self.get_ind_by_address(address)
        try:
            self.client_sockets[ind].connect((address, self.port))
            self.socket_busy[ind] = True
            return True
        except OSError:
            return False

    def reload_socket(self, ind: int):
        self.client_sockets[ind].close()
        self.client_sockets[ind] = socket.socket()
        self.socket_busy[ind] = False

    def close_connection(self, address: str):
        ind = self.get_ind_by_address(address)
        #self.del_key(address)
        self.reload_socket(ind)
        self.del_user(address)

    def kill_server(self):
        self.running = False
        sleep(1)
        self.server_socket.close()
        self.log.kill_log()
        for i in self.client_sockets:
            i.close()
        for i in self.clients_logs:
            try:
                i.kill_log()
            except TypeError:
                pass

    def send(self, address: str, message: str):
        ind = self.get_ind_by_address(address)
        try:
            self.clients_logs[ind].save_data(f"to {address}: {message}")
            # self.client_sockets[ind].send(rsa.encrypt(message.encode(),
            #                                           self.keys[ind]))
            self.log.save_data(f"Send message to {address}")
        except OSError:
            self.log.save_data(f"Can't send message to {address}")

    def raw_send(self, address: str, message: bytes):
        ind = self.get_ind_by_address(address)
        try:
            self.client_sockets[ind].send(message)
            self.clients_logs[ind].save_data(f"to {address}: {message}")
            self.log.save_data(f"Raw send message to {address}")
        except OSError:
            self.log.save_data(f"Raw send to {address} failed")

    def add_user(self, address):
        ind = self.get_free_socket()
        self.clients_logs[ind] = Log(f"{address}.log")
        self.clients_ip[ind] = address
        self.incoming_requests[address] = []
        self.log.save_data(f"Added user {address}")

    # def add_keys(self, address: str, key: rsa.key.PublicKey,
    #              my_key: rsa.key.PrivateKey):
    #     ind = self.get_ind_by_address(address)
    #     try:
    #         self.keys[ind] = key
    #         self.my_keys[ind] = my_key
    #     except TypeError:
    #         return

    def add_request(self, address: str, message: bytes):
        self.incoming_requests[address].append(message.decode())
        self.client_logs[self.__get_ind_by_address(address)] \
            .save_data(f"from {address}: {str(message)}")
        self.log.save_data(f"Get incoming message from {address}")

    def get_free_socket(self):
        for i in range(len(self.socket_busy)):
            if not self.socket_busy[i]:
                return i
        return None

    def get_ind_by_address(self, address: str):
        for i in range(len(self.clients_ip)):
            if self.clients_ip[i] == address:
                return i
            else:
                return None

    def get_request(self, address: str):
        data = self.incoming_requests[address][0]
        self.incoming_requests[address] = [self.incoming_requests[address][i]
                                           for i in range(1, len(
                                             self.incoming_requests[address]))]
        return data

    def check_request(self, address: str):
        return bool(self.incoming_requests.get(address))

    def check_address(self, address: str):
        return True if address in self.clients_ip else False

    def del_user(self, address: str):
        ind = self.get_ind_by_address(address)
        self.clients_logs[ind].kill_log()
        self.clients_logs[ind] = Log
        self.clients_ip[ind] = ""
        self.incoming_requests.pop(address)
        self.log.save_data(f"Deleted user {address}")

    # def del_key(self, address: str):
    #     ind = self.get_ind_by_address(address)
    #     self.keys[ind] = rsa.key.PublicKey
    #     self.my_keys[ind] = rsa.key.PrivateKey

    def __len__(self):
        num = 0
        for i in self.clients_ip:
            if i != "":
                num += 1
        return num

    def __bool__(self):
        for i in self.clients_ip:
            if i != "":
                return True
        return False
