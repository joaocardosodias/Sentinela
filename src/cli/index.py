import threading 
import socket
import sys
import time
import platform  
from dotenv import load_dotenv

try:
    from drone.network_routes import bind_tello_socket, describe_network_plan, load_tello_config
except ModuleNotFoundError:
    from drone.network_routes import bind_tello_socket, describe_network_plan, load_tello_config

load_dotenv()
TELLO_CONFIG = load_tello_config()

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = TELLO_CONFIG.command_address
TELLO_BIND = bind_tello_socket(sock, TELLO_CONFIG)

def recv():
    count = 0
    while True: 
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break


print ('\r\n\r\nTello Python3 Demo.\r\n')
print(describe_network_plan(TELLO_CONFIG))
print("")

print ('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')

print ('end -- quit demo.\r\n')


#recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()

while True: 
    try:
        python_version = str(platform.python_version())
        version_init_num = int(python_version.partition('.')[0]) 
       # print (version_init_num)
        if version_init_num == 3:
            msg = input("");
        else:
            msg = input("");
        
        if not msg:
            break  

        if 'end' in msg:
            print ('...')
            sock.close()  
            break

        # Send data
        msg = msg.encode(encoding="utf-8") 
        sent = sock.sendto(msg, tello_address)
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()  
        break
