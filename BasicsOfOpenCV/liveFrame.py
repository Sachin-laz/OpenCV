import cv2

# 1. Open the video source
# Use an integer (0, 1, 2) for local webcams
# Use a string path for files ("video.mp4") or streams ("rtsp://...")
cap = cv2.VideoCapture("/dev/video0") 

while True:
    # 2. Grab the latest individual frame
    # 'ret' is True if the frame was successfully read
    # 'frame' is the actual image array (NumPy matrix)
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame or video ended.")
        break

    # 3. Show the frame on your screen
    cv2.imshow('Live Camera Feed', frame)

    # Break loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 4. Release the camera hardware resource so other apps can use it
cap.release()
cv2.destroyAllWindows()
