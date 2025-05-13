import time
import threading
import socket
from gpiozero import Button, LED
# from pythonosc.udp_client import SimpleUDPClient
from pythonosc import tcp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from signal import pause

# OSC Setup
osc_dest_ip = "10.27.5.189"     # Qlab Destination IP
osc_dest_port = 53000
osc_listen_ip = "0.0.0.0"           # Qlab Listen Port
osc_listen_port = 53001         # RPi Listen Port
retry_delay = 30


status_led = LED(24)
button1 = Button(17, pull_up=True)

# client = SimpleUDPClient(osc_dest_ip, osc_dest_port) # Send over UDP
# client = tcp_client.SimpleTCPClient(osc_dest_ip, osc_dest_port)  # Send over TCP

number = 0

connected = False

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


def connect_to_qlab(ip, port):
    while True:
        try:
            client = tcp_client.SimpleTCPClient(ip, port)
            print(f"Connected to Qlab at {ip}:{port}")
            # print(client)
            status_led.on()
            global connected
            connected = True
            return client
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            print(f"Cannot connect to Qlab ({e}) - retrying in {retry_delay}s")
            status_led.blink()
            connected = False
            time.sleep(retry_delay)
    print(connected)


def receive_updates(path, value):
    print("Subcribing to Updates")
    client.send_message(path, value)


def button_pressed(path, value):
    print("Button pressed! Cue", {number}, "Triggered")
    client.send_message(path, value)  # Replace with your OSC path/message


def button():
    if button1.is_pressed:
        button_pressed(button1_on_path, 1)
    elif number == 2:
        button_pressed(button2_on_path, 1)
    elif number == 3:
        button_pressed(button3_on_path, 1)
    elif number == 4:
        button_pressed(button4_on_path, 1)
    else:
        print("waiting for input")


def key_press():
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
    elif number == 9:
        print("Exiting")
        quit()
    else:
        print("Not valid input")

# Test to send osc message immediately with executed script
# button_pressed(button1_on_path, 1)


while True:
    client = connect_to_qlab(osc_dest_ip, osc_dest_port)
    while connected == True:
        try:
            button()
            # key_press()

        except (ConnectionRefusedError, socket.timeout, OSError) as error:
            print(f"OSC Message Send Failed: {error}")
            connected = False
