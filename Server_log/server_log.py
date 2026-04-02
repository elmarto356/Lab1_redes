import socket
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
UDP_IP = "0.0.0.0"  # Cambiar a NGROK ip
UDP_PORT = 5500     # Cambiar puerto
LOG_FILE = "chat.log"

def start_log_server():
    # Creación del Socket UDP (SOCK_DGRAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Enlace al puerto
        sock.bind((UDP_IP, UDP_PORT))
        
        print("      SEVER LOGGER ACTIVADO (UDP)      ")
        print(f" Puerto: {UDP_PORT} | Archivo: {LOG_FILE}")

        while True:
            # Recepción de datos (Bloqueante hasta que llega un evento)
            # data: el mensaje enviado por el Servidor B
            # addr: (IP_origen, Puerto_origen)
            data, addr = sock.recvfrom(4096)
            
            # Procesamiento del mensaje
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                contenido = data.decode('utf-8').strip()
            except UnicodeDecodeError:
                contenido = f"[Error Decodificación] {data}"

            # Formato de registro: [Fecha] IP: Origen | Evento: Mensaje
            log_entry = f"[{timestamp}] IP: {addr[0]} | EVENTO: {contenido}"
            
            # Salida por Consola
            print(log_entry)
            
            # Persistencia en Archivo
            # Append para no borrar logs
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")

    except KeyboardInterrupt:
        print("\n[!] Apagando servidor de logs de forma segura...")
    except Exception as e:
        print(f"\n[X] Error crítico en el Logger: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    # Inicialización del archivo si no existe
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"--- INICIO DE SESIÓN DE LOGS: {datetime.now()} ---\n")
            
    start_log_server()