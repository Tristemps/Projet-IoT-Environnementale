from machine import Pin, I2C
import time
from bme680 import BME680_I2C
import sys
import network
import socket

# --- 1. Configuration du réseau ---
WIFI_SSID = 'xxx'
WIFI_PASSWORD = 'xxx'

SERVER_IP = '192.168.x.x'
SERVER_PORT = x
MAX_RETRIES = 5

# --- 2. Configuration du capteur ---
i2c = I2C(scl=Pin(22), sda=Pin(21))

try:
    sensor = BME680_I2C(i2c, address=0x76)
except Exception as e:
    print(f"ERREUR BME680 : Impossible d'initialiser le capteur.")
    print(f"Détail de l'erreur : {e}")
    sys.exit()
    
def connect_to_wifi():
    print(f"Connexion au réseau {WIFI_SSID}...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Try connect to SSID : {WIFI_SSID}")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        while not wlan.isconnected():
            print('.', end = " ")
            time.sleep_ms(500)
    print("\nWi-Fi Config: ",wlan.ifconfig())
    
def send_data_to_server(data):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(data.encode('utf-8'))
        print(f"ENVOI REUSSI: {data}")
    
    except OSError as e:
        print(f"ERREUR ENVOI TCP : {e}. Serveur non joignable ou refus de connexion.")
        
    finally:
        if s:
            s.close()
            
# --- 3. Boucle principale ---
connect_to_wifi()
print("Démarrage du cycle de mesure et d'envoi...")

time.sleep(5)

while True:
    try:        
        temp = sensor.temperature
        pressure = sensor.pressure
        humidity = sensor.humidity
        gas = sensor.gas
        
        data_to_send = f"{temp:.2f},{pressure:.0f},{humidity:.1f},{gas:.0f}"
        
        send_data_to_server(data_to_send)
    
    except Exception as e:
        print(f"Erreur de lecture : {e}")
        
    time.sleep(900)

