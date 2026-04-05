import random

import subprocess
from .serverprocess import OCDIFProcess

from .gdbif import ArgType, gdb_call

from typing import Dict, Optional, List, Set


class OCDIFProbeSession:
    remote_command: str

    def __init__(self, remote_command: str) -> None:
        self.remote_command = remote_command

    def disconnect(self) -> None:
        raise NotImplementedError("disconnect() is not implemented")

    def connect(self) -> None:
        raise NotImplementedError("connect() is not implemented")


class OCDIFProbeCommandSession(OCDIFProbeSession):
    command: List[str]
    process: Optional[OCDIFProcess]

    def __init__(self, remote_command: str, command: List[str]) -> None:
        super().__init__(remote_command)
        self.command = command
        self.process = None

    def disconnect(self) -> None:
        if self.process is not None:
            self.process.stop()
            self.process = None

    def connect(self) -> None:
        assert self.process is None
        self.process = OCDIFProcess(self.command)


class OCDIFProbe:
    def __init__(self) -> None:
        pass

    def get_info(self) -> Dict[str, str]:
        return {"type": "unknown"}

    def create_session(self, port: int) -> OCDIFProbeSession:
        raise NotImplementedError("create_session() is not implemented")


class OCDIFModel:
    probes: Dict[str, OCDIFProbe]
    cur_session: Optional[OCDIFProbeSession]
    name_type: ArgType

    def __init__(self) -> None:
        self.probes = {}
        self.cur_session = None
        self.name_type = ArgType("name", completer=self._name_completer)

    def _name_completer(
        self, word: str, flags: Set[str] = set(), values: Dict[str, str] = {}
    ) -> List[str]:
        return [name for name in self.probes.keys()]

    def add_probe(self, name: str, probe: OCDIFProbe) -> None:
        self.probes[name] = probe

    def disconnect(self) -> None:
        try:
            gdb_call("detach")
        except:
            pass

        if self.cur_session is not None:
            self.cur_session.disconnect()
            self.cur_session = None

    def connect(self, name: str) -> None:
        self.disconnect()
        if name not in self.probes:
            raise Exception(f"Probe {name} not defined")

        port = random.randint(10000, 20000)
        self.cur_session = self.probes[name].create_session(port)

        self.cur_session.connect()

        gdb_call(f"target {self.cur_session.remote_command} localhost:{port}")
