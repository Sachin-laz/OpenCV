import cv2
from imageRead import image

def resize_by_width(image, new_width):
    height, width = image.shape[:2]
    aspectRatio = width/height
    new_height = int(new_width/aspectRatio)
    resized = cv2.resize(image, (new_width, new_height))

    return resized
resizedImage = resize_by_width(image, 1080)

cv2.imshow("resizedImage",resizedImage)

cv2.waitKey(0)
cv2.destroyAllWindows()