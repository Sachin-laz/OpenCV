import cv2

path = "/home/qaasus2/OpenCV/refImage"

image = cv2.imread(f"{path}/single_frame_130.jpg")

pixelVal = image[100, 200]

print("Pixel One\n===========")
print("Blue : ",pixelVal[0])
print("Green : ",pixelVal[1])
print("Red : ",pixelVal[2])

pixelVal2 = image[500, 800]

print("\nPixel two\n===========")
print("Blue : ",pixelVal2[0])
print("Green : ",pixelVal2[1])
print("Red : ",pixelVal2[2])

print(f"Blue Difference : {abs(pixelVal[0]-pixelVal2[0])}")
print(f"Green Difference : {abs(pixelVal[1]-pixelVal2[1])}")
print(f"Red Difference : {abs(pixelVal[2]-pixelVal2[2])}")