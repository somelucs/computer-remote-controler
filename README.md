# computer-remote-controler
Project made to control your Windows remotely from anywhere through a VPN

# How can i use it?

For running this code, you must have the framework Flask and Python installed localy and a VPN to control from anywhere. This code also works on local network too.

# How does the code work?

The screenshot was taken with the python mss library, which constantly captures the monitor input, and is subsequently used in the background by the threading library. The interface is made in JavaScript, which detects mouse clicks and key presses and makes a request to a server route responsible for executing the equivalent command on the computer through pyautogui.
