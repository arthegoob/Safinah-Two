import cv2
import numpy as np

# ---- Pengaturan ----
UKURAN_MINIMAL = 300      # luas minimal (piksel, setelah resize 640). File asal pakai 60;
                          # 300 lebih tahan noise webcam, turunkan kalau objek kecil tak terdeteksi
KEBULATAN_MINIMAL = 0.5   # bola: 1.0 = bulat sempurna
KOTAK_MINIMAL = 0.8       # kotak: luas / luas persegi pembungkusnya (1.0 = persegi sempurna)

AWAL = {
    "Merah_atas": 10,
    "Merah_bawah": 160,
    "Hijau_min": 65,
    "Hijau_max": 95,
    "Biru_min": 100,      # nilai awal tebakan, setel dengan slider
    "Biru_max": 130,
    "Kepekatan_min": 40,
    "Terang_min": 40,
}


def buat_slider():
    cv2.namedWindow("Pengaturan")
    for nama, nilai in AWAL.items():
        cv2.createTrackbar(nama, "Pengaturan", nilai, 255, lambda x: None)


def baca_slider():
    return {n: cv2.getTrackbarPos(n, "Pengaturan") for n in AWAL}


def buat_mask(hsv, s):
    p, t = s["Kepekatan_min"], s["Terang_min"]
    rng = lambda h1, h2: cv2.inRange(hsv, np.array([h1, p, t]), np.array([h2, 255, 255]))

    merah = rng(0, s["Merah_atas"]) | rng(s["Merah_bawah"], 179)
    hijau = rng(s["Hijau_min"], s["Hijau_max"])
    biru = rng(s["Biru_min"], s["Biru_max"])

    alat = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    hasil = []
    for m in (merah, hijau, biru):
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, alat)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, alat, iterations=2)
        hasil.append(m)
    return hasil


def kontur_terbesar(mask):
    kontur, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    kontur = [k for k in kontur if cv2.contourArea(k) >= UKURAN_MINIMAL]
    return max(kontur, key=cv2.contourArea, default=None)


def seberapa_bulat(k):
    keliling = cv2.arcLength(k, True)
    return 4 * np.pi * cv2.contourArea(k) / (keliling ** 2) if keliling else 0


def seberapa_kotak(k):
    (_, _), (w, h), _ = cv2.minAreaRect(k)   # tahan walau kotaknya miring
    return cv2.contourArea(k) / (w * h) if w * h else 0


def deteksi(frame, s):
    """Return (dict nama -> kontur, daftar mask)."""
    hsv = cv2.cvtColor(cv2.GaussianBlur(frame, (7, 7), 0), cv2.COLOR_BGR2HSV)
    m_merah, m_hijau, m_biru = buat_mask(hsv, s)
    hasil = {}

    k = kontur_terbesar(m_merah)
    if k is not None and seberapa_bulat(k) >= KEBULATAN_MINIMAL:
        hasil["merah"] = k

    k = kontur_terbesar(m_hijau)
    if k is not None and seberapa_bulat(k) >= KEBULATAN_MINIMAL:
        hasil["hijau"] = k

    k = kontur_terbesar(m_biru)
    if k is not None and seberapa_kotak(k) >= KOTAK_MINIMAL:
        hasil["biru"] = k

    return hasil, (m_merah, m_hijau, m_biru)


def main():
    buat_slider()
    cap = cv2.VideoCapture(0)
    warna = {"merah": (0, 0, 255), "hijau": (0, 255, 0), "biru": (255, 0, 0)}

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t, l = frame.shape[:2]
        frame = cv2.resize(frame, (640, int(t * 640 / l)))

        hasil, masks = deteksi(frame, baca_slider())
        for nama, k in hasil.items():
            x, y, w, h = cv2.boundingRect(k)
            cv2.rectangle(frame, (x, y), (x + w, y + h), warna[nama], 2)
            cv2.putText(frame, nama, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, warna[nama], 2)

        print(list(hasil.keys()))
        cv2.imshow("Hasil", frame)
        cv2.imshow("Mask merah", masks[0])
        cv2.imshow("Mask hijau", masks[1])
        cv2.imshow("Mask biru", masks[2])
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()