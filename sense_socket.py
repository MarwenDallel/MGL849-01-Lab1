import socket
import time
import threading
from sense_hat import SenseHat

# Initialize the Sense HAT object
sense = SenseHat()

# Server configuration
server_host = '192.168.18.9'
server_port = 1234

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Data storage
data_lock = threading.Lock()
ambient_temp = 0
pressure = 0
humidity = 0
desired_temp = 37.0
fictive_power = 0

def update_desired_temp():
    global desired_temp
    while True:
        for event in sense.stick.get_events():
            if event.action == "pressed":
                with data_lock:
                    if event.direction == "up":
                        desired_temp += 0.5
                    elif event.direction == "down":
                        desired_temp -= 0.5

def read_sense_hat_data():
    global ambient_temp, pressure, humidity, fictive_power
    while True:
        with data_lock:
            # Read data from the Sense HAT
            ambient_temp = sense.get_temperature()
            pressure = sense.get_pressure()
            humidity = sense.get_humidity()
            
            # Calculate fictive power based on the temperature
            temp_threshold = desired_temp - ambient_temp
            if desired_temp <= ambient_temp:
                fictive_power = 0
            else:
                if temp_threshold > 6:
                    fictive_power = 100
                else:
                    fictive_power = (temp_threshold / 6) * 100

def send_data_to_server():
    while True:
        with data_lock:
            # Prepare messages with the correct format and a newline character at the end
            temp_ambient_msg = "TP{:.2f}\n".format(ambient_temp)
            temp_desired_msg = "TD{:.2f}\n".format(desired_temp)
            power_msg = "PW{:.2f}\n".format(fictive_power)
            pressure_msg = "PR{:.2f}\n".format(pressure)
            humidity_msg = "HU{:.2f}\n".format(humidity)

        # Send data to the server
        for message in [temp_ambient_msg, temp_desired_msg, power_msg, pressure_msg, humidity_msg]:
            print("Sending: {}".format(message.strip()))
            client_socket.sendall(message.encode('utf-8'))
        time.sleep(1)

try:
    client_socket.connect((server_host, server_port))
    print("Connected to the server at {}:{}".format(server_host, server_port))
    
    # Start the sensor reading thread
    sensor_thread = threading.Thread(target=read_sense_hat_data)
    sensor_thread.daemon = True  # This thread will automatically close when the main program exits
    sensor_thread.start()

    # Start the data sending thread
    sending_thread = threading.Thread(target=send_data_to_server)
    sending_thread.daemon = True
    sending_thread.start()
    
    # Start the joystick event handling thread
    joystick_thread = threading.Thread(target=update_desired_temp)
    joystick_thread.daemon = True
    joystick_thread.start()

    # Keep the main thread alive while the other threads are running
    while True:
        time.sleep(1)

except Exception as e:
    print("An error occurred: {}".format(e))
finally:
    # Close the connection
    client_socket.close()
    print("Connection closed.")