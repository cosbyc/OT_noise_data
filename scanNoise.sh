#!/bin/bash
CONFIG_DESCRIPTION=''
CONFIG_DESCRIPTION=$1
#CALIBRATION='1548'
CALIBRATION=$2


FREQ_VALUES=(0 2) #MHz
#FREQ_VALUES=(0 2 2.5 3 3.5 4 4.5 5 6 7 8 8.5 9 9.5 10 10.5 11 11.5 12 13) #MHz
#FREQ_VALUES=(0 2 3 4 6 7 8 9 10 11 13) #MHz

PYLINE_FIRST=$(wc -l < noiseData.csv)
PYLINE_LAST=$(($PYLINE_FIRST+${#FREQ_VALUES[@]}))

echo "$CONFIG_DESCRIPTION,pyrange[$PYLINE_FIRST:$PYLINE_LAST],,,,,,,,," >> noiseData.csv
for FREQ in "${FREQ_VALUES[@]}"; do
    echo "Setting Keysight to $FREQ MHz"
    python3 SCPI.py -f "$FREQ"
    sleep 1
    
    while true; do
	echo "Starting noise measurement for $FREQ MHz"
	
	RUN_NUMBER=""
	while IFS= read -r line; do
	    #echo "$line" 
	    if [[ "$line" == *"Failed to lock all links after a general reset, disabling problematic OpticalGroups and continuing"* ]]; then
	        echo "One or both modules didn't lock. Killing and retrying..."
	        pkill -9 "runCalibration"
	        sleep 5
	        continue 2
	        fi
	    
	    if [[ "$line" =~ Run\ ([0-9]+)\ stopped ]]; then
	        RUN_NUMBER="${BASH_REMATCH[1]}"
	        echo "Extracted run number: $RUN_NUMBER"
	    fi
	done < <(runCalibration -r "$CALIBRATION" -b -c pedenoise)
	
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

python3 SCPI.py -f 0

cp -f noiseData.csv OT_noise_data/noiseData.csv
cd OT_noise_data/
git add noiseData.csv
git commit -m "Adding runs: $CONFIG_DESCRIPTION"
git push origin

python3 csvPlotter.py -f "$PYLINE_FIRST" -l "$PYLINE_LAST" -i noiseData.csv -t "$CONFIG_DESCRIPTION"

cd ../
