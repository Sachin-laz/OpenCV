from blackPixel import path
import cv2

image = cv2.imread(f"{path}/Sample.jpg")


height = image.shape[0]
width = image.shape[1]

blackPixelCount = 0

for i in range(height):
    for j in range(width):
        pixel = image[i, j]
        if pixel[0] + pixel[1] + pixel[2] == 0:

            blackPixelCount += 1

print(f"Total Black Pixel Count : {blackPixelCount} ")
