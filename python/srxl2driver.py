from srxl2 import SRXL2, SRXL2Control, SRXL2Telemetry
from machine import UART, Pin
import time

class SRXL2Driver:
    def __init__(self, pin, control_callback, telemetry_callback):
        self.pin = Pin(pin, Pin.IN)
        self.control_callback = control_callback
        self.telemetry_callback = telemetry_callback

    def start(self):
        self.u = UART(1, baudrate = 115200, tx=Pin(8), rx=self.pin, bits=8, parity=None, invert = UART.INV_RX)
        self.rx = bytes()
        self.srxl2 = SRXL2()

    def process(self):

        telemetry_packet = None
        control_packet = None

        while self.u.any() > 0:
            self.rx += self.u.read()
            if len(self.rx) > 2 and len(self.rx) >= self.rx[2]:
                packet = self.srxl2.parse(self.rx)
                if type(packet) == SRXL2Control:
                    control_packet = packet
                elif type(packet) == SRXL2Telemetry and packet.is_esc_telemetry:
                    telemetry_packet = packet
                self.rx = self.rx[self.rx[2]:]
            self.lastt = time.ticks_us()

        if telemetry_packet is not None or control_packet is not None:
            self.rx = bytes()
        if control_packet is not None:
            self.control_callback(control_packet.pwm_channel_data)
        if telemetry_packet is not None:
            self.telemetry_callback(telemetry_packet)

        # Throw away any remaining bytes after 100us of inactivity
        if time.ticks_us() - self.lastt > 100:
            self.rx = bytes()
