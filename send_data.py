import sys
import os
import serial
import time

def read_data(addr="/dev/ttyUSB0"):
    ser = serial.Serial(addr, 9600)

    reading = ser.readline().decode('utf-8')
    tok = reading.split()
    if len(tok) != 2:
        return ""
    return tok


def append_data(filename, d):
    f = open("data/" + filename + ".txt","r")
    #fl = f.readlines()
    print("reading file..")
    fstr = f.read()
    idx = 1
    data48 = fstr.split()
    print(data48)
    f.close()

    print("writing file..")
    fr = open("data/" + filename + ".txt", "w+")
    fw = open("data/" + filename + ".js", "w+")
    fw.write(filename + "_data = [\n") 

    for i in range(1,len(data48)):
        fr.write(data48[i] + "\n")
        fw.write(data48[i] + ",\n")
    fr.write(d)
    fw.write(d + "\n]")

    fr.close()
    fw.close()
    #for ln in fl:
    #    print(ln[-2])

def scp_cmd(pemfile, filename, remotehost, remotedir):
    print("sending file..")
    cmd = 'scp -i %s data/%s.js %s:%s' % (pemfile, filename, remotehost, remotedir)
    print(cmd)
    os.system(cmd)

#python3 send_data.py /Users/robertchuchro/.ssh/shiftry.pem ec2-user@52.10.49.156 /home/ec2-user/data
def main():
    if len(sys.argv) != 4:
        print("Need to supply paramters: 1. .pem file 2. scp address 3. remote dir")
        exit()
    for i in range(1,len(sys.argv)):
        print("param " + str(i) + ": " + sys.argv[i])

    pemfile = sys.argv[1]
    remotehost = sys.argv[2]
    remotedir = sys.argv[3]

    while True:
        #read data here
        d_hum, d_temp = read_data()

        append_data("humidity", d_hum)
        append_data("temperature", d_temp)

        scp_cmd(pemfile, "humidity", remotehost, remotedir)
        scp_cmd(pemfile, "temperature", remotehost, remotedir)

        time.sleep(3600)


if __name__ == "__main__":
    main()
