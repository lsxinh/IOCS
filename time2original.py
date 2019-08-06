# python time2original.py
# cd 'D:/HOMEWORK/rslab/IOCS_2019/code'
# This file is used to compute how long each pixel takes to their original state
## read images
import numpy as np
import spectral.io.envi as envi
from scipy.optimize import fsolve
from spectral import *
import os
import shutil
import matplotlib.pyplot as plt
import cv2

## read images
img= envi.open('D:/HOMEWORK/rslab/IOCS_2019/regression/img_matrix2.hdr')
img_matrix = img.load()
img_matrix = img_matrix.read_bands(range(0,img_matrix.shape[2]))
## read_50
a_50 = envi.open('D:/HOMEWORK/rslab/IOCS_2019/regression/a.hdr')
b_50 = envi.open('D:/HOMEWORK/rslab/IOCS_2019/regression/b.hdr')
c_50 = envi.open('D:/HOMEWORK/rslab/IOCS_2019/regression/c.hdr')
a_50 = a_50.load()
a_50 = a_50.read_band(0)
b_50 = b_50.load()
b_50 = b_50.read_band(0)
c_50 = c_50.load()
c_50 = c_50.read_band(0)
## read statistic result
max_variation = envi.open('D:/HOMEWORK/rslab/IOCS_2019/regression/max_difference.hdr')
max_variation = max_variation.load()
max_variation = max_variation.read_band(0)
## read 4-days mean image
init_state = envi.open('D:/HOMEWORK/rslab/IOCS_2019/regression/0804_0807_mean.hdr')
init_state = init_state.load()
init_state = init_state.read_band(0)
## read time_matrix (hours)
t_matrix = [0,1,2,3,4,5,6,7,24,25,26,27,28,29,30,31,48,49,50,51,52,53,54,55,72,73,74,75,76,77,78,79,192,193,194,195,196,197,198,199,
216,217,218,219,220,221,222,223,240,241,242,243,244,245,246,247,264,265,266,267,268,269,270,271]
## def the function for fsolve
def f(t,p):
    a=p[0]
    b=p[1]
    c = p[2]
    threshold = p[3]
    return a*np.exp(-b*t)+c-threshold
def compute_t(a_50,b_50,c_50,img_matrix,t_matrix,init_state):
    k = 0.1
    t_method = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    t_max = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    t_decay = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    ss_max = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))

    for i in range(0,img_matrix.shape[0]):
        for j in range(0,img_matrix.shape[1]):
            threshold = k*max_variation[i][j] + c_50[i][j]
            if b_50[i][j]!=0:
                t0 = fsolve(f,0,[a_50[i][j],b_50[i][j],c_50[i][j],threshold])
                t_method[i][j] = t0
                indexx = np.argmax(img_matrix[i][j])
                t_max[i][j] = t_matrix[indexx]
                ss_max[i][j] = img_matrix[i][j][indexx]

                t_decay[i][j] = t_method[i][j] - t_max[i][j]
            if t0 <=0 or t_decay[i][j]<0:
                t_method[i][j] = -1
                t_decay[i][j] = -1
    # envi.save_image('t_method1_01.hdr', t_method)
    # envi.save_image('t_max1_01.hdr', t_max)
    # envi.save_image('t_decay1_01.hdr', t_decay)
    envi.save_image('ss_max.hdr', ss_max)

    
def compute_t2(a_50,b_50,c_50,img_matrix,t_matrix,init_state):
    # threshold is based on 4 days mean
    k = 0.1
    t_method = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    t_max = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    t_decay = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    for i in range(0,img_matrix.shape[0]):
        for j in range(0,img_matrix.shape[1]):
            threshold = k*max_variation[i][j] + init_state[i][j]
            if b_50[i][j]!=0:
                t0 = fsolve(f,0,[a_50[i][j],b_50[i][j],c_50[i][j],threshold])
                t_method[i][j] = t0
                indexx = np.argmax(img_matrix[i][j])
                t_max[i][j] = t_matrix[indexx]
                t_decay[i][j] = t_method[i][j] - t_max[i][j]
            if t0 <=0 or t_decay[i][j]<0:
                t_method[i][j] = -1
                t_decay[i][j] = -1
    envi.save_image('t_method2_01.hdr', t_method)
    envi.save_image('t_max2_01.hdr', t_max)
    envi.save_image('t_decay2_01.hdr', t_decay)

def compute_t3(a_50,b_50,c_50,img_matrix,t_matrix,init_state):
    # threshold is based on 4 days mean plus a constant
    t_method = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    t_max = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    t_decay = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    for i in range(0,img_matrix.shape[0]):
        for j in range(0,img_matrix.shape[1]):
            threshold = 0.5 + init_state[i][j]
            if b_50[i][j]!=0:
                t0 = fsolve(f,0,[a_50[i][j],b_50[i][j],c_50[i][j],threshold])
                t_method[i][j] = t0
                indexx = np.argmax(img_matrix[i][j])
                t_max[i][j] = t_matrix[indexx]
                t_decay[i][j] = t_method[i][j] - t_max[i][j]
            if t0 <=0 or t_decay[i][j]<0:
                t_method[i][j] = -1
                t_decay[i][j] = -1
    envi.save_image('t_method3_05.hdr', t_method)
    envi.save_image('t_max3_05.hdr', t_max)
    envi.save_image('t_decay3_05.hdr', t_decay)
def generate_max(a_50,b_50,c_50,img_matrix,t_matrix,init_state):
    t_max = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    ss_max = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))
    max_avg = np.zeros((img_matrix.shape[0], img_matrix.shape[1]))

    for i in range(0,img_matrix.shape[0]):
        for j in range(0,img_matrix.shape[1]):
            
            indexx = np.argmax(img_matrix[i][j])
            t_max[i][j] = t_matrix[indexx]
            ss_max[i][j] = img_matrix[i][j][indexx]
            max_avg[i][j] = ss_max[i][j]- init_state[i][j]

    envi.save_image('t_max.hdr', t_max)
    # envi.save_image('ss_max.hdr', ss_max)
    # envi.save_image('max-avg.hdr', max_avg)

# compute_t2(a_50,b_50,c_50,img_matrix,t_matrix,init_state)

generate_max(a_50,b_50,c_50,img_matrix,t_matrix,init_state)