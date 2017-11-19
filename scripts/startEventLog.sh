#!/usr/bin/env bash
mosquitto_sub -h localhost -q 1 -t home/rtl_433 >>/opt/sensor/temperature-event.log 2>>/opt/sensor/temperature-client-error.log
