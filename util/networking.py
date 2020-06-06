import sys
import socket
import time
from sys import argv
from os.path import join, dirname

sys.path.append(join(dirname(__file__), '..'))

# Constants
HOST = 'localhost'
BUFFER_SIZE = 128


def get_device_ip():
    """
    Gets the IP address of the current device.
    :return: A string IP address.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip


def open_socket(port, on_data, on_quit = None):
    """
    Opens a server socket at the given port on localhost.
    :param port: The port to open the server socket.
    :param on_data: The handler for when data is received. Must return the response to send back.
    :param on_quit: The handler for when there is no data received.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            while True:
                data_enc = conn.recv(BUFFER_SIZE)
                if not data_enc:
                    if on_quit:
                        on_quit()
                    break
                # Decode the data
                data_dec = data_enc.decode('utf-8')
                conn.sendall(on_data(data_dec).encode())


def send_to_socket(port, value, callback = None):
    """
    Sends a string to the socket at the given port.
    :param port: The port of the server socket.
    :param value: The value to send to the server.
    :param callback: The function called after data is received.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, port))
        s.sendall(value.encode())
        data_enc = s.recv(BUFFER_SIZE)
        data_dec = data_enc.decode('utf-8')
        if callback:
            callback(data_dec)


# Tests
if __name__ == "__main__":
    port = 8081
    if len(argv) == 1:
        print("Opened socket on port %s" % port)
        def res(x):
            print(x)
            return 'Done'
        open_socket(port, res)
    else:
        message = argv[1]
        send_to_socket(port, message, lambda s: print("Sent and received: %s" % s))

