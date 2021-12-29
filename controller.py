from machine import UART, Pin
from srxl2 import SRXL2, SRXL2Control, SRXL2Telemetry
from button import ButtonState
import time
import struct
from vehicle import Vehicle
from config import Config

config = Config.load()

vehicle = Vehicle(config)

buttons = (ButtonState(config.primary_button_channel, vehicle.primary_click, reverse=config.primary_button_reverse),)

BUTTON_THRESHOLD = 10

extra_button_pin = Pin(2, Pin.IN, Pin.PULL_DOWN)
extra_button = ButtonState(None, vehicle.primary_click)

init = 0

channel_zeros = {}

def handle_telemetry_packet(packet):
    print(time.ticks_ms())
    print(packet)
    braking = packet.throttle > 5 and packet.power_out == 0
    vehicle.set_state(packet.rpm > 0, braking)

def handle_extra_button():
    pressed = extra_button_pin.value() > 0
    extra_button.update(pressed)

def handle_control_packet(packet):
    #print(packet)
    global init
    if init < 5:
        init += 1
        for b in buttons:
            v = packet.channel_data.get(b.channel)
            channel_zeros[b.channel] = v

    for b in buttons:
        v = packet.channel_data.get(b.channel)
        if v is not None:
            zero = channel_zeros.get(b.channel, 0x8000)
            pressed = (not b.reverse and v > zero + BUTTON_THRESHOLD) or (b.reverse and v < zero - BUTTON_THRESHOLD)
            b.update(pressed)
    v = packet.channel_data.get(config.level_channel)
    if v is not None:
        level = int(100 * (v - config.level_channel_min) / (config.level_channel_max - config.level_channel_min))
        level = max(level, 0)
        level = min(level, 100)
        vehicle.level_setting(level)

u = UART(1, baudrate = 115200, tx=Pin(8), rx=Pin(9), bits=8, parity=None, invert = UART.INV_RX)
led = Pin(25, Pin.OUT)
last_brake = False
lastt = time.ticks_us()
s = bytes();
srxl2 = SRXL2()
while True:
    while u.any() > 0:
        s += u.read()
        if len(s) > 2 and len(s) >= s[2]:
            packet = srxl2.parse(s)
            if type(packet) == SRXL2Control:
                handle_control_packet(packet)
            elif type(packet) == SRXL2Telemetry and packet.is_esc_telemetry:
                handle_telemetry_packet(packet)
            s = s[s[2]:]
        lastt = time.ticks_us()
    time.sleep_us(10)
    if time.ticks_us() - lastt > 100:
        if len(s) > 0:
            print("Throwing away %d bytes" % len(s))
        s = bytes()

    vehicle.update()
    
    handle_extra_button()
