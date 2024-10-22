import network
import time
import socket
from machine import Pin

# Configura el pin del LED en la ESP32
led = Pin(2, Pin.OUT)

# Página web para controlar el LED
def web_page():
    html = """
    <html>
    <head>
        <title>LED SWITCH</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding-top: 50px;
            }
            h1 {
                color: #333;
                font-size: 36px;
                margin-bottom: 20px;
            }
            p {
                margin: 20px;
            }
            button {
                padding: 15px 30px;
                font-size: 18px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                opacity: 0.9;
            }
            .on-button {
                background-color: #28a745;
                color: white;
            }
            .off-button {
                background-color: #dc3545;
                color: white;
            }
            .container {
                display: inline-block;
                padding: 20px;
                border-radius: 10px;
                background-color: white;
                box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LED SWITCH</h1>
            <p><a href="/on"><button class="on-button">Encender</button></a></p>
            <p><a href="/off"><button class="off-button">Apagar</button></a></p>
        </div>
    </body>
    </html>
    """
    return html

# Configuración del modo Access Point en la ESP32
def ap_mode(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while not ap.active():
        pass
    print('Modo AP está activo, puedes conectarte ahora.')
    print('Dirección IP: ' + ap.ifconfig()[0])

    # Configuración del socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print('Conexión por parte de (IP): %s' % str(addr))
        request = conn.recv(1024)
        request_str = request.decode('utf-8')
        print('Contenido = %s' % str(request))
        
        # Encender o apagar el LED
        if '/on' in request_str:
            print('Encendiendo LED')
            led.value(1)
        elif '/off' in request_str:
            print('Apagando LED')
            led.value(0)

        # Respuesta HTTP
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n" + web_page()
        conn.sendall(response)
        conn.close()

# Ejecutar en modo Access Point
ap_mode('ESP32_AP', '12345678')
