#!/bin/bash
if [ $# -gt 0 ]; then
	echo "Motion detected in zone" $1
	sudo python3 /home/pi/Camera/on_motion_script.py $1
else
	echo "All motion detected"
	sudo python3 /home/pi/Camera/on_motion_script.py
fi