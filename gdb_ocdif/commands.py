from .gdbif import ArgCommand
from .model import OCDIFModel

from typing import Dict, Set
from .prettyprint import print_table


class OCDIFListCommand(ArgCommand):
    """
    List registered debug probes
    """

    model: OCDIFModel

    def __init__(self, model: OCDIFModel) -> None:
        super().__init__("ocdif list")
        self.model = model

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        info = [
            {"name": name} | probe.get_info()
            for name, probe in self.model.probes.items()
        ]
        print_table(["name", "target", "serial", "type"], info)


class OCDIFConnectCommand(ArgCommand):
    """
    Connect to a registered debug probe

    To see which probes are avajlable, call: ocdif list
    """

    model: OCDIFModel

    def __init__(self, model: OCDIFModel) -> None:
        super().__init__("ocdif connect")
        self.model = model
        self.add_arg(self.model.name_type)

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        self.model.connect(args["name"])


class OCDIFDisonnectCommand(ArgCommand):
    """
    Disconnect from currently connected probe
    """

    model: OCDIFModel

    def __init__(self, model: OCDIFModel) -> None:
        super().__init__("ocdif disconnect")
        self.model = model

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        self.model.disconnect()
