from sense_hat import SenseHat, ACTION_PRESSED
import time
import signal
import sys

# Initialize the Sense HAT object
sense = SenseHat()

# Set the initial desired temperature
desired_temp = 20.0  # Example initial value of 20 degrees Celsius

# Function to handle the joystick events
def handle_joystick_event(event):
    global desired_temp
    if event.action == ACTION_PRESSED:
        if event.direction == "up":
            desired_temp += 0.5
        elif event.direction == "down":
            desired_temp -= 0.5
        
        # Display the new desired temperature on the computer screen and Sense HAT
        display_temperature(desired_temp)

# Function to display temperature
def display_temperature(temp):
    message = "Desired Temp: {:.1f}C".format(temp)
    sense.show_message("o", scroll_speed=0.05)
    print(message)

# Bind joystick events to the handling function
sense.stick.direction_up = handle_joystick_event
sense.stick.direction_down = handle_joystick_event

# Graceful exit on Ctrl+C
def signal_handler(signum, frame):
    sense.clear()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Display the initial desired temperature
display_temperature(desired_temp)

# Loop to prevent the script from exiting
while True:
    # Read the actual temperature from the Sense HAT
    actual_temp = sense.get_temperature()
    
    # Display the actual temperature on the computer screen
    print("Actual Temperature: {:.1f}C".format(actual_temp))
    
    # Optional: You can also display this on the Sense HAT LED matrix
    # To prevent the message display from clashing with the joystick input,
    # you might want to use a different method or timing for this.
    
    # Wait some time before reading the temperature again
    time.sleep(2)