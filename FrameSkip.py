import cv2
import threading
import queue
import os
import time

# Create folder
os.makedirs("frame_skips", exist_ok=True)

# Queue for checking
check_queue = queue.Queue(maxsize=5)


def check_frame_skip():

    previous_time = None

    while True:

        data = check_queue.get()

        if data is None:
            break

        frame_number, current_time, frame = data

        if previous_time is not None:

            time_difference = current_time - previous_time

            # Expected time for 30 FPS
            expected_time = 1 / 30

            # Check for large gap
            if time_difference > expected_time * 2:

                filename = (
                    f"frame_skips/"
                    f"skip_frame_{frame_number}_"
                    f"{int(time.time() * 1000)}.jpg"
                )

                cv2.imwrite(filename, frame)

                print(
                    f"FRAME SKIP POSSIBLE | "
                    f"Frame: {frame_number} | "
                    f"Gap: {time_difference:.3f}s"
                )

                print("FRAME SAVED:", filename)

        previous_time = current_time

        check_queue.task_done()


# Start background thread
thread = threading.Thread(
    target=check_frame_skip,
    daemon=True
)

thread.start()


# Open camera
cap = cv2.VideoCapture(0)

frame_number = 0

while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        continue

    frame_number += 1

    current_time = time.time()

    # LIVE PREVIEW
    cv2.imshow("Live Preview", frame)

    # Send frame to background checker
    try:
        check_queue.put_nowait(
            (frame_number, current_time, frame.copy())
        )
    except queue.Full:
        pass

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Stop thread
check_queue.put(None)

cap.release()
cv2.destroyAllWindows()
