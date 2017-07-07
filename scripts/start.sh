#!/bin/bash

# Make sudo actually work
HOSTNAME=$(cat /etc/hostname)
echo "127.0.1.1 $HOSTNAME" >> /etc/hosts
hostname $HOSTNAME

ldconfig
useradd -m pi
gpasswd -a pi video

echo "allowed_users=anybody" > /etc/X11/Xwrapper.config

# View commands: echo h | cec-client -s -d 1

echo "on 0" | cec-client -s

# echo "standby 0" | cec-client -s

xinit /usr/src/app/scripts/launchBrowser.sh
