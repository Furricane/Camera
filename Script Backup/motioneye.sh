#!/bin/bash
#sudo cp /usr/local/share/motioneye/extra/motioneye.systemd-unit-local /etc/systemd/system/motioneye.service
#sudo systemctl daemon-reload
#sudo systemctl enable motioneye
#sudo systemctl start motioneye -c /home/pi/Camera/Config/motioneye.conf
sudo kill -SIGTERM $(pgrep meyectl)
sudo -u pi meyectl startserver -b -c /home/pi/motioneye/motioneye.conf