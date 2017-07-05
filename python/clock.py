#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sbb_rs485
import time
from datetime import datetime

SBB_MODULE_ADDR_HOUR = 55
SBB_MODULE_ADDR_MIN  = 56


def main():
    clock = sbb_rs485.PanelClockControl(
        addr_hour=SBB_MODULE_ADDR_HOUR,
        addr_min=SBB_MODULE_ADDR_MIN
    )
    clock.connect()
    while True:
        clock.set_time_now()
        ts = datetime.utcnow()
        sleeptime = 60 - (ts.second + ts.microsecond / 1000000.0)
        time.sleep(sleeptime)


if __name__ == '__main__':
    main()
