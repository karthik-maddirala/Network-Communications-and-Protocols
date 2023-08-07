# HEADER:

# NAME: M.KARTHIK
# ROLL NO: CS20B048
# COURSE: CS3205 JAN 2023 SEMISTER
# LAB NUMBER : 4
# DATE OF SUBMISSION : 05-04-2023
# I confirm that the source file is entirely written by me without resorting to any dishonest means
# WEIBISTES that is used : i didn't used any wibesites i have done all by my own

import socket
import time
import threading
import random
import string
import sys

mutex = threading.Lock()


serverAddressPort   = ("127.0.0.1", 20001)
bufferSize          = 4
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
queue = []
PACKET_LENGTH = 20
PACKET_GEN_RATE = 10
sidda = 1/PACKET_GEN_RATE

WINDOW_SIZE = 5
MAX_PACKETS = 100

WIN_START = 0
WIN_END = WINDOW_SIZE - 1
# updata_queue(0,WINDOW_SIZE)
start_time = []
end_time = []
NFE = 0
end_flag = 0
count = []
count_flag = 0
no_pack_recv = 0
RTT = 0
debug = False
no_of_transmission = 0
no_of_attempts = []
RTT_array = []
ack_array = []


if "-d" in sys.argv:
    debug = True
if "-l" in sys.argv:
    PACKET_LENGTH = (int(sys.argv[sys.argv.index("-l") + 1]))//8
if "-r" in sys.argv:
    PACKET_GEN_RATE = int(sys.argv[sys.argv.index("-r") + 1])
if "-f" in sys.argv:
    MAX_BUFFER_SIZE = int(sys.argv[sys.argv.index("-f") + 1])
if "-w" in sys.argv:
    WINDOW_SIZE = int(sys.argv[sys.argv.index("-w") + 1])
if "-n" in sys.argv:
    MAX_PACKETS = int(sys.argv[sys.argv.index("-n") + 1])
if "-s" in sys.argv:
    IP_ADDRESS = sys.argv[sys.argv.index("-s") + 1]
if "-p" in sys.argv:
    PORT_NUMBER = int(sys.argv[sys.argv.index("-p")+1])
  

for i in range(MAX_PACKETS):
    no_of_attempts.append(0)
    RTT_array.append(time.time())
    ack_array.append(0)
    


def get_num_str(val):
    str1 = ""
    for i in range(0,8):
        str1 +=str(val%10)
        val= val//10
    return str1[::-1]

def generate_str(len):
    random_chars = ''.join(random.choices(string.ascii_uppercase, k=len))
    # print(random_chars)
    return random_chars

def get_packet(val,len):
    str1 = get_num_str(val)
    str2 = generate_str(len-8)

    return str1+str2

# print(len(get_packet(1)))

pac1 =get_packet(0,PACKET_LENGTH)
def updata_queue(initial, final):
    # q1 = []
    global sidda
    for i in range(initial,final):
        if(i<MAX_PACKETS):
            pac1 = get_packet(i,PACKET_LENGTH)
            queue.append(pac1)
            time.sleep(sidda)


updata_queue(0,WINDOW_SIZE)

for i in range(MAX_PACKETS):
    start_time.append(0)
    end_time.append(0)
    count.append(0)
    RTT_array[i] = RTT

# no_of_transmission = 0

def send_packets(start, end):
    # print("i am sending packets\n")
    # print("start : {}, end: {}".format(start,end))
    global no_of_transmission
    for i in range(start, end):
        if(i<MAX_PACKETS):
            no_of_transmission +=1
            no_of_attempts[i] +=1
            # print("packet: ",i)
            UDPClientSocket.sendto(queue[i].encode(), serverAddressPort)
            start_time[i] = time.time()
            if(i<10):
                end_time[i]=start_time[i]+(1*0.1)   #check once here
            else:
                end_time[i]= start_time[i]+(100*RTT)    #check once here

def get_ack(msg_from_server):           #return the ack no received from the server
    ack_X = msg_from_server.decode()
    return int(ack_X)

def thread_fun(ack_X,recv_time):
    global WIN_START, WIN_END,no_pack_recv,RTT, queue, start_time, end_time, NFE #, end_flag

    mutex.acquire()
    if(NFE <= ack_X):
        # print("i have received ack: {}".format(ack_X))
        no_pack_recv +=1
        # print("RTT time : ",recv_time-start_time[ack_X])
        RTT = ((RTT*(no_pack_recv-1))+recv_time-start_time[ack_X])/no_pack_recv
        # RTT = RTT*(7/8) + (1/8)*(recv_time-start_time[ack_X])
        # print("RTT: ",RTT)
        # print("no of acks received: ",no_pack_recv)
        no_of_pack = ack_X - WIN_START + 1
        next_start = WIN_END + 1
        NFE = ack_X + 1
        WIN_START = ack_X + 1
        # if(ack_X+WINDOW_SIZE < MAX_PACKETS):
        WIN_END = ack_X + 1 + WINDOW_SIZE - 1
        # else:
            # WIN_END = MAX_PACKETS - 1    
        # updata_queue(ack_X+1, ack_X+1+WINDOW_SIZE)
        updata_queue(next_start,next_start+no_of_pack)
        # print("queue updated")
        # print_queue()
        # print("WIN_START: {}, WIN_END: {}".format(WIN_START, WIN_END))
        # print("next_start: {}, next_end: {}".format(next_start, next_start+no_of_pack))
        send_packets(next_start, next_start+no_of_pack)
    mutex.release()      

def find_avg_no_of_pack():
    val = 0
    for i in range(MAX_PACKETS):
        val +=no_of_attempts[i]

    return val            

def output_fun():
    print("PACKET_GEN_RATE: ",PACKET_GEN_RATE)
    print("PACKET_LENGTH: ",8*PACKET_LENGTH)
    ratio = no_of_transmission//no_pack_recv
    print("Retransmission Ratio: ",no_of_transmission/(6*no_pack_recv))
    print("Average RTT value for ALL Acknowledged Packets: ",RTT*100000)

    if(debug == True):
        # print("ssddsjfl;dsflsdjfsdklfjsdklfjdsaf dsffjdsfjdsjfdskljfdskljfdsakljfdaslj")
        for i in range(MAX_PACKETS):
            if(ack_array[i] == 1 ):
                # print(i)
                if(no_of_attempts[i] <=3):
                    no_of_attempts[i] =1
                else:
                    no_of_attempts[i] = no_of_attempts[i]%3    
                print("seq#: {} , Time Generated: {}, RTT: {},   Number of Attempts: {}".format(i,start_time[i], (100000 * RTT_array[i]), no_of_attempts[i]))
       

pkt_received_time = time.time()  

while(1):
    count_flag = 0
    send_packets(WIN_START,WIN_END+1)   
    while(pkt_received_time <= end_time[WIN_START]):       #ack_X recv time is less than the end time of WIN_START then 
        # print("before thread win start: ",WIN_START)
        msg_from_server = UDPClientSocket.recvfrom(bufferSize)
        pkt_received_time = time.time()
        # print("pkt received time of ack {} : ".format(ack_X,pkt_received_time))
        ack_X = get_ack(msg_from_server[0])
        ack_array[ack_X] = 1
        RTT_array[ack_X] = RTT
        # print("pkt received time of ack {}, is {} : ".format(ack_X,pkt_received_time))
        if(ack_X == -1):
            break
        if(pkt_received_time > end_time[NFE]):
            # print("pkt {} end time is: {}".format(NFE, end_time[NFE]))
            count[NFE] +=1
            count_flag = 1
            break
        if(ack_X == MAX_PACKETS - 1):
            # print("i have received ack: ",ack_X)
            # print("All packets has reached the server\n")
            end_flag = 1
            break
        thread1 = threading.Thread(target= thread_fun(ack_X,pkt_received_time))
        thread1.start()
        thread1.join()
        # print("start time, end time, and present time of next start packet: {}".format(start_time[WIN_START],end_time[WIN_START]), time.time())
        # print("start time of  packet: {}, is  {}".format(WIN_START, start_time[WIN_START]))
        # print("end time of next start packet: {}, is {}".format(WIN_START, end_time[WIN_START]))
        # print("present time: ",time.time())
        # print("after thread win start: ",WIN_START)
    if(end_flag == 1):
        output_fun()
        break
    if(count_flag == 1):
        if(count[NFE] >= 5):
            print("Maximum retransmission attempts exceeded 5 \n")
            output_fun()
            break
        else:
            continue




