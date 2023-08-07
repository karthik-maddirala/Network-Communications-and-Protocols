import random

file = open('input.txt', 'r')
CRC_file = open('output.txt', 'w')
errordet_file =  open('error_detect.txt', 'w')
burstdet_file = open('bursty_detect.txt', 'w')

p = '100000111'

def find_xor(temp, G):
    temp = temp.lstrip('0')
    ans = str()
    G = G + '0' * (len(temp)-len(G))
    for i in range(len(temp)):
        if(temp[i] != G[i]):
            ans += '1'
        else:
            ans += '0'  
    ans = ans.lstrip('0')
    return ans  

def remove_rem(temp, G):
    ans = str()
    G = G + '0' * (len(temp)-len(G))
    for i in range(len(temp)):
        if(temp[i] != G[i]):
            ans +='1'
        else:
            ans +='0'

    return ans 

def find_rem(s):                           #it will return the remainder when string is divided by given equation
    s = s + "0" * (len(p)-1)
    G = p
    #step-1: divide s with G 
    rem = ''
    temp='0'
    res = ''

    for i in range(len(s)):
        if(int(temp) < int(G)):
            res += '0'
            temp += s[i]
        else:
            res = res +'1'
            rem = find_xor(temp,G)
            temp = rem + s[i] 

    if(int(G)>int(temp)): 
        res +='0'
        rem = temp
    else:
        res = res + '1'
        rem = find_xor(temp, G)

    return rem    


def find_CRC(s):                            #it will return T(x) i.e s - R(x)  really it is s xor R(x)
    CRC_file.write("Input: "+s + '\n') 
    rem = find_rem(s)                       #it will find the remainder when s given binary form is dividied with given equation   

    g = '0' * (len(s)-len(rem)) + rem       #adding zeros before remainder to do xor operation 
    T = remove_rem(s, g)
    return T

def get_corrupt_string(T, num, ind):         #it will give the corrupted  string by giving the CRC string
    T_new = T
    if(ind ==0 ):                            #in case of error detection
        for  i in range(num):
            n1 = random.randint(0,len(T)-1)
            if(T[n1]=='0'):
                T_new = T_new[0:n1]+'1'+T_new[n1+1:len(T)] 
            else:
                T_new = T_new[0:n1]+'0'+T_new[n1+1:len(T)] 

    else:                                    #in case of bursty detection
        str1 = T[num:num+6]
        flip_str1 = str()
        for i in range(6):
            if(str1[i] == '0'):
                flip_str1 +='1'
            else:
                flip_str1 +='0'  
        T_new = T[0:num] + flip_str1 + T[num+6:len(T)]

    return T_new

def error_detection(line, T):
    errordet_file.write("Original String: "+ line)
    errordet_file.write("Original String with CRC: "+ T + '\n')
    for i in range(10):
        num = random.randint(3,135)
        if(num%2 == 0):
            num +=1
        corrupt_str = get_corrupt_string(T, num,0)    
        errordet_file.write("Corrupted String: "+ corrupt_str + '\n')
        errordet_file.write("Number of Errors Introduced: "+ str(num) + '\n')
        rem = find_rem(corrupt_str)
        rem = rem.lstrip('0')
        if(rem == ''):
            errordet_file.write("CRC Check: Error not Detected\n\n")
        else:
            errordet_file.write("CRC Check: Error Detected\n\n")

def bursty_detection(line,T):
    burstdet_file.write("Original String: "+line)
    burstdet_file.write("Original String with CRC: "+T+ '\n')
    for i in range(5):
        num = random.randint(100,110)
        corrupt_str =get_corrupt_string(T,num, 1)
        burstdet_file.write("Corrupted  String: "+ corrupt_str + '\n')
        burstdet_file.write("Number of Errors Introduced: 6\n")
        rem  = find_rem(corrupt_str)
        rem = rem.lstrip('0')
        if(rem == ''):
            burstdet_file.write("CRC Check: Error not Detected\n\n")
        else:
            burstdet_file.write("CRC Check: Error Detected\n\n")    

count = 1
for line in file:
    T = find_CRC(line.strip())                #it will find the corresponding CRC line
    CRC_file.write("CRC: "+ T + '\n\n')

    errordet_file.write("INPUT: "+str(count) + '\n')
    burstdet_file.write("INPUT: "+str(count) + '\n')
    error_detection(line, T)
    bursty_detection(line,T)
    count +=1

file.close()
CRC_file.close()
errordet_file.close()
burstdet_file.close()
