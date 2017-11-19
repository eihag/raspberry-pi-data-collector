#!/usr/bin/env bash
rtl_433 -F json -C si -U | mosquitto_pub -t home/rtl_433 -l --qos 1