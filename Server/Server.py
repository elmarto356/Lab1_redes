import socket
import threading
import json
import sys
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ========================== CONFIGURACIÓN ==========================

TCP_HOST = "0.0.0.0"
TCP_PORT = 9000
HTTP_HOST = "0.0.0.0"
HTTP_PORT = 8000
UDP_LOG_HOST = "127.0.0.1"
UDP_LOG_PORT = 7000
MAX_HISTORIAL = 50
lock = threading.Lock()
usuarios = {}
historial = []
udp_log_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def mandar_log(tipo_evento, mensaje_evento):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] - {tipo_evento} - {mensaje_evento}"
    try:
        udp_log_socket.sendto(
            log_msg.encode("utf-8"),
            (UDP_LOG_HOST, UDP_LOG_PORT)
        )
    except Exception as e:
        print(f"[WARN] No se pudo enviar log UDP: {e}")

def broadcast(mensaje, excluir_usuario=None):
    with lock:
        destinatarios = {
            nombre: sock
            for nombre, sock in usuarios.items()
            if nombre != excluir_usuario
        }

    for nombre, sock in destinatarios.items():
        try:
            sock.sendall(mensaje.encode("utf-8"))
        except Exception:
            pass

def manejar_cliente(conn, addr):
    ip_cliente = f"{addr[0]}:{addr[1]}"
    nombre_usuario = None

    try:
        while True:
            datos = conn.recv(4096)
            if not datos:
                break

            mensaje_raw = datos.decode("utf-8").strip()
            if not mensaje_raw:
                continue

            partes = mensaje_raw.split(" ", 1)
            comando = partes[0].upper()
            argumento = partes[1].strip() if len(partes) > 1 else ""

            if comando == "NICK":
                if not argumento:
                    conn.sendall("ERROR EMPTY_NICK\n".encode("utf-8"))
                    mandar_log("ERROR", f"ip={ip_cliente} motivo=\"NICK sin nombre\"")
                    continue

                nombre_solicitado = re.sub(r'\s+', '', argumento)
                if not nombre_solicitado:
                    conn.sendall("ERROR EMPTY_NICK\n".encode("utf-8"))
                    mandar_log("ERROR", f"ip={ip_cliente} motivo=\"NICK vacío tras limpiar\"")
                    continue

                with lock:
                    if nombre_solicitado in usuarios:
                        conn.sendall("ERROR NICK_IN_USE\n".encode("utf-8"))
                        mandar_log("ERROR", f"ip={ip_cliente} motivo=\"nombre repetido: {nombre_solicitado}\"")
                        continue
                    usuarios[nombre_solicitado] = conn
                    nombre_usuario = nombre_solicitado

                conn.sendall(f"NICK Exitoso".encode("utf-8"))
                mandar_log("CONNECT", f"usuario={nombre_usuario} ip={ip_cliente}")
                broadcast(f"SERVER {nombre_usuario} se ha unido a la cantina\n", nombre_usuario)

            elif comando == "MSG":
                if nombre_usuario is None:
                    conn.sendall("ERROR No registrado".encode("utf-8"))
                    mandar_log("ERROR", f"ip={ip_cliente} motivo=\"MSG sin NICK previo\"")
                    continue
                if not argumento:
                    conn.sendall("ERROR mensaje vacio".encode("utf-8"))
                    mandar_log("ERROR", f"usuario={nombre_usuario} motivo=\"MSG vacío\"")
                    continue

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with lock:
                    historial.append({"user": nombre_usuario, "message": argumento, "timestamp": timestamp})
                    if len(historial) > MAX_HISTORIAL:
                        del historial[0]

                conn.sendall("OK MSG\n".encode("utf-8"))
                broadcast(f"MSG {nombre_usuario} {argumento}\n", nombre_usuario)
                mandar_log("MSG", f"usuario={nombre_usuario} texto=\"{argumento}\"")

            elif comando == "DISCONNECT":
                if nombre_usuario is None:
                    conn.sendall("ERROR NOT_REGISTERED".encode("utf-8"))
                    mandar_log("ERROR", f"ip={ip_cliente} motivo=\"DISCONNECT sin NICK\"")
                    continue

                conn.sendall("OK DISCONNECT".encode("utf-8"))
                mandar_log("DISCONNECT", f"usuario={nombre_usuario} ip={ip_cliente}")
                broadcast(f"SERVER {nombre_usuario} ha abandonado la cantina\n", nombre_usuario)
                break

            else:
                if nombre_usuario is None:
                    conn.sendall("ERROR NOT_REGISTERED\n".encode("utf-8"))
                else:
                    conn.sendall("ERROR UNKNOWN_CMD\n".encode("utf-8"))
                mandar_log("ERROR", f"usuario={nombre_usuario or 'anon'} ip={ip_cliente} motivo=\"comando desconocido: {comando}\"")

    except Exception as e: 
        mandar_log("ERROR", f"usuario={nombre_usuario or 'anon'} ip={ip_cliente} motivo=\"{e}\"")

    # eliminar usuario y la conexion
    if nombre_usuario:
        with lock:
            if nombre_usuario in usuarios:
                del usuarios[nombre_usuario]
    conn.close()

def iniciar_servidor_tcp():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((TCP_HOST, TCP_PORT))
    server_socket.listen(5)
    server_socket.settimeout(1.0)

    print(f"[TCP] Servidor de chat escuchando en {TCP_HOST}:{TCP_PORT}")
    mandar_log("CONNECT", f"Servidor TCP iniciado en puerto {TCP_PORT}")

    while True:
        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            continue
        hilo_cliente = threading.Thread(
            target=manejar_cliente,
            args=(conn, addr),
            daemon=True
        )
        hilo_cliente.start()

class ManejadorHTTP(BaseHTTPRequestHandler):

    def do_GET(self):
        ruta = self.path.split("?")[0]

        if ruta == "/history":
            with lock:
                datos = list(historial)
            cuerpo = json.dumps({
                "history": datos,
                "total": len(datos),
                "max": MAX_HISTORIAL
            }, ensure_ascii=False)
            self._enviar_respuesta(200, cuerpo)

        elif ruta == "/users":
            with lock:
                lista_usuarios = list(usuarios.keys())
            cuerpo = json.dumps({
                "users": lista_usuarios,
                "total": len(lista_usuarios)
            }, ensure_ascii=False)
            self._enviar_respuesta(200, cuerpo)

        else:
            cuerpo = json.dumps({"error": "Ruta no encontrada"}, ensure_ascii=False)
            self._enviar_respuesta(404, cuerpo)
            mandar_log("ERROR", f"HTTP 404 ruta={self.path} ip={self.client_address[0]}")

    def _enviar_respuesta(self, codigo, cuerpo_json):
        cuerpo_bytes = cuerpo_json.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo_bytes)))
        self.send_header("ngrok-skip-browser-warning", "true")
        self.end_headers()
        self.wfile.write(cuerpo_bytes)

    def do_POST(self):
        cuerpo = json.dumps({"error": "Solicitud malformada: solo se acepta GET"}, ensure_ascii=False)
        self._enviar_respuesta(400, cuerpo)
        mandar_log("ERROR", f"HTTP 400 metodo=POST ip={self.client_address[0]}")

    def do_PUT(self):
        cuerpo = json.dumps({"error": "Solicitud malformada: solo se acepta GET"}, ensure_ascii=False)
        self._enviar_respuesta(400, cuerpo)
        mandar_log("ERROR", f"HTTP 400 metodo=PUT ip={self.client_address[0]}")

    def do_DELETE(self):
        cuerpo = json.dumps({"error": "Solicitud malformada: solo se acepta GET"}, ensure_ascii=False)
        self._enviar_respuesta(400, cuerpo)
        mandar_log("ERROR", f"HTTP 400 metodo=DELETE ip={self.client_address[0]}")


def iniciar_servidor_http():
    httpd = HTTPServer((HTTP_HOST, HTTP_PORT), ManejadorHTTP)
    print(f"[HTTP] Servidor HTTP escuchando en {HTTP_HOST}:{HTTP_PORT}")
    mandar_log("CONNECT", f"Servidor HTTP iniciado en puerto {HTTP_PORT}")
    httpd.serve_forever()

def main():
    try:
        hilo_http = threading.Thread(target=iniciar_servidor_http, daemon=True)
        hilo_http.start()
        iniciar_servidor_tcp()
    except KeyboardInterrupt:
        print("Servidor detenido.")
        mandar_log("DISCONNECT", "Servidor detenido por el usuario")
        udp_log_socket.close()
        sys.exit(0)
main()