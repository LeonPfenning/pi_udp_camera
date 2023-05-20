import socket
import struct


class Server:
    def __init__(self, ip: str = "0.0.0.0", port: int = 8123):
        self.HOST = ip  # Standard loopback interface address (localhost)
        self.PORT = port  # Port to listen on (non-privileged ports are > 1023)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # fix for address already in use error: [Errno 98] Address already in use
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()
        print('Listening...')
        self.conn, self.addr = self.server_socket.accept()
        print(f"Connected by {self.addr}")

    def send_data_safe(self, byte_stream: bytes):
        # send length of byte_stream data encoded in 4byte (so client knows what to listen for)
        # kind of overkill since we use uncompressed images that allways have the same size
        # with this implementation we could send compressed images too
        self.conn.send(struct.pack('<L', len(byte_stream)))
        self.conn.send(byte_stream)

    def send_data(self, byte_stream: bytes):
        self.conn.send(byte_stream)

    def receive_data(self, byte_length: int = 8):
        data = self.conn.recv(byte_length)
        if not data:
            print("received package with zero length")
            return None
        data = data.decode()
        return data

    # def receive_all_data(self, byte_length=4):
    #     # Helper function to recv n bytes or return None if EOF is hit
    #     data = bytearray()
    #     while len(data) < byte_length:
    #         packet = self.conn.recv(byte_length - len(data))
    #         if not packet:
    #             return None
    #         data.extend(packet)
    #     return data.decode()

    def close(self):
        self.server_socket.close()