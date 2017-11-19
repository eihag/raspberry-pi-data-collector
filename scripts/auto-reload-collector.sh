#!/bin/sh
/usr/bin/pkill rtl_433
/usr/bin/pkill writeStdInToFile
/usr/bin/pkill sendStdInToIothub
/usr/bin/pkill mosquitto_sub
/usr/bin/screen -d -m -S rtl bash ~/startCollector.sh
/usr/bin/screen -d -m -S poolfile bash ~/startLocalFilePool.sh
/usr/bin/screen -d -m -S outdoorfile bash ~/startLocalFileOutdoor.sh
/usr/bin/screen -d -m -S pooliot bash ~/startIotHubPool.sh
/usr/bin/screen -d -m -S outdooriot bash ~/startIotHubOutdoor.sh
/usr/bin/screen -d -m -S eventlog bash ~/startEventLog.sh
