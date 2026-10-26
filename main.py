# cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

import cv2
import numpy as np
import serial
import time

# --- ARDUINO SETUP ---
try:
    arduino = serial.Serial(port='COM16', baudrate=9600, timeout=0.1)
    time.sleep(2)
    print("Arduino Connected")
except:
    arduino = None
    print("Arduino NOT connected.")

def nothing(x):
    pass

# Setup Tuning Window
cv2.namedWindow("Tuning")
cv2.resizeWindow("Tuning", 400, 400)

# Default values tuned for "Plant Green"
cv2.createTrackbar("LH", "Tuning", 35, 179, nothing)
cv2.createTrackbar("LS", "Tuning", 40, 255, nothing)    
cv2.createTrackbar("LV", "Tuning", 40, 255, nothing)
cv2.createTrackbar("UH", "Tuning", 85, 179, nothing)
cv2.createTrackbar("US", "Tuning", 255, 255, nothing)
cv2.createTrackbar("UV", "Tuning", 255, 255, nothing)

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

while True:

    ret, frame = cap.read()

    if not ret:
        break
    
    frame = cv2.flip(frame, 1)

    height, width = frame.shape[:2]

    screen_center = width // 2
    
    # --- 1. PRE-PROCESSING (REMOVE NOISE) ---
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)

    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # --- 2. GET COLOR RANGES ---
    lh = cv2.getTrackbarPos("LH", "Tuning")
    ls = cv2.getTrackbarPos("LS", "Tuning")
    lv = cv2.getTrackbarPos("LV", "Tuning")

    uh = cv2.getTrackbarPos("UH", "Tuning")
    us = cv2.getTrackbarPos("US", "Tuning")
    uv = cv2.getTrackbarPos("UV", "Tuning")

    # Hyacinth Range (Green)
    lower_green = np.array([lh, ls, lv])
    upper_green = np.array([uh, us, uv])
    
    # Obstacle Range (Red)
    lower_red = np.array([0, 150, 50])
    upper_red = np.array([10, 255, 255])

    # --- 3. CREATE MASKS & CLEAN UP ---
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    mask_red = cv2.inRange(hsv, lower_red, upper_red)

    kernel = np.ones((5, 5), np.uint8)

    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)

    # --- 4. FIND & DRAW HYACINTH (GREEN) ---
    contours_hy, _ = cv2.findContours(
        mask_green,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    command = 's'

    target_x = -1

    for cnt in contours_hy:

        area = cv2.contourArea(cnt)

        if area > 3000:

            x, y, w, h = cv2.boundingRect(cnt)
            
            # Ignore top 40%
            if y < (height * 0.4):
                continue

            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.putText(
                frame,
                "WATER HYACINTH",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            
            target_x = x + w // 2

            break

    # --- 5. FIND & DRAW OBSTACLE (RED) ---
    contours_obs, _ = cv2.findContours(
        mask_red,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    obstacle_detected = False

    for cnt in contours_obs:

        if cv2.contourArea(cnt) > 2000:

            x, y, w, h = cv2.boundingRect(cnt)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)

            cv2.putText(
                frame,
                "OBSTACLE!!",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )

            obstacle_detected = True

            command = 's'

            break

    # --- 6. NAVIGATION LOGIC ---
    if not obstacle_detected and target_x != -1:

        if target_x < screen_center - 60:

            command = 'l'

        elif target_x > screen_center + 60:

            command = 'r'

        else:

            command = 'f'

    # --- 7. UI OVERLAY ---
    cv2.line(
        frame,
        (screen_center, 0),
        (screen_center, height),
        (255, 255, 255),
        1
    )

    cv2.line(
        frame,
        (0, int(height*0.4)),
        (width, int(height*0.4)),
        (200, 200, 200),
        1
    )

    cv2.putText(
        frame,
        "IGNORE ZONE",
        (10, int(height*0.38)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (200, 200, 200),
        1
    )

    # Show Command
    cv2.putText(
        frame,
        f"SENDING: {command}",
        (width-220, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    # ---------- FIXED SERIAL SEND ----------
    if arduino:

        arduino.write((command + '\n').encode())

        print("Sent:", command)

    cv2.imshow("Detection System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

if arduino:
    arduino.close()

cv2.destroyAllWindows()