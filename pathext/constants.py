#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""pathext

 - File: pathext/constants.py
 - Author: Havocesp <https://github.com/havocesp/pathext>
 - Created: 2023-07-28
"""
import os
from enum import IntEnum


class PathPerm(IntEnum):
    D_RX = os.R_OK | os.X_OK
    D_RWX = os.R_OK | os.X_OK | os.W_OK
    F_R = os.R_OK
    F_RW = os.R_OK | os.W_OK
    F_RX = os.R_OK | os.X_OK
    F_RWX = os.R_OK | os.X_OK | os.W_OK
