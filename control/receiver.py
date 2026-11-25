import json
import socket
import time

PORT = 5005
TIMEOUT = 0.5        # seconds without a packet -> failsafe

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
sock.settimeout(0.1)

thrust = 0.0
terakhir = 0.0
status = ""

while True:
    try:
        data, _ = sock.recvfrom(1024)
        thrust = float(json.loads(data)["t"])
        terakhir = time.time()
    except socket.timeout:
        pass
    except (ValueError, KeyError):
        continue                         # ignore garbage packets

    if time.time() - terakhir > TIMEOUT:
        thrust = 0.0
        baru = "FAILSAFE (no data)"
    else:
        baru = f"thrust {thrust:+.2f}"

    if baru != status:                   # print only when something changes
        print(baru)
        status = baru
    # later: send `thrust` to the Pixhawk here