#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""pathext

 - File: pathext/utils.py
 - Author: Havocesp <https://github.com/havocesp/pathext>
 - Created: 2023-07-28
"""
import sys
from pathlib import Path
from subprocess import DEVNULL

from sh import zpaq


def unzpaq(path, output_dir, **kwargs):
    result = None
    try:
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        if Path(path).suffix == '.zpaq':
            result = zpaq(f'-t{kwargs.get("t", "4")}', 'x', f'{path}', f'{output_dir or "."}', _err=DEVNULL, _out=DEVNULL)
            return result
    except Exception as err:
        print(f' - [ERROR] {err}', file=sys.stderr)
