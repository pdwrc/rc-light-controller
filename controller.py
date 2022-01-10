from machine import UART, Pin
from srxl2 import SRXL2, SRXL2Control, SRXL2Telemetry
import time
import struct
import light
from button import ButtonState
import vehicle as veh
from config import config, LightConfig

vehicle = veh.Vehicle(config)

buttons = (
        ButtonState(config.primary_button_channel, vehicle.primary_click, reverse=config.primary_button_reverse),
        ButtonState(config.handbrake_button_channel, vehicle.handbrake_click, reverse=config.handbrake_button_reverse),
        )

BUTTON_THRESHOLD = 10

extra_button_pin = Pin(2, Pin.IN, Pin.PULL_DOWN)
extra_button = ButtonState(None, vehicle.primary_click)

init = False

channel_zeros = {}

packet_count = 0

def handle_telemetry_packet(packet):
    #print(time.ticks_ms())
    #print(packet)
    braking = packet.throttle > 5 and packet.power_out == 0
    vehicle.set_state(packet.rpm > 0, braking, packet.volts_input)

def handle_extra_button():
    pressed = extra_button_pin.value() > 0
    extra_button.update(pressed)

def handle_control_packet(packet):
    global init
    if not init:
        print(packet)
        ok = True
        for b in buttons:
            v = packet.channel_data.get(b.channel)
            if v is None:
                ok = False
            else:
                channel_zeros[b.channel] = v
        if ok and 10 not in packet.channel_data and packet.channel_data != {}:
            init = True
            for l in vehicle.lights:
                l.animate(light.Animation.multi_flash(3))
    else:
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
    global packet_count
    packet_count += 1
    if packet_count >= 100:
        status_led.animate(light.Animation.simple_flash)
        packet_count = 0

status_led = light.Light(LightConfig(25, 0, 100), no_pwm = True)

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
#        if len(s) > 0:
#            print("Throwing away %d bytes" % len(s))
        s = bytes()

    vehicle.update()
    status_led.tick()
    handle_extra_button()
