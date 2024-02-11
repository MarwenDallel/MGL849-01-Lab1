import time
import socket
import random

# Configuration du serveur
server_host = "127.0.0.1"
server_port = 1234


# Fonction pour établir la connexion avec le serveur
def create_client_socket():
    # Création d'une socket client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connexion au serveur
    client_socket.connect((server_host, server_port))
    return client_socket


def calculate_fictive_power(desired_temp, ambient_temp):
    """Calculer la puissance fictive en fonction de la différence de température."""
    temp_diff = desired_temp - ambient_temp
    # Calcul de la puissance fictive
    # La puissance est limitée entre 0 et 100
    return max(0, min(100, (temp_diff / 6) * 100)) if temp_diff > 0 else 0


def send_random_data():
    """Lire les capteurs périodiquement et mettre à jour les valeurs."""
    client_socket = create_client_socket()
    while True:
        # Generate random sensor readings
        ambient_temp_value = random.uniform(15.0, 30.0)
        pressure_value = random.uniform(950.0, 1050.0)
        humidity_value = random.uniform(30.0, 70.0)
        desired_temp_value = random.uniform(15.0, 30.0)

        # Calcul de la puissance fictive
        fictive_power_value = calculate_fictive_power(
            desired_temp_value, ambient_temp_value
        )

        # Préparation des messages
        temp_ambient_msg = "TP{:.2f}\n".format(ambient_temp_value)
        temp_desired_msg = "TD{:.2f}\n".format(desired_temp_value)
        power_msg = "PW{:.2f}\n".format(fictive_power_value)
        pressure_msg = "PR{:.2f}\n".format(pressure_value)
        humidity_msg = "HU{:.2f}\n".format(humidity_value)

        # Envoyer les messages
        for message in [
            temp_ambient_msg,
            temp_desired_msg,
            power_msg,
            pressure_msg,
            humidity_msg,
        ]:
            client_socket.sendall(message.encode("utf-8"))

        # Attente avant la prochaine lecture
        time.sleep(1)


# Lancer la fonction pour envoyer des données
send_random_data()
