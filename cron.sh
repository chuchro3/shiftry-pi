#!/bin/bash

git -C /home/pi/Repos/shiftry-pi/ pull

python3 /home/pi/Repos/shiftry-pi/send_data.py /home/pi/.ssh/shiftry.pem ec2-user@52.10.49.156 /home/ec2-user/data

scp -i /home/pi/.ssh/shiftry.pem /home/pi/logs/shiftry.log ec2-user@52.10.49.156:/home/ec2-user/data

#sudo halt
