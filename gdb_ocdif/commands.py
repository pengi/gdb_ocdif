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


class OCDIFSelectCommand(ArgCommand):
    """
    Select a debug probe as default

    This probe will be used for "ocdif connect" later, if name is omitted

    To see which probes are avajlable, call: ocdif list
    """

    model: OCDIFModel

    def __init__(self, model: OCDIFModel) -> None:
        super().__init__("ocdif select")
        self.model = model
        self.add_arg(self.model.name_type)

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        self.model.select(args["name"])


class OCDIFConnectCommand(ArgCommand):
    """
    Connect to a registered debug probe

    To see which probes are avajlable, call: ocdif list
    """

    model: OCDIFModel

    def __init__(self, model: OCDIFModel) -> None:
        super().__init__("ocdif connect")
        self.model = model
        self.add_arg(self.model.name_type.clone(optional=True))

    def call(self, flags: Set[str], args: Dict[str, str]) -> None:
        # Don't repeat reconnects
        # This is usually just by mistake, and needs to be done explicitly
        self.dont_repeat()
        if "name" in args:
            self.model.connect(args["name"])
        else:
            self.model.connect()


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
