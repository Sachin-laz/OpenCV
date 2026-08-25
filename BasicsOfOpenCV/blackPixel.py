import cv2

path = "/home/sxr19/OpenCV/RefImages/"

if __name__ == "__main__":
    image = cv2.imread(f"{path}/Sample.jpg")

    pixel = image[800, 700]

    color = ["Blue", "Green", "Red"]

    for i in range(len(pixel)):
        if pixel[i] == 0:
            print(f"Black Pixel Found on {color[i]}!!!")
            break
        print(f"{color[i]} : {pixel[i]}")

    if pixel[0] + pixel[1] + pixel[2] == 0:
        print("Black Pixel !!!")
    else:
        print("This is not a Black Pixel")

    height = image.shape[0]
    width = image.shape[1]

    for i in range(height):
        for j in range(width):
            pixel = image[i, j]
            if pixel[0] + pixel[1] + pixel[2] == 0:
                print(f"{i} : {j} This Pixel is a Black Pixel")
