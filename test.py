import serial
from array import array
from math import sin, pi
from random import random
import numpy as np 
from time import time
from collections import deque
import time
import struct


ser = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=0.1) #blocking reading because timeout=0
#ser.write(0xFFFFFFFF)
while True:
    
    def get_int():
        while ser.inWaiting() < 5:
            time.sleep(0.001)
        observation = int(struct.unpack('<I', ser.read(4))[0])
        ser.readline()
        return observation
    

    def get_float():
        while ser.inWaiting() < 5:
            time.sleep(0.001)
        observation = float(struct.unpack('<f', ser.read(4))[0])
        ser.readline()
        return observation
    
    print("odere ", get_int())
    print("accel ", get_float(), get_float(), get_float())
    print("angle ", get_float(), get_float(), get_float())
    print(ser.readline())
    time.sleep(0.5)