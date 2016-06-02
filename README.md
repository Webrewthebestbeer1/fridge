## Setup on a Raspberry Pi 3

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

## Deploy

### Setup database

To create the sqlite database, open the python3 shell and execute

    from app import db
    db.create_all()
    exit()

### Start the app with systemd

    cp fridge.servce /etc/systemd/system/
    systemctl daemon-reload
    systemctl default fridge
    systemctl start fridge

## Authentication

The app provides no authentication on the API endpoints and should therefor be configured with a webserver with whitelisted IPs or similar.

## Performance

### Compressor switching

Compressors have a starter motor that draw high currents in order to get things moving. When the compressor turns off, the pressure at the output is very high. Turning the compressor on again immediately will put a very high workload on the starter motor, thus lowering its lifetime. Instead, we should wait for the pressure to equalize inside the system.

From [Targeting Refrigerators for Repair or Replacement](http://www.kouba-cavallo.com/art/REFRIG7a.pdf)

    In other words, a typical, properly operating refrigerator
    runs about 20 minutes and is off 20 minutes.

### Sample performance

Over a span of 24 hours the compressor switched on 8 times, running 10-20 minutes each time. The temperature of the sensor taped to the fermentation chamber read between 16'C and 17'C.

When set to 6'C, the compressor switched on for 20 minutes and was off for approximately 35 minutes, in general.

We believe the sensor fluctuates more when taped to the chamber compared to being submerged in the chamber.
