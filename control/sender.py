import json
import os
import socket
import time

import pygame

PI_IP = os.environ.get("PI_IP", "")
PORT = 5005
AXIS_THRUST = 1      # change to the axis number you saw in stick_test.py
INVERT = True        # most sticks give negative values when pushed forward
DEADZONE = 0.10      # ignore small drift around the center
HZ = 20              # packets per second

if not PI_IP:
    raise SystemExit("Set PI_IP first")

pygame.init()
pygame.joystick.init()
stik = pygame.joystick.Joystick(0)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def baca_thrust():
    pygame.event.pump()
    try:
        nilai = stik.get_axis(AXIS_THRUST)
    except pygame.error:
        return 0.0                       # controller unplugged -> stop
    if INVERT:
        nilai = -nilai
    if abs(nilai) < DEADZONE:
        return 0.0
    return max(-1.0, min(1.0, nilai))


n = 0
while True:
    thrust = baca_thrust()
    pesan = json.dumps({"t": round(thrust, 3), "n": n}).encode()
    sock.sendto(pesan, (PI_IP, PORT))
    print(f"thrust {thrust:+.2f}")
    n += 1
    time.sleep(1 / HZ)