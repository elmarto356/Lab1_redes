import threading
import socket
import datetime
import re

from Cliente_HTTP import solicitar_usuarios, solicitar_historial

nick_format = re.compile(r'^NICK\s+\w+$')
msg_format = re.compile(r'^MSG\s+[\w\s]+$')
disconnect_format = re.compile(r'^DISCONNECT$')

# Recepcion
def recibir_mensaje(socket_cliente):
    while True:
        try:
            mensaje = socket_cliente.recv(1024).decode('utf-8')
            if mensaje:
                print(f"\n[{datetime.datetime.now()}]: {mensaje}")
            else:
                print("\nConexión cerrada por el servidor.")
                break
        except OSError or ConnectionAbortedError:
            break

# Escritura
def enviar_mensaje(socket_cliente):
    print("Bienvenido al chat! Escribe tu mensaje (ej: MSG tu_mensaje) o DISCONNECT para salir:\n")
    while True:
        mensaje = input()
        if msg_format.match(mensaje):
            socket_cliente.sendall(mensaje.encode('utf-8'))
        elif mensaje == "/users":
            solicitar_usuarios()
        elif mensaje == "/history":
            solicitar_historial()
        elif disconnect_format.match(mensaje):
            socket_cliente.sendall(mensaje.encode('utf-8'))
            print("Desconectando del servidor...")
            socket_cliente.close()
            break
        else:
            print("Por favor, ingrese un comando válido (ej: MSG tu_mensaje o DISCONNECT)")

#hilo para recibir mensajes
def iniciar_hilo(socket_cliente):
    hilo_recepcion = threading.Thread(target=recibir_mensaje, args=(socket_cliente,), daemon=True)
    hilo_recepcion.start()        

# conexion de socket
ip_destino = "0.tcp.sa.ngrok.io" # Cambiar esto por ip de ngrok
puerto_destino = 11167
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_cliente.connect((ip_destino, puerto_destino))

#conectarse al servidor
print("Bienvenido! Registrese para usar el chat\n")
while True:
    n = input()
    if nick_format.match(n):
        socket_cliente.sendall(n.encode('utf-8'))
        respuesta = socket_cliente.recv(1024).decode('utf-8')
        if respuesta == "NICK Exitoso":
            print("Registro exitoso! Ahora puedes enviar mensajes al chat.\n")
            iniciar_hilo(socket_cliente)
            enviar_mensaje(socket_cliente)
            break
        else:
            print("El nombre de usuario ya está en uso. Por favor, elija otro nombre\n")
    else:
        print("Por favor, ingrese un comando válido para registrarse (NICK tu_nombre)\n")