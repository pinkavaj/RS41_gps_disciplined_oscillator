#!/usr/bin/env python

from datetime import datetime
import errno
import sys
import os
from os.path import exists, getsize
import stat
from os import mkfifo, remove
from struct import unpack

import serial


LOG_ROTATE_SEC = 60*60*6
UBX_SYNC = b'\xb5\x62'


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


def ubx_msg_cksum(data):
    ck_a = ck_b = 0
    for b in data:
        ck_a += b
        ck_b += ck_a
    ck_a &= 0xff
    ck_b &= 0xff
    return ck_a, ck_b


def process_ubx_message(data):
    offs = data.find(UBX_SYNC)
    msg = data[offs:]
    if len(msg) < 8:
        return data
    _, msg_class, msg_id, payload_size = unpack('<HBBH', msg[:6])
    if payload_size + 8 > len(msg):
        return data
    msg = msg[:8 + payload_size]
    msg_ck_a, msg_ck_b = msg[-2:]
    ck_a, ck_b = ubx_msg_cksum(msg[2:-2])
    if msg_ck_a != ck_a or msg_ck_b != ck_b:
        log(f'Invalid UBX message {msg.hex(" ")} / {repr(msg)}')
        return data[offs + 2:]
    MSG_CLASS_NAME = {
        0x01: 'NAV',
        0x02: 'RMX',
        0x04: 'INF',
        0x05: 'ACK',
        0x06: 'CFG',
        0x0A: 'MON',
        0x0B: 'AID',
        0x0D: 'TIM',
    }
    log(f'UBX message: {MSG_CLASS_NAME[msg_class]} 0x{msg_class:02X} 0x{msg_id:02X}    {msg[6:-2].hex(" ")}')

    return data[offs + payload_size + 8:]


def open_pipe(pipe_path):
    if not exists(pipe_path):
        mkfifo(pipe_path, 0o0770)
    elif not stat.S_ISFIFO(os.stat(pipe_path).st_mode):
        raise ValueError(f"Error: expected FIFO or no file here '{path}', get somethink else")
    return os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)


def handle_pipe(ser, fpipe):
    try:
        data = os.read(fpipe, 1000000)
        if data:
            ser.write(data)
    except OSError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            raise


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
        junk_fname = out_fname + f"{time_str}_junk.txt"
        pipe_path = out_fname + "gps_serial_port_in"
        fpipe = open_pipe(pipe_path)
        with open(out_fname + f"{time_str}_nmea.txt", "wt") as out_nmea, \
                open(junk_fname, "wt") as out_junk:
            while True:
                if datetime.utcnow().timestamp() >= log_rotate_timestamp:
                    break
                handle_pipe(ser, fpipe)
                data += ser.read(ser.in_waiting or 1)
                if UBX_SYNC in data:
                    data = process_ubx_message(data)
                if not b'\n' in data:
                    continue
                line, data = data.split(b'\n', 1)

                if validate(line):
                    out_nmea.write(line.decode())
                    out_nmea.write("\n")
                else:
                    time_str = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
                    out_junk.write(f"{time_str}: {repr(line)}\n")
        if exists(junk_fname) and getsize(junk_fname) == 0:
            remove(junk_fname)
