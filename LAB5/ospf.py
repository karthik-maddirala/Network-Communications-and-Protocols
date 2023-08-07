# HEADER:

# NAME: M.KARTHIK
# ROLL NO: CS20B048
# COURSE: CS3205 JAN 2023 SEMISTER
# LAB NUMBER : 5
# DATE OF SUBMISSION : 28-04-2023
# I confirm that the source file is entirely written by me without resorting to any dishonest means
# WEIBISTES that is used : i didn't used any wibesites i have done all by my own

import socket
import threading
import random
import time
import numpy as np
import sys


Node_ident = 0
# input_file = [[3,3], [0,1,2,4],[1,2,3,5], [0,2,4,6]]

input_file = [[9,14], [0,1,3,5], [0,7,7,9], 
              [1,7,10,12], [1,2,7,9], [7,8,6,8],
              [7,6,0,2],[2,8,1,3], [8,6,5,7], 
              [2,3,6,8], [2,5,3,5], [6,5,1,3], 
              [3,5,13,15], [3,4,8,10], [5,4,9,11]]


Output_file = []
for i in range(input_file[0][0]):
    ptr = open("output"+str(i)+".txt", "w")
    Output_file.append(ptr)

HELLO_INTERVAL = 1
LSA_INTERVAL = 5
SPF_INTERVAL = 20
bufferSize  = 1024

# print("no of nodes: ", input_file[0][0])
# print("no of links: ", input_file[0][1])
input_file_name = ""
if "-f" in sys.argv:
    # print("hello1")
    input_file_name = sys.argv[sys.argv.index("-f")+1]
if "-i" in sys.argv:
    # print("hello2")
    Node_ident = int(sys.argv[sys.argv.index("-i")+1])
if "-o" in sys.argv:
    # print("hello3")
    output_file = sys.argv[sys.argv.index("-o")+1]
if "-s" in sys.argv:
    # print("hello4")
    SPF_INTERVAL = int(sys.argv[sys.argv.index("-s")+1])
if "-a" in sys.argv:
    # print("hello5")
    LSA_INTERVAL = int(sys.argv[sys.argv.index("-a")+1])
if "-h" in sys.argv:
    # print("hello6")
    HELLO_INTERVAL = int(sys.argv[sys.argv.index("-h")+1])

# print(input_file_name)    
# print(type(HELLO_INTERVAL))
# print(HELLO_INTERVAL)

ptr1 = open(input_file_name, "r")
input_file = []

for line in ptr1:
    temp = line.split()
    temp = [int(i) for i in temp]
    input_file.append(temp)



N = input_file[0][0]

path_array = []
for i in range(N):
    temp_mat = []
    for  j in range(N):
        temp_mat.append("")

    path_array.append(temp_mat)   

for i in range(N):
    for j in range(N):
        if(i ==j):
            path_array[i][j] =""
        else:    
            path_array[i][j] =str(i) + "-"


mutex_list = []
for i in range(N):
    mutex_list.append(threading.Lock())



# adj_matrix_list = []
# last_recv_seqno_list = []

# for j in range(N):
#     adj_matrix = [[-1 for i in range(N)] for j in range(N)]
#     adj_matrix_list.append(adj_matrix)
#     last_recv_seqno_list.append(adj_matrix)

adj_matrix_list = np.full((N,N,N), -1)
last_recv_seqno_list = np.full((N,N,N), -1)

   

# print(adj_matrix)

neighbour_node_list = []
min_list = [[-1 for i in range(N)] for j in range(N)]
max_list = [[-1 for i in range(N)] for j in range(N)]

for i in range(1, input_file[0][1]+1):
    u = input_file[i][0]
    v = input_file[i][1]
    min_val = input_file[i][2]
    max_val = input_file[i][3]
    min_list[u][v] = min_val
    min_list[v][u] = min_val
    max_list[u][v] = max_val
    max_list[v][u] = max_val




LSA_pkt_list = []
for i in range(N):
    LSA_pkt_list.append("")
    

seq_no_list = []
for i in range(N):
    seq_no_list.append(0)

UDP_Socket = []
for i in range(N):
    UDP_Socket.append(socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM))
    

UDP_Socket_address = []


#initializing the UDP_Socket address list
for i in range(N):
    Address_port = ('localhost', 10000+i)
    UDP_Socket_address.append(Address_port)

for i in range(N):
    UDP_Socket[i].bind(UDP_Socket_address[i])
    

#initializing the neighbour list
for i in range(N):
    neighbour_node_list.append([])

no_of_links = input_file[0][1]
for i in range(1,no_of_links+1):
    u = input_file[i][0]
    v = input_file[i][1]
    # print(u, v)
    neighbour_node_list[u].append(v)
    neighbour_node_list[v].append(u)    


def find_neighbour_nodes(ind):  #given a node index ind , it returns the neighbouring nodes lis
    return neighbour_node_list[ind]

def create_hello_pkt(ind):      #ginven a source id and it will return a string ( which is hello packet)
    hello_pkt = "HELLO-"+str(ind)
    return hello_pkt 

def create_helloreply_pkt(i, j):   #j is sender and i is receiver of hello reply packet
    min_val = min_list[i][j]
    max_val = max_list[i][j]

    cost_val = random.randint(min_val+1, max_val-1)
    helloreply_pkt = "HELLOREPLY-"+str(j)+"-"+str(i)+"-"+str(cost_val)

    return helloreply_pkt

def create_LSA_packet(srcid, seqno,neighbour_cost_list):
    nei_cost_str = ""
    for i in range(len(neighbour_cost_list)):
        nei_cost_str +=str(neighbour_cost_list[i][0])
        nei_cost_str += "-"
        nei_cost_str += str(neighbour_cost_list[i][1])
        nei_cost_str += "-"
    nei_cost_str = nei_cost_str[0:len(nei_cost_str)-1]
    LSA_pkt = "LSA-"+str(srcid)+"-"+str(seqno)+"-"+str(len(neighbour_cost_list))+"-"+nei_cost_str

    return LSA_pkt



def sending_fun(ind):
    while(True):
        neighbours_list = find_neighbour_nodes(ind)
        for i in neighbours_list:
            hello_pkt = create_hello_pkt(ind)

            mutex_list[ind].acquire()
            bytes_to_send = str.encode(hello_pkt)
            mutex_list[ind].release()
             
            #print("router ", ind, " sending hello packet to router ", i)
            mutex_list[ind].acquire()
            UDP_Socket[ind].sendto(bytes_to_send, UDP_Socket_address[i])    #sending HELLO pkt from router ind to the neibhour i
            mutex_list[ind].release()

            # print("router ",ind, " sending hello packet to router ", i)
        time.sleep(HELLO_INTERVAL) #sending hello packets to the neighbours for every HELLO_INTERVAL of senconds   


def find_type_of_msg(message):  #it will return the type of the message it received
    str1 = message.split("-")

    return str1[0]

def send_HELLOREPLY_pkt(message, address, j):   #j received the HELLO packet
    str1 = message.split("-")
    i = int(str1[1])
    HELLO_REPLY_pkt = create_helloreply_pkt(i,j)
    msg_to_send = HELLO_REPLY_pkt.encode()

    mutex_list[j].acquire()
    UDP_Socket[j].sendto(msg_to_send, address)
    mutex_list[j].release()


    #print("router ", j, "sending HELLO-REPLY to router ", i)

def find_cost_from_helloreply(message):
    str1 = message.split("-")
    return str1[3]

def find_i_from_helloreply(message):   #find  i in the router
    str1 = message.split("-")
    return str1[2]

# def append_to_LSA_fun(j,message):  #to update the LSA pkt for router j for the hello reply message
#     cost = find_cost_from_helloreply(message)
#     i = find_i_from_helloreply(message)
#     LSA_pkt_list[j] +=str(i)       #changed j to i here
#     LSA_pkt_list[j] +="-"
#     LSA_pkt_list[j] +=str(cost)
#     LSA_pkt_list[j] +="-"

def find_list_of_j_from_LSA(message):
    j_list = []
    str1 = message.split("-")
    no_of_values = int(str1[3])

    k = 4
    for i in range(no_of_values):
        j_list.append(int(str1[k+i*2]))

    return j_list  

def find_corresponding_i_j_cost(ind, message):  
    cost_list = []
    str1 = message.split("-")
    no_of_values = int(str1[3])

    k = 5
    for i in range(no_of_values):
        cost_list.append(int(str1[k+i*2]))

    return cost_list    



def update_adjacent_mat(ind,message):
    list_of_j = find_list_of_j_from_LSA(message)
    cost_list = find_corresponding_i_j_cost(ind, message)
    src_id = int(message.split("-")[1])
    for i in range(len(list_of_j)):
        j = list_of_j[i]
        # if(adj_matrix_list[ind][ind][j] == -1):
        adj_matrix_list[ind][src_id][j] = cost_list[i]
        # else:
        #     adj_matrix_list[ind][ind][j] = min(adj_matrix_list[ind][ind][j], cost_list[i])    

# def find_seqno(message):
#     str1 = message.split("-")

#     return int(str1[2])

def minDistance(dist, sptSet): #to find the minimum distance from the source
    
    min = 1e7
    min_index = -1
    for v in range(N):
            if dist[v] < min and sptSet[v] == False:
                min = dist[v]
                min_index = v
 
    return min_index

def printSolution(dist,ind):
    # print("Vertex \t Distance from Source")
    #print(path_array)
    for node in range(N):
        #print(node, "\t\t", dist[node])
        if(ind != node):
            # Output_file[ind].write(str(node) + "\t\t" + path_array[ind][node]+str(node) + "\t\t" + str(dist[node]) + "\n")
            Output_file[ind].write(str(node) + "\t\t" + str(ind)+"-"+path_array[ind][node][:-1] + "\t\t" + str(dist[node]) + "\n")

def dijkstras_fun(src):

    dist = [1e7] * N
    dist[src] = 0
    sptSet = [False] * N

    for count in range(N):
        u = minDistance(dist, sptSet)

        sptSet[u] = True

        for v in range(N):
            if (adj_matrix_list[src][u][v] > 0 and
                sptSet[v] == False and dist[v] > dist[u] + adj_matrix_list[src][u][v]):
                # if(v in neighbour_node_list[src]):
                #     path_array[src][v] += ""
                # else:
                path_array[src][v] = path_array[src][u] +  str(v) + "-"

                dist[v] = dist[u] + adj_matrix_list[src][u][v]

    printSolution(dist,src)

def update2_adjacent_mat(ind,message):
    str1 = message.split("-")
    cost = int(str1[3])
    j = int(str1[1])
    i = int(str1[2])
    adj_matrix_list[ind][i][j] = cost

def receiving_fun(ind):

    LSA_pkt_list[ind] = ""
    no_of_entries = 0

    while(True):
        
        #print("router ", ind, " is in receiving state")

        mutex_list[ind].acquire()
        bytesAddressPair = UDP_Socket[ind].recvfrom(bufferSize)
        mutex_list[ind].release()
        
        message = bytesAddressPair[0].decode()
        address = bytesAddressPair[1]
        #print("router ", ind, "received the message ",message)
        # time.sleep(0.01)

        
        type_msg = find_type_of_msg(message)

        if(type_msg == "HELLO"): #recieved HELLO msg and we have to send the hello reply back
            str1 = message.split("-")
            i = int(str1[1])
            send_HELLOREPLY_pkt(message,address,ind)
        elif(type_msg == "HELLOREPLY"): #received HELLOREPLY and we have to update the LSA packet
            #no_of_entries +=1
            #append_to_LSA_fun(ind, message, no_of_entries)
            update2_adjacent_mat(ind, message)
        elif(type_msg == "LSA"):     #received the LSA packet and we have to update the routing table
            temp = message.split("-")
            nei_ind = int(temp[1])
            pres_seq_no = int(temp[2])
            received_from = bytesAddressPair[1][1]-10000
            last_seqno = last_recv_seqno_list[ind][ind][nei_ind]
            if(pres_seq_no > last_seqno):
                last_recv_seqno_list[ind][ind][nei_ind] = pres_seq_no
                update_adjacent_mat(ind,message)

                bytes_to_send = str.encode(message)
                for i in neighbour_node_list[ind]:
                    if(i != received_from):
                        
                        mutex_list[ind].acquire()
                        UDP_Socket[ind].sendto(bytes_to_send, UDP_Socket_address[i])
                        mutex_list[ind].release()
                        
        
def create_LSA(ind):

    message = "LSA-"+str(ind)+"-"+str(seq_no_list[ind])+"-"
    adj_mat = adj_matrix_list[ind]
    no_of_entries = 0
    message1 = str()
    for j in range(N):
        if(adj_mat[ind][j] != -1):
            no_of_entries +=1
            message1 += str(j)+"-"+str(adj_mat[ind][j])+"-"

    message += str(no_of_entries) + "-" + message1

    return message            

    

        #if(time.time() >= start_time1 + LSA_INTERVAL):
def send_lsa(ind):
    while(True):
        time.sleep(LSA_INTERVAL)
        messagetosend = create_LSA(ind)
        bytes_to_send = str.encode(messagetosend)

        for i in neighbour_node_list[ind]:             #sending  LSA packet to the its neighbours
            UDP_Socket[ind].sendto(bytes_to_send, UDP_Socket_address[i])
            print("sending LSA PKT from router ", ind, " to router ", i)

def create_routing_table(ind):
    while(True):
        time.sleep(SPF_INTERVAL)
        Output_file[ind].write("Routing Table for  Node No "+ str(ind) +  " at Time " + str(time.time()) + "\n") #keep the time
        Output_file[ind].write("Destination       Path       Cost " + "\n")
        
        dijkstras_fun(ind)
        #start_time2 = time.time()


def for_the_router(i):
    thread1 = threading.Thread(target= sending_fun, args=(i,))  # for the router i creating thread for sending HELLO pkt
    thread2 = threading.Thread(target= receiving_fun, args=(i,)) #for the router i creating thread for receiving  HELLO pkt
    thread3 = threading.Thread(target= send_lsa, args=(i,))
    thread4 = threading.Thread(target= create_routing_table, args=(i,))
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()


for i in range(N):
    for_the_router(i)


time.sleep(42)
for i in range(N):
    Output_file[i].close()