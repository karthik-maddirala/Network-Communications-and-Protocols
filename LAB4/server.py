# HEADER:

# NAME: M.KARTHIK
# ROLL NO: CS20B048
# COURSE: CS3205 JAN 2023 SEMISTER
# LAB NUMBER : 4
# DATE OF SUBMISSION : 05-04-2023
# I confirm that the source file is entirely written by me without resorting to any dishonest means
# WEIBISTES that is used : i didn't used any wibesites i have done all by my own

import socket
import threading
import random
import sys
import time

PACKET_LENGTH = 20
localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = PACKET_LENGTH
debug = False

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

MAX_PACKETS = 100
RAN_DROP_PROB  = 0.05
NFE =0
time_recv = []
pac_drop = []

if "-d" in sys.argv:
    debug = True
if "-p" in sys.argv:
    localport = int(sys.argv[sys.argv.index("-p") + 1])
if "-n" in sys.argv:
    MAX_PACKETS = int(sys.argv[sys.argv.index("-n") + 1])
if "-e" in sys.argv:
    RAN_DROP_PROB = float(sys.argv[sys.argv.index("-e") + 1])

for i in range(MAX_PACKETS):
    time_recv.append(time.time())
    pac_drop.append(False)

to_drop = list()
for i in range(int(MAX_PACKETS*RAN_DROP_PROB)):
    to_drop.append(random.randint(1,MAX_PACKETS-1))

for i in range(0, len(to_drop)):
    pac_drop[to_drop[i]] = True 

   

mutex = threading.Lock()

def threadfun(seq,address,check):
    # print("seq: ",seq)
    global NFE,to_drop
    mutex.acquire()
   
    if(seq == NFE):
        if(check==True):
            # print("packet {} has dropped".format(seq))
            to_drop.remove(seq)
            # if(seq !=0):
            UDPServerSocket.sendto((str(NFE-1).encode()),address)
        else:
            # print("i have received the packet: {}".format(seq))
            NFE +=1
            UDPServerSocket.sendto((str(seq)).encode(), address)
            # print("NFE: ",NFE)
    mutex.release()    


   

def find_seqno(pac):    #given a string to find the sequence number of the packet
    val = 0
    ten = 10000000
    for char in pac:
        if(char.isupper()):
            return val
        else:
            val +=ten*(int(char))
        ten = ten//10

    return val     

def is_drop(seq):
    if seq in to_drop:
        return True
    return False

def output_fun():
    if(debug == True):
        for i in range(MAX_PACKETS):
            print("seq# : {}, Time Received: {}, Packet Dropped: {}".format(i,time_recv[i], pac_drop[i]))
   

while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    pac_received = bytesAddressPair[0].decode()
    # print("i have received the packet: {}".format(pac_received))
    address = bytesAddressPair[1]
    seq_no = find_seqno(pac_received)
    time_recv[seq_no] = time.time()
    # if(is_drop(seq_no)==False):
    thread1 = threading.Thread(target= threadfun(seq_no,address,is_drop(seq_no)))
    thread1.start()
    if(seq_no == MAX_PACKETS-1):
        UDPServerSocket.sendto((str(MAX_PACKETS-1).encode()),address)
        print("server received all the packets and sent all the acknowledgments\n")
        output_fun()
        break




