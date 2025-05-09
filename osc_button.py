import time
import threading
import socket
# from gpiozero import Button, LED
from pythonosc.udp_client import SimpleUDPClient
from pythonosc import tcp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from signal import pause

# OSC Setup
osc_dest_ip = "10.27.5.189"     # Qlab Destination IP
osc_dest_port = 53000
osc_listen_ip = "0.0.0.0"           # Qlab Listen Port
osc_listen_port = 53001         # RPi Listen Port

# client = SimpleUDPClient(osc_dest_ip, osc_dest_port) # Send over UDP
client = tcp_client.SimpleTCPClient(osc_dest_ip, osc_dest_port) # Send over TCP


number = 0

osc_update_path = "/updates"
osc_update_state = 1

button1_on_path = "/cue/3.5/start"
button1_on_value = 1
button1_off_path = "path/to/qlab"
button1_off_value = 0

button2_on_path = "/cue/3.5/pause"
button2_on_value = 0
button2_off_path = "path/to/qlab"
button2_off_value = 0

button3_on_path = "/cue/3.5/stop"
button3_on_value = 0
button3_off_path = "path/to/qlab"
button1_off_value = 0

button4_on_path = "/cue/3.5/load"
button4_on_value = 0
button4_off_path = "path/to/qlab"
button4_off_value = 0


def receive_updates(path, value):
    print("Subcribing to Updates")
    client.send_message(path, value)

def button_pressed(path, value):
    print("Button pressed! Cue", {number}, "Triggered")
    client.send_message(path, value)  # Replace with your OSC path/message


# Enable all replies from Qlab
receive_updates("/alwaysReply", 1)

# Test to send osc message immediately with executed script
# button_pressed(button1_on_path, 1)

while True:
        try:
            user_input = input("Enter a number: ")
            number = int(user_input)
            print("You entered:", number)
            responses = client.get_messages(1)
            print(responses)
            if number == 1:
                button_pressed(button1_on_path, 1)
            elif number == 2:
                button_pressed(button2_on_path, 1)
            elif number == 3:
                button_pressed(button3_on_path, 1)
            elif number == 4:
                button_pressed(button4_on_path, 1)
            elif number ==9:
                 print("Exiting")
                 quit()
            else:
                print("Not valid input")
        except ValueError:
             print("Invalid Input")