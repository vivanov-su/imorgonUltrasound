import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np
import glob
import time
import math
from scipy import ndimage

threshold = 0.25
reader = easyocr.Reader(['en'], gpu=False, detector = 'dbnet18')
start_point = (0,650)
end_point = (1000, 790)

right_side1 = (0, 0)
right_side2 = (370, 550)

rows = 1
columns = 3
plt.rcParams["figure.figsize"] = [10.00, 7.00]
plt.rcParams["figure.autolayout"] = True

folder_dir = "imgFolder/imgFolder/Philips/*.*"
for images in glob.glob(folder_dir):
    image = cv2.imread(images)

    roi1 = image[start_point[1]:end_point[1], start_point[0]:end_point[0]]
    roi2 = image[right_side1[1]:right_side2[1], right_side1[0]:right_side2[0]]
    startTime = time.time()
    text = reader.readtext(roi1, detail = 1, paragraph = True, x_ths = 1, y_ths = 1, batch_size = 3)
    text2 = reader.readtext(roi2, detail = 1, paragraph = True, x_ths = 1, y_ths = 1, batch_size = 3)
    print("Analysis time: ", time.time() - startTime, " seconds")

    with open("output2.txt", 'a') as f:
        for t in text:
            bbox, text = t
            cv2.rectangle(roi1, bbox[0], bbox[2], (0, 255, 255), 5)
            cv2.rectangle(image, start_point, end_point, (0, 0, 255), 5)
            cv2.rectangle(image, right_side1, right_side2, (0, 0, 255), 5)
            print(text)
            f.write(f"{str(text)}\n")
        for t in text2:
            bbox, text2 = t
            cv2.rectangle(roi2, bbox[0], bbox[2], (0, 255, 255), 5)
            print(text2)
            f.write(f"{str(text2)}\n")
        f.close()
    
    #image displays
    plt.subplot(1, 3, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGBA))

    plt.subplot(1, 3, 2)
    plt.imshow(cv2.cvtColor(roi1, cv2.COLOR_BGR2RGBA))

    plt.subplot(1, 3, 3)
    plt.imshow(cv2.cvtColor(roi2, cv2.COLOR_BGR2RGBA))

    plt.show()