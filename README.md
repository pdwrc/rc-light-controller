# Open Source RC Light Controller

This project contains software and instructions for building a multi-channel
light controller for RC cars.

The controller is intended to be highly configurable, and the firmware is open
source, so it can be customised to do whatever you want.

The controller is built around the Raspberry Pi Pico microcontroller, and if
you're comfortable using a soldering iron, it can be assembled very easily from
just a handful of components.

## Features

The controller can be configured to have different lighting modes, selected
using a spare channel on the transmitter, with different brightnesses for
individual channels in the different modes.  

It can configured to activate brake lights automatically, or using a button on
the transmitter.

The controller has a configurable "soft on"/"soft off" setting, which makes
LEDs look more like traditional incandescent bulbs.

## Spektrum Smart support

The controller and software are optimised for use with Spektrum Smart receivers
and ESCs.  When used in conjunction with a Smart ESC and receiver, additional
functionality is available, as the controller can use telemetry data to detect
when the car is moving and braking, 

Additional features include:

* Improved automated brake light mode.
* Read out of current and minimum battery voltage.
* Fine adjustment of brightness levels using the AVC knob on the transmitter.

A Spektrum Smart receiver and ESC communicate using the SRXL2 protocol rather
than PWM.  This allows a single connection to get access to control data for
all channels, and gives access to ESC telemetry data, which is useful for
reliably detecting when the ESC is braking, and when the car is moving.

# Software

To install the software, first flash your Pico with [MicroPython firmware](https://micropython.org/download/rp2-pico/).

Once done, use [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html), [rshell](https://github.com/dhylands/rshell) or [pyboard.py](https://github.com/micropython/micropython/blob/master/tools/pyboard.py) to copy the contents of the `python` directory onto the Pico.  With `mpremote`, this is done as follows:

```
mpremote fs cp python/*.py :
```

You can now start the controller using the following command:

```
mpremote run controller.py
```

This should show some debug output from the firmware.

# Hardware

As noted above, the controller uses the Raspberry Pi Pico microcontroller.  The
controller needs a number of additional components in order to ensure that
inputs and supply voltage are within the Pico's limits, and to switch the LED
load currents.

Assembling the controller will require some sort of prototyping board.  It is
possible to buy boards that are designed to sit under the Pico itself, and it
is possible to build a 3 channel controller on one of these, as shown below:

<img src="images/prototype-assembled.jpg">

<img src="images/prototype-separate.jpg">

The required circuit is shown in the schematic below:

<img src="images/schematic.png">

The schematic is also available as a [PDF](kicad/light-controller.pdf) 

## Power supply

The Pico requires an input voltage of no more than 5.5V, but will operate on
anything above 1.8V.  RC BECs typically run at between 5V and 8V, so if you are
running at more than 5.5V, you will need some way of dropping the supply voltage.

The suggested circuit uses an L4931 voltage regulator to drop the supplied
voltage to 5V.  The L4931 has a low drop out which means that it can deliver 5V
from a 6V input.  If you only ever want to run off 7.4V, there's no need for
low drop-out, and you could use any old 5V regulator.

If you only want to run off 6V, you could replace the regulator, capacitors and
the Schottky diode (D1) with a simple signal diode that will knock 0.7V off the
supply.

A normal diode is fine in place of the Schottky diode, and it probably isn't
needed anyway.  It's to prevent the RC power supply from being powered by the
Pico's USB port, if connected.

## Input

The FET in the input pin is to prevent the Pico's input from seeing more than
3.3V.  

The Spektrum Smart protocol uses 3.3V so in theory this isn't a problem if
using Spektrum Smart equipment, but this provides protection should the ESC and
receiver fail to enter Smart mode for any reason.

## Output

The schematic shows BS170s as the output drivers, as these can control a
current of up to 500mA each.  2N7000 FETs could also be used, but these have a
limit of 200mA.

More output channels can be added easily, up to the Pico's limit of 16 PWM
output pins.



