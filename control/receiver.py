import json
import socket
import time

PORT = 5005
TIMEOUT = 0.5      # no packet for this long -> failsafe
MAX_RATE = 2.0     # max thrust increase per second (1.0 = full range)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
sock.settimeout(0.05)

target = 0.0       # what the stick asks for
tampil = 0.0       # what we actually output (this goes to the Pixhawk later)
terakhir = 0.0
waktu_lalu = time.time()
status = ""


def batasi(tampil, target, dt):
    # slowing down or stopping: instant. Speeding up or reversing: rate-limited.
    if target == 0 or (tampil * target >= 0 and abs(target) <= abs(tampil)):
        return target
    step = MAX_RATE * dt
    return max(tampil - step, min(tampil + step, target))


while True:
    try:
        data, _ = sock.recvfrom(1024)
        target = max(-1.0, min(1.0, float(json.loads(data)["t"])))
        terakhir = time.time()
    except socket.timeout:
        pass
    except (ValueError, KeyError, TypeError):
        continue

    sekarang = time.time()
    dt = sekarang - waktu_lalu
    waktu_lalu = sekarang

    if sekarang - terakhir > TIMEOUT:
        target = 0.0
        pesan = "FAILSAFE (no data)"
    else:
        pesan = f"stick {target:+.2f}"

    tampil = batasi(tampil, target, dt)
    baru = f"{pesan} | out {tampil:+.2f}"
    if baru != status:
        print(baru)
        status = baru
    # later: send `tampil` to the Pixhawk here