# Laboratorio 2: Redes de Computadores - Sistema de Chat TCP/UDP

## Identificación del Equipo
* **Integrante 1:** [Manuel Vega] - Rol USM: [202304644-2]
* **Integrante 2:** [Martin Fonseca] - Rol USM: [202373604-K]
* **Integrante 3:** [Agustin Concha] - Rol USM: [202173648-4]

---

## 1. Instrucciones de Ejecución
Para ejecutar correctamente el sistema, se deben seguir los siguientes pasos en el orden indicado:

**Paso 1: Servidor de Logs UDP**
* Abrir una terminal y ejecutar: `python [nombre_archivo_udp].py`
* El servidor de logs quedará escuchando en el puerto local `[ingresar puerto, ej: 5000]`.

**Paso 2: Servidor Principal (TCP + HTTP)**
* Abrir una segunda terminal y ejecutar: `python [nombre_archivo_servidor].py`
* El servidor iniciará el servicio TCP en el puerto `[puerto tcp]` y el servicio HTTP en el puerto `[puerto http]`.

**Paso 3: Exposición con NGROK (Opcional para pruebas locales, obligatorio para revisión remota)**
* Ejecutar en una nueva terminal: `ngrok start --all` (si usan archivo ngrok.yml) o iniciar ambos túneles por separado.
* Anotar las URLs generadas para TCP y HTTP.

**Paso 4: Ejecución del Cliente**
* Actualizar el puerto de conexion en el arhivo `Cliente_TCP.py`
* En una nueva terminal, ejecutar: `python Cliente_TCP.py`
* Registrar el usuario con el comando `NICK <nombre>` para ingresar a la sala.

---

## 2. Documentación del Protocolo TCP

### 2.1 Flujo Obligatorio
El cliente debe registrarse exitosamente enviando el comando `NICK` antes de poder enviar cualquier otro comando al servidor.

### 2.2 Comandos y Respuestas Esperadas
| Comando | Descripción |
| :--- | :--- |
| `NICK <nombre>` | Registra al usuario en el sistema. |
| `MSG <texto>` | Envía un mensaje a la sala de chat. |
| `DISCONNECT` | Desconecta al usuario del servidor. |

### 2.3 Códigos y Formatos de Error
* **Comando sin registrarse:** Si se envía `MSG` antes de `NICK`, el servidor responde: `[Ej: ERROR: Debe registrarse primero]`.
* **Nombre de usuario repetido:** Si el nombre ya está en uso, el servidor responde: `[Ej: ERROR: Nombre en uso]`.
* **Comando inválido/malformado:** Si se envía texto que no sigue el formato, el servidor responde: `[Ej: ERROR: Comando no reconocido]`.

---

## 3. Funcionalidades Adicionales

### API HTTP
El servidor expone dos endpoints de solo lectura:
* `/users`: Retorna un JSON con los usuarios conectados actualmente.
* `/history`: Retorna un JSON con el historial de mensajes.

### Formato de Logs UDP
Los eventos relevantes del servidor se envían al servidor UDP con el siguiente formato:
`[YYYY-MM-DD HH:MM:SS]-<TIPO_EVENTO> <descripción del evento>`

---

## 4. Consideraciones Adicionales e Inconvenientes
* El sistema fue probado utilizando Python 3.10+.
* Despues de cada mensaje enviado se muestra una confirmacion de que el mensaje fue enviado correctamente
