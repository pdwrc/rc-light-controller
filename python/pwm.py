from machine import UART, Pin, time_pulse_us
import rp2
import time

from light import Animation

#https://github.com/GitJer/PwmIn/blob/main/PwmIn.pio

class RCMode:
    PWM = 0
    SMART = 1

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def time_gap():
    # Measure time that pin is high for.  
    # Input is inverted, so this is the gap between PWM pulses or a series of
    # consecutive 1s in UART

    # Timing loop is 2 instructions

    wrap_target()
    mov(x, invert(null))

    label("timer")
    jmp(x_dec, "test")
    jmp("timerstop")
    label("test")
    jmp(pin, "timer")     # Loop if pin is high
    label("timerstop")

    mov(isr,x)
    push(noblock)

    wait(1,pin,0)

    wrap()

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def time_pulse():
    # Measure time that pin is low for
    # Timing loop is 3 instructions
    wrap_target()
    mov(x, invert(null))

    label("timer")
    jmp(x_dec, "test")
    jmp("timerstop")
    label("test")
    jmp(pin,"timerstop") # If pin is high, stop the timer
    jmp("timer")
    label("timerstop")

    mov(isr,x)
    push(noblock)

    wait(0,pin,0)
    wrap()


def detect_signal_type(vehicle, pin):
    print("Detecting input signal")

    sm = rp2.StateMachine(0, time_gap, freq=1_000_000, jmp_pin=pin, in_base=pin)
    sm.active(1)

    gaps = []
    last_gap_pwm = None

    vehicle.status_led.animate(Animation.simple_flash, loop = True)
            
    while len(gaps) < 50:
        while sm.rx_fifo() > 0:
            gap = (0xFFFFFFFF - sm.get()) * 2
            # SRXL should never be longer than 9/115200 = 78us
            # PWM should not be shorter than 1/333 - 2ms = 1ms
            is_pwm = gap > 500
            if is_pwm == last_gap_pwm:
                gaps.append(gap)
            else:
                gaps = []
            last_gap_pwm = is_pwm

        time.sleep_us(10)
        vehicle.status_led.tick()

    vehicle.status_led.animate(None)

    if last_gap_pwm:
        vehicle.status_led.set_level(0)
        print("Detected PWM signal")
        return RCMode.PWM
    else:
        vehicle.status_led.set_level(100)
        print("Detected SRXL2 signal")
        return RCMode.SMART

class PWMRCDriver:
    def __init__(self, pins, control_callback):
        self.pins = pins
        self.control_callback = control_callback

    def start(self):
        self.sms = []
        for i, pin in enumerate(self.pins):
            sm = rp2.StateMachine(i, time_pulse, freq=1_000_000, jmp_pin=pin, in_base=pin)
            sm.active(1)
            self.sms.append(sm)

    def process(self):
        data = {}
        for i, sm in enumerate(self.sms):
            while sm.rx_fifo() > 0:
                v = (0xFFFFFFFF - sm.get()) * 3
                if v > 700 and v < 2300:
                    data[i+1]  = v
    
        if len(data) > 0:
            self.control_callback(data)
