import time
import threading
import socket
# from gpiozero import Button, LED
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from signal import pause

# OSC Setup
osc_dest_ip = "10.27.5.189"     # Qlab Destination IP
osc_dest_port = 53000           # Qlab Listen Port
osc_listen_port = 53001         # RPi Listen Port
client = SimpleUDPClient(osc_dest_ip, osc_dest_port)

osc_update_path = "/updates"
osc_update_state = 1

button1_on_path = "/cue/3.5/start"
button1_on_value = 1
button1_off_path = "path/to/qlab"
button1_off_value = 0

button2_on_path = "path/to/qlab"
button2_on_value = 0
button2_off_path = "path/to/qlab"
button2_off_value = 0

button3_on_path = "path/to/qlab"
button3_on_value = 0
button3_off_path = "path/to/qlab"
button1_off_value = 0

button4_on_path = "path/to/qlab"
button4_on_value = 0
button4_off_path = "path/to/qlab"
button4_off_value = 0

def receive_updates(path, value):
    print("Subcribing to Updates")
    client.send_message(path, value)

def button_pressed(path, value):
    print("Button pressed! Cue 3.5 Triggered")
    client.send_message(path, value)  # Replace with your OSC path/message



#receive_updates(osc_update_path, osc_update_state)
#receive_updates("/alwaysReply", 0)

# Test to send osc message immediately with executed script
button_pressed(button1_on_path, 1)