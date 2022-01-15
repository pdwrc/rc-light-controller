from machine import UART, Pin, time_pulse_us
import time
import struct
import light
from button import ButtonState
import vehicle as veh
from config import config, LightConfig
from pwm import detect_signal_type, PWMRCDriver, RCMode
from srxl2driver import SRXL2Driver

vehicle = veh.Vehicle(config)

smart_buttons = (
        ButtonState(config.primary_button_channel, vehicle.primary_click, reverse=config.primary_button_reverse),
        ButtonState(config.handbrake_button_channel, vehicle.handbrake_click, reverse=config.handbrake_button_reverse),
        )

pwm_buttons = (
        ButtonState(1, vehicle.primary_click, reverse=config.primary_button_reverse),
        ButtonState(1, vehicle.handbrake_click, reverse=config.handbrake_button_reverse),
        )

BUTTON_THRESHOLD = 10

extra_button_pin = Pin(2, Pin.IN, Pin.PULL_DOWN)
extra_button = ButtonState(None, vehicle.primary_click)

init = False
good_packets = 0
mode = None

channel_zeros = {}

packet_count = 0

input_pin = Pin(9, Pin.IN)

def handle_telemetry_packet(packet):
    #print(time.ticks_ms())
    #print(packet)
    braking = packet.throttle > 5 and packet.power_out == 0
    vehicle.set_state(packet.rpm > 0, braking, packet.volts_input)

def handle_extra_button():
    pressed = extra_button_pin.value() > 0
    extra_button.update(pressed)

def handle_control_packet(channel_data):
    global init
    global good_packets
    if not init:
        print(channel_data)
        ok = True
        for b in buttons:
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
        for b in buttons:
            v = channel_data.get(b.channel)
            if v is not None:
                zero = channel_zeros.get(b.channel, 0x8000)
                pressed = (not b.reverse and v > zero + BUTTON_THRESHOLD) or (b.reverse and v < zero - BUTTON_THRESHOLD)
                b.update(pressed)
        v = channel_data.get(config.level_channel)
        if v is not None:
            level = int(100 * (v - config.level_channel_min) / (config.level_channel_max - config.level_channel_min))
            level = max(level, 0)
            level = min(level, 100)
            vehicle.level_setting(level)
    global packet_count
    packet_count += 1
    if packet_count >= 100:
        vehicle.status_led.animate(light.Animation.multi_flash(1 if init else 2, 75, 75, 50))
        packet_count = 0

#detect()

mode = detect_signal_type(vehicle, input_pin)
if mode == RCMode.SMART:
    driver = SRXL2Driver(input_pin, handle_control_packet, handle_telemetry_packet)
    buttons = smart_buttons
else:
    driver = PWMRCDriver([input_pin], handle_control_packet)
    buttons = pwm_buttons

last_brake = False
driver.start()
while True:
    driver.process()
    vehicle.update()
    vehicle.status_led.tick()
    handle_extra_button()
    time.sleep_us(10)
