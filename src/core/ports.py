import socket

ports = [8080, 3000, 5000]

def check_ports():
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            pass
    raise Exception("No available ports to start the server.")