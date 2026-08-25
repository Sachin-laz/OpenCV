from imageRead import path
import cv2

image = cv2.imread(f"{path}/single_frame_130.jpg")

print("Blue :", image[100, 200, 0])
print("Green :", image[100, 200, 1])
print("Red :", image[100, 200, 2])

blue = image[:, :, 0]

print(blue.shape)
print("Top-left blue value:", blue[0, 0])
print("Maximum blue:", blue.max())
print("Minimum blue:", blue.min())