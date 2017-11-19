#!/usr/bin/env bash
mosquitto_sub -h localhost -t home/rtl_433 --qos 1|python3 ~/writeStdInToFile.py -c outdoorSensor