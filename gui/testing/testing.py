import socket, ipaddress, threading
import time 
def check_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        socket.setdefaulttimeout(2.0) # seconds (float)
        result = sock.connect_ex((ip,port))
        if result == 0:
            # print ("Port is open")
            return "OPEN"
        else:
            # print ("Port is closed/filtered")
            return "CLOSED"
        sock.close()
    except:
        return "CLOSED"
while True:
    t_start = time.time()
    ip = ipaddress.ip_address('10.6.131.127')
    print(check_port('10.6.131.127', 5000))
    time.sleep(0.1)
    t_duration = (time.time() - t_start)
    print(t_duration)