#NAME               : M.KARHIK
#Roll Number        : CS20B048
#Course             : CS3205 Jan. 2023 semister
#Lab number         : 2
#Date of submission : 04-03-2023
#I confirm that the source file is entirely written by me
#without resorting to any dishonest means.
#website(s) : i didn't took the help of any website i have written on my own



import os
import socket 
import time
import signal

f1 = open("NR.output","w")
f2 = open("RDS.output","w")
f3 = open("TDS.output","w")
f4 = open("ADS.output","w")

K            = 20000
CLIENT_PORT  = K
NR_PORT      = K+53

bufferSize = 1024

CLIENT_ADD_PORT =('localhost',CLIENT_PORT)
NR_ADD_PORT = ('localhost',NR_PORT)

PORT_NUM_LIST = [K+54,K+55,K+56,K+57,K+58,K+59,K+60,K+61,K+62] #RDS,TDS1,TDS2,ADS1,ADS2,ADS3,ADS4,ADS5,ADS6
ADD_PORT_LIST = list(range(9))

for i in range(0,9):
    ADD_PORT_LIST[i] = ('localhost',PORT_NUM_LIST[i])

#from the given input storing the ip address and the ADS corresponding to the name

ff = open("input.txt","r")
ip_dict = {}       # dictionary with corresponding name and the  ip address
ADS_dict = {}      # dictionary with given key and the corresponding ADS 
port_num_dict ={}
port_num_dict["ADS1"] = K+57
port_num_dict["ADS2"] = K+58
port_num_dict["ADS3"] = K+59
port_num_dict["ADS4"] = K+60
port_num_dict["ADS5"] = K+61
port_num_dict["ADS6"] = K+62

flag =0
ADS_name = ""

count = 1

while True:
    line = ff.readline()
    if line == "":
        break
    else:
        arr = line.split(" ")
        if(len(arr)==2):
            change_ads = arr[0].split(".")
            l= len(arr[1])
            if(len(change_ads) == 2):
                ip_dict["ADS"+str(count)] = (arr[1])[0:l-1]
                count = count +1
            else:
                ip_dict[arr[0]] = (arr[1])[0:l-1]

            if flag ==1 : # that is it is in the ADS side
                s1 = arr[0].split(".")
                ADS_dict[s1[1]] = ADS_name

        elif(len(arr)==1) and arr[0] !="BEGIN_DATA\n" and arr[0] != "END_DATA":
            l = len(arr[0])
            s1 = (arr[0])[0:l-1]
            s2 = s1.split("_")
            ADS_name = s2[2]
            flag = 1    

def fun(ind):
    #opening a socket for the specific server
    ind_soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    ind_soc.bind(ADD_PORT_LIST[ind])

    byte_add_pair = ind_soc.recvfrom(bufferSize)
    server_name = byte_add_pair[0].decode()

    if(ind ==0):   #RDS server
    
        if(server_name[-3:]=="com"):
            ip_add1 = ip_dict["TDS_com"]
            port_num1 = PORT_NUM_LIST[1]
            f2.write(f"querey sent: {server_name}, response ip:{ip_add1} and port_num: {port_num1}\n")
            f2.close()
            ind_soc.sendto(str.encode("TDS1"),NR_ADD_PORT)
        elif(server_name[-3:]=="edu"):   
            ip_add1 = ip_dict["TDS_edu"]
            port_num1 = PORT_NUM_LIST[2]
            f2.write(f"querey sent: {server_name}, response ip:{ip_add1} and port_num: {port_num1}\n")
            f2.close() 
            ind_soc.sendto(str.encode("TDS2"),NR_ADD_PORT)

    elif(ind==1):   #TDS1 server , it will send the corresponding  ADS server name
        arr = server_name.split(".")
        ind_soc.sendto(str.encode(ADS_dict[arr[1]]),NR_ADD_PORT)

        #we should write the ip address and port number of the corresponding ADS in the file
        name1 = ADS_dict[arr[1]]
        ip_add2 = ip_dict[name1]
        port_num2 = port_num_dict[name1]
        f3.write(f"query sent: {server_name}, response ip:{ip_add2} and port_num: {port_num2}\n")
        f3.close()
        
    elif(ind==2):    #TDS2 server, it will send the corresponding  ADS server name
        arr = server_name.split(".")
        ind_soc.sendto(str.encode(ADS_dict[arr[1]]),NR_ADD_PORT)

        #we should write the ip address and port number of the corresponding ADS in the file
        name1 = ADS_dict[arr[1]]
        ip_add2 = ip_dict[name1]
        port_num2 = port_num_dict[name1]
        f3.write(f"query sent: {server_name}, response ip:{ip_add2} and port_num: {port_num2}\n")
        f3.close()

    else :
        ip_address = ip_dict[server_name]
        ind_soc.sendto(str.encode(ip_address),NR_ADD_PORT) 

        ip_add3 = ip_dict[server_name]
        f4.write(f"query sent: {server_name}, response :{ip_add3}\n")
        f4.close()



def NR_fun():
    NR_SOC = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
    NR_SOC.bind(NR_ADD_PORT)

    while(True):
        byte_add_pair = NR_SOC.recvfrom(bufferSize)
        server_name = byte_add_pair[0].decode()
        client_address = byte_add_pair[1]

        #if the server_name is bye we have to send the msg and to exit          <-
        if(server_name == "bye"):
            NR_SOC.sendto(byte_add_pair[0],CLIENT_ADD_PORT)
            break
        #else the below  code

        pid1 = os.fork()  #creating the child process in the local DNS server
        temp1 = -1
        if(pid1 == 0):
            fun(0)
            temp1 = os.getpid()
        else :
            time.sleep(1)
            NR_SOC.sendto(byte_add_pair[0],ADD_PORT_LIST[0]) # sending the server name to the root DNS (RDS) server
            addpair_form_RDS = NR_SOC.recvfrom(bufferSize)

        if(temp1 != -1):
            os.kill(temp1, signal.SIGTERM)  #child process corresponding to RDS has been  killed
           
        #upto here we have got the corresponding TDS server

        TDS_server_name = addpair_form_RDS[0].decode()
        ind = -1
        if(TDS_server_name=="TDS1"):
            ind = 1
        elif(TDS_server_name=="TDS2"):
            ind = 2 

        pid2 = os.fork()  #second child process to communicate with the TDS server
        temp2 = -1
        if(pid2 == 0):
            fun(ind) 
            temp2 = os.getpid()
        else:
            time.sleep(1)   
            NR_SOC.sendto(byte_add_pair[0],ADD_PORT_LIST[ind]) #servername , TDS address port
            addpair_from_TDS = NR_SOC.recvfrom(bufferSize)

        if(temp2!=-1):
            os.kill(temp2,signal.SIGTERM) #child process corresponding to TDS has been killed

        #upto here we got the correspondig ADS name

        ADS_server_name = addpair_from_TDS[0].decode()
        ind = -1
        if(ADS_server_name == "ADS1"):
            ind = 3      
        elif(ADS_server_name == "ADS2"):
            ind = 4
        elif(ADS_server_name == "ADS3"):
            ind = 5
        elif(ADS_server_name == "ADS4"):
            ind = 6
        elif(ADS_server_name == "ADS5"):
            ind = 7
        elif(ADS_server_name == "ADS6"):
            ind = 8

        pid3 = os.fork()   #third child process to  communicate with the ADS server   
        temp3 = -1

        if(pid3 == 0):
            fun(ind)
            temp3 = os.getpid()
        else:
            time.sleep(1)
            NR_SOC.sendto(byte_add_pair[0],ADD_PORT_LIST[ind]) #servername, corresponding ADS address port
            addpair_from_ADS = NR_SOC.recvfrom(bufferSize)     #here the IP address will be returned

        if(temp3 != -1):
            os.kill(temp3, signal.SIGTERM)     #child process corresponding to the ADS has been killed  

        f1.write(f"query that was sent: {server_name},response sent was: {addpair_from_ADS[0].decode()} \n")
        #finally we have to send the IP address to the client
        NR_SOC.sendto(addpair_from_ADS[0],CLIENT_ADD_PORT)     
                           

#1: CLIENT SOCKET
CLIENT_SOC = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)  #opening a socket for the client
CLIENT_SOC.bind(CLIENT_ADD_PORT)

#opening child process to communicate with the local DNS server
pid = os.fork()

if(pid == 0):  #that is the child process
    NR_fun()
elif pid > 0 :  # that is the parent process
    while(True):
         time.sleep(1)   # since the local DNS server should run first
         command = input("Enter the server name: ")
         time.sleep(1)
         CLIENT_SOC.sendto(str.encode(command),NR_ADD_PORT)
         byte_add_pair = CLIENT_SOC.recvfrom(bufferSize)
         ip_add_recv = byte_add_pair[0].decode()
         if(ip_add_recv == "bye"):
             f1.close()
             break
         else:
             print("DNS Mapping : ", ip_add_recv)

