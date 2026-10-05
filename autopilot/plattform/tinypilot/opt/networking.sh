#
#   Copyright (C) 2020 Sean D'Epagnier
#
# This Program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.  

DEBUG=/tmp/bootlocal.log

# configure network
NETWORK_FILE=/home/tc/.pypilot/networking.txt
MODE=`grep ^mode= $NETWORK_FILE | sed 's/mode=//g'`
SSID=`grep ^ssid= $NETWORK_FILE | sed 's/ssid=//g'`
KEY=`grep ^key=  $NETWORK_FILE | sed 's/key=//g'`
CLIENT_SSID=`grep ^client_ssid= $NETWORK_FILE | sed 's/client_ssid=//g'`
CLIENT_KEY=`grep ^client_key= $NETWORK_FILE | sed 's/client_key=//g'`
CLIENT_ADDRESS=`grep ^client_address= $NETWORK_FILE | sed 's/client_address=//g'`

# normal defaults
if [ "$SSID" = "" ]; then
    MODE="Master"
    SSID="pypilot"
    KEY=""
    CLIENT_SSID=""
    CLIENT_KEY=""
    CLIENT_ADDRESS=""
fi

# stop all networking services
sv d wpa_supplicant
sv d dhcpcd
sv d hostapd
sv d dnsmasq

if [ "$MODE" = "Managed" ]; then
    cp /opt/wpa_supplicant.conf /etc/wpa_supplicant.conf
    if [ "$CLIENT_KEY" = "" ]; then
        KEYMGMT="NONE"
        sed -i s/psk=/#psk=/1 /etc/wpa_supplicant.conf
    else
        KEYMGMT="WPA-PSK"
    fi
    # write wpa_supplicant.conf
    sed -i s/%SSID%/$CLIENT_SSID/1 /etc/wpa_supplicant.conf
    sed -i s/%KEY%/$CLIENT_KEY/1 /etc/wpa_supplicant.conf
    sed -i s/%KEYMGMT%/$KEYMGMT/1 /etc/wpa_supplicant.conf
    sv u wpa_supplicant
    if [ "$CLIENT_ADDRESS" != "" ]; then
        ifconfig wlan0 $CLIENT_ADDRESS
        if [ "$?" = 0 ]; then
           echo 'ifconfig set client address!'
           exit 0
        fi
        # if failed, fallback to dhcp
    fi

    chpst -utc tce-load -i dhcpcd > /dev/null
    sv u dhcpcd
else
    if [ "$KEY" = "" ]; then
        WPA=0
        KEY="notempty" #  unused field must not be empty
    else
        WPA=1
    fi

    # write hostapd.conf
    sed s/%SSID%/$SSID/1 /opt/hostapd.conf | sed s/%KEY%/$KEY/1 | sed s/%WPA%/$WPA/1 > /etc/hostapd.conf

    echo '192.168.14.1 pypilot' >> /etc/hosts
    echo 'start hostapd' >> $DEBUG
    chpst -utc tce-load -i hostapd > /dev/null
    sv u hostapd

    ifconfig wlan0 up 192.168.14.1
    # dns and dhcp server
    echo 'start dnsmasq' >> $DEBUG
    chpst -utc tce-load -i dnsmasq > /dev/null
    mkdir -p /var/lib/misc
    sv u dnsmasq
fi
