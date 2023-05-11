import socket
import os
import threading

ip_port = ('192.168.138.1',8080)
buffer_size = 1024
queuing_size = 10

def msg_handing(con):
    while True:   
        client_req = con.recv(buffer_size).decode('utf-8')
        msg = client_req.split(" ")
        server_resp = ""
    
        if msg[0] == "EXIT":
            server_resp = "Disconnected from the server!"
            con.send(server_resp.encode('utf-8'))
            break

        elif msg[0] == "LIST":
            files = os.listdir("server_data")
            file_num = len(files)
            if file_num == 0:
                server_resp = "Server directory is empty!"
                con.send(server_resp.encode('utf-8'))
            else:
                for i in range(0, file_num):
                    if i == file_num - 1:
                        server_resp += files[i]
                    else:
                        server_resp += files[i] + '\n'
                con.send(server_resp.encode('utf-8'))

        elif msg[0] == "OVERWRITE":
            text = "This is the content for overwriting"
            file_name = msg[1]
            file_path = "server_data/" + file_name
            if os.path.exists(file_path):
                f = open(file_path, 'w')
                f.write(text)
                f.close()
                server_resp = "The file {} overwritten!".format(msg[1])
            else:
                server_resp = "File not found!"
            con.send(server_resp.encode('utf-8'))

        elif msg[0] == "DELETE":
            file_num = len(os.listdir("server_data"))
            if file_num == 0:
                server_resp = "Server directory is empty!"
                con.send(server_resp.encode('utf-8'))
            else:
                file_name = msg[1]
                file_path = "server_data/" + file_name
                if os.path.exists(file_path):
                    file_path = "server_data/" + file_name
                    os.remove(file_path)
                    server_resp = "The file {} deleted!".format(file_name)
                    con.send(server_resp.encode('utf-8'))
                else:
                    server_resp =  "File not found!"
                    con.send(server_resp.encode('utf-8'))

        elif msg[0] == "PUSH":
            file_size = int(con.recv(1024).decode("utf-8"))
            file_name = msg[1]
            file_path = "server_data/" + file_name
            f = open(file_path, 'wb')
            received_size = 0
            while received_size < file_size:
                size = 0 
                if file_size - received_size > 1024:
                    size = 1024
                else: 
                    size = file_size - received_size
                filedata = con.recv(size) 
                filedata_len = len(filedata)
                received_size += filedata_len
                f.write(filedata)
            f.close()
            server_resp = "Received the file {}!".format(msg[1])
            con.send(server_resp.encode('utf-8'))
    con.close()

if __name__ == '__main__':
    r = socket.gethostbyname(socket.gethostname())
    print(r)
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) 
    server.bind(ip_port) #link ip and port
    server.listen(queuing_size) #queuing size
    print("[LISTENTING] Server is listening...")
    while 1:
        con,address = server.accept()  # waiting for new connection
        print("[NEW CONNECTION] ({}, {}) connected.".format(address, 8080))
        server_resp = "Welcome to the File Server!"
        con.send(server_resp.encode('utf-8'))
        thread = threading.Thread(target=msg_handing, args=(con,))
        thread.setDaemon(True)
        thread.start()
