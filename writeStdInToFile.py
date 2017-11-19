#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import sys
import getopt
import json

configFilePath = r'config.properties'


def non_blank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line


def read_sensor_data(configsection):

    TEMP_FILE = configsection['TEMP_FILE']
    BATT_FILE = configsection['BATT_FILE']
    HUMID_FILE = configsection['HUMID_FILE']
    DEVICE_ID = configsection['DEVICE_ID']

    print("Listening for device: '{}'".format(DEVICE_ID))

    for line in non_blank_lines(sys.stdin):

        print("Event received ")
        jsondata = json.loads(line)

        if 'device' not in jsondata:
            print('Ignoring event in unknown format (no device)')
            continue

        temperature = "{:.3f}".format(jsondata["temperature_C"])
        humidity = "{:.3f}".format(jsondata["humidity"])
        batterystatus = jsondata["battery"]
        deviceid = "{:}".format(jsondata["device"])

        print("DeviceId: '{}' ".format(deviceid))

        if deviceid != DEVICE_ID:
            continue

        print("Copying input to file")

        if batterystatus.lower() == "ok":
            batterystatus = 100
        else:
            batterystatus = 20

        batterystatus = "{:}".format(batterystatus)

        print("temp:" + temperature)
        file = open(TEMP_FILE, "w")
        file.write(temperature)
        file.close()

        print("humidity:" + humidity)
        file = open(HUMID_FILE, "w")
        file.write(humidity)
        file.close()

        print("battery status: " + batterystatus)
        file = open(BATT_FILE, "w")
        file.write(batterystatus)
        file.close()

        print("Done.")


def usage_and_exit(exitcode):
    print('Usage:')
    print('writeStdInToFile.py -c <configSection>')
    sys.exit(exitcode)


def main(argv):
    print("Starting up..")

    config = ''
    try:
        opts, args = getopt.getopt(argv, "hc:", ["config="])
    except getopt.GetoptError:
        usage_and_exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage_and_exit(0)
        elif opt in ("-c", "--config"):
            config = arg
        else:
            assert False, "unhandled option: " + opt

    if config == '':
        usage_and_exit(2)

    print("Config used: '{}'".format(config))

    configp = configparser.ConfigParser()
    configp.read(configFilePath)

    configsection = configp[config]

    try:
        read_sensor_data(configsection)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
