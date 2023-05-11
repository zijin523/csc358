import socket
import os

p = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
p.connect(('192.168.138.1',8080))
buffer_size = 1024
server_resp = p.recv(buffer_size)
print(server_resp.decode('utf-8'))
while True:
    msg = input('>')
    # avoid empty msg
    if not msg:
        continue
    p.send(msg.encode('utf-8'))  
    
    if msg.startswith('EXIT'):
        server_resp = p.recv(buffer_size)
        print(server_resp.decode('utf-8'))
        break
    elif msg.startswith("DELETE"):
        server_resp = p.recv(buffer_size).decode('utf-8')
        print(server_resp)
        
    elif msg.startswith("LIST"):
        server_resp = p.recv(buffer_size).decode('utf-8')
        print(server_resp)
    
    elif msg.startswith("OVERWRITE"):
        server_resp = p.recv(buffer_size).decode('utf-8')
        print(server_resp)

    elif msg.startswith("PUSH"):
        op, file_name = msg.split(" ")
        file_path = "client_data/" + file_name
        if os.path.isfile(file_path):
            size = os.stat(file_path).st_size
            p.send(str(size).encode("utf-8"))
            f = open(file_path, 'rb')
            for line in f:
                p.send(line) 
            f.close()
        server_resp = p.recv(buffer_size)
        print(server_resp.decode('utf-8'))

p.close()