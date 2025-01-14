import cv2
import time, math, numpy as np
import HandTrackingModule as htm
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize webcam settings
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)  # Use the default webcam
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
detector = htm.handDetector(maxHands=1, detectionCon=0.85, trackCon=0.8)

# Audio setup (volume control)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume.iid, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()  # (-63.5, 0.0, 0.5) min max

minVol = -30
maxVol = volRange[1]

hmin = 50
hmax = 200
volBar = 400
volPer = 0
vol = 0
color = (0, 215, 255)

tipIds = [4, 8, 12, 16, 20]
mode = ''
active = 0

pyautogui.FAILSAFE = False

# Create a black borderless window for OpenCV
cv2.namedWindow("Gesture Control", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Gesture Control", cv2.WND_PROP_TOPMOST, 1)  # Always on top
cv2.resizeWindow("Gesture Control", 360, 240)  # Resize window to 360x240

# Function to move the window to the bottom-left corner
def move_window_to_bottom_left():
    screen_width, screen_height = pyautogui.size()
    cv2.moveWindow("Gesture Control", 0, screen_height - 240)  # Bottom-left corner

move_window_to_bottom_left()

# Define the putText function
def putText(mode, loc=(250, 450), color=(0, 255, 255)):
    cv2.putText(img, str(mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, color, 3)


# Adding horizontal scrolling and click functionality
last_x, last_y = 0, 0  # Variables to track last known hand position for horizontal scroll

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    fingers = []

    if len(lmList) != 0:
        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0 - 1]][1]:
            if lmList[tipIds[0]][1] >= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        elif lmList[tipIds[0]][1] < lmList[tipIds[0 - 1]][1]:
            if lmList[tipIds[0]][1] <= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        if (fingers == [0, 0, 0, 0, 0]) & (active == 0):
            mode = 'N'
        elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (active == 0):
            mode = 'Scroll'
            active = 1
        elif (fingers == [1, 1, 0, 0, 0]) & (active == 0):
            mode = 'Zoom'  # Change from 'Volume' to 'Zoom'
            active = 1
        elif (fingers == [1, 1, 1, 1, 1]) & (active == 0):
            mode = 'Cursor'
            active = 1

    # Scroll mode
    if mode == 'Scroll':
        active = 1
        putText(mode)
        cv2.rectangle(img, (200, 410), (245, 460), (255, 255, 255), cv2.FILLED)
        if len(lmList) != 0:
            if fingers == [0, 1, 0, 0, 0]:
                putText(mode='U', loc=(200, 455), color=(0, 255, 0))
                pyautogui.scroll(300)

            if fingers == [0, 1, 1, 0, 0]:
                putText(mode='D', loc=(200, 455), color=(0, 0, 255))
                pyautogui.scroll(-300)
            elif fingers == [0, 0, 0, 0, 0]:
                active = 0
                mode = 'N'

    # Zoom mode (replaces Volume Mode)
    if mode == 'Zoom':
        active = 1
        putText(mode)
        if len(lmList) != 0:
            # Pinch gesture for zoom
            x1, y1 = lmList[4][1], lmList[4][2]  # Thumb position
            x2, y2 = lmList[8][1], lmList[8][2]  # Index finger position
            length = math.hypot(x2 - x1, y2 - y1)  # Calculate distance between thumb and index fingers

            # Zoom In/Out logic based on distance
            if length < 50:  # Threshold for zoom in/out
                cv2.circle(img, (x1, y1), 10, color, cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, color, cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), color, 3)

                zoomFactor = np.interp(length, [hmin, hmax], [0.0, 10.0])  # Zoom factor
                pyautogui.hotkey('ctrl', '-')  # Zoom in
            else:
                pyautogui.hotkey('ctrl', '+')  # Zoom out

            cv2.circle(img, (x1, y1), 10, color, cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, color, cv2.FILLED)

            # Exit Zoom mode if gesture [1, 1, 1, 0, 0] (thumb, index, middle extended, ring and little fingers not)
            if fingers == [1, 1, 1, 0, 0]:
                mode = 'N'  # Reset to No action mode
                active = 0
                putText(mode='Exited Zoom', loc=(250, 450), color=(0, 0, 255))  # Optional: Show exit message

    # Cursor mode
    if mode == 'Cursor':
        active = 1
        putText(mode)
        cv2.rectangle(img, (110, 20), (620, 350), (255, 255, 255), 3)

        if fingers[1:] == [0, 0, 0, 0]:  # thumb excluded
            active = 0
            mode = 'N'
        else:
            if len(lmList) != 0:
                x1, y1 = lmList[8][1], lmList[8][2]
                w, h = pyautogui.size()
                X = int(np.interp(x1, [110, 620], [w - 1 , 0]))
                Y = int(np.interp(y1, [20, 350], [0, h - 1]))
                cv2.circle(img, (lmList[8][1], lmList[8][2]), 7, (255, 255, 255), cv2.FILLED)
                cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 255, 0), cv2.FILLED)  # thumb

                if X % 2 != 0:
                    X = X - X % 2
                if Y % 2 != 0:
                    Y = Y - Y % 2

                pyautogui.moveTo(X, Y)

    # Click gesture: [0, 1, 1, 1, 0] ( index, middle, ring fingers and little finger extended, thumb finger not)
    if mode == 'N' and fingers == [0, 0, 0, 0, 1]:  # 1, 1, 1, 1, 0 gesture for click
        pyautogui.click()

    # Horizontal Scroll (if hand moves left or right)
    if mode == 'Cursor':
        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]  # Thumb
            x2, y2 = lmList[8][1], lmList[8][2]  # Index finger

            # Track horizontal movement
            if last_x != 0 and abs(x2 - last_x) > 50:
                if x2 - last_x > 0:  # Right movement
                    pyautogui.hscroll(-10)
                elif x2 - last_x < 0:  # Left movemenqt
                    pyautogui.hscroll(10)

            last_x = x2

    # Display the final frame
    cv2.imshow("Gesture Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
