import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np
import glob
import time
import math
from scipy import ndimage
from tinydb import TinyDB, Query
import xlsxwriter
import json

threshold = 0.25
reader = easyocr.Reader(['en'], gpu=False, detector = 'dbnet18')
start_point = (0,650)
end_point = (850, 790)

right_side1 = (90, 0)
right_side2 = (370, 550)

rows = 1
columns = 3
plt.rcParams["figure.figsize"] = [10.00, 7.00]
plt.rcParams["figure.autolayout"] = True

folder_dir = "imgFolder/imgFolder/Philips/*.*"
workbook = xlsxwriter.Workbook('extractedText.xlsx')
worksheet = workbook.add_worksheet('Data')

row = 0
col = 0
User = Query()

startTime = time.time()
for images in glob.glob(folder_dir):
    image = cv2.imread(images)
    roi1 = image[start_point[1]:end_point[1], start_point[0]:end_point[0]]
    roi2 = image[right_side1[1]:right_side2[1], right_side1[0]:right_side2[0]]
    text = reader.readtext(roi1, detail = 0, paragraph = True, x_ths = 1, y_ths = 1, batch_size = 3)
    text2 = reader.readtext(roi2, detail = 0, paragraph = True, x_ths = 1, y_ths = 1, batch_size = 3)
    
    with open("output2.txt", 'a') as f:
        with open('db.json', 'r') as data:
            for t in text:
                #print(text)
                #f.write(f"{str(text)}\n")
                result1 = ''.join(text)
                worksheet.write(row, col, result1)
                row += 1
            for t in text2:
                #print(text2)
                #f.write(f"{str(text2)}\n")
                result2 = ''.join(text2)
                worksheet.write(row, col, result2)
                row += 1
        f.close()
        
worksheet.autofit()
workbook.close()

print("Analysis time: ", time.time() - startTime, " seconds")