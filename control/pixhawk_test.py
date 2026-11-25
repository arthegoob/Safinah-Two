import sys
from pymavlink import mavutil

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"

m = mavutil.mavlink_connection(PORT, baud=115200)
print("Waiting for heartbeat...")
hb = m.wait_heartbeat(timeout=10)
if hb is None:
    raise SystemExit("No heartbeat. Check the cable, port, and permissions.")

print("Heartbeat from system", m.target_system, "component", m.target_component)
print("Vehicle type:", hb.type, "(10 = rover, 11 = boat)")
print("Armed:", bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED))
print("Custom mode number:", hb.custom_mode)