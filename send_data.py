import sys
import os
import serial
import picamera
from picamera import PiCamera
from time import sleep

_DATA_DIR = "/home/pi/Repos/shiftry-pi/data/"

def read_data(ser):

    #do a reading to clear any stale data
    try:
        buffer = ser.readline().decode('utf-8')
    except UnicodeDecodeError:
        print("Warning: UnicodeDecodeError while buffering")

    reading = ser.readline().decode('utf-8')
    tok = reading.split()
    print(tok)
    if len(tok) != 3:
        return (-1,-1,-1) 
    return tok


def append_data(filename, d):
    f = open(_DATA_DIR + filename + ".txt","r")
    #print("reading file..")
    fstr = f.read()
    idx = 1
    data48 = fstr.split()
    #print(data48)
    f.close()

    #print("writing file..")
    fr = open(_DATA_DIR + filename + ".txt", "w+")
    fw = open(_DATA_DIR + filename + ".js", "w+")
    fw.write(filename + "_data = [\n") 

    for i in range(1,len(data48)):
        fr.write(data48[i] + "\n")
        fw.write(data48[i] + ",\n")
    fr.write(d)
    fw.write(d + "\n]")

    fr.close()
    fw.close()

def take_picture(filename = "photo.jpg"):
    camera = PiCamera()
    camera.rotation = 270
    camera.start_preview()
    sleep(2)
    #print("capturing photo..")
    try:
        camera.capture(_DATA_DIR + filename)
    except picamera.exc.PiCameraRuntimeError:
        print("There was an error capturing the photo")
    finally:
        camera.stop_preview()
        camera.close()

def scp_cmd(pemfile, filename, remotehost, remotedir):
    #print("sending file..")
    cmd = 'scp -i %s %s%s %s:%s' % (pemfile, _DATA_DIR, filename, remotehost, remotedir)
    #print(cmd)
    os.system(cmd)

#python3 send_data.py /Users/robertchuchro/.ssh/shiftry.pem ec2-user@52.10.49.156 /home/ec2-user/data
def main():
    if len(sys.argv) != 4:
        print("Need to supply paramters: 1. .pem file 2. scp address 3. remote dir")
        exit()
    #for i in range(1,len(sys.argv)):
    #    print("param " + str(i) + ": " + sys.argv[i])

    pemfile = sys.argv[1]
    remotehost = sys.argv[2]
    remotedir = sys.argv[3]
    
    #addr="/dev/ttyUSB0"
    addr="/dev/ttyACM0"
    try:
        ser = serial.Serial(addr, 9600)
    except serial.SerialException:
        print("Error: Could not open serial connection for reading")
        return
    #except FileNotFoundError as e:
    #    print(e.filename + " not found")
    #    return

    while True:
        #read data here
        d_hum, d_temp, d_moist = read_data(ser)
        if d_hum != -1:
            break

    take_picture("photo.jpg")

    append_data("humidity", d_hum)
    append_data("temperature", d_temp)
    append_data("moisture", d_moist)

    scp_cmd(pemfile, "humidity.js", remotehost, remotedir)
    scp_cmd(pemfile, "temperature.js", remotehost, remotedir)
    scp_cmd(pemfile, "moisture.js", remotehost, remotedir)
    scp_cmd(pemfile, "photo.jpg", remotehost, remotedir)

    ser.close()

if __name__ == "__main__":
    main()
