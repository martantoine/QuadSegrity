# System includes
import serial, time, os, threading
import onnxruntime as ort
import numpy as np

# Own includes
import window

connection_status = False
actuation_status = False
ser = serial.Serial()
auto_model_path = "Undefined"
onnx_model = None
actuators_command = np.zeros((1, 8)).astype(np.float32)
continuous_run = False
one_time_run = False

def connection_cb():
    """
    Connect or disconnect serial port
    """
    global connection_status, ser
    
    if not connection_status: # try opening the serial port 
        try:
            ser = serial.Serial(serial_port, baudrate=115200, timeout=1) #non-blocking reading because timeout=1
            print("Opened port")
            ser.read_until(b'Reset successful\n')
            print("Communication established")
            connection_status = True
        except:
            print("Failed to open port or establish communication!")
    else:
        try:
            if ser.is_open():
                ser.close()
                print("Port closed")
        except:
            print("Failed to close the port, port might have been already closed!")

    serial_port = window.update_connection(connection_status)
    
def serial_send(msg):
    """
    Send to serial port the msg, wait until 1sc are elapsed or less if the msg was send successfuly

    Params:
        msg (string): msg to send, no end of line required
    """
    try:
        if ser.is_open():
            ser.write_line(msg)
            i = 0
            while (i < 10) and (ser.out_waiting > 0):
                time.sleep(0.1)
            if ser.out_waiting > 0:
                print("Failed to send msg: " + msg)
        else:
            print("Port not open, will not send msg: " + msg)
    except:
        print("Exception when trying to serial send following msg: " + msg)

def send_actuators_command():
    """
    Function transforming the checkboxes' states representing the actuaotors' status,
    into a string order passed to the MCU through serial
    """
    commands = window.get_jog_commands()
    commands_txt = ''.join(['1' if x else '0' for x in commands])
    serial_send(commands_txt)

def inference_task():
    """
    Thread taking care of the inference
    Receives "orders" through global variables: one_time_run and continuous_run
    """
    global actuators_command, onnx_model, one_time_run
    if not onnx_model:
        print("Error, onnx InferenceSession not valid!")
        return

    while True:
        if continuous_run or one_time_run:
            window.set_running_state(True)
            window.set_running_state(True)
            if one_time_run:
                one_time_run = False
            zaxis_obs=np.array([[0, 0, 1]]).astype(np.float32)
            obs = np.concatenate((zaxis_obs, actuators_command), axis=1)

            actuators_command = onnx_model.run(None, {'input': obs})[0]
            commands_txt = ''.join(['1' if round(-x) else '0' for x in actuators_command[0]])
            print("commands: " + commands_txt)
            serial_send(commands_txt)  
        else:
            window.set_running_state(False)

        time.sleep(1)

def auto_init():
    """
    Create the onnx inference environment, and the inference thread
    A separate thread is required for inference because inference can happens continuously
    which would block the rest of the GUI otherwise
    """
    global onnx_model
    if not os.path.isfile(auto_model_path):
        print("Following file is not existing: " + auto_model_path)
        return

    onnx_model = ort.InferenceSession(auto_model_path)
    if onnx_model == None:
        print("Failed to init model")
        return
    thread = threading.Thread(name="Inference", target=inference_task, args=(), daemon=True)
    thread.start()
    if thread:
        print("Inference thread successfully started")
        window.enable_inference_gui()

def one_step():
    """
    Run one step / one inference of the onnnx model
    """
    global one_time_run
    one_time_run = True

def toggle_continuous_run(state):
    """
    Run continuously, step after step, one inference at a time, of the onnnx model
    """
    global continuous_run
    continuous_run = state

    