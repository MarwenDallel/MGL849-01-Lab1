import multiprocessing
import time
import socket
from sense_hat import SenseHat
from shared_priority_queue import SharedPriorityQueue

# Initialisation du SenseHat
sense = SenseHat()

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


# Niveaux de priorité pour la file d'attente
LOW_PRIORITY = 10
MEDIUM_PRIORITY = 5
HIGH_PRIORITY = 1

# Définition d'une file d'attente prioritaire qui est sûre pour les processus
message_queue = SharedPriorityQueue()

# Variables partagées pour les données des capteurs
ambient_temp = multiprocessing.Value("d", 0.0)
pressure = multiprocessing.Value("d", 0.0)
humidity = multiprocessing.Value("d", 0.0)
desired_temp = multiprocessing.Value("d", 37.0)
fictive_power = multiprocessing.Value("d", 0.0)


def calculate_fictive_power(desired_temp, ambient_temp):
    """Calculer la puissance fictive en fonction de la différence de température."""
    temp_diff = desired_temp - ambient_temp
    # Calcul de la puissance fictive
    # La puissance est limitée entre 0 et 100
    return max(0, min(100, (temp_diff / 6) * 100)) if temp_diff > 0 else 0


# Fonction pour envoyer les données à partir de la file d'attente
def send_data_from_queue(message_queue):
    """Envoyer des données depuis la file d'attente."""
    client_socket = create_client_socket()
    while True:
        while not message_queue.empty():
            try:
                # Attendre le prochain message de la file (bloquant jusqu'à ce qu'un élément soit disponible)
                message = message_queue.get()
                # Envoyer le message
                client_socket.sendall(message.encode("utf-8"))
            except socket.error as e:
                print(f"Erreur de socket: {e}")
                # Tentative de reconnexion
                client_socket = create_client_socket()
            except Exception as e:
                print(f"Erreur inattendue: {e}")


def read_sensors_periodically(message_queue):
    """Lire les capteurs périodiquement et mettre à jour les valeurs partagées."""
    while True:
        # Lecture des capteurs
        ambient_temp.value = sense.get_temperature()
        pressure.value = sense.get_pressure()
        humidity.value = sense.get_humidity()

        # Calcul de la puissance fictive
        fictive_power.value = calculate_fictive_power(
            desired_temp.value, ambient_temp.value
        )

        # Préparation des messages
        temp_ambient_msg = "TP{:.2f}\n".format(ambient_temp.value)
        temp_desired_msg = "TD{:.2f}\n".format(desired_temp.value)
        power_msg = "PW{:.2f}\n".format(fictive_power.value)
        pressure_msg = "PR{:.2f}\n".format(pressure.value)
        humidity_msg = "HU{:.2f}\n".format(humidity.value)

        # Ajout des messages dans la file avec une priorité moyenne
        for message in [temp_ambient_msg, pressure_msg, humidity_msg]:
            message_queue.put(message, MEDIUM_PRIORITY)

        # Ajout des messages dans la file avec une basse priorité
        for message in [temp_desired_msg, power_msg]:
            message_queue.put(message, LOW_PRIORITY)

        # Attente avant la prochaine lecture
        time.sleep(1)


def handle_user_input(message_queue):
    """Gérer les entrées utilisateur pour ajuster la température désirée."""
    while True:
        # Gestion des événements du joystick
        for event in sense.stick.get_events():
            if event.action == "pressed":
                # Ajustement de la température désirée
                if event.direction == "up":
                    desired_temp.value += 0.5
                elif event.direction == "down":
                    desired_temp.value -= 0.5

                # Calcul de la puissance fictive après modification de la température
                fictive_power.value = calculate_fictive_power(
                    desired_temp.value, ambient_temp.value
                )

                # Préparation des messages avec une haute priorité
                temp_desired_msg = "TD{:.2f}\n".format(desired_temp.value)
                power_msg = "PW{:.2f}\n".format(fictive_power.value)

                # Ajout des messages dans la file avec une haute priorité
                for message in [temp_desired_msg, power_msg]:
                    message_queue.put(message, HIGH_PRIORITY)


# Démarrage des processus
# Processus d'envoi des données
sender_process = multiprocessing.Process(
    target=send_data_from_queue, args=(message_queue,)
)
sender_process.start()

# Processus de lecture des capteurs
sensor_process = multiprocessing.Process(
    target=read_sensors_periodically, args=(message_queue,)
)
sensor_process.start()

# Processus de gestion des entrées utilisateur
user_input_process = multiprocessing.Process(
    target=handle_user_input, args=(message_queue,)
)
user_input_process.start()
