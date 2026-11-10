import os
import cv2
FOLDER = os.path.dirname(os.path.abspath(__file__))
NAMES = ["other.jpg"]
#NAMES = ["me1.jpg", "me2.jpg", "me3.jpg", "me4.jpg", "me5.jpg", "v1.jpg", "v2.jpg", "v3.jpg"]

cam = cv2.VideoCapture(0)
i = 0
while i < len(NAMES):
    ok, frame = cam.read()
    if not ok:
        print("Camera not working")
        break
    shown = frame.copy()
    cv2.putText(shown, "SPACE = save " + NAMES[i] + "   ESC = quit",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Capture", shown)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:        # ESC
        break
    if key == 32:        # SPACE
        cv2.imwrite(os.path.join(FOLDER, NAMES[i]), frame)
        print("Saved", NAMES[i])
        i += 1

cam.release()
cv2.destroyAllWindows()