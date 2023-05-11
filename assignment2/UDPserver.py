import socket
import time
import random

#basic attributes for server
hostname = "localhost"
port = 8000
seq_max = None
client = None
packets_num = None
filename = None
#establish connections
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = (hostname, port)
s.bind(address)
#basic attributes for sr
buffer = []
pre_ack = -1
bytes_num = 0
l = None
while True:
	#All attributes are None
	#Wait to receive the filename
	if packets_num == None and client == None and seq_max == None:
		while True:
			num = int(random.uniform(1, 10)) 
			#If the packet contains filename does not lose
			#filename, maximum sequence number, client pipline number, number of packet
			if num >= 4:
				f, c = s.recvfrom(1024)
				filename = f
				client = c
				seq, _ = s.recvfrom(1024)
				seq_max = int(seq.decode())
				p, _ = s.recvfrom(1024)
				packets_num = int(p.decode())
				s.sendto('ack'.encode(), client)
				break
		print("{} successfully received".format(filename.decode))
		#Create the data file and log file
		filename = filename.decode()
		filepath = "server_data/" + filename
		f = open(filepath, "wb")
		l = open("server_data/log.txt", "w")
		l.write("Receiver: received {}\n".format(filename))
	#The packets havent been finished sending
	elif packets_num != None and packets_num > 0:
		ack, _ = s.recvfrom(1024)
		ack = ack.decode('utf-8')
		content, _ = s.recvfrom(1024)
		num = int(random.uniform(1, 10))
		#if packet loss does not occur
		if num >= 4:
			#update the file bytes and packet num 
			bytes_num += len(content)
			packets_num -= 1
			print("Receiver: Incoming ACK{}".format(str(ack)))
			print("Receiver: Expected ACK{}".format(str((pre_ack + 1) % seq_max)))
			#if the ack expected != the packet num
			#put the packet into the buffer
			if (pre_ack + 1) % seq_max != int(ack):
				l.write("Receiver: received PKT{}\n".format(ack))
				buffer.append((int(ack), content))
			#if the ack expected == the packet num
			else:
				#Write the data and update the ack
				l.write("Receiver: received PKT{}\n".format(ack))
				f.write(content)
				pre_ack = int(ack)
				n = 0
				#check buffer and remove the packet possible
				while n < len(buffer):
					packet = buffer[n]
					if packet[0] == (pre_ack + 1) % seq_max:
						pre_ack = (pre_ack + 1) % seq_max
						f.write(packet[1])
						buffer.pop(n)
					else:
						n += 1
			s.sendto(ack.encode(), client)
			l.write("Receiver: sent an ACK{}\n".format(ack))
	#All packets have been recevied
	elif packets_num != None and packets_num == 0:
		f.close()
		l.write("Receiver: file transfer completed\n")
		l.write("Receiver: number of bytes received: {} bytes\n".format(bytes_num))
		l.close()
		seq_max = None
		client = None
		packets_num = None
		filename = None
		buffer = []
		pre_ack = -1
		bytes_num = 0
		s.close()
		break
	
	

