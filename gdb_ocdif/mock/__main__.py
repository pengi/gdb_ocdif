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

# Posix entry point
#
# This is not inteneded to be used by end users, but simplifies debugging

from .gdb import commandlist, Command
from ..gdbif import ArgCommand, ArgType
from pprint import pprint
from typing import Set, Dict

import argparse
import time


class GDBMOCKSleepCommand(ArgCommand):
    """
    Sleep
    """

    def __init__(self) -> None:
        super().__init__("sleep")
        self.add_arg(ArgType("time"))

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        time.sleep(float(args["time"]))


GDBMOCKSleepCommand()


def argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="GDB OCDIF mock entry",
        description="""To debug gdb_ocdif. Not to be used by end user, but to be\
                        able to access pydebug without running from gdb embedded py\
                    thon""",
    )
    parser.add_argument(
        "-c",
        "--command",
        default=[],
        dest="commands",
        action="append",
        help="Command to run. Can be added multiple times",
    )
    return parser


def command_matches(command: Command, cmdstr: str) -> bool:
    if cmdstr == command.name:
        return True
    elif not command.prefix and cmdstr.startswith(command.name + " "):
        return True
    else:
        return False


def run_command(cmdstr: str) -> None:
    for command in commandlist:
        if command_matches(command, cmdstr):
            argument = cmdstr[len(command.name) :].lstrip()
            print(f"GDB-MOCK command: {command.name!r} argument: {argument!r}")
            command.invoke(argument, True)


args = argparser().parse_args()
for cmdstr in args.commands:
    run_command(cmdstr)
