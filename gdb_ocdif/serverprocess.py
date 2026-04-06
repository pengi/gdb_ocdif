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

from typing import List, Optional, IO
import subprocess as sp
import selectors as sels
import threading as thr
from .gdbif import Thread
from .scrollback import scrollback_write
import shlex
import os.path


class OCDIFProcess(Thread):
    _prefix: str
    _command: List[str]
    _running: bool

    _monitor_line: Optional[str]
    _monitor_semaphore: thr.Semaphore

    def __init__(self, command: List[str], prefix: Optional[str] = None) -> None:
        super().__init__()
        if prefix is not None:
            self._prefix = prefix
        elif command is not None:
            self._prefix = os.path.basename(command[0])
        else:
            self._prefix = "OCD"
        self._command = command
        self._running = True
        self._alive = False

        self._monitor_line = None
        self._monitor_semaphore = thr.Semaphore(0)

    def stop(self) -> None:
        self._running = False
        self.join()
        self._threaded_print("   ", "closed")

    def monitor_start(self, line: str) -> None:
        assert self._monitor_line is None
        self._monitor_line = line

    def monitor_wait(self, timeout: Optional[float] = None) -> None:
        if not self._monitor_semaphore.acquire(timeout=timeout):
            raise Exception("OCD output monitor fail")  # TODO: Better exception
        assert self._monitor_line is None

    def _print_command(self) -> None:
        same_line: List[str] = []
        for part in self._command:
            if part[0] == "-":
                self._threaded_print("   ", "   " + shlex.join(same_line))
                same_line = []
            same_line.append(part)
        self._threaded_print("   ", "   " + shlex.join(same_line))

    def run(self) -> None:
        self._threaded_print("   ", "Calling:")
        self._print_command()

        process: sp.Popen[str] = sp.Popen(
            self._command,
            stdin=sp.DEVNULL,
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
            bufsize=1,  # Line buffer
            text=True,  # IO[str]
            universal_newlines=True,  # Needed for linebuffer
        )
        self._alive = True

        def process_stdout(stream: IO[str], mask: int) -> None:
            line = stream.readline()

            # If monitored line is receieved, release the monitor semaphore back
            if self._monitor_line is not None and self._monitor_line in line:
                self._monitor_semaphore.release()
                self._monitor_line = None
                self._threaded_print(" # ", line)
            else:
                self._threaded_print(" > ", line)

        assert process.stdout is not None

        selector = sels.DefaultSelector()
        selector.register(process.stdout, sels.EVENT_READ, process_stdout)

        while process.poll() is None and self._running:
            events = selector.select(0.5)
            for key, mask in events:
                key.data(key.fileobj, mask)

        self._alive = False
        if process.returncode is not None:
            self._threaded_print(
                "   ",
                f"Process '{self._command[0]}' exited with code {process.returncode}\n",
            )
        else:
            process.terminate()
            try:
                outs, errs = process.communicate(timeout=2.0)
                self._threaded_print(" > ", outs)
            except sp.TimeoutExpired:
                process.kill()
                outs, errs = process.communicate()
                self._threaded_print(" > ", outs)

        selector.close()

    def _threaded_print(self, prefix: str, text: Optional[str]) -> None:
        if text is None:
            return
        for line in text.splitlines():
            scrollback_write(self._prefix + prefix, text)
