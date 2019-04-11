__author__ = 'Lehrfeld Artur'
import struct
import sys
import socket
import subprocess
#------------------------------------------------WLASNE FUNKCJE
def cidr_to_netmask(cidr):
    host_bits=32-int(cidr)
    netmask=socket.inet_ntoa(struct.pack('!I',(1<<32)-(1<<host_bits)))
    return netmask

def get_subnet_mask(ip):
    config=subprocess.Popen('ipconfig',stdout=subprocess.PIPE)
    while True:
        line=config.stdout.readline()
        if ip.encode() in line:
            break
    mask=config.stdout.readline().split(b':')[-1].replace(b' ',b'').decode()
    return mask

def int_to_bin(tab):
    i = 0
    for x in tab:
        tab[i] = bin(x)[2:].zfill(8)
        i += 1
    return tab

def splitting_the_octets(tab):
    tab_list=[]
    for j in range(0,len(tab)):
        for i in range(0, len(tab[j])):
            tab_list.append(tab[j][i])
            i += 1
        j+=1
    return tab_list

def combining_into_octets(tab_list):
    tab=["","","",""]
    for j in range(0,8):
        tab[0] += str(tab_list[j])
    for j in range(8, 16):
        tab[1]+= str(tab_list[j])
    for j in range(16, 24):
        tab[2]+= str(tab_list[j])
    for j in range(24, 32):
        tab[3] += str(tab_list[j])
    return tab

def binary_to_decimal(tab_binary):
    tab_decimal=[int(tab_binary[0],2),int(tab_binary[1],2),int(tab_binary[2],2),int(tab_binary[3],2)]
    return tab_decimal;

def negation(tab):
    pom=list()
    for x in tab:
        if(x=='0'):
            pom.append('1')
        else:
            pom.append('0')
    return pom

def write_with_dots_to_file(file, tab):
    i=0
    for x in tab:
        file.write(str(x))
        i += 1
        if (i != 4):
            file.write(".")

#------------------------------------------------Obsluga plikow
file=open("wynik.txt",'w')
#------------------------------------------------Organizacja danych

dane=['','']
if(len(sys.argv)==1):
    hostname = socket.gethostname()
    dane[0]=socket.gethostbyname(hostname)
    ip = dane[0].split(".")
    dane[1]=get_subnet_mask(dane[0])[:-2]
    mask=dane[1].split(".")
else:
    dane=str(sys.argv[1])
    if "/" in dane:
        dane=dane.split("/")
        ip=dane[0].split(".")
        mask=dane[1].split(".")
    else:
        print("Wrong ip/mask passed in arguments")
        sys.exit(0)
print("Arguments: (IP,Netmask)")
print(dane)
file.write("Data:")
file.write("\nIP: "+dane[0])
if(len(sys.argv)==2):
    file.write("\nMask CIDR: "+dane[1])

#------------------------------------------------WALIDACJA DANYCH
i=0
try:
    for x in ip:
        ip[i] = int(x)
        i += 1
except ValueError:
    print("Wrong arguments")
    sys.exit()

if(len(sys.argv)!=1):
    if len(ip) != 4 or len(mask) != 1 :
        print("IP musi posiadac 4 oktety, a maska byc w formacie CIDR!")
        sys.exit()
    mask[0]=int(mask[0])
    for x in ip:
        if x < 0 or x > 255:
            print("W IP podano liczbe ze zlego zakresu! (0-255)")
            sys.exit()
    if mask[0] < 0 or mask[0] > 24:
        print("Maska powinna byc z zakresu: (1-32)")
        sys.exit()
#------------------------------------------------Private/Public IP
if(ip[0]=='10' or (ip[0]=='192'and ip[1]=='168') or (ip[0]=='172' and '16'<=ip[1]<='31') ):
    print("\nIP is private")
    file.write("\nIP is private")
else:
    print("\nIP is public")
    file.write("\nIP is public")

#------------------------------------------------Zamiana na binarne
ip=int_to_bin(ip)
if(len(mask)==1):
    mask=cidr_to_netmask(mask[0])
    mask = mask.split(".")
file.write("\n\nMask decimal: ")
write_with_dots_to_file(file,mask)
i=0
for x in mask:
    mask[i]=int(x)
    i+=1
mask=int_to_bin(mask)

print("\nMask binary:")
print(mask)
print("IP binary:")
print(ip)
file.write("\nMask binary: ")
write_with_dots_to_file(file,mask)
file.write("\nIP binary: ")
write_with_dots_to_file(file,ip)
print("-------------------------------------------------")
#------------------------------------------------Dzielenie oktetow na pojedyncze znaki
ip_list=splitting_the_octets(ip)
mask_list=splitting_the_octets(mask)
#------------------------------------------------Network adress
network = []
for x, y in zip(ip_list, mask_list):
    network.append(int(x, 2) & int(y, 2))

print("\nNetwork:")
network_octets=combining_into_octets(network)
network_decimal=binary_to_decimal(network_octets)
print(network_octets)
print(network_decimal)
file.write("\n\nNetwork binary: ")
write_with_dots_to_file(file,network_octets)
file.write("\nNetwork decimal: ")
write_with_dots_to_file(file,network_decimal)
#------------------------------------------------NetworkClassaw
klasa=""
if(network[0]==0):
    klasa="A"
elif(network[1]==0):
    klasa="B"
elif(network[2]==0):
    klasa="C"
elif(network[3]==0):
    klasa="D"
else:
    klasa="E"
print("Klasa sieci: "+klasa)
file.write("\nNetwork class: "+klasa)
#------------------------------------------------Broadcast
broadcast=[]
for x, y in zip(ip_list, negation(mask_list)):
    broadcast.append(int(x, 2) | int(y, 2))
print("\nBroadcast:\n"+str(combining_into_octets(broadcast))+"\n"+str(binary_to_decimal(combining_into_octets(broadcast))))
file.write("\n\nBroadcast binary: ")
write_with_dots_to_file(file,combining_into_octets(broadcast))
file.write("\nBroadcast decimal: ")
write_with_dots_to_file(file,binary_to_decimal(combining_into_octets(broadcast)))
#------------------------------------------------First and last host
first=network
if(first[-1]==0):
    first[-1]=1
else:
    first[-1]=0

last=broadcast
if(last[-1]==0):
    last[-1]=1
else:
    last[-1]=0

first=combining_into_octets(first)
last=combining_into_octets(last)
print("\nFirst host:\n"+str(first))
print(binary_to_decimal(first))
print("\nLast host:\n"+str(last))
print(binary_to_decimal(last))
file.write("\n\nFirst host binary: ")
write_with_dots_to_file(file,first)
file.write("\nFirst host decimal: ")
write_with_dots_to_file(file,binary_to_decimal(first))
file.write("\n\nLast host binary: ")
write_with_dots_to_file(file,last)
file.write("\nLast host decimal: ")
write_with_dots_to_file(file,binary_to_decimal(last))
#------------------------------------------------Number of hosts
i=0
for x in negation(mask_list):
    if(x=='1'):
        i+=1
nrhosts=(2 ** i  - 2)
print("\nMax hosts in network: ")
print(nrhosts)
file.write("\n\nMax hosts in network: "+str(nrhosts))
#------------------------------------------------Ping if host
broadcast=combining_into_octets(broadcast)
if(ip==network_octets or ip==broadcast):
    print("IP is a host")
else:
    print("\nDo you want to ping this IP? y=yes, n=no")
    wybor=input()
    if(wybor=='y'):
        command=['ping', dane[0]]
        subprocess.call(command)
file.close()