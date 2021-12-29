import unittest
import struct

import srxl2



def test_control_packet():

    parser = srxl2.SRXL2()
    hdr = struct.pack("<BBBBBBH",
            0xA6,
            0xCD,
            0,
            0,
            0,
            0,
            1234
            )

    channel_data = struct.pack("<LHH",
            0b1001,
            100,
            200
            )

    data = bytearray(hdr + channel_data)

    data[2] = len(data)
    p = parser.parse(data)
    assert p is not None
    assert type(p) == srxl2.SRXL2Control
    assert p.rssi == 0
    assert p.frame_losses == 1234
    assert p.channel_mask == 0b1001
    assert p.channel_data == { 1 : 100, 4: 200 }

    #short packet
    p = parser.parse(data[:-1])
    assert p is None

def test_telemetry_packet():

    parser = srxl2.SRXL2()
    hdr = struct.pack(">BBBBBBHHHHHBBBB",
            0xA6,
            0x80,
            0,
            0,
            0x20,  # ESC
            0,
            1234,  # 12340 RPM
            1370,  # 13.7V
            200,   # 20degC
            2000,  # 2A
            210,   # 21 degC
            12,    # 1.2A 
            148,   # 7.4V
            100,   # 50%
            150,   # 75%
            )

    data = bytearray(hdr)

    data[2] = len(data)
    p = parser.parse(data)
    assert p is not None
    assert type(p) == srxl2.SRXL2Telemetry
    assert p.device == srxl2.SRXL2Telemetry.DEVICE_ESC
    assert p.rpm == 12340
    assert "%.1f" % p.volts_input == "13.7"
    assert p.temp_fet == 20
    assert p.current_motor == 20000
    assert p.temp_bec == 21
    assert p.current_bec == 1200
    assert p.volts_bec == 7.4
    assert p.throttle == 50
    assert p.power_out == 75
    
    # short packet
    p = parser.parse(data[:-1])
    assert p is None

