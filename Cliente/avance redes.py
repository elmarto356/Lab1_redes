import threading
import socket
import datetime
import json
import re

nick_format = re.compile(r'^NICK\s+\w+$')
msg_format = re.compile(r'^MSG\s+[\w\s]+$')
disconnect_format = re.compile(r'^DISCONNECT$')

# Recepcion
def recibir_mensaje(socket_cliente):
    while True:
        mensaje = socket_cliente.recv(1024).decode('utf-8')
        if mensaje:
            print(f"[{datetime.datetime.now()}]: {mensaje}")
        else:
            print("Conexión cerrada por el servidor.")
            break

# Escritura (debe tener un NICK)
def enviar_mensaje(socket_cliente):
    while True:
        mensaje = input("Bienvenido al chat! Escribe tu mensaje (ej: MSG tu_mensaje) o DISCONNECT para salir:\n")
        if msg_format.match(mensaje):
            socket_cliente.sendall(mensaje.encode('utf-8'))
        elif disconnect_format.match(mensaje):
            socket_cliente.sendall(mensaje.encode('utf-8'))
            print("Desconectando del servidor...")
            break
        else:
            print("Por favor, ingrese un comando válido (ej: MSG tu_mensaje o DISCONNECT)")

#hilo para recibir mensajes
def iniciar_hilo(socket_cliente):
    hilo_recepcion = threading.Thread(target=recibir_mensaje, args=(socket_cliente,), daemon=True)
    hilo_recepcion.start()        

# conexion de socket
ip_destino = "127.0.0.1" # Cambiar esto por ip de ngrok
puerto_destino = 8080
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_cliente.connect((ip_destino, puerto_destino))

#conectarse al servidor
n = input("Bienvenido! Registrese para usar el chat\n")
if nick_format.match(n):
    socket_cliente.sendall(n.encode('utf-8'))
    iniciar_hilo(socket_cliente)
    recibir_mensaje(socket_cliente)
    enviar_mensaje(socket_cliente)
else:
    print("Por favor, ingrese un comando válido para registrarse (ej: NICK tu_nombre)")

