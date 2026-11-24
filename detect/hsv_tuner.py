import cv2
import numpy as np

def nothing(x):
    pass

cv2.namedWindow("Slider")
cv2.createTrackbar("H min", "Slider", 0, 179, nothing)
cv2.createTrackbar("H max", "Slider", 179, 179, nothing)
cv2.createTrackbar("S min", "Slider", 0, 255, nothing)
cv2.createTrackbar("S max", "Slider", 255, 255, nothing)
cv2.createTrackbar("V min", "Slider", 0, 255, nothing)
cv2.createTrackbar("V max", "Slider", 255, 255, nothing)

cap = cv2.VideoCapture(0)
while True:
    ok, frame = cap.read()
    if not ok:
        break

    hsv = cv2.cvtColor(cv2.GaussianBlur(frame, (7, 7), 0), cv2.COLOR_BGR2HSV)
    low = np.array([cv2.getTrackbarPos("H min", "Slider"),
                    cv2.getTrackbarPos("S min", "Slider"),
                    cv2.getTrackbarPos("V min", "Slider")])
    high = np.array([cv2.getTrackbarPos("H max", "Slider"),
                     cv2.getTrackbarPos("S max", "Slider"),
                     cv2.getTrackbarPos("V max", "Slider")])

    mask = cv2.inRange(hsv, low, high)
    hasil = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("Asli", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Hasil", hasil)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("p"):
        print("low :", low.tolist(), " high:", high.tolist())
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()