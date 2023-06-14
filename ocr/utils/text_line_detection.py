import math
import numpy as np
import cv2
from scipy.signal import argrelmin

def createKernel(kernelSize=9, sigma=4, theta=1.5):
    "create anisotropic filter kernel according to given parameters"
    assert kernelSize % 2 # must be odd size
    halfSize = kernelSize // 2

    kernel = np.zeros([kernelSize, kernelSize])
    sigmaX = sigma
    sigmaY = sigma * theta

    for i in range(kernelSize):
        for j in range(kernelSize):
            x = i - halfSize
            y = j - halfSize

            expTerm = np.exp(-x**2 / (2 * sigmaX) - y**2 / (2 * sigmaY))
            xTerm = (x**2 - sigmaX**2) / (2 * math.pi * sigmaX**5 * sigmaY)
            yTerm = (y**2 - sigmaY**2) / (2 * math.pi * sigmaY**5 * sigmaX)

            kernel[i, j] = (xTerm + yTerm) * expTerm

    kernel = kernel / np.sum(kernel)
    return kernel

def applySummFunctin(img):
    res = np.sum(img, axis = 0)    #  summ elements in columns
    return res

def normalize(img):
    (m, s) = cv2.meanStdDev(img)
    m = m[0][0]
    s = s[0][0]
    img = img - m
    img = img / s if s>0 else img
    return img

def smooth(x, window_len=11, window='hanning'):
    #     if x.ndim != 1:
    #         raise ValueError("smooth only accepts 1 dimension arrays.") 
    # if x.size < window_len:
    #     raise ValueError("Input vector needs to be bigger than window size.") 
    if window_len<3:
        return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'") 
    s = np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    else:
        w = eval('np.'+window+'(window_len)')

    y = np.convolve(w/w.sum(),s,mode='valid')
    return y

def get_line_coordinate(text, blanks):
    x1 = 0
    w = text.shape[1]
    y1 = 0
    lines = []
    for i, blank in enumerate(blanks):
        y2 = blank
        h  = y2-y1
        lines.append((x1, y1, w, h))
        y1 = blank
    return lines

def text_line_detection(img_array, min_line_height):
    img_copy = img_array.copy()
    # Convert color image to gray image
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    # Rotate image
    img_array = np.transpose(img_array)
    # Filtering image
    imgFiltered1 = cv2.filter2D(img_array, -1, createKernel(), borderType=cv2.BORDER_REPLICATE)
    # Normalize image
    img_array = normalize(imgFiltered1)
    # Get mean and standard deviation
    summ = applySummFunctin(img_array)
    smoothed = smooth(summ, 35)
    mins = argrelmin(smoothed, order=2)
    arr_mins = np.array(mins)
    coordinate = get_line_coordinate(img_copy, arr_mins[0])
    new_coordinate = []
    # post process line (if there is only one lines, use whole image, otherwise, use postprocess coordinate)
    for coord in coordinate:
        y = coord[1]
        h = coord[3]
        if h>min_line_height and y<img_copy.shape[0]:
            new_coordinate.append(coord)
    if len(new_coordinate)==1:
        w = img_copy.shape[1]
        h = img_copy.shape[0]
        return [[0, 0, w, h]]
    else:
        return new_coordinate
