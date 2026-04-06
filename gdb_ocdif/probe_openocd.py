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

from .gdbif import ArgCommand, ArgType
from .model import OCDIFModel, OCDIFProbe, OCDIFProbeSession, OCDIFProbeCommandSession

from typing import Dict, Set, List, Optional


class OCDIFOpenOCD(OCDIFProbe):
    interface: str
    target: str
    serial: Optional[str]
    transport: str
    debug_level: int

    def __init__(
        self,
        interface: str,
        target: str,
        serial: Optional[str],
        transport: str,
        debug_level: int,
    ) -> None:
        super().__init__()
        self.interface = interface
        self.target = target
        self.serial = serial
        self.transport = transport
        self.debug_level = debug_level

    def get_info(self) -> Dict[str, str]:
        return {
            "type": "OpenOCD",
            "interface": self.interface,
            "target": self.target,
            "serial": str(self.serial),
            "transport": self.transport,
        }

    def create_session(self, port: int) -> OCDIFProbeSession:
        script = [
            f"debug_level {self.debug_level}",
            f"source [find interface/{self.interface}.cfg]",
            f"transport select {self.transport}",
            f"source [find target/{self.target}.cfg]",
            f"gdb_port {port}",
            "tcl_port disabled",
            "telnet_port disabled",
            "$_TARGETNAME configure -rtos auto",
            'echo "session started"',
        ]

        if self.serial is not None:
            script += [f"adapter serial {self.serial}"]

        command = ["openocd"]
        for line in script:
            command += ["-c", line]

        return OCDIFProbeCommandSession(
            remote_command="extended-remote",
            reset_halt_command="monitor reset halt",
            command=command,
            started_indicator="session started",
            start_delay=0.5,
        )


class OCDIFOpenOCDCommand(ArgCommand):
    model: OCDIFModel

    INTERFACES: List[str] = ["jlink"]
    TRANSPORTS: List[str] = ["swd", "jtag"]

    def __init__(self, model: OCDIFModel) -> None:
        super().__init__("ocdif openocd")
        self.add_arg(ArgType("name"))
        self.add_arg(ArgType("interface", completer=self.INTERFACES))
        self.add_arg(ArgType("target"))
        self.add_arg(ArgType("serial", optional=True))
        self.add_arg(ArgType("transport", completer=self.TRANSPORTS, optional=True))
        self.add_arg(ArgType("debug_level", optional=True))
        self.model = model

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        probe = OCDIFOpenOCD(
            args.get("interface", ""),
            args.get("target", ""),
            args.get("serial"),
            args.get("transport", "swd"),
            int(args.get("debug_level", "1")),
        )
        self.model.add_probe(args["name"], probe)
