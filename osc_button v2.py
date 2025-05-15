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
button2 = Button(27, pull_up=True)
button3 = Button(5, pull_up=True)
button4 = Button(6, pull_up=True)

lock = threading.Lock()


# client = SimpleUDPClient(osc_dest_ip, osc_dest_port) # Send over UDP
# client = tcp_client.SimpleTCPClient(osc_dest_ip, osc_dest_port)  # Send over TCP

number = 0
heatbeat = 60
connected = False
checked = False
tested = False

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
    global checked
    while checked == False:
        try:
            client = tcp_client.SimpleTCPClient(ip, port)
            print(f"Connected to Qlab at {ip}:{port}")
            response = client.get_messages(1)
            # print(f"Response: {response}")
            # print(f"Checked = {checked}")
            status_led.on()
            checked = True
            return client
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            print(f"Cannot connect to Qlab ({e}) - retrying in {retry_delay}s")
            status_led.blink()
            checked = False
            print(f"Checked = {checked}")
            time.sleep(retry_delay)


def keep_alive():
    global connected, client, checked
    print("Keep Alive Started")
    client = 0
    while True:
        # print(f"Connected = {connected}")
        # print(f"Thread Client = {client}")
        time.sleep(5)
        with lock:
            if client:
                try:
                    client.send_message("/ping", 1)
                    # print(f"Check Loop Client {client}")
                    # print(f"Connected = {connected}")
                    connected = True
                    response = client.get_messages(1)
                    # print(f"Check Response: {response}")
                    # return connected
                except Exception as e:
                    print(f"Keep-alive failed: {e} Client = {client}")
                    connected = False
                    checked = False

                    # print(f"Connected = {connected}")


def receive_updates(path, value):
    print("Subcribing to Updates")
    client.send_message(path, value)


def button_pressed(path, value):
    print(f"Button pressed! OSC, Path: {path}, Value: {value}")
    client.send_message(path, value)  # Replace with your OSC path/message
    response = client.get_messages(1)
    print(f"Response: {response}")

# First attempt at sending messages based on button - Not currently used


def button():
    if button1.when_pressed:
        button_pressed(button1_on_path, 1)
    elif button2.when_pressed:
        button_pressed(button2_on_path, 1)
    elif button3.when_pressed:
        button_pressed(button3_on_path, 1)
    elif button4.when_pressed:
        button_pressed(button4_on_path, 1)
    elif button3.when_released:
        print("LOAD CUE")
    else:
        print("waiting for input")


def button1_on():
    global checked
    try:
        if checked == True:
            button_pressed(button1_on_path, 1)
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button2_on():
    global checked
    try:
        if checked == True:
            button_pressed(button2_on_path, 1)
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button3_on():
    global checked
    try:
        if checked == True:
            button_pressed(button3_on_path, 1)
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button4_on():
    global checked
    try:
        if checked == True:
            button_pressed(button4_on_path, 1)
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked

# Test to send osc message immediately with executed script
# button_pressed(button1_on_path, 1)


threading.Thread(target=keep_alive, daemon=True).start()

while True:
    global client
    # print(f"Connected = {connected}")
    try:
        if checked == False:
            client = connect_to_qlab(osc_dest_ip, osc_dest_port)
            print(f"Client: {client}")
            print(f"Checked: {checked}")
            response = client.get_messages(1)
            # print(f"Response: {response}")
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False

    else:
        button1.when_pressed = button1_on
        button2.when_pressed = button2_on
        button3.when_pressed = button3_on
        button4.when_pressed = button4_on
        button3.when_released = button4_on

    time.sleep(1)
