
class ChannelState:
    FORWARD = 1
    NEUTRAL = 0
    REVERSE = -1

class Channel:
    threshold = 75

    def __init__(self):
        self.state = ChannelState.NEUTRAL

    def update(self, state):
        self.state = state 

    @property
    def reverse(self):
        return self.state == ChannelState.REVERSE

    @property
    def neutral(self):
        return self.state == ChannelState.NEUTRAL

    
