#!/bin/sh
echo "Starting the serial virtual port"
socat -d -d pty,rawer,echo=0,link=/tmp/ttyV0 pty,rawer,echo=0,link=/tmp/ttyV1 & 
sleep 1
echo
echo
echo "Follow those steps to successfuly connect to the serial port simulator"
echo "1. start the UI with python GUI/window.py"
echo "2. enter in the serial_port text input /dev/pts/2"
echo "3. enter in a terminal the command 'echo \"Reset successful\\\n\" > /dev/pts/1', do not execute yet!"
echo "4. click connect on the UI"
echo "5. execute the command entered in 3., you have exactly 2nds form the moment you clicked on the UI button 'connect'"