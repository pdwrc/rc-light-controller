
class ChannelState:
    FORWARD = 1
    NEUTRAL = 0
    REVERSE = -1

class Channel:
    threshold = 120

    def __init__(self, channel):
        self.channel = channel
        self.state = ChannelState.NEUTRAL

    def update(self, state):
        self.state = state 

    @property
    def reverse(self):
        return self.state == ChannelState.REVERSE
    
