"""
======================================================================
Created By      : Sachin QA
Script Name     : Green Frame Detection
Purpose         : Detect and report green frames during continuous
                  camera streaming without affecting the live preview.

Description:
    This script performs parallel green-frame verification while the
    camera stream is running.

How It Works:
    1. The camera continuously captures frames using OpenCV.
    2. The captured frame is immediately displayed in the live preview.
    3. A copy of the frame is sent to a verification queue.
    4. A separate background thread reads frames from the queue.
    5. The frame is converted from BGR to HSV color space.
    6. A configured HSV range is used to identify green pixels.
    7. The percentage of green pixels in the frame is calculated.
    8. If the green-pixel percentage exceeds the configured threshold,
       the frame is identified as a possible green frame.
    9. The detected green frame is saved for further analysis.
   10. The frame number, timestamp, green-pixel percentage and saved
       image path are reported in the terminal.

Parallel Verification:
    The live camera preview and green-frame verification run
    independently.

    Camera / Preview:
        The main thread handles camera capture and live preview.

    Verification:
        A background thread handles green-frame analysis.

    A non-blocking queue is used so that the verification process
    does not block the live camera preview.

Queue Handling:
    If the verification queue is full, the frame is skipped only
    for verification. The camera preview continues without waiting
    for the verification thread.

Result:
    The script reports the total number of captured frames and
    detected green frames after the test.

Stopping:
    Press 'Q' in the live preview window to stop the test cleanly.

======================================================================
"""

#!/usr/bin/env python3

import cv2
import threading
import queue
import os
from datetime import datetime


CAMERA = "/dev/video0"

SAVE_DIR = "green_frames"

QUEUE_SIZE = 5

GREEN_PIXEL_PERCENT = 80.0

MAX_CONSECUTIVE_READ_FAILURES = 10


os.makedirs(SAVE_DIR, exist_ok=True)


# ------------------------------------------------------------
# Queue
# ------------------------------------------------------------

frame_queue = queue.Queue(maxsize=QUEUE_SIZE)

stop_event = threading.Event()


# ------------------------------------------------------------
# Counters
# ------------------------------------------------------------

frame_count = 0
green_count = 0
read_failures = 0


# ============================================================
# GREEN FRAME DETECTOR THREAD
# ============================================================

def green_frame_detector():

    global green_count

    while not stop_event.is_set():

        try:

            frame_number, frame = frame_queue.get(
                timeout=0.5
            )

        except queue.Empty:

            continue

        try:

            # Convert BGR -> HSV
            hsv = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2HSV
            )

            # Green range
            lower_green = (35, 80, 50)
            upper_green = (85, 255, 255)

            green_mask = cv2.inRange(
                hsv,
                lower_green,
                upper_green
            )

            # Count green pixels
            green_pixels = cv2.countNonZero(
                green_mask
            )

            total_pixels = (
                frame.shape[0] *
                frame.shape[1]
            )

            green_percent = (
                green_pixels /
                total_pixels
            ) * 100.0

            # ------------------------------------------------
            # GREEN FRAME
            # ------------------------------------------------

            if green_percent >= GREEN_PIXEL_PERCENT:

                green_count += 1

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )

                filename = os.path.join(
                    SAVE_DIR,
                    f"green_frame_"
                    f"{frame_number}_"
                    f"{timestamp}.jpg"
                )

                cv2.imwrite(
                    filename,
                    frame
                )

                print(
                    f"\n[GREEN FRAME DETECTED]"
                    f"\nFrame        : {frame_number}"
                    f"\nGreen        : {green_percent:.2f}%"
                    f"\nSaved        : {filename}\n"
                )

        finally:

            frame_queue.task_done()


# ============================================================
# CAMERA
# ============================================================

print("=" * 60)
print(" CAMERA GREEN FRAME PARALLEL VERIFICATION")
print("=" * 60)

print(f"Camera       : {CAMERA}")
print(f"Queue size   : {QUEUE_SIZE}")
print(f"Threshold    : {GREEN_PIXEL_PERCENT}%")
print(f"Save folder  : {SAVE_DIR}")
print(f"Read failure : {MAX_CONSECUTIVE_READ_FAILURES} consecutive")
print("Press Q to stop")
print("=" * 60)


# ------------------------------------------------------------
# Open camera using V4L2
# ------------------------------------------------------------

cap = cv2.VideoCapture(
    CAMERA,
    cv2.CAP_V4L2
)


if not cap.isOpened():

    print(f"ERROR: Cannot open {CAMERA}")
    exit(1)


print("Camera started")


# ------------------------------------------------------------
# Start detector
# ------------------------------------------------------------

detector_thread = threading.Thread(
    target=green_frame_detector,
    daemon=True
)

detector_thread.start()


# ============================================================
# CAMERA + LIVE PREVIEW
# ============================================================

consecutive_failures = 0

try:

    while not stop_event.is_set():

        ret, frame = cap.read()


        # ----------------------------------------------------
        # Camera read failure
        # ----------------------------------------------------

        if not ret or frame is None:

            consecutive_failures += 1
            read_failures += 1

            if consecutive_failures == 1:

                print(
                    "\n[CAMERA READ ERROR]"
                )

            elif (
                consecutive_failures
                == MAX_CONSECUTIVE_READ_FAILURES
            ):

                print(
                    "\n[CAMERA FAILURE]"
                )

                print(
                    f"Camera failed for "
                    f"{consecutive_failures} "
                    f"consecutive reads."
                )

                stop_event.set()

                break

            continue


        # ----------------------------------------------------
        # Successful frame
        # ----------------------------------------------------

        consecutive_failures = 0

        frame_count += 1


        # ----------------------------------------------------
        # Send frame to detector
        # ----------------------------------------------------

        try:

            frame_queue.put_nowait(
                (
                    frame_count,
                    frame.copy()
                )
            )

        except queue.Full:

            # Detector is slower than camera.
            # Do not block camera preview.
            pass


        # ----------------------------------------------------
        # Live preview
        # ----------------------------------------------------

        cv2.imshow(
            "Camera Preview",
            frame
        )


        # ----------------------------------------------------
        # Keyboard
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            print("\nQ pressed.")

            stop_event.set()

            break


except KeyboardInterrupt:

    print("\nCtrl+C pressed.")

    stop_event.set()


finally:

    print("\nStopping camera...")

    stop_event.set()

    # Release camera
    cap.release()

    # Destroy preview
    cv2.destroyAllWindows()

    # Wait for detector
    detector_thread.join(timeout=2)


# ============================================================
# RESULT
# ============================================================

print("=" * 60)
print(" TEST COMPLETED")
print("=" * 60)

print(f"Total frames       : {frame_count}")
print(f"Green frames       : {green_count}")
print(f"Read failures      : {read_failures}")
print(f"Consecutive failed : {consecutive_failures}")

print("=" * 60)
