import socket
import time
import random

l = open("client_data/log.txt", "w")
#basic attributes for client
data_size = 80
seq_max = 10
timeout = 1
window_size = 4
hostname = "localhost"
port = 8000
#establish connections
c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.settimeout(timeout)
server_address = (hostname, port)
#write log
l.write("starting on host {}\n".format(hostname))
#open the file and assign content of the file to data
filename = input("filename:")
filepath = "client_data/" + filename   
f = open(filepath, "rb")
data = f.read()
size = len(data) 
#write log
l.write("Sender: sent file {}\n".format(filename))
#Splite data into packets
packets = []
seq = 0
i = 0
while i < size:
    if size < data_size:
        packet = data[i:i + size]
        i += size
    else:
        packet = data[i:i + data_size]
        i += data_size
    #seq, content, timeout, e_time, s_time
    packets.append([seq%seq_max, packet, 0, 0, 0]) 
    seq += 1
f.close()
#Send the filename
while True: 
    try:
        c.sendto(filename.encode(), server_address)
        c.sendto(str(seq_max).encode(), server_address)
        c.sendto(str(len(packets)).encode(), server_address)
        ack, _ = c.recvfrom(1024)
        break
    except socket.timeout:
        continue
#num of packets sent
i = 0 
#num of packets received
r = 0 
#attributes for satisitc
effective_byte = 0
byte = 0
packet_send = 0
#Send the first window size of packet
window_packet = []
for i in range(0, min(len(packets), window_size)):
    c.sendto(str(packets[i][0]).encode(), server_address)
    c.sendto(packets[i][1], server_address)
    packets[i][2] = time.time() #setup timeout
    packets[i][4] = time.time() #setup s_start
    window_packet.append(packets[i])
    l.write("Sender: sent PKT{}\n".format(str(window_packet[-1][0])))

    effective_byte += len(packets[i][1])
    byte += len(packets[i][1])
    packet_send += 1
#move i to the index of next packet 
i += 1
#attributes for satisitc
max_RTT = None
min_RTT = None
total_RTT = 0
count = 0
loss = 0
#Reciving Ack and send packets
while len(packets) > r:
    try:
        ack, _ = c.recvfrom(1024)
        pre_ack = int(ack.decode())
        l.write("Sender: received ACK{}\n".format(str(ack.decode())))
        #Successfully received and send the next one
        if int(ack.decode()) == window_packet[0][0]:
            #Console print
            print("ACK{} received".format(str(ack.decode())))
            #Record receving time
            window_packet[0][3] = time.time()
            print("Start Time: {} sec".format(window_packet[0][4]))
            print("End Time: {} sec".format(window_packet[0][3]))
            RTT = window_packet[0][3] - window_packet[0][4]
            total_RTT += RTT
            count += 1
            if max_RTT == None and min_RTT == None:
                max_RTT = RTT
                min_RTT = RTT
            else:
                if RTT > max_RTT:
                    max_RTT = RTT
                elif RTT < min_RTT:
                    min_RTT = RTT
            print("RTT: {} sec".format(RTT))
            n = 0
            while n < len(window_packet):
                packet = window_packet[n]
                #check all packet in the window which has been previously received
                if packet[3] != 0 and packet[0] == (pre_ack % seq_max):
                    pre_ack += 1
                    window_packet.pop(n)
                    r += 1
                    if (len(packets) - 1) - i >= 0:
                        packets[i][2] = time.time()
                        packets[i][4] = time.time()
                        window_packet.append(packets[i])
                        c.settimeout(timeout)
                        i += 1
                        #write log
                        l.write("Sender: sent PKT{}\n".format(str(window_packet[-1][0])))
                        #send the next avaliable packet in window
                        c.sendto(str(window_packet[-1][0]).encode(), server_address)
                        c.sendto(window_packet[-1][1], server_address)
                        #record for satistic
                        effective_byte += len(window_packet[-1][1])
                        byte += len(window_packet[-1][1])
                        packet_send += 1
                else:
                    n += 1 
        #packet loss occurs
        else:
            #find which packet is lost 
            for packet in window_packet:
                if packet[0] == int(ack.decode()):
                    packet[3] = time.time()
                    break
            #Update the timeout 
            t = time.time() - window_packet[0][2]
            if (timeout - t) > 0:
                c.settimeout(timeout - t)  
    #Handle timeout  
    # Update the sending time and send it again          
    except socket.timeout:
        loss += 1
        c.settimeout(timeout)
        window_packet[0][4] = time.time()
        print("PKT{} Request Time Out".format(str(window_packet[0][0])))
        c.sendto(str(window_packet[0][0]).encode(), server_address)
        c.sendto(window_packet[0][1], server_address) 
        #Record for satistic
        byte += len(window_packet[0][1])
        packet_send += 1
        #Write log
        l.write("Sender: sent PKT{}\n".format(str(window_packet[0][0])))
#Write the log and console print
l.write("Sender: file transfer completed\n")
l.write("Sender: number of effective bytes sent: {} bytes\n".format(str(effective_byte)))
l.write("Sender: number of packets sent: {} packets\n".format(str(packet_send)))
l.write("Sender: number of bytes sent: {} bytes\n".format(str(byte)))
l.close()
print("Maximum RTT: {} msec".format(max_RTT * 1000))
print("Minimum RTT: {} msec".format(min_RTT * 1000))
print("Average RTT: {} msec".format(total_RTT / count))
print("Packet loss rate:{}%".format(loss * 100 / len(packets)))
        