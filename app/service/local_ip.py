import socket


def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)
