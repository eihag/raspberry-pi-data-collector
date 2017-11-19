#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import configparser
import sys
import getopt
import json
import time
import logging
from timeout import timeout


FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

API_VERSION = '2016-02-03'
configFilePath = r'config.properties'


def non_blank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line


def read_sensor_data(configsection):

    iothub_hostname = configsection['IOTHUB_HOSTNAME']
    iothub_device_id = configsection['IOTHUB_DEVICE_ID']
    iothub_sas_token = configsection['IOTHUB_SAS_TOKEN']

    sensor_device_id = configsection['DEVICE_ID']

    logger.info("Listening for device: '{}'".format(sensor_device_id))

    for line in non_blank_lines(sys.stdin):
        logger.info("Event received ")
        jsondata = json.loads(line)

        if 'device' not in jsondata:
            logger.info('Ignoring event in unknown format (no device)')
            continue

        device_id = "{:}".format(jsondata["device"])

        logger.info("DeviceId: '{}' ".format(device_id))
        # print("sas: '{}'".format(iothub_sas_token))

        if device_id != sensor_device_id:
            continue

        logger.info("Sending event to iothub")
        send_to_iothub(iothub_hostname, iothub_device_id, iothub_sas_token, line)

        # throttle sending data to iothub.
        time.sleep(20)


def send_to_iothub(iothub_hostname, iothub_device_id, iothub_sas_token, message):
    while True:
        try:
            url = 'https://%s/devices/%s/messages/events?api-version=%s' % (iothub_hostname, iothub_device_id, API_VERSION)
            http_call(url, iothub_sas_token, message)
            return
        except Exception as e:
            logger.exception(e)
            time.sleep(30)
            continue
        else:
            break

@timeout(30)
def http_call(url, iothub_sas_token, message):
    r = requests.post(url, headers={'Authorization': iothub_sas_token}, data=message)
    logger.info("result: {} {}".format(r.text, r.status_code))


def usage_and_exit(exitcode):
    logger.info('Usage:')
    logger.info('sendStdInToIothub.py -c <configSection>')
    sys.exit(exitcode)


def main(argv):
    logger.info("Starting up..")

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

    logger.info("Config used: '{}'".format(config))

    configp = configparser.ConfigParser()
    configp.read(configFilePath)

    configsection = configp[config]

    try:
        read_sensor_data(configsection)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
