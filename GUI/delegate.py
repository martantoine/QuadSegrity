import window

connection_status = False
actuation_status = False

def connection_cb():
    global connection_status
    connection_status = not connection_status
    device_port = window.get_device_port()
    window.update_connection(connection_status)
    print(device_port)
    print("connection_cb not implemented")

def send_actuators_command():
    print(window.get_jog_commands())

    print("send_actuators_state not implemented")

def one_step():
    print("one_step not implemented")

def toggle_continuous_run():
    global actuation_status
    actuation_status = not actuation_status
    window.update_actuation_auto(actuation_status)

    print("toggle_continuous_run not implemented")
