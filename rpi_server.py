import socket
import time
from influxdb import InfluxDBClient 

INFLUX_HOST = "influxdb-service.bme-stack.svc.cluster.local"
INFLUX_PORT = x
INFLUX_DB = "bme680_db"
INFLUX_MEASUREMENT = "bme680_measure"

HOST = 'x.x.x.x'
PORT = x

def init_influx_client():
    try:
        client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=INFLUX_DB)
        print("Client InfluxDB V1 initialisé.")
        
        client.create_database(INFLUX_DB)
        return client
    except Exception as e:
        print(f"ERREUR INFLUXDB: Échec de l'initialisation du client : {e}")
        raise


def insert_data(influx_client, temp, pressure, humidity, gas):
    json_body = [
        {
            "measurement": INFLUX_MEASUREMENT,
            "tags": {
                "source": "esp32"
            },
            "fields": {
                "temperature": temp,
                "pressure": pressure,
                "humidity": humidity,
                "gas": gas
            }
        }
    ]
    
    try:
        influx_client.write_points(json_body)

    except Exception as e:
        print(f"ERREUR INFLUXDB : Échec de l'écriture : {e}")


def start_server():
    print(f"RPi 4 : Démarrage du serveur TCP sur le port {PORT}...")
    
    try:
        influx_client = init_influx_client() 
    except Exception:
        print("Arrêt du serveur.")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        
        print("En attente de connexion de l'ESP32...")
        
        while True:
            try:
                conn, addr = s.accept()
                print(f"\nConnexion établie avec {addr}")
                
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            print("Connexion fermée par l'ESP32. Attente de la prochaine connexion.")
                            break
                            
                        data_string = data.decode('utf-8').strip()

                        if data_string:
                            try:
                                temp, pressure, humidity, gas = map(float, data_string.split(','))

                                insert_data(influx_client, temp, pressure, humidity, gas) 

                                print("-" * 40)
                                print(f"DONNÉES REÇUES et ENVOYÉES À INFLUXDB.")
                                print(f"  Température : {temp:.2f} °C")
                                print(f"  Pression    : {pressure:.0f} hPa")
                                print(f"  Humidité    : {humidity:.1f} %")
                                print(f"  Qualité Air : {gas:.0f} Ohms")

                            except ValueError:
                                print(f"Format de données incorrect : '{data_string}'. CSV attendu.")
                            except Exception as e:
                                print(f"Erreur lors du traitement ou de l'écriture BDD : {e}")
                                
            except KeyboardInterrupt:
                print("\nArrêt du serveur par l'utilisateur.")
                break
            except Exception as e:
                print(f"Erreur du serveur de socket : {e}")

    print("Serveur fermé.")

if __name__ == "__main__":
    start_server()
