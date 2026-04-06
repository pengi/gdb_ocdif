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

# Mocked version of gdb interface
#
# This needs to be available in the library to be easily loaded in place of
# gdb, to make testing and debugging work without too much trouble.

from typing import List, Callable
import shlex
import sys

# Re-export Thread, since gdb has its own gdb-safe subclass
from threading import Thread

COMMAND_USER = 0x1234000101
COMPLETE_NONE = 0x1234000201

DEFAULT_INT = 0x123456

commandlist: List["Command"] = []


class Command:
    name: str
    command_class: int
    completer_class: int
    prefix: bool

    def __init__(
        self,
        name: str,
        command_class: int,
        completer_class: int = DEFAULT_INT,
        prefix: bool = False,
    ) -> None:
        commandlist.append(self)
        self.name = name
        self.command_class = command_class
        self.completer_class = completer_class
        self.prefix = prefix

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        extra_args_str = " *" if self.prefix else ""
        return f"<command: {self.name}{extra_args_str}>"

    def dont_repeat(self) -> None:
        pass

    def invoke(self, argument: str, from_tty: bool) -> None:
        pass

    def complete(self, text: str, word: str) -> object:
        pass


def execute(command: str) -> None:
    print(f"GDB-MOCK execute: {command}")


def string_to_argv(text: str) -> List[str]:
    """
    This should split as gdb. But for testing of the functional behaviour of
    commands, keep it simple and split like shell commands instead
    """
    return shlex.split(text)


#####
# For synced write implementation
#####


def write(text: str) -> None:
    sys.stdout.write(text)


def prompt_hook(current_prompt: str) -> str:
    return current_prompt
