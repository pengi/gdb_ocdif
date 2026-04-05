from typing import List, Optional
import subprocess as sp


class OCDIFProcess:
    process: Optional[sp.Popen]

    def __init__(self, command: List[str]) -> None:
        self.process = sp.Popen(command, stdin=sp.DEVNULL)

    def stop(self) -> None:
        if self.process is not None:
            self.process.terminate()
            self.process.wait(2.0)
            self.process.kill()
            self.process = None
