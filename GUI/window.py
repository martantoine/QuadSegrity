import dearpygui.dearpygui as dpg
import delegate

dpg.create_context()

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
    else:
        button_txt = "Connect"
        label_txt = "disconnected"
    dpg.configure_item(item="connection_button", label=button_txt)
    dpg.set_value("connection_status", "Status: " + label_txt)

def get_jog_commands():
    """
    Read all valves' state and output a boolean array

    Returns:
        [bool]: vavles' state
    """
    commands = []
    for i in range(10):
        commands.append(dpg.get_value("valve_" + str(i) + "_checkbox"))
    return commands

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

def get_device_port():
    """
    Returns the device port string (e.g COM3, /dev/usb1)
    """
    return dpg.get_value("device_port_input")

def get_auto_path():
    """
    Returns the device port string (e.g COM3, /dev/usb1)
    """
    return dpg.get_value("auto_model_input")

def file_dialog_cb(send, app_data):
    """
    Update the UI label to show to the user the file was indeed selected
    """
    dpg.set_value("select_label", "Path: " + app_data["file_path_name"])

def main():
    dpg.create_viewport(decorated=False, resizable=False, width=700, height=400)
    
    with dpg.window(label="MainWindow", no_title_bar=True, no_resize=True, no_collapse=True, no_move=True, no_background=False, no_scrollbar=True, width=700, height=400):
        dpg.add_separator(label="Communication")
        with dpg.group(horizontal=False):
            dpg.add_input_text(label=": Device Port", tag="device_port_input")
            with dpg.tooltip(parent="device_port_input"):
                dpg.add_text("Example for Windows: COM7, for Linux/Mac: /dev/ttyUSB0")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Connect", callback=delegate.connection_cb, tag="connection_button")
                dpg.add_text("Status: Unknown", tag="connection_status")
        
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
                    dpg.add_file_extension(".zip", color=(244, 10, 10, 255))
                dpg.add_button(label="Select model", callback=lambda:dpg.show_item("file_dialog"), tag="select_model_button")
                dpg.add_text("Path: Undefined", tag="select_label")

            dpg.add_button(label="One Step", callback=delegate.one_step, tag="one_step_button")
            dpg.add_button(label="Run Continuously", callback=delegate.toggle_continuous_run, tag="toggle_continuous_button")
            dpg.add_text("Status: Idle", tag="actuation_status")
            
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
                            dpg.add_checkbox(label="Valve 4", default_value=True, tag="valve_4_checkbox")
                with dpg.group(horizontal=False):
                    dpg.add_text("Knee Joints")
                    with dpg.group(horizontal=True):
                        with dpg.group(horizontal=False):
                            dpg.add_checkbox(label="Valve 5", default_value=True, tag="valve_5_checkbox")
                            dpg.add_checkbox(label="Valve 6", default_value=True, tag="valve_6_checkbox")
                            dpg.add_checkbox(label="Valve 7", default_value=True, tag="valve_7_checkbox")
                            dpg.add_checkbox(label="Valve 8", default_value=True, tag="valve_8_checkbox")
                            dpg.add_checkbox(label="Valve 9", default_value=True, tag="valve_9_checkbox")
            dpg.add_button(label="Send Command", width=500, height=50, callback=delegate.send_actuators_command)

    dpg.setup_dearpygui()
    dpg.show_viewport()

    change_mode(None, "Auto") # Set default mode to auto
    
    while dpg.is_dearpygui_running():
        # Main GUI loop
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

if __name__ == "__main__":
    main()