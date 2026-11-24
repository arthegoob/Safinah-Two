import os
import sys
import threading
import time

import cv2
import requests

# Di Windows (simulasi) pakai pin palsu. Di Pi pakai pin asli.
if sys.platform == "win32":
    os.environ.setdefault("GPIOZERO_PIN_FACTORY", "mock")
from gpiozero import LED

from color_detect import AWAL, deteksi

# ---- Pengaturan ----
PIN = {"merah": 17, "hijau": 27, "biru": 22}   # nomor GPIO (BCM), sesuaikan dengan kabelmu
FRAME_STABIL = 5       # objek harus terlihat berturut-turut sekian frame (anti salah deteksi)
JEDA_UPLOAD = 5        # detik, jeda minimal antar upload
UPLOAD_URL = os.environ.get("UPLOAD_URL", "")
UPLOAD_KEY = os.environ.get("UPLOAD_KEY", "")

led = {nama: LED(pin) for nama, pin in PIN.items()}
WARNA = {"merah": (0, 0, 255), "hijau": (0, 255, 0), "biru": (255, 0, 0)}


def set_led(aktif):
    """aktif = nama objek yang terdeteksi, atau None. Hanya satu LED menyala."""
    for nama, l in led.items():
        if nama == aktif:
            l.on()
        else:
            l.off()


def kirim_foto(frame):
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        return
    try:
        r = requests.post(
            UPLOAD_URL,
            files={"image": ("capture.jpg", buf.tobytes(), "image/jpeg")},
            headers={"x-api-key": UPLOAD_KEY},
            timeout=5,
        )
        print("Upload:", r.status_code, r.text)
    except requests.RequestException as e:
        print("Upload gagal:", e)


def main():
    if not UPLOAD_URL or not UPLOAD_KEY:
        print("PERINGATAN: UPLOAD_URL / UPLOAD_KEY belum di-set, upload dimatikan")

    cap = cv2.VideoCapture(0)
    hitung = {"merah": 0, "hijau": 0, "biru": 0}   # berapa frame berturut-turut terlihat
    terakhir_upload = 0
    led_sekarang = "belum"

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t, l = frame.shape[:2]
        frame = cv2.resize(frame, (640, int(t * 640 / l)))
        polos = frame.copy()          # salinan tanpa kotak, untuk dikirim ke website

        hasil, _ = deteksi(frame, AWAL)

        # Hitung kestabilan: naik kalau terlihat, reset ke 0 kalau hilang
        for nama in hitung:
            hitung[nama] = hitung[nama] + 1 if nama in hasil else 0

        # Pilih objek yang sudah stabil; kalau lebih dari satu, ambil yang terbesar
        stabil = [n for n in hasil if hitung[n] >= FRAME_STABIL]
        aktif = max(stabil, key=lambda n: cv2.contourArea(hasil[n]), default=None)

        set_led(aktif)
        if aktif != led_sekarang:
            print("LED:", aktif or "semua mati")
            led_sekarang = aktif

        # Kotak biru -> kirim foto (di thread lain supaya video tidak macet)
        if aktif == "biru" and UPLOAD_URL and time.time() - terakhir_upload > JEDA_UPLOAD:
            terakhir_upload = time.time()
            threading.Thread(target=kirim_foto, args=(polos,), daemon=True).start()

        for nama, k in hasil.items():
            x, y, w, h = cv2.boundingRect(k)
            cv2.rectangle(frame, (x, y), (x + w, y + h), WARNA[nama], 2)
            cv2.putText(frame, nama, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WARNA[nama], 2)
        if os.environ.get("HEADLESS") != "1":
            cv2.imshow("Deteksi", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    set_led(None)
    cap.release()
    cv2.destroyAllWindows()


main()