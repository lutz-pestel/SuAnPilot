#!/bin/sh

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

/opt/splash &
SPLASHPID=$!

# more sane date... need to be within 20 years or so for
# gps to set the date correctly as well...
date -s 1705112000
uptime

echo 'starting runit' >> $DEBUG
su tc -c 'tce-load -i runit' > /dev/null
runsvdir /service &

# setup watchdog to watch runit
echo 'starting watchdog' >> $DEBUG
chpst -utc tce-load -i watchdog > /dev/null
watchdog

# start pypilot
echo 'loading python' >> $DEBUG
chpst -utc tce-load -i python > /dev/null

echo 'loading serial drivers' >> $DEBUG
chpst -utc tce-load -i usb-serial-4.4.20-piCore_v7+ > /dev/null
chpst -utc tce-load -i usb-serial-4.4.20-piCore+ > /dev/null
/sbin/modprobe i2c-dev

echo 'loading python drivers' >> $DEBUG
chpst -utc tce-load -i python-serial python-RTIMULib pypilot > /dev/null
chpst -utc tce-load -i python-scipy gcc_libs > /dev/null

echo 'running pypilot' >> $DEBUG
sv u pypilot

kill $SPLASHPID # kill splash screen
#chown tc /dev/fb*  # give user access to framebuffer

echo 'loading lcd drivers' >> $DEBUG
#chpst -utc tce-load -i python-ugfx >/swc/null
chpst -utc tce-load -i python-RPi.GPIO wiringPi > /dev/null
#sv u pypilot_lcdclient

#why here?!?
chpst -utc tce-load -i setuptools > /dev/null

echo 'loading gpsd' >> $DEBUG
chpst -utc tce-load -i gpsd gpsd-python > /dev/null
sv u gpsd

# create access point
echo 'setting up access point' >> $DEBUG
# load wifi drivers
echo 'nameserver 8.8.8.8' > /etc/resolv.conf
echo '192.168.14.1 pypilot' >> /etc/hosts
echo '127.0.0.1 pool.ntp.org' >> /etc/hosts

chpst -utc tce-load -i wifi firmware-ralinkwifi > /dev/null

echo 'start hostapd' >> $DEBUG
chpst -utc tce-load -i hostapd > /dev/null
sv u hostapd

# configure network
ifconfig wlan0 up 192.168.14.1

# dns server
echo 'start dnsmasq' >> $DEBUG
chpst -utc tce-load -i dnsmasq > /dev/null
mkdir -p /var/lib/misc
sv u dnsmasq

# automatically set the date from gps
echo 'starting gps services' >> $DEBUG
sv u gpsdate
sv u gpsprobe

# start dhcp server
#echo 'start dhcpd' >> $DEBUG
#sv u udhcpd

# start webserver
echo 'starting webapp' >> $DEBUG
chpst -utc tce-load -i python-click python-engineio python-flask python-flask_socketio python-gevent python-geventwebsocket python-greenlet python-itsdangerous python-jinja2 python-markupsafe python-socketio python-werkzeug python-six python-pkg_resources > /dev/null
#sv u pypilot_webapp

# Start openssh daemon
echo 'start sshd' >> $DEBUG
chpst -utc tce-load -i openssh > /dev/null
sv u openssh

echo 'loading scientific library' >> $DEBUG
chpst -utc tce-load -i python-scipy gcc_libs > /dev/null

echo 'loading python pil' >> $DEBUG
chpst -utc tce-load -i freetype harfbuzz libtiff libjpeg-turbo
chpst -utc tce-load -i libjpeg-turbo libtiff python-PIL > /dev/null
sleep 3

# ------ Put other system startup commands below this line

echo 'loading tools' >> $DEBUG
chpst -utc tce-load -i screen nano alsa > /dev/null


#echo 'loading desktop' >> $DEBUG
#chpst -utc tce-load -i flwm_topside wbar Xorg 2> /dev/null > /dev/null

# Set CPU frequency governor to ondemand (default is performance)
echo ondemand > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

echo 'adding gateway' >> $DEBUG
route add default gw 192.168.14.20

#chpst -utc tce-load -i ntp > /dev/null
#ntpdate srcf-ntp.stanford.edu &

echo 'load dev environment' >> $DEBUG
chpst -utc tce-load -i gcc gdb binutils git emacs squashfs-tools make glibc_base-dev linux-4.4.y_api_headers pkg-config curl-dev gettext python-dev swig

#chpst -utc tce-load -i gtk2-dev xorg-proto-dev zlib_base-dev libpthread-stubs gstreamer-dev gst-plugins-base-dev portaudio-dev mesa-dev cmake libnotify-dev libSM-dev setuptools > /dev/null

#echo 'loading plotter' >> $DEBUG
#chpst -utc tce-load -i opencpn wxWidgets alsa portaudio curl > /dev/null
#su tc -c startx
#su tc -c 'DISPLAY=:0 opencpn'

echo 'done' >> $DEBUG
