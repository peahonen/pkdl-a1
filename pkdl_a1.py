#!/usr/bin/env python3

import sys
import time
import serial
import struct
from datetime import datetime
import argparse

def configmsg(args,now):
    a=0x01
    b=0x01
    c=0x01
    d=0x00
    e=0x03
    r=0x00

    body = struct.pack('<BBBBhhHHHBBBBBBBBBBBBBBBBBBBBB',
                0x01,
                a,
                0x01,
                0x00,
                int(args.maxtemp*100),
                int(args.mintemp*100),
                int(args.maxhumidity*10),
                int(args.minhumidity*10),
                (args.interval + 4)//5,
                0x00,
                r,
                0x00,
                0x00,
                args.timezone,
                b,
                now.year-2000,
                now.month,
                now.day,
                now.hour,
                now.minute,
                now.second,
                c,
                d,
                e,
                0x30,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00)
    fcs = struct.pack('<H', sum(body)+256+len(body)-1)

    header = struct.pack('<BBB',
                         0x5a,
                         0xa5,
                         len(body))
    return (header+body+fcs)

def main():
    parser = argparse.ArgumentParser(
                    prog = 'pkdl-ai',
                    description = 'Configure LIDL PKDL-A1 climate data logger',
                    epilog = 'Start recording, reconnect device and read PDF report to confirm settings')
    parser.add_argument('-T', '--maxtemp', type=int, default=40)
    parser.add_argument('-t', '--mintemp', type=int, default=0)
    parser.add_argument('-R', '--maxhumidity', type=int, default=80)
    parser.add_argument('-r', '--minhumidity', type=int, default=30)
    parser.add_argument('-i', '--interval', type=int, default=3600)
    parser.add_argument('-z', '--timezone', type=int, default=3)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-d', '--device', default="/dev/tty.usbmodem00000000050C1")
    args = parser.parse_args()
    now = datetime.now()

    s=configmsg(args,now)
    if args.verbose:
        print(" ".join("%02x" % b for b in s))
    if not args.dry_run:
        ser = serial.Serial(args.device)
        ser.write(s)
        r = ser.read(len(s))
        if args.verbose:
            print(" ".join("%02x" % b for b in r))
        ser.close()
        if s == r:
            return 0
        else:
            return 1

if __name__ == '__main__':
    sys.exit(main())

