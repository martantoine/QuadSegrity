import numpy as np
import random
from scipy.signal import butter, filtfilt
from collections import deque
import time

cutoff_freq = 0.5  # Cutoff frequency (Hz)
fs = 2
angle_x = deque([0]*100, maxlen=100)

def new_estimate(new_angle_acc_x):
    angle_x.append(angle_x[-1] + new_angle_acc_x / fs)

    #nyquist_freq = 0.5 * fs
    #normalized_cutoff_freq = cutoff_freq / nyquist_freq
    #b, a = butter(4, normalized_cutoff_freq, btype='lowpass')

    #angle_filtered = filtfilt(b, a, angle_x)

    return np.rad2deg(angle_x[-1])


for i in range(100):
    new_angle_acc_x = np.random.randn()
    
    angle = new_estimate(new_angle_acc_x)
    print(new_angle_acc_x, angle)
# Design the low-pass filter

# Print the filtered angle
#print(angle_filtered)