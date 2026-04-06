import queue
from .gdbif import gdbif_raw_write, gdbif_register_event


class OCDIFScrollback:
    _queue: queue.Queue[str]

    def __init__(self) -> None:
        self._queue = queue.Queue()
        gdbif_register_event(lambda events: events.before_prompt, self._output)

    def write_text(self, prefix: str, text: str) -> None:
        for line in text.splitlines():
            self._queue.put(prefix + line.rstrip())

    def _output(self) -> None:
        try:
            while True:
                line = self._queue.get(False)
                gdbif_raw_write(line)
        except queue.Empty:
            pass


scrollback_buffer = OCDIFScrollback()


def scrollback_write(prefix: str, text: str) -> None:
    scrollback_buffer.write_text(prefix, text)
