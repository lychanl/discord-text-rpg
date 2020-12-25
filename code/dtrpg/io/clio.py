from typing import Any

from dtrpg.io.text_io import TextIO


class CommandLineIO(TextIO):
    PLAYER_ID = 'ConsolePlayer'

    def run(self, *args: Any, **kwargs: Any) -> None:
        while True:
            inp = input('> ')
            out = self.command(self.PLAYER_ID, inp)
            print(out)
