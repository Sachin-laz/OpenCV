import cv2
from imageRead import path

image = cv2.imread(f"{path}/single_frame_130.jpg")

print(image.shape)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

print(gray.shape)

print(image[100,100])
print(gray[100,100])

cv2.imshow("Original", image)
cv2.imshow("Gray", gray)

cv2.waitKey(0)
cv2.destroyAllWindows()