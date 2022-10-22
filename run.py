import cv2
from detectout import run
path = r"C:\Users\asus4\source\repos\yolov5-owspz\runs\detect\exp30\中式米食丙級必勝精選.jpg"
#img = cv2.imread(path)

a=run(weights='best.pt',source=path)
print(a[0])