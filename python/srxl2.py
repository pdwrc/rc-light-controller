import struct

class SRXL2InvalidPacketException(Exception):
    pass

class SRXL2Packet:

    def __init__(self, packet):
        self.length = packet[2]

        self.process_struct('fields', packet[3:])


    def process_struct(self, name, data):

        fmt = self._structs_[name]
        if len(data) < struct.calcsize(fmt):
            raise SRXL2InvalidPacketException("Short packet")
        fields = struct.unpack(fmt, data[0:struct.calcsize(fmt)])
        for i, (name, fmt, mult) in enumerate(self._struct_maps_[name][1]):
            if mult != 1:
                setattr(self, name, fields[i] * mult)
            else:
                setattr(self, name, fields[i])


    @classmethod
    def setup(cls):
        cls._structs_ = {}
        for name, (endian, fields) in cls._struct_maps_.items():
            fmt = ''.join(fmt_s for name, fmt_s, mult in fields)
            cls._structs_[name] = endian + fmt
        cls._header_size_ = struct.calcsize(cls._structs_['fields']) + 2

class SRXL2Control(SRXL2Packet):

    _struct_maps_ = {
        "fields": ('<', (
            ('command', 'B', 1),
            ('reply_id', 'B', 1),
            ('rssi', 'B', 1),
            ('frame_losses', 'H', 1),
            ('channel_mask', 'L', 1)
            ))
        }

    def __init__(self, packet):
        super().__init__(packet)
        self.channel_data = {}
        self.pwm_channel_data = {}
        i = self._header_size_ + 1


        if self.command != 0:
            return 

        for n in range(32):
            if 1 << n & self.channel_mask:
                if len(packet) < i + 2:
                    raise SRXL2InvalidPacketException("Short packet")
                self.channel_data[n+1] = struct.unpack('<H', packet[i:i+2])[0]
                self.pwm_channel_data[n+1] = int(1000 + (1000*self.channel_data[n+1]/0xFFFF))
                i += 2

    def __repr__(self):
        s = '[CTL] %d' % self.channel_mask
        for channel in sorted(self.channel_data.keys()):
            s += '#%s: %5s ' % (channel, self.channel_data[channel])
        return s


class SRXL2Telemetry(SRXL2Packet):

    DEVICE_ESC = 0x20 

    _struct_maps_ = {
        'fields': ('<', (
            ('dest_id', 'B', 1),
            ('device', 'B', 1),
            ('s_id', 'B', 1),
            ('telemetry', '14s', 1),
            )),

        DEVICE_ESC: ('>', (
            ('rpm', 'H', 10),
            ('volts_input', 'H', 1),
            ('temp_fet', 'H', 0.1),
            ('current_motor', 'H', 10),
            ('temp_bec', 'H', 0.1),
            ('current_bec', 'B', 100),
            ('volts_bec', 'B', 0.05),
            ('throttle', 'B', 0.5),
            ('power_out', 'B', 0.5),
        ))
    }


    def __init__(self, packet):
        super().__init__(packet)
        if self.device in self._struct_maps_:
            self.process_struct(self.device, self.telemetry)

    def __repr__(self):
        s = "[ESC] "
        s += "MOTOR: %5dRPM %3.2fA  IN: %2.1fV  FET: %2.1f°C " % (self.rpm, self.current_motor/1000, self.volts_input/100, self.temp_fet)
        s += "BEC: %2.1f°C  " % (self.temp_bec)
        s += "%1.1fA  " % (self.current_bec/1000)
        s += "%1.1fV  " % (self.volts_bec)
        s += "THROTTLE: %3d%%  POWER: %3d%%" % (self.throttle, self.power_out)
        return s

    @property
    def is_esc_telemetry(self):
        return self.device == self.DEVICE_ESC


for cls in (SRXL2Control, SRXL2Telemetry):
    cls.setup()

class SRXL2:

    PACKET_TYPES = {
        0xCD: SRXL2Control,
        0x80: SRXL2Telemetry,
        }

    def parse(self, packet):
        if len(packet) < 3:
            return None
        (mfr_id, packet_type, length) = struct.unpack("BBB", packet[0:3])
        if mfr_id != 0xA6 or packet_type not in self.PACKET_TYPES:
            print("Unkown packet: %d %d" %(mfr_id, packet_type))
            return None

        try:
            return self.PACKET_TYPES[packet_type](packet)
        except SRXL2InvalidPacketException as e:
            print("Invalid packet")
        return None


