#!/bin/bash
sudo kill -SIGTERM $(pgrep motion)
sudo motion -c /home/pi/Camera/Config/motion.conf