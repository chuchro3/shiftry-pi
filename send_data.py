import sys
import os
import serial
import datetime
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
    if len(tok) != 4:
        return (-1,-1,-1,-1) 
    return tok


def append_data(filename, d, smoothen=False):
    f = open(_DATA_DIR + filename + ".txt","r")
    #print("reading file..")
    fstr = f.read()
    idx = 1
    data48 = fstr.split('\n')[:200]
    #print(data48)
    f.close()

    if smoothen:
        prev = float(data48[-1])
        curr = float(d)
        delta = abs(prev - curr)
        if delta > 4.0:
            d = str(round(.75*curr + .25*prev, 2))

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
    return data48[-1]

def take_picture(filename = "photo.jpg"):
    camera = PiCamera()
    camera.rotation = 270
    camera.start_preview()
    sleep(2)
    print("capturing photo..")
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

def getHeartbeat():
    
    with open(_DATA_DIR + "heartbeat.txt", "r") as f:
        date_str = f.read().strip()
        time = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    return time

def setHeartbeat(time):

    with open(_DATA_DIR + "heartbeat.txt", "w+") as f:
        f.write(str(time))

#python3 send_data.py /Users/robertchuchro/.ssh/shiftry.pem ec2-user@52.10.49.156 /home/ec2-user/data
def main():
    time = datetime.datetime.now()
    heartbeat = getHeartbeat()
    if time < heartbeat:
        print("Snoozing ... " + str(time))
        exit()

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

    while True:
        #read data here
        d_hum, d_temp, d_moist, d_soil_temp = read_data(ser)
        if d_hum != -1:
            break
    
    if (time.hour == 9 and time.minute < 30):
        take_picture("photo.jpg")
        scp_cmd(pemfile, "photo.jpg", remotehost, remotedir)

    prev_hum = append_data("humidity", d_hum, True)
    prev_temp = append_data("temperature", d_temp, True)
    prev_soil_temp = append_data("soil_temperature", d_soil_temp, False)
    append_data("moisture", d_moist, False)
    append_data("time", '\"' + time.strftime("%m/%d/%Y, %I:%M:%S %p") + '\"', False)


    ser.close()

    delta_hum  = abs( float(prev_hum)  - float(d_hum)  )
    delta_temp = abs( float(prev_temp) - float(d_temp) )
    delta_soil_temp = abs( float(prev_soil_temp) - float(d_soil_temp) )
    delay = int( max(10, 24 - delta_temp - (delta_hum / 2) - delta_soil_temp) )
    setHeartbeat(time + datetime.timedelta(minutes=delay))
    
    scp_cmd(pemfile, "humidity.js", remotehost, remotedir)
    scp_cmd(pemfile, "temperature.js", remotehost, remotedir)
    scp_cmd(pemfile, "soil_temperature.js", remotehost, remotedir)
    scp_cmd(pemfile, "moisture.js", remotehost, remotedir)
    scp_cmd(pemfile, "time.js", remotehost, remotedir)

if __name__ == "__main__":
    main()
