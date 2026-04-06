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
