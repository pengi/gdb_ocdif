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

import random
import atexit
import time
from .serverprocess import OCDIFProcess
from .gdbif import ArgType, gdb_call, set_prompt_hook, gdbif_register_event
from .scrollback import OCDIFScrollback
from typing import Dict, Optional, List, Set


class OCDIFProbeSession:
    remote_command: str
    reset_halt_command: str

    def __init__(self, remote_command: str, reset_halt_command: str) -> None:
        self.remote_command = remote_command
        self.reset_halt_command = reset_halt_command

    def disconnect(self) -> None:
        raise NotImplementedError("disconnect() is not implemented")

    def connect(self) -> None:
        raise NotImplementedError("connect() is not implemented")


class OCDIFProbeCommandSession(OCDIFProbeSession):
    command: List[str]
    process: Optional[OCDIFProcess]
    started_indicator: Optional[str]
    start_delay: Optional[float]

    def __init__(
        self,
        remote_command: str,
        reset_halt_command: str,
        command: List[str],
        started_indicator: Optional[str] = None,
        start_delay: Optional[float] = None,
    ) -> None:
        super().__init__(remote_command, reset_halt_command)
        self.command = command
        self.process = None
        self.started_indicator = started_indicator
        self.start_delay = start_delay

    def disconnect(self) -> None:
        if self.process is not None:
            self.process.stop()
            self.process = None

    def connect(self) -> None:
        assert self.process is None
        self.process = OCDIFProcess(self.command)
        if self.started_indicator is not None:
            self.process.monitor_start(self.started_indicator)
        self.process.start()
        if self.started_indicator is not None:
            self.process.monitor_wait()
        if self.start_delay is not None:
            time.sleep(self.start_delay)


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
    cur_name: Optional[str]
    name_type: ArgType
    scrollback: OCDIFScrollback

    selected_name: Optional[str]

    def __init__(self) -> None:
        self.probes = {}
        self.cur_session = None
        self.cur_name = None
        self.selected_name = None
        self.name_type = ArgType("name", completer=self._name_completer)
        self.scrollback = OCDIFScrollback()
        # set_prompt_hook(self._prompt_hook)

        # Catch inferior exits, so we can gracefully follow up with a closed
        # OCD session
        gdbif_register_event(lambda events: events.exited, self._exit_handler)
        gdbif_register_event(lambda events: events.gdb_exiting, self._exit_handler)

    def _prompt_hook(self, current_prompt: str) -> str:
        if self.cur_name is None:
            return "(gdb) "
        else:
            return f"({self.cur_name} gdb) "

    def _name_completer(
        self, word: str, flags: Set[str] = set(), values: Dict[str, str] = {}
    ) -> List[str]:
        return [name for name in self.probes.keys()]

    def _exit_handler(self) -> None:
        if self.cur_session is not None:
            self.cur_session.disconnect()
            self.cur_session = None
            self.cur_name = None

    def add_probe(self, name: str, probe: OCDIFProbe) -> None:
        self.probes[name] = probe

    def select(self, name: str) -> None:
        assert name in self.probes
        self.selected_name = name

    def disconnect(self) -> None:
        if self.cur_session is not None:
            try:
                gdb_call("detach")
            except:
                pass
        # detach has probably already disconnected, re-check
        if self.cur_session is not None:
            self.cur_session.disconnect()
            self.cur_session = None
            self.cur_name = None

    def connect(self, name: Optional[str] = None) -> None:
        self.disconnect()

        if name is None:
            name = self.selected_name

        if name is None:
            raise Exception(f"No probe selected, need to select or specify")

        if name not in self.probes:
            raise Exception(f"Probe {name} not defined")

        port = random.randint(10000, 20000)
        self.cur_session = self.probes[name].create_session(port)
        self.cur_name = name

        self.cur_session.connect()

        gdb_call(f"target {self.cur_session.remote_command} localhost:{port}")

    def reset_halt(self) -> None:
        assert self.cur_session is not None
        gdb_call(self.cur_session.reset_halt_command)
