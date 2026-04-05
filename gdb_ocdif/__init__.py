from .gdbif import ArgCommand, gdb_call, commandlist
from .model import OCDIFModel
from .probe_openocd import OCDIFOpenOCDCommand
from .commands import OCDIFListCommand, OCDIFConnectCommand, OCDIFDisonnectCommand

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
OCDIFConnectCommand(model)
OCDIFDisonnectCommand(model)
