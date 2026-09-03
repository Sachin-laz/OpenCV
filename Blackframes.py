"""
======================================================================
Created By      : Sachin QA
Script Name     : Black Frame Detection
Purpose         : Detect and report black frames during camera
                  streaming without affecting the live preview.

Description:
    This script performs parallel black-frame verification while the
    camera stream is running.

How It Works:
    1. The camera continuously captures frames using OpenCV.
    2. The captured frame is immediately displayed in the live preview.
    3. A copy of the frame is sent to a queue for verification.
    4. A separate background thread reads frames from the queue.
    5. The frame is converted from BGR to grayscale.
    6. The average brightness of the frame is calculated.
    7. The percentage of dark pixels is also calculated.
    8. If the brightness and dark-pixel conditions satisfy the
       configured threshold, the frame is identified as a black frame.
    9. The detected black frame is saved for further analysis.
   10. The frame number, timestamp, brightness and dark-pixel
       percentage are printed in the terminal.

Parallel Verification:
    The live camera preview and black-frame verification run
    independently.

    Camera / Preview:
        The main thread handles camera capture and live preview.

    Verification:
        A background thread handles black-frame analysis.

    A non-blocking queue is used so that the verification process
    does not wait for or block the live camera preview.

Queue Handling:
    If the verification queue is full, the frame is skipped only
    for verification. The camera preview is not blocked.

Result:
    The script provides the total number of captured frames,
    detected black frames and camera read errors after the test.

Stopping:
    Press 'Q' in the live preview window to stop the test cleanly.

======================================================================
"""



import cv2
import threading
import queue
import numpy as np
from datetime import datetime
import os

CAMERA = "/dev/video0"

QUEUE_SIZE = 5
BLACK_THRESHOLD = 10.0

SAVE_DIR = "black_frames"
os.makedirs(SAVE_DIR, exist_ok=True)

check_queue = queue.Queue(maxsize=QUEUE_SIZE)
stop_event = threading.Event()

frame_count = 0
black_count = 0
read_errors = 0


def check_black_frames():

    global black_count

    while not stop_event.is_set():

        try:
            frame_number, frame, timestamp = check_queue.get(
                timeout=0.5
            )

        except queue.Empty:
            continue

        try:

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            brightness = np.mean(gray)

            dark_pixels = np.sum(gray < 20)
            total_pixels = gray.size

            dark_percent = (
                dark_pixels / total_pixels
            ) * 100


            # ------------------------------------------------
            # BLACK FRAME DETECTION
            # ------------------------------------------------

            if (
                brightness < BLACK_THRESHOLD
                and dark_percent > 95
            ):

                black_count += 1

                filename = os.path.join(
                    SAVE_DIR,
                    f"black_frame_{frame_number}_"
                    f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                )

                cv2.imwrite(
                    filename,
                    frame
                )

                print(
                    "\n[BLACK FRAME DETECTED]"
                    f"\nFrame       : {frame_number}"
                    f"\nTimestamp   : {timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')}"
                    f"\nBrightness  : {brightness:.2f}"
                    f"\nDark pixels : {dark_percent:.2f}%"
                    f"\nSaved       : {filename}\n"
                )

        finally:

            check_queue.task_done()


# ------------------------------------------------------------
# Start detector thread
# ------------------------------------------------------------

thread = threading.Thread(
    target=check_black_frames,
    daemon=True
)

thread.start()


# ------------------------------------------------------------
# Open camera
# ------------------------------------------------------------

cap = cv2.VideoCapture(
    CAMERA,
    cv2.CAP_V4L2
)

if not cap.isOpened():

    print(f"ERROR: Cannot open {CAMERA}")
    stop_event.set()
    exit(1)


print("=" * 60)
print(" BLACK FRAME PARALLEL VERIFICATION")
print("=" * 60)

print(f"Camera       : {CAMERA}")
print(f"Threshold    : {BLACK_THRESHOLD}")
print(f"Save folder  : {SAVE_DIR}")
print("Press Q to stop")
print("=" * 60)


try:

    while not stop_event.is_set():

        ret, frame = cap.read()

        if not ret or frame is None:

            if stop_event.is_set():
                break

            read_errors += 1

            print("[CAMERA READ ERROR]")

            continue


        frame_count += 1

        # Timestamp of the captured frame
        timestamp = datetime.now()


        # ----------------------------------------------------
        # Live preview
        # ----------------------------------------------------

        cv2.imshow(
            "Live Preview",
            frame
        )


        # ----------------------------------------------------
        # Send frame to detector
        # ----------------------------------------------------

        try:

            check_queue.put_nowait(
                (
                    frame_count,
                    frame.copy(),
                    timestamp
                )
            )

        except queue.Full:

            # Don't block live preview
            pass


        # ----------------------------------------------------
        # Q to stop
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):

            print("\nQ pressed. Stopping...")

            stop_event.set()

            break


except KeyboardInterrupt:

    stop_event.set()


finally:

    stop_event.set()

    cap.release()

    cv2.destroyAllWindows()

    thread.join(timeout=2)


print("=" * 60)
print(" TEST COMPLETED")
print("=" * 60)

print(f"Total frames        : {frame_count}")
print(f"Black frames        : {black_count}")
print(f"Runtime read errors : {read_errors}")

print("=" * 60)