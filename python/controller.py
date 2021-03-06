import time
time.sleep(1)

try:
    from machine import Pin
except:
    from machine_mock import Pin
import struct
import light
from button import Button
from channel import ChannelState, Channel
import vehicle as veh
from config import config, LightConfig, RCMode
from pwm import detect_signal_type, PWMRCDriver
from srxl2driver import SRXL2Driver
from animation import Animation, BreatheAnimation, SimpleAnimation
import cli
import therm

vehicle = veh.Vehicle(config)

status_led = vehicle.status_led

#smart_buttons = (
#        Button(config.primary_button_channel, vehicle.primary_click, reverse=config.primary_button_reverse),
#        Button(config.handbrake_button_channel, vehicle.handbrake_click, reverse=config.handbrake_button_reverse),
#        )

#pwm_buttons = (
#        Button(1, vehicle.primary_click, reverse=config.primary_button_reverse),
#        Button(1, vehicle.handbrake_click, reverse=config.handbrake_button_reverse),
#        )

if config.hardware_button_pin is not None:
    hardware_button_pin = Pin(config.hardware_button_pin, Pin.IN, Pin.PULL_DOWN)
else:
    hardware_button_pin = None
hardware_button = Button(vehicle.primary_click)

init = False
good_packets = 0
mode = None

channel_zeros = {}

packet_count = 0

input_pin = Pin(config.input_pins[0], Pin.IN)

def handle_telemetry_packet(packet):
    # First telemetry packet may have a bogus voltage
    if init:
        braking = packet.throttle > 5 and packet.power_out == 0
        vehicle.set_state(packet.rpm > 0, braking, packet.volts_input, packet.temp_fet)
    else:
        print("LOG voltage: %d" % (packet.volts_input))

def handle_hardware_button():
    if hardware_button_pin is not None:
        pressed = hardware_button_pin.value() > 0
        hardware_button.update(pressed)

def handle_control_packet(channel_data):
    global init
    global good_packets
    cm = config.channel_map(mode, vehicle)
    if not init:
        ok = False
        for ch, rev in cm.keys():
            v = channel_data.get(ch)
            if v is not None:
                channel_zeros[ch] = v
                ok = True
        # For SMART, we only calibrate after we see channel 10 disappear.
        if ok and ((10 not in channel_data and channel_data != {}) or mode == RCMode.PWM):
            good_packets += 1
            if good_packets > 30:
                init = True
                for l in vehicle.lights:
                    l.animate(SimpleAnimation.multi_flash(3), menu = True)
                vehicle.startup_complete()
    else:
        for (ch, reverse), target in cm.items():
            v = channel_data.get(ch)
            if v is not None:
                zero = channel_zeros.get(ch, 1500 if mode == RCMode.PWM else 0x8000)
                #if ch == 1:
                #    print("%d vs %d + %d" % (v, zero, target.threshold))
                if v > zero + target.threshold:
                    state = ChannelState.FORWARD
                elif v < zero - target.threshold:
                    state = ChannelState.REVERSE
                else:
                    state = ChannelState.NEUTRAL
                if reverse:
                    state *= -1
                target.update(state, v - zero)
        if mode == RCMode.SMART:
            v = channel_data.get(config.level_channel)
            if v is not None:
                level = int(100 * (v - config.level_channel_min) / (config.level_channel_max - config.level_channel_min))
                level = max(level, 0)
                level = min(level, 100)
                vehicle.level_setting(level)
    global packet_count
    packet_count += 1
    if packet_count >= 100:
        if not hardware_button.pressed and not vehicle.in_menu and not vehicle.in_telemetry:
            vehicle.status_led.set_level(100 if mode == RCMode.SMART else 0)
            vehicle.status_led.animate(SimpleAnimation.multi_flash(1 if init else 2, 75, 75, 50, invert = mode == RCMode.SMART))
        packet_count = 0


def sample_temperature():
    temp = therm.get_value()
    vehicle.ext_temperature = temp

print("LOG Controller starting");

cli = cli.CLI(vehicle)

mode = detect_signal_type(vehicle, config.input_pins, hardware_button_pin, cli)
if mode == None:
    mode = RCMode.PWM
    vehicle.startup_complete()
if mode == RCMode.SMART:
    driver = SRXL2Driver(config.input_pins[0], handle_control_packet, handle_telemetry_packet)
else:
    driver = PWMRCDriver(config.input_pins, handle_control_packet)
vehicle.mode = mode

last_brake = False
driver.start()
now = time.ticks_ms()
#for l in vehicle.lights:
#    l.animate(BreatheAnimation(2000,3000), loop = True)

therm.init()

while True:
    driver.process()
    vehicle.update()
    handle_hardware_button()
    sample_temperature()
    cli.process()
    time.sleep_us(10)
    #handle_control_packet({})


