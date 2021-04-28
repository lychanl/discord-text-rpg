from dtrpg.io.text_io import TextIO

from asyncio import Lock
from discord import Client, Message
from traceback import print_exception
from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from dtrpg.core import Game


class DiscordBotIO(Client, TextIO):
    LIMIT = 2000

    def __init__(self, game: 'Game', token: str, channel: str = None, prefix: str = ''):
        self._token = token
        self._action_lock = Lock()
        self._game_channel = channel
        self._prefix = prefix

        TextIO.__init__(self, game)
        Client.__init__(self)

    def run(self) -> None:
        Client.run(self, self._token)

    def split_messages(self, messages: Sequence[str]) -> Sequence[str]:
        if not messages:
            return None
        out = [messages[0]]
        for msg in messages[1:]:
            if len(msg) + len(out[-1]) + 1 < self.LIMIT:
                out[-1] = out[-1] + '\n' + msg
            else:
                out[-1] = [msg]

        return out

    async def on_message(self, message: Message) -> None:
        if message.author == self.user:
            return

        if not self._game_channel or str(message.channel) != self._game_channel:
            return

        if not message.content.startswith(self._prefix):
            return

        content = message.content[len(self._prefix):]

        try:
            async with self._action_lock:
                out = self.command(message.author.id, content)

            if out:
                for msg in self.split_messages(out):
                    await message.channel.send(msg)

        except Exception as e:
            print("An exception has occured!")
            print_exception(type(e), e, e.__traceback__)
            print("Message:")
            print(message.content)
            print("Sender:")
            print(message.author)

            await message.channel.send(self._game.config['UNHANDLED_EXCEPTION'])
