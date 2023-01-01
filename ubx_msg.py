#!/usr/bin/env python

import struct
import sys


UBX_SYNC = b'\xb5\x62'
MSG = (
    0,  # U1 Time-pulse 1
    1,  # U1 reserved
    0,  # U2 reserved
    0,  # I2 cable delay (ns)
    0,  # I2 RF group delay (ns)
    4,  # U4 freq or period (Hz / us)
    int(10e6), # U4 freq or period of locked (Hz / us)
    0,  # U4 pulse len ration (us or 2^-32)
    0x80000000, # U4 pulse ratio lock (us or 2^-32)
    0, # I4 user configurable time pulse delay (ns)
    0x0000086F, # X4 flags
)
MSG_STRUCT = '<BBHhhIIIIII'


def ubx_msg_cksum(data):
    ck_a = ck_b = 0
    for b in data:
        ck_a += b
        ck_b += ck_a
    ck_a &= 0xff
    ck_b &= 0xff
    return ck_a, ck_b


def main():
    msg_class = 0x06
    msg_id = 0x31
    payload = struct.pack(MSG_STRUCT, *MSG)

    msg = UBX_SYNC
    msg += struct.pack('<BBH', msg_class, msg_id, len(payload))
    msg += payload
    msg += struct.pack('<BB', *ubx_msg_cksum(msg[2:]))
    sys.stdout.buffer.write(msg)
    #for c in msg:
    #    print(f"0x{c:02X}")


if __name__ == '__main__':
    main()
