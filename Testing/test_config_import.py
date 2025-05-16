from configparser import ConfigParser

config = ConfigParser()
file_found = False
print(file_found)
config.read("config.ini")

server = config["SERVER"]
buttons = config["BUTTONS"]

host = (server["osc_dest_ip"])
port = int(server["osc_dest_port"])

button1_on_path = buttons["button1_on_path"]

host2 = "192.168.10.1"

host3 = config.get("SERVER", "osc_dest_ip2", fallback="127.0.0.1")
print(f"host 3: {host3}")

print(f"Host: {host}")
print(f"Port: {port}")
print(host2)

print(button1_on_path)

print(type(host))
print(type(port))
print(type(host2))
