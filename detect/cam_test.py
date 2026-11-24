import cv2

cap = cv2.VideoCapture(0)  # 0 = kamera pertama
if not cap.isOpened():
    print("Kamera tidak bisa dibuka")
    raise SystemExit

while True:
    ok, frame = cap.read()
    if not ok:
        print("Gagal ambil frame")
        break

    cv2.imshow("Kamera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):  # tekan q untuk keluar
        break

cap.release()
cv2.destroyAllWindows()