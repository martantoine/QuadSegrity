import gui_window

connection_status = False

def connection_cb():
    global connection_status
    connection_status = not connection_status
    gui_window.update_connection(connection_status)
    
    print("connection_cb not implemented")

def send_actuators_command():
    print(gui_window.get_jog_commands())
    print("send_actuators_state not implemented")