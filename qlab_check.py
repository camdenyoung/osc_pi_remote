import time
import threading
import socket
# from gpiozero import Button, LED
# from pythonosc.udp_client import SimpleUDPClient
from pythonosc import tcp_client
# from pythonosc.dispatcher import Dispatcher
# from pythonosc import osc_server
from signal import pause

# OSC Setup
osc_dest_ip = "127.0.0.1"       # Qlab Destination IP
osc_dest_port = 53000           # Qlab Destination Port
osc_listen_ip = "0.0.0.0"       # RPi Listen Port
osc_listen_port = 53001         # RPi Listen Port
retry_delay = 30

number = 0
heatbeat = 60
connected = False
checked = False
tested = False

osc_update_path = "/updates"
osc_update_state = 1


def receive_updates(path, value):
    print("Subcribing to Updates")
    client.send_message(path, value)


def connect_to_qlab(ip, port):
    global checked
    while checked == False:
        try:
            client = tcp_client.AsyncDispatchTCPClient(
                ip, port)
            print(f"Connected to Qlab at {ip}:{port}")
            checked = True
            response = client.handle_messages(1)
            print(f"Response: {response}")
            # status_led.on()
            return client
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            print(f"Cannot connect to Qlab ({e}) - retrying in {retry_delay}s")
            # status_led.blink()
            checked = False
            time.sleep(retry_delay)


while True:
    global client
    try:
        if checked == False:
            client = connect_to_qlab(osc_dest_ip, osc_dest_port)
            print(f"Client: {client} Checked: {checked}")
            response = client.handle_messages(1)
            print(f"Response: {response}")
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
    # else:
    #    user_input = input("Enter a number:")
    #    number = int(user_input)
