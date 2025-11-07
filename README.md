# Projet-IoT-Environnementale
Ce projet illustre une chaîne de données complète et résiliente, allant d'un capteur embarqué (BME680 + ESP32) à une plateforme d'analyse et de visualisation conteneurisée (Kubernetes, InfluxDB, Grafana) sur un Raspberry Pi 4 (Edge Computing).

## Architecture du Projet
1. **Capteur (ESP32 + BME680)** : Collecte les données de Température, Pression, Humidité et Qualité de l'Air (Gaz).
2. **Réseau (Wi-Fi + TCP)** : L'ESP32 envoie les données au Raspberry Pi 4 via une connexion TCP sur le NodePort de Kubernetes.
3. **Serveur Python (Pod Kubernetes)** : Reçoit les données brutes et les injecte dans la base de données.
4. **Base de Données (InfluxDB)** : Stockage des données de séries temporelles.
5. **Visualisation (Grafana)** : Création de tableaux de bord pour la surveillance en temps réel.

## Partie 1 : Le Nœud Embarqué (ESP32 / MicroPython)
Le rôle de l'ESP32 est de lire le capteur BME680, de se connecter au Wi-Fi, et d'envoyer les mesures sous forme de chaîne CSV au serveur sur le Raspberry Pi.

**Configuration du Matériel**
- **ESP32** : Plateforme MicroPython.
- **Capteur BME680** : Connecté via I2C (ex: SCL sur GPIO 22, SDA sur GPIO 21).

**Code MicroPython (main.py)**
Ce script est configuré pour se connecter au réseau Wi-Fi, puis à l'adresse externe exposée par Kubernetes (le NodePort).

## Partie 2 : Le Serveur d'Ingestion sur Kubernetes (k3s)
Le Raspberry Pi exécute k3s, la distribution légère de Kubernetes. Le serveur Python est déployé comme un Pod dans un Namespace bme-stack.

### A. Les Déploiements YAML
On a besoin de trois manifestes YAML : InfluxDB, Grafana et le Pod Python (avec son service NodePort).
**Service Python (python-server-service.yaml)** : Expose le port 8080 du Pod vers le réseau local via un NodePort.

### B. Le Script d'Ingestion Python (rpi_server.py)
Ce script doit impérativement utiliser le nom de service interne de Kubernetes pour se connecter à InfluxDB.

## Partie 3 : Stockage et Visualisation (InfluxDB & Grafana)
Les données reçues par le serveur Python sont formatées en points InfluxDB (V1) et écrites dans la base bme680_db.
- **Connexion Grafana** : Grafana accède à InfluxDB en utilisant le nom de service interne : http://influxdb-service.bme-stack.svc.cluster.local:8086.
- **Requêtes InfluxQL** : Les tableaux de bord Grafana utilisent des requêtes simples pour visualiser la mesure bme680_measure :

SELECT mean("temperature") FROM "bme680_measure" WHERE $timeFilter GROUP BY time(1m) fill(null)
