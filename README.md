## Setup Raspberry Pi 3

### Enable 1-wire protocol

    sudo vim /boot/config.tx

Append

    dtoverlay=w1-gpio

### Automatically load kernel modules on boot

    sudo vim /etc/modules

Append

    w1-gpio
    w1-therm

### Disable WLAN Power Management

    sudo vim /etc/network/interfaces

Append

    wireless-power off
