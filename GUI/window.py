import time
import dearpygui.dearpygui as dpg
import delegate

dpg.create_context()

#############################################################
##                     COMMUNICATION                       ##
#############################################################
def update_connection(state):
    """
    Update UI elements (button and label) related to connection status
    the button's action (Connect or Disconnect) performs the opposite of the current status (Disconnected or Connected)
    i.o.w: if connected, the button will trigger a disconnection, etc

    Args:
        state (bool): connection status (true -> connected, false -> disconnected)
    """
    button_txt = ""
    label_txt = ""
    if state:
        button_txt="Disconnect"
        label_txt = "connected"
        dpg.enable_item("all_modes")
    else:
        button_txt = "Connect"
        label_txt = "disconnected"
        dpg.disable_item("all_modes")
    dpg.configure_item(item="connection_button", label=button_txt)
    dpg.set_value("connection_status", "Status: " + label_txt)

def get_device_port():
    """
    Returns the device port string (e.g COM3, /dev/usb1)
    """
    return dpg.get_value("device_port_input")

#############################################################
##                          MODE                           ##
#############################################################
def change_mode(sender, app_data):
    """
    Swap between auto and manual (aka jog) modes

    Args:
        sender: automatically entered by dpg
        app_data (string): radio button label
    """
    if app_data == "Auto":
        dpg.enable_item("auto_group")
        dpg.disable_item("manual_group")
    elif app_data == "Manual":
        dpg.disable_item("auto_group")
        dpg.enable_item("manual_group")
        delegate.toggle_continuous_run(False)


#############################################################
##                        MANUAL                           ##
#############################################################
def get_jog_commands():
    """
    Read all valves' state and output a boolean array

    Returns:
        [bool]: vavles' state
    """
    commands = []
    for i in range(8):
        commands.append(dpg.get_value("valve_" + str(i) + "_checkbox"))
    return commands


#############################################################
##                          AUTO                           ##
#############################################################
def file_dialog_cb(send, app_data):
    """
    Update the UI label to show to the user the file was indeed selected
    """
    dpg.set_value("select_label", "Path: " + app_data["file_path_name"])
    delegate.auto_model_path = app_data["file_path_name"]    

def enable_inference_gui():
    """
    Called by the delegate.auto_init() function if the model and thread for inference
    were sucessfully started
    This function enables the inference buttons which are by default disabled
    """
    dpg.enable_item("inference_group")

def update_actuation_auto(state):
    """
    Update UI elements (button and label) related to the actuation of the auto mode
    the button's action (Start or Stop) performs the opposite of the current status (Idling or Running)
    
    Args:
        state (bool): connection status (true -> Running, false -> Idling)
    """
    button_txt = ""
    label_txt = ""
    if state:
        button_txt="Stop"
        label_txt = "Running"
    else:
        button_txt = "Start"
        label_txt = "Idling"
    dpg.configure_item(item="toggle_continuous_button", label=button_txt)
    dpg.set_value("actuation_status", "Status: " + label_txt)

def toggle_continuous_cb():
    """
    Callback functions called by pressing the "Run Continously" or "Stop" button
    Will change through delegate.toggle_continuous_run() a status variable
    This status variable controls the behavior of the inference thread
    """
    state_str = dpg.get_value("actuation_status")
    if state_str == "Status: Idling":
        # No longer idling, state is now running
        delegate.toggle_continuous_run(True)
        # When running, it is only possible to stop the inference
        dpg.configure_item(item="toggle_continuous_button", label="Stop")
    else:
        delegate.toggle_continuous_run(False)

def set_running_state(state):
    """
    Update the GUI elements related to auto mode (button and label)
    If inference is running -> Status: Running, else -> Status: Idling

    Params:
        state (bool): True -> Running, False -> Idling
    """
    if state:
        dpg.set_value("actuation_status", "Status: Running")
    else:
        dpg.set_value("actuation_status", "Status: Idling")
        # When idling, the button "stop" transforms into "run continuously"
        dpg.configure_item(item="toggle_continuous_button", label="Run Continuously")
    
def main():
    """
    Function setting up the UI
    """
    dpg.create_viewport(decorated=False, resizable=False, width=700, height=500)
    
    with dpg.window(label="MainWindow", no_title_bar=True, no_resize=True, no_collapse=True, no_move=True, no_background=False, no_scrollbar=True, width=700, height=500):
        dpg.add_separator(label="Communication")
        with dpg.group(horizontal=False):
            dpg.add_input_text(label=": Device Port", tag="device_port_input")
            with dpg.tooltip(parent="device_port_input"):
                dpg.add_text("Example for Windows: COM7, for Linux/Mac: /dev/ttyUSB0")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Connect", callback=delegate.connection_cb, tag="connection_button")
                dpg.add_text("Status: disconnected", tag="connection_status")
        
        with dpg.group(tag="all_modes"):
            dpg.add_separator(label="Mode Selection")
            with dpg.group(horizontal=True):
                dpg.add_radio_button(items=["Auto", "Manual"], callback=change_mode, tag="mode_selection_radio_button")
                
            dpg.add_separator(label="Auto Mode")
            with dpg.group(horizontal=False, tag="auto_group"):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Init", callback=delegate.auto_init, tag="auto_init_button")
                    with dpg.file_dialog(directory_selector=False,
                                        show=False,
                                        callback=file_dialog_cb,
                                        tag="file_dialog",
                                        height=300,
                                        default_path="../Mujoco/rl/model/"):                 
                        dpg.add_file_extension(".onnx", color=(244, 10, 10, 255))
                    dpg.add_button(label="Select model", callback=lambda:dpg.show_item("file_dialog"), tag="select_model_button")
                    dpg.add_text("Path: Undefined", tag="select_label")

                with dpg.group(tag="inference_group"):
                    dpg.add_button(label="One Step", callback=delegate.one_step, tag="one_step_button")
                    dpg.add_button(label="Run Continuously", callback=toggle_continuous_cb, tag="toggle_continuous_button")
                    dpg.add_text("Status: Idling", tag="actuation_status")
                dpg.disable_item("inference_group") # inference buttons inacessible if the model is not initialized

            dpg.add_separator(label="Manual Mode")
            with dpg.group(tag="manual_group"):
                with dpg.group(horizontal=True, horizontal_spacing=200):
                    with dpg.group(horizontal=False):
                        dpg.add_text("Hip Joints")
                        with dpg.group(horizontal=True):
                            with dpg.group(horizontal=False):
                                dpg.add_checkbox(label="Valve 0", default_value=True, tag="valve_0_checkbox")
                                dpg.add_checkbox(label="Valve 1", default_value=True, tag="valve_1_checkbox")
                                dpg.add_checkbox(label="Valve 2", default_value=True, tag="valve_2_checkbox")
                                dpg.add_checkbox(label="Valve 3", default_value=True, tag="valve_3_checkbox")
                    with dpg.group(horizontal=False):
                        dpg.add_text("Knee Joints")
                        with dpg.group(horizontal=True):
                            with dpg.group(horizontal=False):
                                dpg.add_checkbox(label="Valve 4", default_value=True, tag="valve_4_checkbox")
                                dpg.add_checkbox(label="Valve 5", default_value=True, tag="valve_5_checkbox")
                                dpg.add_checkbox(label="Valve 6", default_value=True, tag="valve_6_checkbox")
                                dpg.add_checkbox(label="Valve 7", default_value=True, tag="valve_7_checkbox")
                dpg.add_button(label="Send Command", width=500, height=50, callback=delegate.send_jog_actuators_command)

    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg.disable_item("all_modes") # all modes (manual and auto)'s interface is disabled by default since no serial communication is established by default
    change_mode(None, "Auto") # Set default mode to auto
    
    while dpg.is_dearpygui_running():
        # Main GUI loop
        update_connection(delegate.communication_get_status())
        dpg.render_dearpygui_frame()
        time.sleep(1.0/60.0)

    dpg.destroy_context()

if __name__ == "__main__":
    main()