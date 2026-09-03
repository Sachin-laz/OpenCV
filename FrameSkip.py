"""
======================================================================
Created By      : Sachin QA
Script Name     : Frame Skip Detection
Purpose         : Detect and report possible frame skips during
                  continuous camera streaming without affecting
                  the live preview.

Description:
    This script performs parallel frame-skip verification while the
    camera stream is running.

How It Works:
    1. The camera continuously captures frames using OpenCV.
    2. Each successfully captured frame is assigned a frame number.
    3. A human-readable timestamp is recorded for every frame.
    4. A monotonic timestamp is also recorded for accurate timing
       calculations.
    5. The frame is immediately displayed in the live preview.
    6. Only the frame number and timing information are sent to a
       background verification queue.
    7. A separate background thread compares the current frame
       timestamp with the previous frame timestamp.
    8. The time gap between the two frames is calculated.
    9. If the gap is greater than the configured skip threshold,
       a possible frame-skip event is reported.
   10. The previous frame and timestamp, current frame and timestamp,
       actual gap and expected gap are displayed.

Frame Skip Verification:
    For a 30 FPS stream, the expected frame interval is approximately
    0.033333 seconds.

    If the detected gap is greater than the configured threshold,
    the script reports:

        Previous Frame
        Previous Timestamp
        Current Frame
        Current Timestamp
        Actual Gap
        Expected Gap
        Threshold

Parallel Verification:
    The live camera preview runs in the main thread while frame-skip
    verification runs in a separate background thread.

    Only lightweight timing information is placed into the queue.
    The actual image is not copied or processed by the verification
    thread.

Queue Handling:
    A non-blocking queue is used so that the verification thread
    cannot hold or block the camera preview.

    If the queue is full, the timing information is dropped for
    verification and the event is counted as a queue drop.

Result:
    The script reports the total captured frames, possible frame
    skips, runtime camera read errors and queue drops.

Stopping:
    Press 'Q' in the live preview window to stop the test cleanly.

======================================================================
"""


import cv2
import threading
import queue
import time
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA = "/dev/video0"

QUEUE_SIZE = 5

EXPECTED_FPS = 30

EXPECTED_INTERVAL = 1.0 / EXPECTED_FPS

# Consider a gap greater than 2x expected interval
SKIP_THRESHOLD = EXPECTED_INTERVAL * 2


# ============================================================
# QUEUE + STOP EVENT
# ============================================================

check_queue = queue.Queue(maxsize=QUEUE_SIZE)

stop_event = threading.Event()


# ============================================================
# COUNTERS
# ============================================================

frame_count = 0
skip_count = 0
read_errors = 0
queue_drops = 0


# ============================================================
# FRAME SKIP CHECKING THREAD
# ============================================================

def check_frame_skip():

    global skip_count

    previous_frame = None
    previous_timestamp = None
    previous_monotonic = None

    while not stop_event.is_set():

        try:

            frame_number, timestamp, monotonic_time = (
                check_queue.get(timeout=0.5)
            )

        except queue.Empty:

            continue

        try:

            # ------------------------------------------------
            # Compare current frame with previous frame
            # ------------------------------------------------

            if previous_timestamp is not None:

                time_difference = (
                    monotonic_time -
                    previous_monotonic
                )

                # ------------------------------------------------
                # POSSIBLE FRAME SKIP
                # ------------------------------------------------

                if time_difference > SKIP_THRESHOLD:

                    skip_count += 1

                    print(
                        "\n"
                        "============================================================\n"
                        "[FRAME SKIP POSSIBLE]\n"
                        "============================================================\n"
                        f"Previous Frame : {previous_frame}\n"
                        f"Previous Time  : "
                        f"{previous_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')}\n"
                        "\n"
                        f"Current Frame  : {frame_number}\n"
                        f"Current Time   : "
                        f"{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')}\n"
                        "\n"
                        f"Gap            : {time_difference:.6f} sec\n"
                        f"Expected Gap   : {EXPECTED_INTERVAL:.6f} sec\n"
                        f"Threshold      : {SKIP_THRESHOLD:.6f} sec\n"
                        "============================================================\n"
                    )

            # ------------------------------------------------
            # Store current frame information
            # for next comparison
            # ------------------------------------------------

            previous_frame = frame_number
            previous_timestamp = timestamp
            previous_monotonic = monotonic_time

        finally:

            check_queue.task_done()


# ============================================================
# START CHECKING THREAD
# ============================================================

thread = threading.Thread(
    target=check_frame_skip,
    daemon=True
)

thread.start()


# ============================================================
# OPEN CAMERA
# ============================================================

cap = cv2.VideoCapture(
    CAMERA,
    cv2.CAP_V4L2
)

if not cap.isOpened():

    print(f"ERROR: Cannot open {CAMERA}")

    stop_event.set()

    exit(1)


# ============================================================
# START MESSAGE
# ============================================================

print("=" * 60)
print(" FRAME SKIP PARALLEL VERIFICATION")
print("=" * 60)

print(f"Camera       : {CAMERA}")
print(f"Expected FPS : {EXPECTED_FPS}")
print(f"Expected Gap : {EXPECTED_INTERVAL:.6f} sec")
print(f"Skip Gap     : {SKIP_THRESHOLD:.6f} sec")
print(f"Queue Size   : {QUEUE_SIZE}")

print("Press Q to stop")

print("=" * 60)


# ============================================================
# CAMERA + LIVE PREVIEW
# ============================================================

try:

    while not stop_event.is_set():

        ret, frame = cap.read()


        # ----------------------------------------------------
        # CAMERA READ FAILURE
        # ----------------------------------------------------

        if not ret or frame is None:

            # Don't report an error during shutdown
            if stop_event.is_set():
                break

            read_errors += 1

            print("[CAMERA READ ERROR]")

            continue


        frame_count += 1


        # ----------------------------------------------------
        # TIMESTAMPS
        # ----------------------------------------------------

        # Human-readable timestamp
        timestamp = datetime.now()

        # Accurate interval calculation
        monotonic_time = time.monotonic()


        # ----------------------------------------------------
        # LIVE PREVIEW
        # ----------------------------------------------------

        cv2.imshow(
            "Live Preview",
            frame
        )


        # ----------------------------------------------------
        # SEND ONLY TIMING DATA TO CHECKER
        #
        # No frame.copy() here.
        # This keeps verification lightweight.
        # ----------------------------------------------------

        try:

            check_queue.put_nowait(
                (
                    frame_count,
                    timestamp,
                    monotonic_time
                )
            )

        except queue.Full:

            # Do NOT block camera/preview
            queue_drops += 1


        # ----------------------------------------------------
        # PRESS Q TO EXIT
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            print("\nQ pressed. Stopping...")

            stop_event.set()

            break


except KeyboardInterrupt:

    print("\nCtrl+C pressed. Stopping...")

    stop_event.set()


finally:

    # --------------------------------------------------------
    # CLEAN SHUTDOWN
    # --------------------------------------------------------

    stop_event.set()

    cap.release()

    cv2.destroyAllWindows()

    thread.join(timeout=2)


# ============================================================
# FINAL RESULT
# ============================================================

print("=" * 60)
print(" TEST COMPLETED")
print("=" * 60)

print(f"Total frames        : {frame_count}")
print(f"Possible skips      : {skip_count}")
print(f"Runtime read errors : {read_errors}")
print(f"Queue drops         : {queue_drops}")

print("=" * 60)