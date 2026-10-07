#!/bin/sh
#
#   Copyright (C) 2020 Sean D'Epagnier
#
# This Program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.  

# Start serial terminal
#/usr/sbin/startserialtty &

DEBUG=/tmp/bootlocal.log
#DEBUG=/dev/stdout
echo -ne "\033[9;0]" > /dev/tty1 # disable blanking
echo -e '\033[?16;0;224c' > /dev/tty1 # stop cursor from blinking

# use sdtool to disallow writing to sd card
#/opt/sdtool /dev/mmcblk0 lock

# use hdparm to disallow mounting rw
#hdparm -r1 /dev/mmcblk0
hdparm -r1 /dev/mmcblk0p1
#hdparm -r1 /dev/mmcblk0p2

# ensure root fs is readonly
#mount /dev/mmcblk0p2 -o remount,ro

# more sane date... need to be within 20 years or so for
# gps to set the date correctly as well...
date -s 202003141100

chown tc /var/lock

date >> $DEBUG
echo 'starting runit' >> $DEBUG
su tc -c 'tce-load -i runit' > /dev/null

runsvdir /service &
# display splash screen
date >> $DEBUG
echo 'loading wiringpi' >> $DEBUG
chpst -utc tce-load -i wiringPi  >> $DEBUG

date >> $DEBUG
echo 'showing splash' >> $DEBUG
micropython /opt/hatconfig.py >> $DEBUG
/opt/splash spi & >> $DEBUG

# load python
PYTHON=python`cat /opt/python`

date >> $DEBUG
echo 'loading python' >> $DEBUG
time chpst -utc tce-load -i $PYTHON 2>> $DEBUG

# create python3 symlink
ln -s /usr/local/bin/$PYTHON /usr/local/bin/python3

date >> $DEBUG
echo 'copying python pyc' >> $DEBUG
#cp -r /tmp/tcloop/python3.6/usr/local/lib/python3.6/__pycache__/* /usr/local/lib/python3.6/__pycache__
#touch /usr/local/lib/python3.6/__pycache__/*

date >> $DEBUG
echo 'loading serial drivers' >> $DEBUG
chpst -utc tce-load -i usb-serial-4.9.22-piCore-v7 > /dev/null
chpst -utc tce-load -i usb-serial-4.9.22-piCore > /dev/null
/sbin/modprobe i2c-dev

# start pypilot
date >> $DEBUG
echo 'loading python drivers' >> $DEBUG
time chpst -utc tce-load -i $PYTHON-serial $PYTHON-RTIMULib $PYTHON-ujson pypilot 2>> $DEBUG

date >> $DEBUG
echo 'running pypilot' >> $DEBUG
sv u pypilot

date >> $DEBUG
echo 'loading lcd drivers' >> $DEBUG
chpst -utc tce-load -i $PYTHON-RPi.GPIO $PYTHON-spidev > /dev/null

date >> $DEBUG
echo 'running pypilot hat' >> $DEBUG
sv u pypilot_hat

#load pyudev
# set gpsd baud hint the first time a gps is plugged in
cp /mnt/mmcblk0p2/.pypilot/gpsd_baud_hint /tmp
date >> $DEBUG
chpst -utc tce-load -i $PYTHON-pyudev > /dev/null

date >> $DEBUG
echo 'loading gpsd' >> $DEBUG
chpst -utc tce-load -i gpsd > /dev/null
sv u gpsd

sleep 12

chpst -utc tce-load -i firmware-ralinkwifi firmware-rpi3-wireless firmware-atheros firmware-rtlwifi > /dev/null
chpst -utc tce-load -i wifi > /dev/null

#chown tc /dev/fb*  # give user access to framebuffer
date >> $DEBUG
echo 'loading lirc modules' >> $DEBUG
chpst -utc tce-load -i lirc-4.9.20-piCore_v7+ lirc-4.9.20-piCore+ >> $DEBUG
insmod /mnt/mmcblk0p2/tinypilot/modules/modules/rc-core.ko
insmod /mnt/mmcblk0p2/tinypilot/modules/modules/lirc_dev.ko
insmod /mnt/mmcblk0p2/tinypilot/modules/modules/lirc_rpi.ko
insmod /mnt/mmcblk0p2/tinypilot/modules/v7_modules/rc-core.ko
insmod /mnt/mmcblk0p2/tinypilot/modules/v7_modules/lirc_dev.ko
insmod /mnt/mmcblk0p2/tinypilot/modules/v7_modules/lirc_rpi.ko
date >> $DEBUG
echo 'loading lirc' >> $DEBUG
chpst -utc tce-load -i lirc > /dev/null

date >> $DEBUG
echo 'starting lirc' >> $DEBUG
sv u lircd

# create access point
date >> $DEBUG
echo 'setting up access point' >> $DEBUG
# load wifi drivers
echo 'nameserver 8.8.8.8' > /etc/resolv.conf
echo '127.0.0.1 pool.ntp.org' >> /etc/hosts

# setup network
/opt/networking.sh

# automatically set the date from gps
date >> $DEBUG
echo 'starting gpsdate service' >> $DEBUG
sv u gpsdate

# Start openssh daemon
date >> $DEBUG
echo 'start sshd' >> $DEBUG
chpst -utc tce-load -i openssh > /dev/null
sv u openssh

date >> $DEBUG
echo 'loading python signalk dependencies' >> $DEBUG
chpst -utc tce-load -i $PYTHON-zeroconf $PYTHON-requests $PYTHON-websocket > /dev/null

# start webserver
date >> $DEBUG
echo 'starting web' >> $DEBUG
chpst -utc tce-load -i $PYTHON-click $PYTHON-engineio $PYTHON-flask $PYTHON-flask_socketio $PYTHON-gevent $PYTHON-geventwebsocket $PYTHON-greenlet $PYTHON-itsdangerous $PYTHON-jinja2 $PYTHON-markupsafe $PYTHON-socketio $PYTHON-werkzeug $PYTHON-six  > /dev/null
sv u pypilot_web

# setup watchdog to watch runit
date >> $DEBUG
echo 'starting watchdog' >> $DEBUG
chpst -utc tce-load -i watchdog > /dev/null
watchdog

# important stuff is loaded, sleep so it can start faster
time sleep 12

# scientific library needed for compass calibration
date >> $DEBUG
echo 'loading scientific library' >> $DEBUG
chpst -utc tce-load -i py3.6-numpy 2>> $DEBUG
chpst -utc tce-load -i $PYTHON-scipy > /dev/null

# load python image library used by hat lcd program if new text is drawn and not cached
date >> $DEBUG
echo 'loading python pil' >> $DEBUG
chpst -utc tce-load -i freetype harfbuzz >> $DEBUG
chpst -utc tce-load -i libjpeg-turbo openjpeg-lib $PYTHON-PIL > /dev/null


sleep 30 # wait a while before loading development tools

# ------ Put other system startup commands below this line

date >> $DEBUG
echo 'loading tools' >> $DEBUG
chpst -utc tce-load -i screen nano > /dev/null


#echo 'loading desktop' >> $DEBUG
#chpst -utc tce-load -i flwm_topside wbar Xorg 2> /dev/null > /dev/null

# Set CPU frequency governor to ondemand (default is performance)
echo ondemand > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

date >> $DEBUG
echo 'load dev environment' >> $DEBUG

chpst -utc tce-load -i gcc gdb binutils git emacs squashfs-tools make glibc_base-dev linux-4.9.y_api_headers pkg-config curl-dev gettext $PYTHON-dev swig >> $DEBUG

chpst -utc tce-load -i setuptools > /dev/null

#chpst -utc tce-load -i gtk2-dev xorg-proto-dev zlib_base-dev libpthread-stubs gstreamer-dev gst-plugins-base-dev portaudio-dev mesa-dev cmake libnotify-dev libSM-dev setuptools > /dev/null

#echo 'loading plotter' >> $DEBUG
#chpst -utc tce-load -i opencpn wxWidgets alsa portaudio curl > /dev/null
#su tc -c startx
#su tc -c 'DISPLAY=:0 opencpn'

date >> $DEBUG
echo 'done' >> $DEBUG
