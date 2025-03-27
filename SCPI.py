#!/usr/bin/env python

import pyvisa as visa
import argparse

parser = argparse.ArgumentParser(description='Send message to Keysight generator')
parser.add_argument('-f', '--freq', help="Frequency to set device to", default=None, required=False)
args = parser.parse_args()

rm = visa.ResourceManager("@py")

if args.freq is not None:
    instrument = rm.open_resource('USB0::2391::22279::MY59003134::0::INSTR')
    instrument.write(f"SOURCE1:FREQ +{args.freq}E6")
    current_freq = instrument.query("SOURCE1:FREQ?")

    print(f"Frequency set to: {current_freq}")
else:
    print("Scanning for devices...")
    resources = rm.list_resources()
    for resource in resources:
        try:
            instrument = rm.open_resource(resource)
            idn = instrument.query("*IDN?")
            print(f"{resource} => {idn}")
        except Exception as e:
            print(f"Failed to query {resource}: {e}")
