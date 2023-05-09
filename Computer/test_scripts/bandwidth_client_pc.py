import time
from socket import *

count = 1000
BUFSIZE = 1024000
# ip = input("ip: ")
# port = input("Port: ")
ip = '169.254.148.62'
port = 8123


def client():
    testdata = 'x' * (BUFSIZE-1) + '\n'
    s = socket(AF_INET, SOCK_STREAM)
    t2 = time.time()
    s.connect((ip, int(port)))
    t3 = time.time()
    i = 0
    while i < count:
        i = i+1
        s.send(bytearray(testdata, "utf-8"))
    t4 = time.time()
    s.shutdown(1)
    t5 = time.time()
    data = s.recv(BUFSIZE)
    t6 = time.time()
    bandwidth_Mbyte = (BUFSIZE * count) / (t4 - t3) / 1000 / 1000
    print(data.decode())
    print('ping:', (t3-t2)+(t6-t5)/2)
    print('Time:', t4-t3, 'sec.')
    print('Bandwidth:', round(bandwidth_Mbyte, 3), 'Mbyte/sec.')
    print('Bandwidth:', round(bandwidth_Mbyte*8, 3), 'Mbit/sec.')


if __name__ == '__main__':
    client()
