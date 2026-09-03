import cv2

path = "/home/qaasus2/OpenCV/refImage"
image = cv2.imread(f"{path}/single_frame_130.jpg")
if __name__ == "__main__":
    try:
        if image is None:
            print("FAIL: Image could not be loaded")
        else:
            print("Image Shape ", image.shape)
            print(f"Height of the Image : {image.shape[0]}")
            print(f"Width of the Image : {image.shape[1]}")
            print(f"Channels of the Image : {image.shape[2]}")

    except Exception as e:
        print(f"The Issue is : {e}")

    finally:
        print("Image Validation script is executed")

