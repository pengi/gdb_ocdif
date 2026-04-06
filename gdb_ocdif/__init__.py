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

from .gdbif import ArgCommand, gdb_call, commandlist
from .model import OCDIFModel
from .probe_openocd import OCDIFOpenOCDCommand
from .commands import (
    OCDIFListCommand,
    OCDIFSelectCommand,
    OCDIFConnectCommand,
    OCDIFDisonnectCommand,
    OCDIFResetCommand,
    OCDIFReloadCommand,
)

from typing import Set, Dict


class OCDIFTools(ArgCommand):
    """Tools for managing On-Board Debugger server instances"""

    state: OCDIFModel

    def __init__(self, state: OCDIFModel) -> None:
        super().__init__("ocdif", True)
        self.state = state

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        gdb_call("help ocdif")


model = OCDIFModel()

OCDIFTools(model)
OCDIFOpenOCDCommand(model)
OCDIFListCommand(model)
OCDIFSelectCommand(model)
OCDIFConnectCommand(model)
OCDIFDisonnectCommand(model)
OCDIFResetCommand(model)
OCDIFReloadCommand(model)
