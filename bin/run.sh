#!/bin/bash

echo "Updating service config"
sudo cp /home/opc/hardTextScanner/config/hardTextScanner.service /etc/systemd/system/

echo "Reloading service daemon"
sudo systemctl daemon-reload

echo "Stopping hardTextScanner"
sudo systemctl stop hardTextScanner &

echo "Kill all zombies"
ps ax | grep hardTextScanner | grep uwsgi | awk {'print $1'} | xargs kill -9

echo "Restarting"
sudo systemctl restart hardTextScanner

echo "Service started"
sudo systemctl status hardTextScanner
