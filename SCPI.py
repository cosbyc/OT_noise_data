#!/usr/bin/env python

import pyvisa as visa
import argparse

parser = argparse.ArgumentParser(description='Send message to Keysight generator')
parser.add_argument('-f', '--freq', help="Frequency to set device to", default=None, required=False)
parser.add_argument('-a', '--amp', help="Amplitude to set device to", default=None, required=False)
args = parser.parse_args()

freq=args.freq
amp=args.amp

rm = visa.ResourceManager("@py")

if freq is not None:
    instrument = rm.open_resource('USB0::2391::22279::MY59003134::0::INSTR')
    if freq == '0':
        instrument.write(f"OUTPUT1 OFF")
        print(f"Channel 1 off")
    else:        
        instrument.write(f"SOURCE1:FREQ +{freq}E6")
        instrument.write(f"OUTPUT1 ON")
        current_freq = instrument.query("SOURCE1:FREQ?")
        print(f"Frequency set to: {current_freq}")

elif amp is not None:
    instrument = rm.open_resource('USB0::2391::22279::MY59003134::0::INSTR')
    if amp == '0':
        instrument.write(f"OUTPUT1 OFF")
        print(f"Channel 1 off")
    else:        
        instrument.write(f"SOURCE1:AMP +{amp}")
        instrument.write(f"OUTPUT1 ON")
        current_amp = instrument.query("SOURCE1:AMP?")
        print(f"Amplitude set to: {current_amp}") 
    
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
