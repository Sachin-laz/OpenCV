import cv2
import threading
import queue
import numpy as np
import os
import time

# Create folder
os.makedirs("black_frames", exist_ok=True)

# Queue for checking frames
check_queue = queue.Queue(maxsize=5)


def check_black_frames():

    while True:

        frame = check_queue.get()

        if frame is None:
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate brightness
        brightness = np.mean(gray)

        # Check if frame is black
        if brightness < 10:

            filename = f"black_frames/black_{int(time.time() * 1000)}.jpg"

            cv2.imwrite(filename, frame)

            print("BLACK FRAME SAVED:", filename)

        check_queue.task_done()


# Start background thread
thread = threading.Thread(
    target=check_black_frames,
    daemon=True
)

thread.start()


# Open camera
cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        continue

    # LIVE PREVIEW
    cv2.imshow("Live Preview", frame)

    # Send copy to background checker
    try:
        check_queue.put_nowait(frame.copy())
    except queue.Full:
        pass

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Stop thread
check_queue.put(None)

cap.release()
cv2.destroyAllWindows()
