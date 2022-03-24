import json
import os

from pins import Pins, VERSION

class RCMode:
    PWM = 0
    SMART = 1

class BrakeMode:
    SIMPLE = 0
    SMART = 1
    LIFT_OFF_DELAY = 2

    labels = {
        SIMPLE: "Simple",
        SMART: "Smart",
        LIFT_OFF_DELAY: "Lift-off"
    }

    title = "Brake mode"
    description = """
    <p>Select mode for brake lights.</p>
    <ul>
      <li><b>Simple</b> - brake lights activate with reverse throttle.</li>
      <li><b>Smart</b> - brake lights activate with first application of reverse throttle only.</li>
      <li><b>Lift-off</b> - brake lights activate for a short period whenever throttle is released.</li>
    </ul>
    """

class ButtonMode:
    NONE = 0
    BRAKE = 1
    FLASH = 2
    EMERGENCY_TOGGLE = 3

    title = "Secondary button"

    labels = {
        NONE: "None",
        BRAKE: "Brake",
        FLASH: "Full beam flash",
        EMERGENCY_TOGGLE: "Emergency lights",
    }

    description = """
    <p>Secondary button function:</p>
    <ul>
      <li><b>None</b> - no action</li>
      <li><b>Brake</b> - activate brake lights</li>
      <li><b>Full beam flash</b> - activate <i>full-bean flash</i> mode while button is pressed</li>
      <li><b>Emergency lights</b> - toggle emergency lights</li>
    </ul>
    """

class EmergencyMode:
    OFF = 0
    MODE_2 = 1
    MODE_1_2 = 2

    title = "Emergency light mode"

    labels = {
        OFF: "Not active",
        MODE_2: "Activate in mode 2 only",
        MODE_1_2: "Activate in modes 1 and 2",
    }

    description = """
    Set which mode(s) emergency lights are active in.
    """

class SteeringThresholdConfig:
    title = "Steering Threshold"
    name = "steering_threshold"
    description = """
    Steering position threshold for triggering turn signals.  Increase this value to increase the amount of steering required to trigger turn signals.  This threshold is also used to detect "activity" when considering if sleep mode should be activated.
    """

class SleepWhenLightsOnMode:
    labels = {
        0: "Sleep only when lights off",
        1: "Sleep in any mode",
    }

    title = "Sleep when lights on"

    description = """
    Set whether sleep mode activates when lights are on.
    """

class SleepDelayConfig:
    title = "Sleep delay"
    name = "sleep_delay"

    description = """
        Time, in seconds, from last activity before sleep animation starts.
    """

class BreatheTimeConfig:
    title = "Sleep animation speed"
    name = "breathe_time"

    description = """
        Speed of sleep animation.  Length, in milliseconds, of "breathe" effect.
    """

class BreatheGapConfig:
    title = "Sleep animation gap"
    name = "breathe_gap"

    description = """
        Time, in milliseconds, between "breaths" of the sleep animation.
    """

class BreatheMinimumBrightnessConfig:
    title = "Sleep animation minimum brightness"
    name = "breathe_min_brightness"

    description = """
        The minimum brightness of the sleep animation.  This is set a
        percentage of the maximum brightness.  If set to zero, the lights will
        turn fully off between "breaths".  High values will give a more subtle
        effect.
    """

class FadeTimeConfig:
    title = "Fade speed"
    name = "fade_time"

    description = """
    Adjust how fast lights transition between different brightness levels.
    Sets the time of the transition in milliseconds.  Set to zero for an
    instant transition.  Higher values give a softer transition, simulating
    traditional incandescent bulbs.
    """


class LightState:

    def __init__(self, name, title, description, default):
        self.name = name
        self.title = title
        self.description = description
        self.default = default

LightStates = (
    LightState(
        "mode1",
        "Mode 1",
        "Brightness of channel in mode 1",
        50 
    ),
    LightState(
        "mode2",
        "Mode 2",
        "Brightness of channel in mode 2",
        100 
    ),
    LightState(
        "flash",
        "Full beam flash",
        "Brightness of channel when <i>full beam flash</i> is activated. Set to zero to disable function on this channel.",
        100 
    ),
    LightState(
        "brake",
        "Brake",
        "Brightness of channel when braking. Set to zero to disable function on this channel.",
        0 
    ),
    LightState(
        "turn_left",
        "Left turn",
        "Brightness of channel for left turn signal. Set to zero to disable function on this channel.",
        0 
    ),
    LightState(
        "turn_right",
        "Right turn",
        "Brightness of channel for right turn signal. Set to zero to disable function on this channel.",
        0 
    ),
    LightState(
        "emergency1",
        "Emergency 1",
        "Brightness of channel when emergency lights are activated.  Emergency light mode flashes two channels in an alternating sequence.  This is the first channel. Set to zero to disable function on this channel.",
        0 
    ),
    LightState(
        "emergency2",
        "Emergency 2",
        "Brightness of channel when emergency lights are activated.  Emergency lights mode flashes two channels in an alternating sequence.  This is the second channel. Set to zero to disable function on this channel.",
        0 
    ),
    LightState(
        "breathe",
        "Sleep",
        "Brightness of channel when sleep animation is activated.  Set to zero to disable function on this channel.",
        0 
    ),
)

class LightConfig:

    properties = (
            "mode1",
            "mode2",
            "flash",
            "brake",
            "breathe",
            "turn_left",
            "turn_right",
            "emergency1",
            "emergency2",
            )

    def __init__(self, pin, mode1, mode2, brake = 0, flash = 0, breathe = 0, turn_left = 0, turn_right = 0, emergency1 = 0, emergency2 = 0, menu = 50):
        self.pin = pin
        self.mode1 = mode1
        self.mode2 = mode2
        self.brake = brake
        self.flash = flash
        self.breathe = breathe
        self.turn_left = turn_left
        self.turn_right = turn_right
        self.emergency1 = emergency1
        self.emergency2 = emergency2
        self.menu = menu

    def as_dict(self):
        d = {
            "pin": self.pin,
        }
        for p in self.properties:
            d[p] = getattr(self, p)
        return d

    def set_value(self, prop, value):
        if prop in self.properties:
            try:
                setattr(self, prop, int(value))
            except ValueError:
                return False

            return True
        return False


class PWMMode:
    SW_TH = 0
    TH_ST = 1

    labels = {
        SW_TH: "Input 1: Switch / Input 2: Throttle",
        TH_ST: "Input 1: Throttle / Input 2: Steering",
    }

    title = "PWM Channel mode"
    description = "Configure which RC channels are connected to the controller's inputs."

class Config:

    properties = ("primary_button_channel", "primary_button_reverse", "handbrake_button_channel", "handbrake_button_reverse", 
                "fade_time", "secondary_button_mode", "emergency_mode", "pwm_mode", "breathe_time", "breathe_gap", "sleep_delay",
                "sleep_when_lights_on", "breathe_min_brightness", "steering_threshold", "pwm_brake_mode")

    def __init__(self, data):
        self.version = VERSION

        self.lights = []
        lights = data.get("lights")
        if lights is not None:
            self.lights = [ LightConfig(
                x.get("pin"), 
                x.get("mode1", 0), 
                x.get("mode2", 100), 
                x.get("brake", 0), 
                x.get("flash", 0), 
                x.get("breathe",0),
                x.get("turn_left",0),
                x.get("turn_right",0),
                x.get("emergency1",0),
                x.get("emergency2",0),
            ) for x in lights ]
        else:
            for pin in Pins.OUTPUTS:
                self.lights.append(LightConfig(pin, 20, 100))

            # First light should breathe
            self.lights[0].breathe = 40

            # Second light should flash
            self.lights[1].flash = 100

            # Make the last light a brake light
            self.lights[-1].brake = 100
            self.lights[-1].mode2 = 20

        self.pwm_mode = data.get("pwm_mode", PWMMode.SW_TH)
        self.primary_button_channel = data.get("primary_button_channel", 8)
        self.primary_button_reverse = data.get("primary_button_reverse", False)
        self.handbrake_button_channel = data.get("handbrake_button_channel", 8)
        self.handbrake_button_reverse = data.get("handbrake_button_reverse", True)
        self.level_channel = data.get("level_channel", 6)
        self.level_channel_min = data.get("level_channel_min", 1250)
        self.level_channel_max = data.get("level_channel_max", 1750)
        self.sleep_delay = data.get("sleep_delay", 5)
        self.sleep_when_lights_on = int(data.get("sleep_when_lights_on", 0))
        self.breathe_min_brightness = data.get("breathe_min_brightness", 0)
        self.breathe_time = data.get("breathe_time", 4000)
        self.breathe_gap = data.get("breathe_gap", 1000)
        self.fade_time = data.get("fade_time", 90)
        self.secondary_button_mode = data.get("secondary_button_mode", ButtonMode.NONE)
        self.emergency_mode = data.get("emergency_mode", EmergencyMode.OFF)
        self.steering_threshold = data.get("steering_threshold", 100)
        self.pwm_brake_mode = data.get("pwm_brake_mode", BrakeMode.SMART)
        self.hardware_button_pin = Pins.BUTTON
        self.input_pins = Pins.INPUTS
        self.status_led_pins = Pins.STATUS_LEDS

    def load():
        try:
            with open("config.json") as fin:
                return Config(json.load(fin))
        except:
            new_config = Config({})
            return new_config

    def config_data(self):
        data = {}
        data["lights"] = [ light.as_dict() for light in self.lights ]
        for x in self.properties:
            data[x] = getattr(self, x)

        return data

    def save(self):
        with open("config.json", "w") as fout:
            json.dump(self.config_data(), fout)
        print("LOG config saved")

    def set_value(self, path, value):
        parts = path.split('/')
        prop = parts[0]

        if len(parts) == 1 and parts[0] in self.properties:
            try:
                if type(getattr(self, path)) == bool:
                    setattr(self, path, bool(int(value)))
                else:
                    setattr(self, path, int(value))
                print("LOG setting %s to %s" % (path, value))
                return True
            except ValueError:
                return False
        elif parts[0] == 'lights' and len(parts) == 3:
            (x, n, prop) = parts
            try:
                n = int(n)
            except ValueError:
                return False
            return self.lights[n].set_value(prop, value)

        return False

    def channel_map(self, mode, vehicle):
        cm = {}
        if mode == RCMode.SMART:
            cm[(self.primary_button_channel, self.primary_button_reverse)] = vehicle.primary_button
            cm[(self.handbrake_button_channel, self.handbrake_button_reverse)] = vehicle.secondary_button
            cm[(1, False)] = vehicle.throttle
            cm[(4, False)] = vehicle.steering
        else:

            if self.pwm_mode == PWMMode.SW_TH or len(self.input_pins) > 2:
                cm[1, False] = vehicle.primary_button
                cm[1, True] = vehicle.secondary_button
                if len(self.input_pins) > 1:
                    cm[2, False] = vehicle.throttle
                if len(self.input_pins) > 2:
                    cm[3, False] = vehicle.steering
            elif self.pwm_mode == PWMMode.TH_ST:
                cm[1, False] = vehicle.throttle
                if len(self.input_pins) > 1:
                    cm[2, False] = vehicle.steering

        return cm
        

config = Config.load()

