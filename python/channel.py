from config import config

class ChannelState:
    FORWARD = 1
    NEUTRAL = 0
    REVERSE = -1

class Channel:
    threshold = 75

    def __init__(self):
        self.state = ChannelState.NEUTRAL
        self.position = None

    def update(self, state, position = None):
        self.state = state 
        if position is not None:
            self.position = position

    @property
    def reverse(self):
        return self.state == ChannelState.REVERSE

    @property
    def forward(self):
        return self.state == ChannelState.FORWARD

    @property
    def right(self):
        return self.forward

    @property
    def left(self):
        return self.reverse

    @property
    def neutral(self):
        return self.state == ChannelState.NEUTRAL

class SteeringChannel(Channel):

    @property
    def threshold(self):
        return config.steering_threshold
    
