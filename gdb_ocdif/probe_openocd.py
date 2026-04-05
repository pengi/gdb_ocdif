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

        return OCDIFProbeCommandSession("extended-remote", command)


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
