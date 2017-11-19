#!/bin/sh
scp *.py rpi1:~
scp config.properties rpi1:~
scp scripts/*.sh rpi1:~

# scp bridge.conf rpi1:/etc/mosquitto/conf.d

ssh rpi1 "~/auto-reload-collector.sh"
