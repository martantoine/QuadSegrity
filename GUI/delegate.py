import window
import serial, time

connection_status = False
actuation_status = False
ser = serial.Serial()

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
    commands = window.get_jog_commands()
    commands_txt = ''.join(['1' if x else '0' for x in commands])
    serial_send(commands_txt)

def auto_init():
    onnx_path = window.get_auto_path()
    ort_sess = ort.InferenceSession(onnx_path)
    
def one_step():
    print("one_step not implemented")

def toggle_continuous_run():
    global actuation_status
    actuation_status = not actuation_status
    window.update_actuation_auto(actuation_status)

    print("toggle_continuous_run not implemented")
