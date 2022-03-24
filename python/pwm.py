from machine import UART, Pin, time_pulse_us
import rp2
import time
from config import RCMode
from animation import SimpleAnimation

#https://github.com/GitJer/PwmIn/blob/main/PwmIn.pio


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


def detect_signal_type(vehicle, pins, hardware_button_pin, cli):
    print("LOG Detecting input signal")

    gaps = []

    sms = []
    last_gap_pwm = []
    for i, pin in enumerate(pins):
        p = Pin(pin, Pin.IN)
        sm = rp2.StateMachine(i, time_gap, freq=1_000_000, jmp_pin=p, in_base=p)
        sm.active(1)
        sms.append(sm)
        gaps.append([])
        last_gap_pwm.append(None)

    vehicle.status_led.animate(SimpleAnimation.flash(), loop = True)
    hardware_button_clicked = False
            
    while all(len(g) < 50 for g in gaps):
        for i, sm in enumerate(sms):
            while sm.rx_fifo() > 0:
                gap = (0xFFFFFFFF - sm.get()) * 2
                # SRXL should never be longer than 9/115200 = 78us
                # PWM should not be shorter than 1/333 - 2ms = 1ms
                is_pwm = gap > 500
                if is_pwm == last_gap_pwm[i]:
                    gaps[i].append(gap)
                else:
                    gaps[i] = []
                last_gap_pwm[i] = is_pwm

        time.sleep_us(10)
        cli.process()
        vehicle.update()
        if hardware_button_pin is not None and hardware_button_pin.value() == 1:
            hardware_button_clicked = True
            break

    vehicle.status_led.animate(None)

    # Wait for button to be released, if pressed.
    if hardware_button_clicked:
        while hardware_button_pin.value() == 1:
            time.sleep_us(10)

    if hardware_button_clicked:
        return None

    for i, g in enumerate(gaps):
        if len(g) >= 50:
            pwm = last_gap_pwm[i]
            print("LOG Detected %s signal on channel %d" % ("PWM" if pwm else "SMART", i))
            break

    if pwm:
        print("LOG Detected PWM signal")
        return RCMode.PWM
    else:
        print("LOG Detected SRXL2 signal")
        return RCMode.SMART

class PWMRCDriver:
    def __init__(self, pins, control_callback):
        self.pins = pins
        self.control_callback = control_callback

    def start(self):
        self.sms = []
        for i, pin in enumerate(self.pins):
            p = Pin(pin, Pin.IN)
            sm = rp2.StateMachine(i, time_pulse, freq=1_000_000, jmp_pin=p, in_base=p)
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
