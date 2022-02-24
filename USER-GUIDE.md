# User Guide

The PDWRC Light Controller is highly configurable light controller for RC
vehicles.

The controller has multiple output channels, which can be configured to
different brightnesses in different modes.

The controller has two control modes:

1. Standard RC inputs, referred to as "PWM Mode".
2. Spektrum Smart mode.  This requires a Spektrum Smart receiver and ESC, and
   proides some additional functionality.

The controller can be programmed and configured using either the button on the
controller itself, or a switched AUX channel on your receiver.

# Installation 

The controller can be connected to up to two inputs via 3 pin servo cables, and
up to four outputs via 2 pin connectors.  The layout of the connectors is as
shown below:

<img src="docs/v1-connector.png">

Care should be taken to ensure that connectors are correct orientated.

When connecting to an input that is already in use (e.g. throttle or steering)
a Y-lead with two female and one male plug will be required, so that both the
controller and the existing servo/ESC can be connected to the receiver.

If you are connecting to an otherwise unused output (e.g. an Aux channel) or
your receiver has a second output for the same channel, a straight-through
cable with female plugs can be used.

## PWM Mode

The controller can be connected to up to two RC channels.  These can be any of
the following combinations:

* Input 1 = Switch (Aux)
* Input 1 = Throttle
* Input 1 = Switch (Aux) / Input 2 = Throttle
* Input 1 = Throttle / Input 2 = Steering

In modes 2 and 4 where an Aux channel is not used as a switch, the controller
configuration is done using a button 1 on the controller.

## Smart Mode for Spektrum Smart ESC and Receiver

To use Smart mode, connect Input 1 of the controller to the throttle channel
using a Y-cable.  Smart mode gives the controller access to all RC channels via
this single cable.

## Light connections

LEDs can be connected to each of the light channels.  

Power for the lights is drawn from the BEC via the input cable(s).  You should
ensure that the LEDs have appropriate current limiting resistors for your BEC's
voltage.  It is recommend that you limit each channel to 500mA, and the total
of all channels to 1A, although this will also depend on the spec of your BEC,
and what else you have connected to it.

Note that the negative connections on the LEDs are _not_ a common ground, and
must be wired separately for each channel.  The positive wire is common, and
can be shared, if desired.

# Start up

When power is first applied to the controller, the status LED will flash
quickly to indicate that it is searching for a signal on channel 1.  If a Smart
signal is present, this step may complete almost immediately.

Once a signal is found, the status LED will blink for every 100 control
messages it receives.  For a PWM signal, the LED will be normally off and flash
on.  For a Smart signal, the LED will be normally on and will flash off.

If you press Button 1 on the controller during signal detection, the controller
will activate in PWM mode. 

Once a signal is detected, the controller will detect the centre position of
all channels, so it is important that you don't touch any controls on the
transmitter until this is done.  The controller will flash all lights three
times once initialisation is complete.

## Smart / AVC calibration

After detecting a Smart signal, the controller will wait for the completion of
AVC calibration before becoming it completes initialisation.  This requires the
vehicle to be completely still for five seconds.

# Operation

## Inputs

The controller is controlled using the switch on an AUX channel if you have
one, or Button 1 on the controller.  These two controls are equivalent, and in
the rest of this documentation will be referred to as the primary button.

If you are using an AUX channel, then a secondary button is available by
clicking the button in the opposite direction (i.e. if your transmitter has a
rocker switch, pressing in one direction is the primary button, and the
opposite direction is the secondary button)

The controller uses short and long clicks for different purposes.  A short
click is one that is less than 0.5 seconds.  A long click is more than 0.5
seconds but less than 3 seconds.  Holding for longer than 3 seconds is used to
access the menu, as described below.

## Basic operation

The controller has three lighting modes:

* Off
* Mode 1
* Mode 2

Clicking the primary button will move from Off to Mode 1, and will then toggle
between Mode 1 and Mode 2.

Holding the primary button for more than half a second in Mode 1 or Mode 2
before releasing will switch back to "Off".

The brightness level of each channel in each of Mode 1 and Mode 2 can be
configured using the menu (see below).

## Flash function (Smart mode only)

In Smart mode, the controller can detect when the vehicle is moving, and when
it is, the function of the primary button changes so that it activates the
"flash" brightness level for each channel for as long as the button is held.
Again, the "flash" brightness level is configurable for each channel.

## Brake lights

The controller will activate brake lights when the vehicle is braking.  Which
lights are activated, and their brightness level, is configurable via the menu.

In Smart mode, the controller uses telemetry data from the ESC to determine
when the vehicle is braking.

In PWM Mode, the controller will activate brake lights based on throttle
inputs.  Exactly how this is done is configurable, and is described under the
"PWM Brake Mode" setting below.

The controller can also be configured to activate brake lights when the
secondary button is pressed.

## Sleep animation

The controller can be configured to display a "breathing" effect on some or all
lights if the car has not moved for a certain period of time.

In PWM mode, movement is considered to be any movement of any connected control
(button, steering or throttle).  In Smart mode, the ESC must additionally be
reporting zero speed in order to activate.

# Configuration menu

The controller is configured using a built in menu system.   

To access the menu system, press and hold the primary button.  After three
seconds, the lights and status LED will flash.  After a further three seconds
the lights and status LED will flash again.  Now release the button.  The
lights will flash once more, to indicate that you are at the first item in the
menu.

The menu system is navigated using a series of short and long clicks.  A long
click is one that lasts longer than 0.5 seconds.

A short click means "next" and a long click means "select".

## Menu navigation

The first item in the menu is "quit", so a long click here will take you out of
the menu.  You can also quit the menu by applying throttle from anywhere in the
menu.

After each click, the controller will flash the lights to indicate your
position in the menu,  For example, click once to progress to the second item,
and the lights will flash twice.  Click again and the lights will flash three
times.

Keep clicking, and you will eventually see a single flash, indicating that you
have cycled back to the first item.  

After the flashes, some lights or all lights may stay on.  This helps show your
current position or the current setting, and is explained below.

Note that you don't have to wait for the flashes.  For example, click three
times in quick succession and you will end up on the fourth item.

The menu has number of sub-menus.  Long-clicking on the item in the menu will
take you into the sub-menu.  The first item in a sub-menu is always "up" and
will take you back into your previous position in the previous menu.  Short
clicks will cycle you through the options in the sub-menu.

## Changing settings

To change a menu item, navigate to that item as described above, and long
click to enter the menu item.  Short clicks will then cycle through the
available options, and a long click will select the current option and return
you to the menu.

For simple, multi-choice menu items the brightness of the lights will increase
as you move through the possible values,  with the lights off indicating the
first option.  So for example, PWM Brake Mode has three possible values:

* Simple (lights off)
* Smart (lights 50%)
* Drag brake (lights 100%)

Short clicks will cycle through these options.  A long click will select the
currently indicated item.

Some options use a different approach in order to give you a preview of the
current selection.  This is described below, where applicable.

In Smart mode, some menu items can also be adjusted using the AVC control on
the transmitter.

## Menu structure

The overall menu structure is shown below:

* 1\. Quit 
* 2\. Settings menu
    * 1\. (Go up)
    * 2\. Channel mode (PWM) [ Switch+Throttle / Throttle+Steering ]
    * 3\. Brake mode (PWM) [ Simple / Smart / Drag ]
    * 4\. Soft on/off speed
    * 5\. Handbrake mode (brake on secondary button) [ On / Off ]
    * 6\. Turn signal steering threshold
    * 7\. Sleep animation menu
        * 1\. (Go up)
        * 2\. Start delay [0s / 5s / 10s / 30s / 60s]
        * 3\. Sleep when lights on [ On / Off ]
        * 4\. Pulse duration
        * 5\. Off duration
        * 6\. Off brightness
* 3\. Light channel 1 menu
    * 1\. (Go up)
    * 2\. Mode 1 brightness
    * 3\. Mode 2 brightness
    * 4\. Brake brightness
    * 5\. Flash brightness
    * 6\. Left turn brightness
    * 7\. Right turn brightness
    * 8\. Sleep brightness
* 4\. Channel 2 menu 
    * _As for channel 1_
* 5\. Channel 3 menu
    * _As for channel 1_
* 6\. Channel 4 menu
    * _As for channel 1_

### Settings

#### Channel mode (PWM mode only)

This setting configures which receiver channels are connected to the controller.  The options are:

0. Channel 1 = AUX (Switch), Channel 2 = Throttle (or disconnected)
1. Channel 2 = Throttle, Channel 2 = Steering (or disconnected)

This setting has no effect in Smart mode.

#### Brake mode (PWM mode only)

In PWM mode, the controller can use one of three different modes for braking:

0. Simple — the brake lights come on whenever you put the throttle in reverse.
1. Smart — the brake lights come on the first time you put the throttle in
   reverse.  If you return to neutral and then reverse again, this is assumed
   to be reverse, and the brake lights do not come on.  Forwards throttle
   resets, so the next reverse action is a brake.
2. Drag brake mode — the brake lights come on for a short time whenever the throttle
   is released.

This setting has no effect in Smart mode, as ESC telemetry to detect braking.

#### Soft on/off speed

This setting controls how quickly the LEDs transition between different levels.
Increasing this gives a smoother transition between levels, making LEDs appear
more like traditional incandescent bulbs.  

When this option is selected, all channels will flash on and off to give a
preview of the current transition speed.

The speed can be set between 0 and 33ms.  Clicking the primary button cycle
through five possible values.

In Smart mode, the AVC button can also be used to set the level.

#### Handbrake mode

This setting controls whether the secondary button will activate the brake
lights.  When this menu item is selected, the primary button will toggle
between the two modes. 

#### Turn signal steering threshold

This setting controls how far the steering must be turned before the turn
signals activate.

After selecting this option, turn the steering to the desired threshold
position and long press the primary button to use that position as the
threshold.  The steering can be turned in either direction when setting the
value.  The same threshold will be used in both directions.

#### Sleep animation

#### Sleep start delay

This setting controls the time after the last movement before the sleep
animation begins.  Clicking the primary button will cycle through the following
options (0s, 5s, 10s, 30s, and 60s).

#### Sleep when lights on

This setting controls whether sleep mode will activate if the lights are mode 1
or mode 2.  If set to "off", sleep mode will only activate when the lights are
switched off.  If set to "on", sleep mode will activate after the specified
delay regardless of mode.

# Firmware updates

To install new firmware, ensure that the controller is powered off, then hold
down button 2 while connecting a USB cable to a computer.  The button can be
released as soon as the cable is connected.  The controller should appear as a
USB disk called "RPI-RP2".  Simply copy the provided `.uf2` file onto this
drive.  After a few seconds, the disk will disappear, and the controller will
restart.  You can then disconnect the USB cable.




