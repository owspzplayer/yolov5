import cv2
import detectout
from detectout import detecto
path = 'C://Users//asus4//Source//Repos//yolov5-owspz//data//images//zidane.jpg'
img = cv2.imread(path)

a=detecto(img)
print("*****************")
print(a[0]['class'])