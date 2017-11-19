## raspberry-pi-data-collector ##
Collect temperature data from 433mhz pool sensor using SDR (Software-defined radio) on Raspberry Pi.

## Flow
1. Use SDR to collect data from 433 mhz temperature sensor
2. Send data to local MQTT server
3. A number of clients subscribe to MQTT data and do the following:
    - Write temperature to local file (see [homebridge-sensor-data-file]())
    - Write to local event log
    - Send data to Azure IotHub (see [amqp-influxdb-forwarder](https://github.com/eihag/amqp-influxdb-forwarder))
 


## Temperature sensor
 * "TFA Venice" pool thermometer, https://www.amazon.de/TFA-Dostmann-Poolthermometer-30-3056-10-Wassertemperatur/dp/B010NSG4V2

First I tried the WeatherHawk Myblue-T bluetooth dongle, inspired by this article:
https://medium.com/jesseproudman/raspberry-pi-weatherhawk-myblue-t-bluetooth-temperature-sensors-9dac2c8be482.
However, the range of the bluetooth dongle is extremely limited. I therefore moved on to a 433mhz solution.

For some reason the TFA sensor is detected by RTL_433 as "Ambient Weather F007TH Thermo-Hygrometer".
This could indicate it is an OEM product being sold under various brands.


## SDR radio
SDR radio for Raspberry Pi:
* NooElec Smart SDR, https://www.amazon.de/gp/product/B01GDN1T4S

Works perfectly with the RTL_433 project.

## Setup

#### Setup RTL 433
<pre>
sudo apt-get install libtool libusb-1.0.0-dev librtlsdr-dev rtl-sdr

git clone https://github.com/merbanan/rtl_433.git

cd rtl_433/
mkdir build
cd build
cmake ../
make
sudo make install

</pre>
#### Setup local MQTT server
<pre>
sudo apt-get install mosquitto mosquitto-clients
</pre>

you may want to change the config if you plan to handle large bursts of messages
<pre>
sudo vim /etc/mosquitto/mosquitto.conf
sudo systemctl restart mosquitto
</pre>
add
<pre>
max_inflight_messages 10000
max_queued_messages 40000
</pre>



#### Collect samples and send to local MQTT server
<pre>
rtl_433 -F json -C si -U | mosquitto_pub -t home/rtl_433 -l
</pre>
or use startCollector.sh script

Test everything is working with simple client
<pre>
mosquitto_sub -h localhost -t home/rtl_433
</pre>


#### Subscribe to topic and write to local file
This is used by homebridge plugin to provide Apple HomeKit access to data - I can ask Siri for my pool temperature.
<pre>
mosquitto_sub -h localhost -t home/rtl_433|~/writeStdInToFile.py -c poolSensor
</pre>
or use startLocalFile.sh script

#### Subscribe to topic and generate local event log
<pre>
mosquitto_sub -h localhost -t home/rtl_433>>/opt/sensor/temperature-event.log 2>>/opt/sensor/tempeature-client-error.log
</pre>
or use startEventLog.sh script

#### Subscribe to topic and send to Azure IotHub
First we need a SAS (shared access signature) token for our device
https://github.com/Azure/iothub-explorer
<pre>
npm install -g iothub-explorer
iothub-explorer login your-iot-connectionstring
iothub-explorer create yourDeviceName
iothub-explorer sas-token -d 315360000 yourDeviceName
</pre>
(-d 315360000 = Token expires in 10 years)

I spent some time bridging Mosquitto MQTT to Iothub, setting up Mosquitto, Azure certificates, etc. 

Then I realized the easiest way to send data to Azure IotHub was a simple python script performing a HTTP POST:
<pre>
mosquitto_sub -h localhost -t home/rtl_433|~/sendStdInToIothub.py -c poolSensor
</pre>


To monitor activity on Azure IotHub:
<pre>
iothub-explorer monitor-events --login HostName=<hostname>.azure-devices.net\;SharedAccessKeyName=iothubowner\;SharedAccessKey=<mysecretkey>
</pre>

## Replay old events

<pre>
cat event-output-aa | mosquitto_pub -t home/rtl_433 -l
</pre>

or start with latest entries

<pre>
cat event-output-aa | perl -e 'print reverse &lt;&gt;' | mosquitto_pub -t home/rtl_433 -l
</pre>

or replay given date
<pre>
grep 2017-08-30 temperature-event.log | mosquitto_pub -t home/rtl_433 -l
</pre>

#### Local dev install of Mosquitto on Mac
<pre>
brew install mosquitto
brew services start mosquitto
</pre>

Test publication of event
<pre>
mosquitto_pub -f temperature-sample.json -t home/rtl_433
</pre>

