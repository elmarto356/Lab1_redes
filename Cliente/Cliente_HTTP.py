import socket
import ssl
import json

def solicitar_usuarios():
    host = "agglutinogenic-precociously-alexandra.ngrok-free.dev"
    puerto = 443  

    request = (
        f"GET /users HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"ngrok-skip-browser-warning: true\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_ssl = ssl.create_default_context().wrap_socket(sock, server_hostname=host)
    sock_ssl.connect((host, puerto))
    sock_ssl.sendall(request.encode("utf-8"))

    response = b""
    while True:
        datos = sock_ssl.recv(4096)
        if not datos:
            break
        response += datos
    sock_ssl.close()

    partes = response.decode("utf-8").split("\r\n\r\n", 1)
    if len(partes) == 2:
        try:
            data = json.loads(partes[1])
            print("Usuarios conectados:", data.get("users", []))
        except json.JSONDecodeError:
            print("Error al decodificar JSON.")


def solicitar_historial():
    host = "agglutinogenic-precociously-alexandra.ngrok-free.dev"
    puerto = 443

    request = (
        f"GET /history HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"ngrok-skip-browser-warning: true\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_ssl = ssl.create_default_context().wrap_socket(sock, server_hostname=host)
    sock_ssl.connect((host, puerto))
    sock_ssl.sendall(request.encode("utf-8"))

    response = b""
    while True:
        datos = sock_ssl.recv(4096)
        if not datos:
            break
        response += datos
    sock_ssl.close()

    partes = response.decode("utf-8").split("\r\n\r\n", 1)
    if len(partes) == 2:
        try:
            data = json.loads(partes[1])
            print("Historial:", data.get("history", []))
        except json.JSONDecodeError:
            print("Error al decodificar JSON.")