#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""pathext

 - File: pathext/core.py
 - Author: Havocesp <https://github.com/havocesp/pathext>
 - Created: 2023-07-28
"""
import os
import pwd
import shlex
import string
import sys
from bz2 import BZ2File
from datetime import datetime as dt
from gzip import GzipFile
from pathlib import Path
# noinspection PyProtectedMember
from subprocess import CalledProcessError, Popen, list2cmdline
# noinspection PyPep8Naming
from typing import Dict, List, Text as Str, Tuple, Union as U
from zipfile import ZipFile

from binaryornot.check import is_binary, is_binary_string
from rarfile import RarFile
# noinspection PyUnresolvedReferences
from sh import Command, RunningCommand, zpaq

from pathext.constants import PathPerm


class PathExt(type(Path())):
    """Enhanced Path class with extra properties and methods.

    This is an enhanced version of the Path class from the pathlib module with
    extra properties and methods like:

    - ext: File extension.
    - mime: File mime type.
    - size: File size in bytes.
    - type: File type.
    - owner: File owner.
    - group: File group.
    - permissions: File permissions.
    - created: File creation date.
    - modified: File modification date.
    - accessed: File last access date.
    - is_binary: Check if is a binary file.
    """

    class PathType:
        FILE = 'file'
        DIR = 'dir'
        SYMLINK = 'symlink'
        SOCKET = 'socket'
        CHAR_DEVICE = 'char_device'
        BLOCK_DEVICE = 'block_device'
        FIFO = 'fifo'
        RESERVED = 'reserved'

    def glob(self: 'PathExt', pattern: Str) -> List['PathExt']:
        # self.ha
        return list(map(PathExt, super().glob(pattern)))

    def iterdir(self: 'PathExt') -> List['PathExt']:
        return [PathExt(ee) for ee in super().iterdir()]

    def rglob(self: 'PathExt', pattern: Str = None) -> List['PathExt']:
        return list(map(PathExt, super().rglob(pattern or '*')))

    # def rmdir(self, ignore_empt=False) -> bool:
    #     shutil.rmtree(super().cwd(), ignore_errors=True)
    #     super().cwd().rmdir()
    #     return not

    @property
    def expandvars(self: 'PathExt') -> 'PathExt':
        return PathExt(os.path.expandvars(f'{self}'))

    @property
    def exts(self) -> U[None, Str]:
        _tmp_path = Path(self)
        if _tmp_path.is_symlink:
            _tmp_path = super().resolve()
        if _tmp_path.is_file:
            if '.tar' in super().suffixes:
                return ''.join(super().suffixes[-2:])
            else:
                return super().suffix

    @property
    def stem(self) -> Str:
        _stem = super().name or ''
        return _stem.replace(self.exts or '', '')

    _decompress_cmd_map = {
        '.7z': '7z -mmt2 x "{}"',
        '.Z': 'uncompress.real "{}"',
        '.ace': '',
        '.ar': '',
        '.arj': '',
        '.arz': '',
        '.bz2': 'pbzip2 -d  "{}" ',
        '.bz': 'pbzip2 -d  "{}" ',
        '.bzip2': 'pbzip2 -d "{}" ',
        '.gz': 'unpigz -p4 "{}" ',
        '.gzip': 'unpigz -p 4 "{}" ',
        '.lrz': '',
        '.lz': '',
        '.lz4': '',
        '.lzh': '',
        '.lzip': '',
        '.lzma': '',
        '.lzo': '',
        '.pea': '',
        '.rar': 'rar x "{}"',
        '.tZ': '',
        '.tar': 'tar -xf "{}"',
        '.tar.Z': 'tar --use-comppress-program="uncompress.real" -xf "{}"',
        '.tar.bz': 'tar   --use-compress-program=pbzip2 -xf',
        '.tar.bz2': 'tar  --use-compress-program=pbzip2 -xjf "{}"',
        '.tar.bzip': '',
        '.tar.bzip2': 'tar -xjf "{}"',
        '.tar.gz': 'tar -xzf "{}"',
        '.tar.lrz': '',
        '.tar.lz': '',
        '.tar.lz4': '',
        '.tar.lzip': 'tar --lzip -xf "{}"',
        '.tar.lzma': 'tar --lzma -xf "{}"',
        '.tar.lzo': '',
        '.tar.xz': 'tar --xz -xf "{}"',
        '.tar.z': '',
        '.tar.zst': '',
        '.tar.zstd': 'tar --zstd -xf "{}"',
        '.tarbz2': 'tar --use-compress-program="lbzip2" -xf "{}"',
        '.taz': '',
        # '.tb2': '',
        '.tbz': 'tar -xjf "{}"',
        '.tbz2': 'tar -xjf "{}"',
        '.tgz': 'tar -xzf "{}"',
        '.tlrz': '',
        '.tlz': '',
        '.txz': '',
        '.tz': '',
        '.tzst': '',
        '.wmz': '',
        '.xz': 'xz --decompress "{}"',
        '.zip': 'unzip "{}"',
        '.zipx': '',
        '.zz': '',
    }
    _ext2mime_map = {}
    _mime2ext_map = {}
    _size_units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    def __new__(cls, path=None):
        cls._load()
        return Path.__new__(PathExt, path)

    # def __new__(cls, path=None):
    #     return Str.__new__(PathExt, path)

    # def __init__(self, path=None):
    #     super(type(Path()), PathExt).__init__(path)
    @classmethod
    def _load(cls) -> Tuple[Dict, Dict]:
        mime_globs_file = Path('/usr/share/mime/globs')

        if mime_globs_file.is_file():
            lines = mime_globs_file.read_text().splitlines()

            for ln in lines:
                if ln and not ln.startswith('#'):
                    mime, ext = ln.split(':')
                    ext = ext.strip('*')
                    if ext in cls._ext2mime_map:
                        if mime not in cls._ext2mime_map[ext]:
                            cls._ext2mime_map[ext].append(mime)
                    else:
                        cls._ext2mime_map[ext] = [mime]

                    if mime in cls._mime2ext_map:
                        cls._mime2ext_map[mime].append(ext)
                    else:
                        cls._mime2ext_map[mime] = [ext]
        return cls._ext2mime_map, cls._mime2ext_map

    @property
    def is_compressed(self) -> bool:
        """

        :return:
        """
        return self.is_binary and self.extension in self._decompress_cmd_map

    @property
    def is_video(self) -> bool:
        """

        :return:
        """
        return self.is_binary and (self.extension.strip('.') in self.mime or 'video' in self.mime)

    @property
    def is_audio(self) -> bool:
        """

        :return:
        """
        return self.is_binary and (self.extension.strip('.') in self.mime or 'audio' in self.mime)

    @property
    def is_font(self) -> bool:
        """

        :return:
        """
        return self.is_binary and (self.extension.strip('.') in self.mime or 'font' in self.mime)

    @property
    def realpath(self) -> 'PathExt':
        """

        :return:
        """
        return PathExt(super().resolve())

    @property
    def is_file(self) -> bool:
        """

        :return:
        """
        return super().is_file()

    @property
    def is_dir(self) -> bool:
        """

        :return:
        """
        return super().is_dir()

    @property
    def is_absolute(self) -> bool:
        """

        :return:
        """
        return super().is_absolute()

    @property
    def is_empty(self) -> bool:
        """Check if current self path value is empty or not.

        :return: True if curent instance path is empty, or False otherwise.
        """
        if self.is_file:
            return self.size == 0
        elif self.is_dir:
            return not any(self.iterdir())

    @property
    def is_mount(self) -> bool:
        """

        :return:
        """
        return super().is_mount()

    @property
    def is_symlink(self) -> bool:
        """

        :return:
        """
        return super().is_symlink()

    @property
    def extension(self) -> Str:
        """

        :return:
        """
        file_ext = ''
        for suffix in self.suffixes:
            if suffix in self._ext2mime_map:
                file_ext += suffix
        return file_ext

    ext = extension

    @property
    def mime(self) -> U[List[Str], Str]:
        """Guess mime type for path.

        >>> PathExt.home().joinpath('.bashrc').mime
        'application/shell'

        :return:
        """
        file_ext = self.ext
        result = self._ext2mime_map.get(file_ext)
        return result[0] if len(result or []) == 1 else result

    @property
    def size(self) -> int:
        """Return the size of the file in bytes."""
        if self.is_readable:
            if self.is_file:
                return self.stat().st_size
            elif self.is_dir:
                return sum([entry.stat().st_size for entry in self.rglob('*') if not entry.is_symlink and self.is_file])
            else:
                raise FileNotFoundError(f'"{self}" not found or is not neither a directory nor a file.')
        else:
            raise PermissionError(f'Access denied for "{self}" path.')

    def size_as(self, unit: Str, precision: int = 3, raw=False) -> Str:
        """Get a human-readable string format of self instance file size.

        >>> PathExt.home().joinpath('.face').size_as('kb')
        '132.9 Kb'

        :param unit: accepted values: b, kb, mb, gb, tb, pb
        :param precision: round result to supplied precision.
        :param raw: if set, a float will be result instead of Str.
        :return: Human-readable self instance file size.
        """
        unit = Str(unit).upper()

        if isinstance(unit, Str) and unit.upper() in self._size_units:
            bytes_num = self.size
            idx = 0
            while bytes_num >= 1024 and idx < len(self._size_units) - 1:
                bytes_num /= 1024
                idx += 1
            if raw:
                return round(bytes_num, precision)
            else:
                return f"{bytes_num:.{precision}f} {self._size_units[idx].title()}"
        else:
            raise ValueError(f"Invalid supplied unit: {unit}. Accepted values are: {', '.join(self._size_units).rstrip(', ')}")

    @property
    def type(self) -> Str:
        """Return the type of the file."""
        _types = {'file': 0o100000, 'dir': 0o040000, 'link': 0o120000, 'socket': 0o140000, 'char': 0o020000, 'block': 0o060000, 'fifo': 0o010000, 'special': 0o170000}
        return next((k for k, v in _types.items() if self.stat().st_mode & v), 'unknown')

    @property
    def owner_id(self) -> int:
        """

        :return:
        """
        return self.stat().st_uid

    @property
    def owner(self) -> Str:
        """

        :return:
        """
        return pwd.getpwuid(self.owner_id).pw_name

    @property
    def group_id(self) -> int:
        """

        :return:
        """
        return self.stat().st_gid

    def permissions(self, octal: bool = False) -> Str | int:
        """Return the permissions of the file.

        :param octal: If True, return the permissions as an octal number.
        :return: The permissions of the file as a string or an octal number.
        """
        perm = oct(self.stat().st_mode)[-3:]
        if octal:
            return int(perm)
        return perm

    @property
    def lines(self) -> List[Str]:
        """

        :return:
        """
        if self.is_readable and not self.is_binary:
            return self.content.splitlines()

    @property
    def is_readable(self) -> bool:
        """

        :return:
        """
        _tmp_path = self.resolve()
        if _tmp_path.is_file or _tmp_path.is_dir:
            return os.access(self, PathPerm.D_RX if _tmp_path.is_dir else PathPerm.F_R)
        else:
            return False

    @property
    def is_writable(self) -> bool:
        """

        :return:
        """
        _tmp_path = self.resolve()
        if _tmp_path.is_file or _tmp_path.is_dir:
            return os.access(self, PathPerm.D_RWX if _tmp_path.is_dir else PathPerm.F_RW)
        else:
            return False

    @property
    def is_executable(self) -> bool:
        """

        :return:
        """
        return self.is_file and os.access(self, PathPerm.F_RX)

    @property
    def cwd(self) -> 'PathExt':
        """

        :return:
        """
        return PathExt(super().cwd())

    @property
    def dirname(self) -> 'PathExt':
        """

        :return:
        """
        return PathExt(super().parent)

    @property
    def last_modified(self) -> float:
        """

        :return:
        """
        return super().stat().st_mtime

    @property
    def last_modified_date(self) -> dt:
        """

        :return:
        """
        return dt.fromtimestamp(self.last_modified)

    @property
    def last_access(self) -> float:
        """

        :return:
        """
        return self.stat().st_atime

    @property
    def last_access_date(self) -> dt:
        """

        :return:
        """
        return dt.fromtimestamp(self.last_access)

    @property
    def created(self) -> float:
        """

        :return:
        """
        return self.stat().st_ctime

    @property
    def created_date(self) -> dt:
        """

        :return:
        """
        return dt.fromtimestamp(self.created)

    @property
    def is_binary(self) -> bool:
        """Check if self instance is a binary file or not.

        :return: True if self instance is a binary file. False, otherwise.
        """
        return self.is_readable and is_binary(Str(self.resolve()))

    @property
    def escape(self) -> 'PathExt':
        """

        :return:
        """
        return PathExt(shlex.quote(self.resolve()))

    @property
    def content(self) -> bytes | Str:
        """

        :return:
        """
        if self.is_readable and self.is_file:
            if self.is_binary:
                if self.is_compressed:
                    # if self.extension in ('.tar.gz', '.tar.bz2', '.tar.xz', '.tar.Z', '.tgz',):
                    #     with TarFile.open(self, 'r|*') as compressed:
                    #         content = compressed.open(self, 'rb').e.read()
                    #         if not is_binary_string(content):
                    #             return content.decode('utf-8', 'ignore')
                    if self.extension == '.rar':
                        with RarFile(self, 'rb').open(self, 'rb') as compressed:
                            content = compressed.read()
                            if not is_binary_string(content):
                                return content.decode('utf-8', 'ignore')
                    if self.extension == '.zip':
                        with ZipFile(self, 'rb').open(self, 'rb') as compressed:
                            content = compressed.read()
                            if not is_binary_string(content):
                                return content.decode('utf-8', 'ignore')
                    elif self.extension == '.gz':
                        with GzipFile(self, 'rb') as compressed:
                            content = compressed.read()
                            if not is_binary_string(content):
                                return content.decode('utf-8', 'ignore')
                    elif self.extension == '.bz2':
                        with BZ2File(self, 'rb') as compressed:
                            content = compressed.read()
                            if not is_binary_string(content):
                                return content.decode('utf-8', 'ignore')
                else:
                    return self.read_bytes()
            else:
                return self.read_text()

    @property
    def content_info(self) -> Tuple[int, int, int]:
        """If self instance is a text file, count their lines, words and chars and return results as tuple.

        Works like 'wc' command in Linux.

        :return: the num of lines, words and chars readed from self content.
        """
        _lines = self.lines
        if _lines:
            _words = []
            _chars = 0
            for ln in _lines:
                _wds = ln.strip(string.whitespace).split()
                for _wd in _wds:
                    if _wd.strip(string.whitespace):
                        _words.append(_wd.strip(string.whitespace))
                        _chars += len(_wd.strip(string.whitespace))
            return len(_lines), len(_words), _chars
        else:
            raise IOError(f'File "{self}" is binary or is empty.')

    @property
    def num_lines(self) -> int:
        """

        :return:
        """
        return len(self.lines)

    wcl = num_lines
    lno = num_lines

    @property
    def num_words(self) -> int:
        """

        :return:
        """
        return self.wc[1]

    wc = num_words

    @property
    def num_chars(self) -> int:
        """

        :return:
        """
        return self.wc[2]
        # def mime2ext(self, mime) -> U[List[Str], Str]:  #     result = self._mime2ext_map.get(mime)  #     return result[0] if len(result or []) == 1 else result

    cc = num_chars

    @classmethod
    def _run_cmd(cls, *command):
        pr = None
        try:

            def _safe_cmd(*_cmds) -> List[Str]:
                _cmd = list(map(Str, _cmds))
                _cmd_str = list2cmdline(_cmds)
                return shlex.split(_cmd_str)

            pr = Popen(_safe_cmd(*command))
            # pr.
            # self.label.setText(f"{task_name} successful!")
        except CalledProcessError as err:
            print(f' - [ERROR] {" ".join(command)} failed: {err}', file=sys.stderr)
        return pr


if __name__ == '__main__':
    print(PathExt('/root').is_readable)
