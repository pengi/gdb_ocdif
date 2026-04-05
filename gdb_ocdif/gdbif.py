# Copyright © 2026 Max Sikström
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gdb
import traceback

from typing import List, Tuple, Dict, Callable, Optional, Set


def gdb_call(command: str) -> None:
    gdb.execute(command)


class ArgType:
    def __init__(
        self,
        name: str,
        completer: (
            None | Callable[[str, Set[str], Dict[str, str]], List[str]] | List[str]
        ) = None,
        getter: Optional[Callable[[str, Set[str], Dict[str, str]], str]] = None,
        optional: bool = False,
    ) -> None:
        self.name = name
        self.completer = completer
        self.getter = getter
        self.optional = optional

    def complete(
        self, word: str, flags: Set[str] = set(), values: Dict[str, str] = {}
    ) -> int | List[str]:
        if self.completer is None:
            return gdb.COMPLETE_NONE
        elif callable(self.completer):
            return self.completer(word, flags, values)
        else:
            return [name for name in self.completer if name.startswith(word)]

    def get(
        self, word: str, flags: Set[str] = set(), values: Dict[str, str] = {}
    ) -> str:
        if self.getter is None:
            return word
        else:
            return self.getter(word, flags, values)


class ArgInvalidException(Exception):
    pass


# For arguments:
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/CLI-Commands-In-Python.html


class ArgCommand(gdb.Command):
    name: str
    arg_list: List[ArgType]
    arg_mods: List[Tuple[str, str]]

    def __init__(
        self,
        name: str,
        prefix: bool = False,
    ) -> None:
        if prefix:
            super().__init__(name, gdb.COMMAND_USER, gdb.COMPLETE_NONE, True)
        else:
            super().__init__(name, gdb.COMMAND_USER)
        self.name = name
        self.arg_list = []
        self.arg_mods = []

    def add_arg(self, argtype: ArgType) -> None:
        self.arg_list.append(argtype)

    def add_mod(self, letter: str, name: str) -> None:
        self.arg_mods.append((letter, name))

    def _preprocess_argv(self, text: str) -> Tuple[Set[str], List[str]]:
        argv = gdb.string_to_argv(text)

        if len(argv) > 0 and argv[0].startswith("/"):
            # First arg is modifiers
            mods = argv[0][1:]
            argv = argv[1:]
        else:
            mods = ""

        if len(argv) > len(self.arg_list):
            raise ArgInvalidException()

        flags: Set[str] = set()

        for m_letter, m_name in self.arg_mods:
            if mods.count(m_letter) > 0:
                flags.add(m_name)

        return flags, argv

    def complete(self, text: str, word: str) -> int | List[str]:
        try:
            flags, argv = self._preprocess_argv(text)

            # If ends with space, then it's the next argument that should start
            if len(text) == 0 or text[-1] == " ":
                argv.append("")

            if len(argv) > len(self.arg_list):
                return gdb.COMPLETE_NONE

            args: Dict[str, str] = {}
            for cur_arg, cur_argtype in zip(argv[:-1], self.arg_list):
                args[cur_argtype.name] = cur_argtype.get(cur_arg, flags, args)

            return self.arg_list[len(argv) - 1].complete(argv[-1], flags, args)
        except ArgInvalidException:
            return gdb.COMPLETE_NONE

    def process_args(self, text: str) -> Tuple[Set[str], Dict[str, str]]:
        flags, argv = self._preprocess_argv(text)

        for i, argtype in enumerate(self.arg_list):
            if not argtype.optional and len(argv) <= i:
                raise ArgInvalidException()

        args: Dict[str, str] = {}
        for cur_arg, cur_argtype in zip(argv, self.arg_list):
            args[cur_argtype.name] = cur_argtype.get(cur_arg, flags, args)

        return flags, args

    def print_help(self) -> None:
        args = [self.name]
        if len(self.arg_mods) > 0:
            args += ["/" + "".join(letter for letter, name in self.arg_mods)]
        args += [
            ("[<%s>]" if arg.optional else "<%s>") % (arg.name,)
            for arg in self.arg_list
        ]
        print("Usage:", *args)

    def invoke(self, argument: str, from_tty: bool) -> None:
        try:
            flags, values = self.process_args(argument)
            self.call(flags, values)
        except ArgInvalidException:
            self.print_help()
        except Exception as e:
            print(traceback.format_exc())
            raise e

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        raise NotImplementedError("call() needs to be overridden in subclass")
