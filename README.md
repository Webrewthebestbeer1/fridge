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

## Performance

### Compressor switching

Compressors have a starter motor that draw high currents in order to get things moving. When the compressor turns off, the pressure at the output is very high. Turning the compressor on again immediately will put a very high workload on the starter motor, thus lowering its lifetime. Instead, wait for the pressure to equalize inside the system.

From [Targeting Refrigerators for Repair or Replacement](http://www.kouba-cavallo.com/art/REFRIG7a.pdf)

    In other words, a typical, properly operating refrigerator
    runs about 20 minutes and is off 20 minutes.

### Sample performance

Over a span of 24 hours the compressor switched on 8 times, running 10-20 minutes each time. The temperature of the sensor taped to the fermentation chamber read between 16'C and 17'C.

We believe the sensor fluctuates more when taped to the chamber compared to being submerged in the chamber.
