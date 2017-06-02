#!/bin/bash
sudo kill -SIGTERM $(pgrep motion)
if [ $# -gt 0 ]; then
	sudo motion -s -c /home/pi/Camera/Config/motion.conf
else
	sudo motion -c /home/pi/Camera/Config/motion.conf
fi