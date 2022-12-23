#!/usr/bin/env python

from datetime import datetime
import sys

import serial


LOG_ROTATE_SEC = 60*60*6


def log(text):
    print(text, file=sys.stderr)


def validate(sentence):
    sentence = sentence.strip()
    if not b"$" in sentence or not b"*" in sentence:
        log(f"ERR: Invalid sentence '{sentence}'")
        return False
    msg, cksum = sentence.split(b"$", 1)[1].strip().split(b"*", 1)
    calc_cksum = 0
    for c in msg:
        calc_cksum ^= c
    exp = f"{calc_cksum:02X}".encode()
    if cksum != exp:
        log(f"ERR: Invalid computed checksum {exp}, expected {cksum}")
        return False
    return True


if __name__=='__main__':

    """ NMEA sentence with checksum error (3rd field
       should be 10 not 20)
    """

    if len(sys.argv) != 3:
        log(f"Usage: {sys.argv[0]} <SERIAL_PORT> <output_files_prefix>")
        exit(1)
    serial_name = sys.argv[1]
    out_fname = sys.argv[2]

    data = b''
    ser = serial.Serial(serial_name, 9600)
    while True:
        time_str = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        log_rotate_timestamp = datetime.utcnow().timestamp() + LOG_ROTATE_SEC
        with open(out_fname + f"{time_str}_nmea.txt", "wt") as out_nmea, \
                open(out_fname + f"{time_str}_junk.txt", "wt") as out_junk:
            while True:
                if datetime.utcnow().timestamp() >= log_rotate_timestamp:
                    break
                data += ser.read(ser.in_waiting or 1)
                if not b'\n' in data:
                    continue
                line, data = data.split(b'\n', 1)

                if validate(line):
                    out_nmea.write(line.decode())
                    out_nmea.write("\n")
                else:
                    time_str = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
                    out_junk.write(f"{time_str}: {repr(line)}\n")
