import socket
import struct


class Client:
    def __init__(self, ip: str, port: int):
        self.IP = ip
        self.Port = port

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.IP, self.Port))
        self.rdFile = self.client_socket.makefile('rb')
        print("communication with rpi initialized...")

    # sends strings
    def send_msg(self, msg: str):
        self.client_socket.send(msg.encode())

    def get_data_safe(self) -> bytes:
        data = self.client_socket.recv(struct.calcsize('<L'))
        data_byte_count = struct.unpack('<L', data)[0]
        if not data_byte_count:
            raise Exception("data received with zero length")
        # get data
        data_stream = self.rdFile.read(data_byte_count)     # robust enough "receive all" implementation?
        return data_stream

    def get_data(self, data_byte_count: int) -> bytes:
        data_stream = self.rdFile.read(data_byte_count)     # robust enough "receive all" implementation?
        return data_stream

    def close(self):
        self.rdFile.close()
        self.client_socket.close()
