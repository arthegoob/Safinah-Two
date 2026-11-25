import sys
import time
from pymavlink import mavutil

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
mav = mavutil.mavlink
m = mavutil.mavlink_connection(PORT, baud=115200)
m.wait_heartbeat()
SYS, COMP = m.target_system, 1       # the autopilot is normally component 1
print("Connected to system", SYS)


def cmd(command, *params):
    p = list(params) + [0] * (7 - len(params))
    m.mav.command_long_send(SYS, COMP, command, 0, *p)


def override(pwm):
    # channel 1 (steering) neutral, channel 3 (throttle) = pwm, the rest ignored
    m.mav.rc_channels_override_send(SYS, COMP, 1500, 0, pwm, 0, 0, 0, 0, 0)


def drain():
    servo = None
    while True:
        msg = m.recv_match(blocking=False)
        if msg is None:
            return servo
        t = msg.get_type()
        if t == "STATUSTEXT":
            print("Pixhawk:", msg.text)
        elif t == "COMMAND_ACK":
            print("ACK command", msg.command, "result", msg.result)
        elif t == "SERVO_OUTPUT_RAW":
            servo = msg


def tahan(pwm, detik):
    akhir = time.time() + detik
    servo = None
    while time.time() < akhir:
        override(pwm)
        servo = drain() or servo
        time.sleep(0.1)
    if servo:
        print(f"override {pwm} -> servo1..4:",
              servo.servo1_raw, servo.servo2_raw, servo.servo3_raw, servo.servo4_raw)
    else:
        print(f"override {pwm} -> no servo data yet")


cmd(mav.MAV_CMD_SET_MESSAGE_INTERVAL, mav.MAVLINK_MSG_ID_SERVO_OUTPUT_RAW, 200000)
cmd(mav.MAV_CMD_DO_SET_MODE, 1, 0)       # custom mode on, 0 = Manual
tahan(1500, 2)
print("Arming (nothing should be connected to MAIN OUT)...")
cmd(mav.MAV_CMD_COMPONENT_ARM_DISARM, 1)
tahan(1500, 2)
try:
    for pwm in (1600, 1500, 1400, 1500):
        tahan(pwm, 2)
finally:
    override(1500)
    cmd(mav.MAV_CMD_COMPONENT_ARM_DISARM, 0)
    print("Disarmed")