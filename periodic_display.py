from sense_hat import SenseHat
import time

# Initialisation de la Sense HAT
sense = SenseHat()

# Fonction pour lire et afficher les valeurs
def read_and_display_sense_data():
    while True:
        # Lire les valeurs de température, humidité et pression
        temp = sense.get_temperature()
        humidity = sense.get_humidity()
        pressure = sense.get_pressure()

        # Affichage des valeurs
        print("Temperature: {:.1f}C".format(temp))
        print("Humidity: {:.1f}%".format(humidity))
        print("Pressure: {:.1f}mbar".format(pressure))

# Appeler la fonction
read_and_display_sense_data()