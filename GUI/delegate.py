# System includes
import serial, time, os, threading
import onnxruntime as ort
import numpy as np

# Own includes
import window

# Global variables
auto_model_path = "Undefined"
onnx_model = None
actuation_status = False
continuous_run = False
one_time_run = False
actuators_command = np.zeros((1, 8)).astype(np.float32)

connection_status = False
communication_thread = threading.Thread()
communication_order = ""
sensor_reading = ""

#############################################################
##                     COMMUNICATION                       ##
#############################################################
def communication_task(serial_port):    
    """
    Communication thread, receive orders through the global variable communication_order
    No mutex because modifying this variable is atomic
   
    Params:
        serial_port (string): serial port to start the serial communication with
    """
    global communication_order, sensor_reading
    try:
        ser = serial.Serial(serial_port, baudrate=115200, timeout=2) #non-blocking reading because timeout=1
        #if ser.read_until(b'Reset successful\n') != b'Reset successful\n':
            #print("Failed to sync with the MCU, closing serial port and communication thread")
            #ser.close()
            #return
        
        while ser.isOpen():
            if communication_order == "close":
                print("Closing serial port and communication thread")
                communication_order = ""
                ser.close()
                return
            elif communication_order != "":
                # Reading sensors reading
                while ser.in_waiting > 0: #readline is blocking for the timeout, hence must check before reading
                    sensor_reading = ser.readline().decode("ascii")
                    print("sensor reading: " + sensor_reading)

                # Sending Actuators commands
                communication_order += "\n"
                ser.write(communication_order.encode("ascii"))
                communication_order = ""
    except:
        print("Serial port failed to start or have just closed!")
        return

def communication_get_status():
    """
    Getter called by the main window's loop in order to update the communication port's dislayed state up to date
    """
    return communication_thread.is_alive()

def connection_cb():
    """
    Connect or disconnect serial port
    """
    global communication_thread, communication_order
    
    if communication_thread.is_alive():
        communication_order = "close"
    else:
        communication_thread = threading.Thread(name="Communication", target=communication_task, args=(window.get_device_port(),), daemon=True)
        print("Starting communication thread")
        communication_thread.start()
    window.update_connection(communication_thread.is_alive())


#############################################################
##                         ACTUATION                       ##
#############################################################
def send_jog_actuators_command():
    """
    Function transforming the checkboxes' states representing the actuators' status,
    into a string order passed to the MCU through serial
    """
    global communication_order
    commands = window.get_jog_commands()
    commands_txt = ''.join(['1' if x else '0' for x in commands])
    print("commands: " + commands_txt)
    communication_order = commands_txt

def sensor_reading_conversion(string_format: str):# -> list[float]:
    """
    Convert a tab-separated ASCII string of numbers into an array of floats.

    Parameters:
    ascii_string (str): A string containing numbers separated by tab characters.

    Returns:
    list[float]: A list of floating-point numbers parsed from the input string.
    """
    return [float(part) for part in string_format.split('\t')]

def inference_task():
    """
    Thread taking care of the inference
    Receives "orders" through global variables: one_time_run and continuous_run
    """
    global actuators_command, onnx_model, one_time_run, communication_order
    if not onnx_model:
        print("Error, onnx InferenceSession not valid!")
        return

    while True:
        if continuous_run or one_time_run:
            window.set_running_state(True)
            window.set_running_state(True)
            if one_time_run:
                one_time_run = False
            
            #zaxis_obs=np.array([[0, 0, 1]]).astype(np.float32)
            zaxis_obs = sensor_reading_conversion(sensor_reading)
            obs = np.concatenate((zaxis_obs, actuators_command), axis=1)

            actuators_command = onnx_model.run(None, {'input': obs})[0]
            commands_txt = ''.join(['1' if round(-x) else '0' for x in actuators_command[0]])
            print("obs: " + str(obs) + ", commands: " + commands_txt)
            
            communication_order = commands_txt
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