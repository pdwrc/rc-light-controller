# User Guide

The PDWRC Light Controller is highly configurable light controller for RC
vehicles.

The controller has multiple output channels, which can be configured to
different brightnesses in different modes.

The controller has two control modes:

1. Standard RC inputs, referred to as "PWM Mode".
2. Spektrum Smart mode.  This requires a Spektrum Smart receiver and ESC, and
   enables some additional functionality.

The controller can be programmed and configured using either a button on the
controller itself, or an AUX channel on your receiver.  Ideally the AUX channel
should have a rocker switch.

# Installation 

The controller can be connected to up to two inputs using three pin servo
cables, and up to four outputs using two pin connectors.  The layout of the
connectors is as shown below:

<img src="docs/v1-connector.png">

Care should be taken to ensure that connectors are correctly orientated.

When connecting to an input that is already in use (e.g. throttle or steering)
a Y-lead with two female and one male plug will be required, so that both the
controller and the existing servo/ESC can be connected to the receiver.

If you are connecting to an otherwise unused output (e.g. an Aux channel) or
your receiver has a second output for the same channel, a straight-through
cable with two female plugs can be used.

## Input connections in PWM Mode

The controller can be connected to up to two RC channels.  These can be any of
the following combinations:

| Mode | Input 1 | Input 2 | 
|------|---------|---------| 
| 1 | Switch (Aux) | _unused_ | 
| 2 | Throttle | _unused_ | 
| 3 | Switch (Aux) | Throttle | 
| 4 | Throttle | Steering |

A switch channel is needed to remotely control lights and configure the
controller.  In modes 2 and 4, controller configuration is done using Button 1
on the controller, and remote control is not possible.

The throttle channel is required for the brake light function.

The steering channel is required for the turn signal function.

## Input connections in Smart Mode for Spektrum Smart ESC and Receiver

To use Smart mode, connect Input 1 of the controller to the throttle channel
using a Y-cable.  Smart mode gives the controller access to all RC channels via
this single cable, so there is no need to connect any other channels.

## Light connections

LEDs can be connected to each of the output channels.  

You can connect lights to the channels in any order, as the same configuration
is available on all channels (for example, any channel can be configured to be
brake light).  

By default, channel 2 is configured with a "high beam flash", and channel 4 is
configured as a combined tail/brake light.

### Electrical details

Power for the lights is drawn from the BEC via the input cable(s).  You should
ensure that the LEDs are designed to work with your BEC's voltage, and that the
total current drawn does not exceed the capabilities of the BEC.

The controller is designed to handle up to 500mA per channel.

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

The controller is controlled using a switch on an AUX channel if you have
one, or Button 1 on the controller.  These two controls are equivalent, and in
the rest of this documentation will be referred to as the _primary button_.

Button 1 is the button closest to input and output connections.  Button 2 is
the button closest to the USB port, and is used only for firmware updates.

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

## High beam flash function (Smart mode only)

In Smart mode, the controller can detect when the vehicle is moving, and when
it is, the function of the primary button changes so that it activates the
"high beam flash" brightness level for each channel for as long as the button
is held.  The brightness level is configurable for each channel.

## Sleep animation

The controller can be configured to display a "breathing" effect on some or all
lights if the car has not moved for a certain period of time.

In PWM mode, movement is considered to be any movement of any connected control
(button, steering or throttle).  In Smart mode, the ESC must additionally be
reporting zero speed in order to activate.

# Telemetry (Smart mode only)

When in Smart mode, the controller can use telemetry information from the ESC
to show the current battery voltage.

To access the telemetry, press and hold the primary button until you see all
lights flash once, then release the primary button.  

The lights will now flash in sequence to indicate the current average cell
voltage.  For example, if the average cell voltage is 3.85V, all lights will
flash three times, followed by a short gap, then eight times, then a short gap,
then five times.

A further short click of the primary button will cause the controller to read
out the lowest voltage recorded since the unit was powered on.  This is useful
to show how much the battery voltage is dropping when under load.  

Once the voltage read-out is complete, the controller returns to normal
operation.

# Configuration menu

The controller is configured using a built in menu system.   

To access the menu system, press and hold the primary button.  After three
seconds, the lights and status LED will flash.  After a further three seconds
the lights and status LED will flash again.  Now release the button.  The
lights will flash once more, to indicate that you are at the first item in the
menu.

The menu system is navigated using a series of short and long clicks.  

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

After the flashes, some lights may stay on.  This helps show your current
position or the current setting, and is explained below.

Note that you don't have to wait for the flashes.  For example, click three
times in quick succession and you will end up on the fourth item.

The menu has number of sub-menus.  Long-clicking on the item in the menu will
take you into the sub-menu.  The first item in a sub-menu is always "up" and
will take you back into in the previous menu.  Short clicks will cycle you
through the options in the sub-menu.

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

Short clicks will cycle through these options.  A long click will select and
save the current valueu.

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
        * 6\. Minimum brightness [0% / 10% / 20% / 30% / 40% / 50%]
* 3\. Light channel 1 menu
    * 1\. (Go up)
    * 2\. Mode 1 brightness
    * 3\. Mode 2 brightness
    * 4\. Brake brightness
    * 5\. High beam flash brightness
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

This setting has no effect in Smart mode, as ESC telemetry is used to detect braking.

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

After selecting this option, turn the steering in either direction to the
desired threshold position and long press the primary button to use that
position as the threshold.  The same threshold will be used for both left and
right directions.

#### Sleep animation

The controller can display a "breathing" animation on some or all lights when
the car is stationary.

The brightness of each channel in sleep mode can be set individually.

#### Sleep start delay

This setting controls the time after the last movement or control activity
before the sleep animation begins.  Clicking the primary button will cycle
through the following options (0s, 5s, 10s, 30s, and 60s).

In PWM mode, the delay is timed from the last time steering, throttle or switch
input is made via the transmitter.  In Smart mode, the delay is timed from the
last control movement, or movement of the car.

#### Sleep when lights on

This setting controls whether sleep mode will activate if the lights are mode 1
or mode 2.  If set to "off", sleep mode will only activate when the lights are
switched off.  If set to "on", sleep mode will activate after the specified
delay regardless of mode.

#### Sleep pulse duration

This setting controls the speed of the breathe animation.  The time can be
adjusted between 0.5s and 5.5s, in steps of 1s by clicking the primary button.
In Smart mode, this can also be adjusted using the AVC control.  Each time a
change is made, the animation will restart to show the effect of the current
setting.

Note that this menu will preview the animation on all light channels,
regardless of breathe brightness setting for each channel.

#### Sleep gap duration

This setting controls the gap between "breaths" of the sleep animation.  The
time can be adjusted between 0.5s and 5.5s, in steps of 1s by clicking the
primary button.  In Smart mode, this can also be adjusted using the AVC
control.  Each time a change is made, the animation will restart to show the
effect of the current setting.

#### Sleep minimum brightness

This setting controls the brightness of the LEDs between breaths.  This is set
as a percentage of the maximum brightness, and can be set to 0%, 10%, 20%, 30%,
40% or 50%.

#### Light channel menus

A separate sub menu sets the brightnesses for each lighting channel.  As you
cycle through the top-level menu, the lights on the selected channel will
switch on to indicate which lights will be configured.  A long press will enter
the sub menu for that channel.  The first item on the sub menu is "Go up", then
each subsequent item controls the brightness of that channel in each mode.

As you cycle through the menu, the current brightness setting for each mode
will be shown on the lights.  A long press will enter the setting.  The
brightness can be adjusted by clicking the primary button to cycle through the
available brightnesses.  In Smart mode, the brightness can be adjusted using
the AVC control.  A long press will save the current brightness, and return to
the sub menu for the channel.

The available modes are described below:

#### Mode 1 brightness

This controls the brightness of the channel in mode 1.

#### Mode 2 brightness

This controls the brightness of the channel in mode 2.

#### Brake brightness

This controls the brightness of the channel when braking.  If this is set to
off, the lights will keep their current brightness when braking.

#### High beam flash brightness

This controls the brightness of the channel when "high beam flash" is activated (i.e. the
primary button is clicked when the car is moving).  Note that the high beam flash is only
available in Smart mode.  

If this is set to off, the lights will keep their current brightness when
high beam flash is activated.

#### Left turn brightness

This controls the brightness of the channel when the left turn signals are
activated.

If set to off, the lights will keep their current brightness when turning.

#### Right turn brightness

This controls the brightness of the channel when the right turn signals are
activated.

If set to off, the lights will keep their current brightness when turning.

#### Sleep brightness

This controls the brightness of the channel when the sleep animation is
activated.

If set to off, the lights will be off when the sleep animation is activated.

# Firmware updates

Firmware updates are provided in the form of a ".uf2" file.

To install new firmware, ensure that the controller is powered off, then hold
down button 2 while connecting the controller to your computer using a USB
cable.  The button can be released as soon as the cable is connected.  The
controller should appear as a USB disk called "RPI-RP2".  Simply copy the
provided `.uf2` file onto this drive.  After a few seconds, the disk will
disappear, the controller will restart and the LED will start flashing to
indicate that it is looking for a signal.  You can then disconnect the USB
cable.

Note that this requires a micro USB cable with data wires.  Many micro USB
cables are intended only for charging devices, and do not have data wires.  If
the controller does not appear as a USB disk it is likely that you are using a
charge-only cable.

