import sys
import socket
from os.path import join, dirname

sys.path.append(join(dirname(__file__), '..'))

def get_device_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip