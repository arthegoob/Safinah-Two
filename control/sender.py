import json
import os
import socket
import time

import pygame

PI_IP = os.environ.get("PI_IP", "")
PORT = 5005
AXIS_THRUST = 1        # your thrust axis from stick_test.py
INVERT = True          # forward = negative on the axis, so flip it
DEADZONE = 0.10
HZ = 20
DEADMAN_BUTTON = None  # e.g. 5: thrust only while that button is held. None = off

if not PI_IP:
    raise SystemExit("Set PI_IP first")

pygame.init()
pygame.joystick.init()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

stik = pygame.joystick.Joystick(0) if pygame.joystick.get_count() else None


def baca_thrust():
    global stik
    for e in pygame.event.get():
        if (e.type == pygame.JOYDEVICEREMOVED and stik is not None
                and e.instance_id == stik.get_instance_id()):
            print("Controller unplugged -> thrust 0")
            stik = None
        elif e.type == pygame.JOYDEVICEADDED and stik is None:
            stik = pygame.joystick.Joystick(e.device_index)
            print("Controller connected:", stik.get_name())

    if stik is None:
        return 0.0
    try:
        if DEADMAN_BUTTON is not None and not stik.get_button(DEADMAN_BUTTON):
            return 0.0
        nilai = stik.get_axis(AXIS_THRUST)
    except pygame.error:
        return 0.0

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