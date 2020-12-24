from typing import Any

from dtrpg.io.text_io import TextIO


class CommandLineIO(TextIO):
    PLAYER_ID = 'ConsolePlayer'

    def run(self, *args: Any, **kwargs: Any) -> None:
        while True:
            inp = input('> ')
            command, *args = inp.split()
            out = self.command(self.PLAYER_ID, command, *args)
            print(out)
