import gui_window

connection_status = False

def connection_cb():
    global connection_status
    print("connection_cb not implemented")
    connection_status = not connection_status
    gui_window.update_connection(connection_status)

def send_actuators_state():
    print("send_actuators_state not implemented")