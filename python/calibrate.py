#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import sbb_rs485


def getch():
    import termios
    import sys
    import tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    return _getch()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log(level, message):
    if (level == 1):
        pf = "[{0}{1}{2}] ".format(bcolors.OKGREEN, "OK", bcolors.ENDC)
    if (level == 4):
        pf = "[{0}{1}{2}]".format(bcolors.FAIL, "FAIL", bcolors.ENDC)
    print("{0} {1}".format(pf, message))


def fmt_ser(ser):
    ss = "{0}{1}{2}{3}".format(
        str(hex(ser[0]))[2:].upper(),
        str(hex(ser[1]))[2:].upper(),
        str(hex(ser[2]))[2:].upper(),
        str(hex(ser[3]))[2:].upper(),
    )
    return ss


def send_msg(msg):
    print("sending: {0}".format(msg))


def main():
    parser = argparse.ArgumentParser(
        description="Calibrate a SBB panel",
    )
    parser.add_argument(
        '--port',
        '-p',
        help="Serial port",
        type=str,
        default='/dev/ttyUSB0',
    )
    parser.add_argument(
        '--address',
        '-a',
        help="Address",
        type=int,
        default=0,
    )
    args = parser.parse_args()

    cc = sbb_rs485.PanelControl(args.port)
    cc.connect()
    cc.serial.timeout = 2

    changed = False
    test_ser = cc.get_serial_number(args.address)
    if len(test_ser) != 4:
        print("ERROR: cannot connect to module")
        sys.exit(1)

    set_pos_before = input(
        "Do you want to set position before calibrate (y/N): {0}".format(
            bcolors.BOLD
        )
    )
    print(bcolors.ENDC, end="")
    if set_pos_before.lower() == "y":
        pos_before = input("Module position: {0}".format(bcolors.BOLD))
        print(bcolors.ENDC, end="")
        cc.set_position(args.address, int(pos_before))

    confirm_calib = input(
        "Start calibration process (Y/n): {0}".format(
            bcolors.BOLD
        )
    )
    print(bcolors.ENDC, end="")
    if confirm_calib.lower() == "n":
        print("cancelled")
        sys.exit()

    calb_start = cc.pack_msg(b'\xCC', args.address)
    calb_step  = cc.pack_msg(b'\xC6', args.address)
    calb_pulse = cc.pack_msg(b'\xC7', args.address)
    cc.send_msg(calb_start)

    print("STEP: Press + until a blade falls. Then Press n (press q to exit)")
    while not changed:
        inp = getch()
        if inp == "+":
            cc.send_msg(calb_step)
        if inp == "q":
            print("exiting")
            sys.exit(1)
        if inp == "n":
            print("OK")
            changed = True
    print("PULSE: Press + until a blade falls. Then Press n (press q to exit)")
    changed = False
    while not changed:
        inp = getch()
        if inp == "+":
            cc.send_msg(calb_pulse)
        if inp == "q":
            print("exiting")
            sys.exit(1)
        if inp == "n":
            print("OK")
            changed = True

    newpos = input("Current blade position: {0}".format(bcolors.BOLD))
    print(bcolors.ENDC, end="")
    newpos = int(newpos)
    calb_win = cc.pack_msg(b'\xCB', args.address, newpos)
    cc.send_msg(calb_win)
    print("Module calibrated")


if __name__ == '__main__':
    main()
