from dtrpg.io.text_io import TextIO
from dtrpg.utils import split_messages

from asyncio import Lock
from discord import Client, Guild, Message
import os
from traceback import print_exception
from typing import TYPE_CHECKING
import yaml

if TYPE_CHECKING:
    from dtrpg.core import Game


class DiscordBotIO(Client, TextIO):
    LIMIT = 2000

    def __init__(
            self, game: 'Game', token: str, channel: str = None, prefix: str = '',
            admin_prefix: str = '', admin_channel: str = None, config_path: str = None):
        self._token = token
        self._action_lock = Lock()
        self._settings_lock = Lock()
        self._config_path = config_path
        self._guild_settings = {}
        self._game_channel = channel
        self._prefix = prefix
        self._admin_prefix = admin_prefix
        self._admin_channel = admin_channel

        self._admin_commands = {
            'help': self.admin_help,
            'show_settings': self.show_settings,
            'set_game_channels': self.set_game_channels,
            'set_game_prefix': self.set_game_prefix,
            'set_admin_channels': self.set_admin_channels,
            'set_admin_prefix': self.set_admin_prefix,
            'set_admin_role': self.set_admin_role,
        }

        if config_path:
            if os.path.isfile(config_path):
                with open(self._config_path, 'r') as config:
                    self._guild_settings = yaml.safe_load(config)

        TextIO.__init__(self, game)
        Client.__init__(self)

    def _run(self) -> None:
        Client.run(self, self._token)

    async def on_message(self, message: Message) -> None:
        if message.author == self.user:
            return

        try:
            admin_message = self.check_admin_message(message)
            if admin_message:
                out = await self.on_admin_message(message, admin_message)

                if out:
                    for msg in split_messages(out):
                        await message.channel.send(msg)
                return
        except Exception as e:
            print('An exception has occured!')
            print_exception(type(e), e, e.__traceback__)
            print('Message:')
            print(message.content)
            print('Sender:')
            print(message.author)

        try:
            game_message = self.check_game_message(message)
            if game_message:
                out = await self.on_game_message(message, game_message)

                if out:
                    for msg in self.split_messages(out):
                        await message.channel.send(msg)

        except Exception as e:
            print('An exception has occured!')
            print_exception(type(e), e, e.__traceback__)
            print('Message:')
            print(message.content)
            print('Sender:')
            print(message.author)

            await message.channel.send(self._game.config['UNHANDLED_EXCEPTION'])

    def check_channel(self, message: Message, setting: str, default: str) -> bool:
        guild_id = message.channel.guild.id

        channels = self._guild_settings.get(guild_id, {})\
            .get(setting, None)
        if channels is not None:
            if channels and message.channel.id not in channels:
                return False
        elif default:
            if str(message.channel) != default:
                return False

        return True

    def check_prefix(self, message: Message, setting: str, default: str) -> str:
        guild_id = message.channel.guild.id

        prefix = self._guild_settings.get(guild_id, {}).get(setting, default)

        if not message.content.startswith(prefix):
            return None

        return message.content[len(prefix):].strip()

    def check_game_message(self, message: Message) -> str:
        if not self.check_channel(message, 'channels', self._game_channel):
            return None
        message.guild
        return self.check_prefix(message, 'prefix', self._prefix)

    def check_admin_message(self, message: Message) -> str:
        guild_id = message.channel.guild.id
        admin_role = self._guild_settings.get(guild_id, {}).get('admin_role', None)
        if not any(role.id == admin_role for role in message.author.roles)\
                and not message.author.guild_permissions.administrator:
            return None

        if not self.check_channel(message, 'admin_channels', self._admin_channel):
            return None

        return self.check_prefix(message, 'admin_prefix', self._admin_prefix)

    async def on_game_message(self, message: Message, content: str) -> list:
        async with self._action_lock:
            return self.command(message.author.id, content)

    async def on_admin_message(self, message: Message, content: str) -> list:
        async with self._settings_lock:
            tokens = content.split()
            if not tokens:
                return None

            if tokens[0] in self._admin_commands:
                out = self._admin_commands[tokens[0]](message.guild, *tokens[1:])

                return [out]

            else:
                return ['Invalid admin command']

    def admin_help(self, *args: list) -> str:
        return 'Commands list:\n' + '\n'.join('`' + str(c) + '`' for c in self._admin_commands)\
             + '\n\nGame commands are prefixed with the *game_prefix* set. '\
             + 'If *channels* are set, only messages on these channels are considered'\
             + '\n\nAdministrative commands are prefixed with the *admin_prefix* '\
             + 'and are be limited to *admin_channels* (if set). '\
             + 'Only administrators or memebers of a specified role may use admin commands'

    def show_settings(self, guild: Guild, *args: list) -> str:
        settings = self._guild_settings.get(guild.id, {})

        prefix = settings.get('prefix', self._prefix)
        channels = settings.get('channels', None)
        if channels:
            channels = ' '.join(
                [' '.join([str(t) for t in guild.text_channels if t.id == c]) for c in channels]
            )
        else:
            channels = self._game_channel or ''
        admin_prefix = settings.get('admin_prefix', self._admin_prefix)
        admin_channels = settings.get('admin_channels', None)
        if admin_channels:
            admin_channels = ' '.join(
                [' '.join([str(t) for t in guild.text_channels if t.id == c]) for c in admin_channels]
            )
        else:
            admin_channels = self._admin_channel or ''
        admin_role = settings.get('admin_role', None)
        if admin_role:
            admin_role = ''.join([r for r in guild.roles if r.id == admin_role])
        else:
            admin_role = '-'
        return f'game_prefix: `{prefix}`\ngame_channels: `{channels}`\n'\
            + f'admin_prefix: `{admin_prefix}`\nadmin_channels: `{admin_channels}`\nadmin_role: `{admin_role}`'

    def possibly_save_config(self) -> None:
        if self._config_path:
            with open(self._config_path, 'w') as config:
                yaml.dump(self._guild_settings, config)

    def prepare_guild_settings(self, guild: Guild) -> dict:
        if guild.id not in self._guild_settings:
            self._guild_settings[guild.id] = {}
        return self._guild_settings[guild.id]

    def get_channel_list(self, guild: Guild, *args: list) -> list:
        channels = []
        for arg in args:
            channel = [c for c in guild.text_channels if c.mention == arg]
            if not channel:
                return f'{arg} is not a valid channel'
            channels.append(channel[0].id)

        return channels

    def set_game_channels(self, guild: Guild, *args: list) -> str:
        settings = self.prepare_guild_settings(guild)

        settings['channels'] = self.get_channel_list(guild, *args)
        self.possibly_save_config()

        return 'Channels set'

    def set_game_prefix(self, guild: Guild, *args: list) -> str:
        settings = self.prepare_guild_settings(guild)
        prefix = args[0] if args else ''
        settings['prefix'] = prefix
        self.possibly_save_config()

        return f'Prefix set to {prefix}' if prefix else 'Prefix cleared'

    def set_admin_prefix(self, guild: Guild, *args: list) -> str:
        settings = self.prepare_guild_settings(guild)
        prefix = args[0] if args else ''
        settings['admin_prefix'] = prefix
        self.possibly_save_config()

        return f'Prefix set to {prefix}' if prefix else 'Prefix cleared'

    def set_admin_channels(self, guild: Guild, *args: list) -> str:
        settings = self.prepare_guild_settings(guild)

        settings['admin_channels'] = self.get_channel_list(guild, *args)
        self.possibly_save_config()

        return 'Channels set'

    def set_admin_role(self, guild: Guild, *args: list) -> str:
        settings = self.prepare_guild_settings(guild)
        if args:
            role = [r for r in guild.roles if r.mention == args[0]]
            if not role:
                return f'{args[0]} is not a valid role'
            role = role[0].id
        else:
            role = None

        settings['admin_role'] = role
        self.possibly_save_config()

        return 'Role set' if role else 'Role cleared'
