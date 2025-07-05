import os
import cv2
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def identify_number(model, image):
    image = image/255
    image_resize = cv2.resize(image, (28,28)) 
    image_resize_2 = image_resize.reshape(1,28,28,1)
    model_pred = np.argmax(model.predict(image_resize_2),axis=1)
    return model_pred[0]

def extract_number(model,sudoku):
    sudoku = cv2.resize(sudoku, (450,450))
    grid = np.zeros([9,9])
    for i in range(9):
        for j in range(9):
            image = sudoku[i*50:(i+1)*50,j*50:(j+1)*50]
            if image.sum() > 79000:
                grid[i][j] = identify_number(model,image)
            else:
                grid[i][j] = 0
    return grid.astype(int)