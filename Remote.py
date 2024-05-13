import serial
import sys
import onnxruntime as ort
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np

COMMAND_BYTES_LEN = 4
OBSERVATION_BYTES_LEN = 24
onnx_path = "remote_model.onnx"

if len(sys.argv) < 2:
    print("Usage: python Remote.py <serial_port>")
    sys.exit(1)
if len(sys.argv) == 3:
    onnx_path = sys.argv[2]

serial_port = sys.argv[1]
ort_sess = ort.InferenceSession(onnx_path)

with serial.Serial(serial_port, baudrate=115200, timeout=0) as ser: #blocking reading because timeout=0
    ser.write(0xFFFFFFFF) #send the reset command
    print(ser.read_until()) 
    observation = ser.read(4)

    scaled_action = ort_sess.run(None, {"input": observation})[0]
    ser.write(scaled_action)