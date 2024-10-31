import network
import time
import socket
from machine import Pin, ADC

led = Pin("LED", Pin.OUT)
adc = ADC(Pin(26))  # Configuración del pin ADC 26

# Generar página HTML con JavaScript para actualizar el valor del ADC
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
            .adc-value {
                font-size: 24px;
                margin-top: 20px;
            }
        </style>
        <script>
            // Función para actualizar el valor del ADC
            function updateADC() {
                fetch('/adc')
                .then(response => response.text())
                .then(data => {
                    document.getElementById("adcValue").innerText = "Valor ADC: " + data;
                });
            }
            // Actualizar el valor cada segundo
            setInterval(updateADC, 1000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>LED SWITCH</h1>
            <p><a href="/on"><button class="on-button">Encender</button></a></p>
            <p><a href="/off"><button class="off-button">Apagar</button></a></p>
            <div class="adc-value" id="adcValue">Valor ADC: --</div>
        </div>
    </body>
    </html>
    """
    return html

# Configuración del modo AP
def ap_mode(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while not ap.active():
        pass
    print('Modo AP está activo, puedes conectarte ahora.')
    print('Direccion IP: ' + ap.ifconfig()[0])

    # Configuración del socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print('Conexión por parte de (IP): %s' % str(addr))
        request = conn.recv(1024)
        request_str = request.decode('utf-8')
        print('Content = %s' % str(request))

        # Rutas para encender/apagar LED y leer el ADC
        if '/on' in request_str:
            print('Encendiendo LED')
            led.value(1)
        elif '/off' in request_str:
            print('Apagando LED')
            led.value(0)
        elif '/adc' in request_str:
            # Leer el valor del ADC y mapearlo de 0 a 100
            adc_value = int(adc.read_u16() / 65535 * 100)
            conn.send("HTTP/1.1 200 OK\nContent-Type: text/plain\nConnection: close\n\n" + str(adc_value))
            conn.close()
            continue

        # Responder con la página principal
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n" + web_page()
        conn.sendall(response)
        conn.close()

ap_mode('TLACUA', '12345678')

