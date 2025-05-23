# VERSION 3

import time
import threading
import socket
import configparser
from gpiozero import Button, LED, Device
# from pythonosc.udp_client import SimpleUDPClient
from pythonosc import tcp_client
# from pythonosc.dispatcher import Dispatcher
# from pythonosc import osc_server
from signal import pause

# MOCK PIN FACTORY FOR DEVELOPMENT WITHOUT A PI
# from gpiozero.pins.mock import MockFactory
# Device.pin_factory = MockFactory()

CONFIG_FILE = 'config.ini'

first = True


def load_config():
    global first
    config = configparser.ConfigParser()
    check = config.read(CONFIG_FILE)
    if not check:
        print(f"Config Not Found - {CONFIG_FILE}")
        exit(1)
    else:
        if first == True:
            print(f"Loading Config - {CONFIG_FILE}")
            first = False
        else:
            print(f"Refreshing Config - {CONFIG_FILE}")
        return config


def update_config():
    global osc_dest_ip, osc_dest_port, retry_delay, button1_on_path, button1_on_value, button1_off_path, button1_off_value, button2_on_path, button2_on_value, button2_off_path, button2_off_value, button3_on_path, button3_on_value, button3_off_path, button3_off_value, button4_on_path, button4_on_value, button4_off_path, button4_off_value
    # OSC SETUP
    osc_dest_ip = config['server'].get(
        'host', '127.0.0.1')            # Qlab Destination IP
    osc_dest_port = config['server'].getint(
        'port', 53000)                # Qlab Destination Port
    retry_delay = config['server'].getint(
        'retry_delay', "30")            # Server retry delay
    button1_on_path = config['buttons']['btn1_on_path']
    button1_on_value = config['buttons'].getfloat('btn1_on_value')
    button1_off_path = config['buttons']['btn1_off_path']
    button1_off_value = config['buttons'].getfloat('btn1_off_value')

    button2_on_path = config['buttons']['btn2_on_path']
    button2_on_value = config['buttons'].getfloat('btn2_on_value')
    button2_off_path = config['buttons']['btn2_off_path']
    button2_off_value = config['buttons'].getfloat('btn2_off_value')

    button3_on_path = config['buttons']['btn3_on_path']
    button3_on_value = config['buttons'].getfloat('btn3_on_value')
    button3_off_path = config['buttons']['btn3_off_path']
    button3_off_value = config['buttons'].getfloat('btn3_off_value')

    button4_on_path = config['buttons']['btn3_on_path']
    button4_on_value = config['buttons'].getfloat('btn3_on_value')
    button4_off_path = config['buttons']['btn3_off_path']
    button4_off_value = config['buttons'].getfloat('btn3_off_value')


# GPIO SETUP
btn1_led = LED(18)
btn2_led = LED(23)
btn3_led = LED(12)
btn4_led = LED(16)
button1 = Button(17, pull_up=True)
button2 = Button(27, pull_up=True)
button3 = Button(5, pull_up=True)
button4 = Button(6, pull_up=True)


def status_led(mode):
    if mode == "flash":
        print(f"LED MODE: {mode}")
        btn1_led.blink(0.5, 0.5)
        btn2_led.blink(0.5, 0.5)
        time.sleep(0.5)
        btn3_led.blink(0.5, 0.5)
        btn4_led.blink(0.5, 0.5)
    elif mode == "on":
        print(f"LED MODE: {mode}")
        btn1_led.on()
        btn2_led.on()
        btn3_led.on()
        btn4_led.on()
    else:
        btn1_led.off()
        btn2_led.off()
        btn3_led.off()
        btn4_led.off()


# LOCK THREADS
lock = threading.Lock()


# INIT VARIABLES
number = 0
heatbeat = 60
connected = False
checked = False
tested = False

osc_update_path = "/updates"
osc_update_state = 1


def connect_to_qlab():
    global checked, config
    while checked == False:
        try:
            config = load_config()
            update_config()
            client = tcp_client.SimpleTCPClient(osc_dest_ip, osc_dest_port)
            print(f"Connected to Qlab at {osc_dest_ip}:{osc_dest_port}")
            response = client.get_messages(1)
            # print(f"Response: {response}")
            # print(f"Checked = {checked}")
            status_led("on")
            checked = True
            # receive_updates(osc_update_path, osc_update_state)
            return client
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            print(
                f"Cannot connect to Qlab {osc_dest_ip}:{osc_dest_port} - ({e}) - retrying in {retry_delay}s")
            status_led("flash")
            checked = False
            print(f"Checked = {checked}")
            update_config()
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
                    # response = client.get_messages(1)
                    # print(f"Check Response: {response}")
                    # return connected
                except Exception as e:
                    print(
                        f"Keep-alive failed: {e} - {osc_dest_ip}:{osc_dest_port}")
                    connected = False
                    checked = False

                    # print(f"Connected = {connected}")


def receive_updates(path, value):
    print("Subcribing to Updates")
    client.send_message(path, value)


def button_pressed(path, value):
    if path:
        print(f"Button pressed! OSC, Path: {path}, Value: {value}")
        client.send_message(path, value)
    else:
        print(
            f"Path or Value is Empty.  Path: {path} Value: {value} - Message Not Sent")
        # for msg in client.get_messages(1):
        # print("Received:", msg)
        # response = client.get_messages(timeout=1)
        # print(f"Response: {response}")


def button1_on():
    global checked
    try:
        if checked == True:
            button_pressed(button1_on_path, button1_on_value)
            btn1_led.off()
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button2_on():
    global checked
    try:
        if checked == True:
            button_pressed(button2_on_path, button2_on_value)
            btn2_led.off()
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button3_on():
    global checked
    try:
        if checked == True:
            button_pressed(button3_on_path, button3_on_value)
            btn3_led.off()
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button4_on():
    global checked
    try:
        if checked == True:
            button_pressed(button4_on_path, button4_on_value)
            btn4_led.off()
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button1_off():
    global checked
    try:
        if checked == True:
            button_pressed(button1_off_path, button1_off_value)
            btn1_led.on()
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button2_off():
    global checked
    try:
        if checked == True:
            button_pressed(button2_off_path, button2_off_value)
            btn2_led.on()
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button3_off():
    global checked
    try:
        if checked == True:
            button_pressed(button3_off_path, button3_off_value)
            btn3_led.on()
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked


def button4_off():
    global checked
    try:
        if checked == True:
            button_pressed(button4_off_path, button4_off_value)
            btn4_led.on()
    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        return checked

        # Test to send osc message immediately with executed script
        # button_pressed(button1_on_path, 1)


threading.Thread(target=keep_alive, daemon=True).start()


while True:
    global client, config
    # print(f"Connected = {connected}")
    try:
        config = load_config()
        update_config()
        if checked == False:
            client = connect_to_qlab()
            print(f"Client: {client}")
            print(f"Checked: {checked}")
            response = client.get_messages(1)
            # print(f"Response: {response}")
            # receive_updates(osc_update_path, osc_update_state)

    except (ConnectionRefusedError, socket.timeout, OSError) as error:
        print(f"OSC Message Send Failed: {error}")
        connected = False
        checked = False
        update_config()

    else:
        # update_config()
        button1.when_pressed = button1_on
        button1.when_released = button1_off
        button2.when_pressed = button2_on
        button2.when_released = button2_off
        button3.when_pressed = button3_on
        button3.when_released = button3_off
        button4.when_pressed = button4_on
        button4.when_released = button4_off
        # button1.when_held = test()

    time.sleep(30)
