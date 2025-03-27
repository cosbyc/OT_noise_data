#!/bin/bash

FREQ_VALUES=(2 2.5 3 3.5 4 4.5 5 5.5 6 7 8 8.5 9 9.5 10 10.5 11 11.5 12) #MHz

for FREQ in "${FREQ_VALUES[@]}"; do
    echo "Setting Keysight to $FREQ MHz"
    python3 SCPI.py -f "$FREQ"
    sleep 1
    
    while true; do
	echo "Starting noise measurement for $FREQ MHz"
	
	RUN_NUMBER=""
	while IFS= read -r line; do
	    echo "$line"  # Debugging output
	    
	    if [[ "$line" == *"Failed to lock all links after a general reset, disabling problematic OpticalGroups and continuing"* ]]; then
	        echo "One or both modules didn't lock. Killing and retrying..."
	        pkill -9 "runCalibration"
	        sleep 5
	        continue 2  # Restart the outer loop
	        fi
	    
	    if [[ "$line" =~ Run\ ([0-9]+)\ stopped ]]; then
	        RUN_NUMBER="${BASH_REMATCH[1]}"
	        echo "Extracted run number: $RUN_NUMBER"  # Debugging output
	    fi
	done < <(runCalibration -r 273 -b -c pedenoise)
	
	if [[ -n "$RUN_NUMBER" ]]; then
	    echo "Finished run with: $FREQ MHz, Run number: $RUN_NUMBER"
	    python3 spud.py -s -r "$RUN_NUMBER" --noiseFreq "$FREQ"
	    break  # Move to the next parameter value
	else
	    echo "Run number not found....  trying again" # maybe was one of those rare weird crashes
	    sleep 1
	fi
    done
done
