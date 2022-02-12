from machine import UART, Pin, time_pulse_us
import time
import struct
import light
from button import Button
from channel import ChannelState, Channel
import vehicle as veh
from config import config, LightConfig
from pwm import detect_signal_type, PWMRCDriver, RCMode
from srxl2driver import SRXL2Driver



vehicle = veh.Vehicle(config)
status_led = vehicle.status_led

smart_buttons = (
        Button(config.primary_button_channel, vehicle.primary_click, reverse=config.primary_button_reverse),
        Button(config.handbrake_button_channel, vehicle.handbrake_click, reverse=config.handbrake_button_reverse),
        )

pwm_buttons = (
        Button(1, vehicle.primary_click, reverse=config.primary_button_reverse),
        Button(1, vehicle.handbrake_click, reverse=config.handbrake_button_reverse),
        )

hardware_button_pin = Pin(config.hardware_button_pin, Pin.IN, Pin.PULL_DOWN)
hardware_button = Button(None, vehicle.primary_click)

init = False
good_packets = 0
mode = None

channel_zeros = {}

packet_count = 0

input_pin = Pin(config.input_pins[0], Pin.IN)

def handle_telemetry_packet(packet):
    braking = packet.throttle > 5 and packet.power_out == 0
    vehicle.set_state(packet.rpm > 0, braking, packet.volts_input)

def handle_hardware_button():
    pressed = hardware_button_pin.value() > 0
    hardware_button.update(pressed)

def handle_control_packet(channel_data):
    global init
    global good_packets
    if not init:
        print(channel_data)
        ok = True
        for b in channels:
            v = channel_data.get(b.channel)
            if v is None:
                ok = False
            else:
                channel_zeros[b.channel] = v
        # For SMART, we only calibrate after we see channel 10 disappear.
        if ok and ((10 not in channel_data and channel_data != {}) or mode == RCMode.PWM):
            good_packets += 1
            if good_packets > 10:
                init = True
                for l in vehicle.lights:
                    l.animate(light.Animation.multi_flash(3))
    else:
        for b in channels:
            v = channel_data.get(b.channel)
            if v is not None:
                zero = channel_zeros.get(b.channel, 0x8000)
                if v > zero + b.threshold:
                    state = ChannelState.FORWARD
                elif v < zero - b.threshold:
                    state = ChannelState.REVERSE
                else:
                    state = ChannelState.NEUTRAL
                b.update(state)
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
            vehicle.status_led.animate(light.Animation.multi_flash(1 if init else 2, 75, 75, 50, invert = mode == RCMode.SMART))
        packet_count = 0



time.sleep(0.5)
print("Controller starting");

mode = detect_signal_type(vehicle, input_pin, hardware_button_pin)
if mode == RCMode.SMART:
    driver = SRXL2Driver(config.input_pins[0], handle_control_packet, handle_telemetry_packet)
    vehicle.throttle = Channel(config.throttle_channel)
    channels = smart_buttons + (vehicle.throttle,)
else:
    driver = PWMRCDriver(config.input_pins, handle_control_packet)
    channels = pwm_buttons

last_brake = False
driver.start()
while True:
    driver.process()
    vehicle.update()
    handle_hardware_button()
    time.sleep_us(10)
