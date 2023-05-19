from .command import Command
from devices.Sonicator import Sonicator

class SonicatorParentCommand(Command):
    """Parent class for all sonicator commands."""
    receiver_cls = Sonicator

    def __init__(self, receiver : Sonicator, **kwargs):
        super().__init__(receiver, **kwargs)

    class SonicatorConnect(SonicatorParentCommand):
        "Open the serial port for the Sonicator controlled by an arduino device."

        def __init__(self, receiver : Sonicator, **kwargs):
            super().__init__(receiver, **kwargs)

        def execute(self) -> None:
            self._was_successful, self._result_message = self._receiver.start_serial()

    class SonicatorInitialize(SonicatorParentCommand):
        """Initialize the sonicator by checking power connection, status, and stopping sonicator if in motion"""

        def __init__(self, receiver : Sonicator, **kwargs):
            super().__init__(receiver, **kwargs)

        def execute(self) -> None:
            self._was_successful, self._result_message = self._receiver.initialize()

    class SonicatorDeinitialize(SonicatorParentCommand):
        """Deinitialize the sonicator by checking power connection, status, and stopping sonicator if in motion"""

        def __init__(self, receiver : Sonicator, **kwargs):
            super().__init__(receiver, **kwargs)
        def execute(self) -> None:
            self._was_successful, self._result_message = self._receiver.deinitialize()

    class Sonicatorstartsonicating(SonicatorParentCommand):
        def __init__(self, receiver : Sonicator, **kwargs):
            super().__init__(receiver, **kwargs)
        def execute(self) -> None:
            self._was_successful, self._result_message = self._receiver.start_sonicating()

    class Sonicatorstopsonicating(SonicatorParentCommand):
        def __init__(self, receiver : Sonicator, **kwargs):
            super().__init__(receiver, **kwargs)
        def execute(self) -> None:
            self._was_successful, self._result_message = self._receiver.stop_sonicating()