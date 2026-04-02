import socket
import json

#json
request_users = (
    "GET /users HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "\r\n"
)

request_history = (
    "GET /history HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "\r\n"
)
#Todo en unas funciones para llamarlas desde el otro cliente

#Usuarios conectados
def solicitar_usuarios():
    ip_destino = "127.0.0.1" # Cambiar esto por ip de ngrok
    puerto_destino = 8081
    socket_http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_http.connect((ip_destino, puerto_destino))
    socket_http.sendall(request_users.encode('utf-8'))
    
    
    response = socket_http.recv(4096).decode('utf-8')
    partes = response.split("\r\n\r\n", 1)
    if len(partes) == 2:
        headers, body = partes
        try:
            data = json.loads(body)
            print("Usuarios conectados:", data.get("users", []))
        except json.JSONDecodeError:
            print("Error al decodificar la respuesta JSON.")
    
    socket_http.close()


#Historial de mensajes
def solicitar_historial():
    ip_destino = "127.0.0.1" # Cambiar esto por ip de ngrok
    puerto_destino = 8000
    socket_http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_http.connect((ip_destino, puerto_destino))
    socket_http.sendall(request_history.encode('utf-8'))

    response = socket_http.recv(4096).decode('utf-8')
    partes = response.split("\r\n\r\n", 1)
    if len(partes) == 2:
        headers, body = partes
        try:
            data = json.loads(body)
            print("Historial de mensajes:", data.get("history", []))
        except json.JSONDecodeError:
            print("Error al decodificar la respuesta JSON.")
    
    socket_http.close()