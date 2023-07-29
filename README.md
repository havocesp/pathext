# PathExt

## Description

Just an enhanced version of Python built-in pathlib.Path class.

### Features

**TODO**

## Installation

### With `pip` from official repository:

```shell
$ pip install git+https://github.com/havocesp/pathext
```

## usage

```python
from pathext import PathExt

file_path = PathExt.home().joinpath('.bashrc')

print(file_path.size)  # 54353 bytes
print(file_path.is_video)  # False
print(file_path.is_binary)  # False
print(file_path.num_lines)  # 96
```

## Changelog

### 0.1.0

- Initial vesion
