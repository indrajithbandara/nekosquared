"""
Holds the bot implementation.
"""
import os
import signal
import traceback

import cached_property
from discord.ext import commands

from nekosquared.traits import core
from nekosquared.traits import loggable


# Sue me.
BotInterrupt = KeyboardInterrupt


class Bot(core.BaseTrait, commands.Bot, loggable.Scribe):
    """
    My implementation of the Discord.py bot.

    This accepts a dict with two sub-dictionaries:

    - ``auth`` - this must contain a ``token`` and a ``client_id`` member.
    """

    def __init__(self, bot_config: dict):
        """
        Initialise the bot using the given configuration.
        """
        super().__init__(**bot_config.pop('bot', {}))

        try:
            auth = bot_config['auth']
            self.__token = auth['token']
            self.client_id = auth['client_id']
        except KeyError:
            raise SyntaxError('Ensure config has `auth\' section containing '
                              'a `token\' and `client_id\' field.')

        # Used to prevent recursively calling logout.
        self._logged_in = False

    @classmethod
    def __init_class__(cls, **_):
        """
        This sets up any signals that we should listen to. This attempts to
        ensure a graceful shutdown rather than the bot just killing itself
        immediately. After all, we might still be performing file IO!
        """
        # This signals to the main thread that a signal has been raised.
        # This is then handled in the `run` method.
        def terminate(signal_no, frame):
            raise BotInterrupt(f'Caught interrupt {signal_no} in frame {frame}')

        windows_signals = {signal.SIGABRT, signal.SIGTERM, signal.SIGSEGV}
        unix_signals = {*windows_signals, signal.SIGQUIT}

        signals = unix_signals if not os.name == 'nt' else windows_signals

        for s in signals:
            # Register listener
            signal.signal(s, terminate)

    @cached_property.cached_property
    def invite(self):
        return (
            'https://discordapp.com/oauth2/authorize?scope=bot&'
            f'client_id={self.client_id}'
        )

    async def start(self):
        """Starts the bot with the pre-loaded token."""
        self.logger.info(f'Invite me to your server at {self.invite}')
        self._logged_in = True
        await super().start(self.__token)

    # noinspection PyBroadException
    async def logout(self):
        """
        Overrides the default behaviour by attempting to unload modules
        safely first.
        """
        if not self._logged_in:
            return

        self.logger.info('Unloading modules, then logging out')

        for extension in self.extensions:
            try:
                self.unload_extension(extension)
            except BaseException:
                traceback.print_exc()

        for cog in self.cogs:
            try:
                self.remove_cog(cog)
            except BaseException:
                traceback.print_exc()

        await super().logout()
        self._logged_in = False

    # noinspection PyBroadException
    def add_cog(self, cog):
        """
        The default implementation does not attempt to tidy up if a cog does
        not load properly. This attempts to fix this.
        """
        try:
            self.logger.info(f'Loading cog {type(cog).__name__!r})')
            super().add_cog(cog)
        except BaseException as ex:
            try:
                self.remove_cog(cog)
            finally:
                raise ImportError(ex)

    def remove_cog(self, name):
        """Logs and removes a cog."""
        self.logger.info(f'Removing cog {name!r}')
        super().remove_cog(name)

    def load_extension(self, name):
        """
        Overrides the default behaviour by logging info about the extension
        that is being loaded. This also returns the extension object we
        have loaded.
        :param name: the extension to load.
        :return: the extension that has been loaded.
        """
        self.logger.info(f'Loading extension {name!r}')
        super().load_extension(name)
        return self.extensions[name]

    def unload_extension(self, name):
        """Logs and unloads the given extension."""
        self.logger.info(f'Unloading extension {name!r}')
        super().unload_extension(name)

    # noinspection PyBroadException
    def run(self):
        """
        Alters the event loop code ever-so-slightly to ensure all modules
        are safely unloaded.
        """
        try:
            self.loop.run_until_complete(self.start())
        except BotInterrupt as ex:
            self.logger.warning(f'Received interrupt {ex}')
        except BaseException:
            traceback.print_exc()
        else:
            self.logger.info('The event loop was shut down gracefully')
        finally:
            try:
                if self._logged_in:
                    self.logger.info(
                        'Now unloading. Send a second signal to terminate now')
                    self.loop.run_until_complete(self.logout())
                else:
                    self.logger.info('Everything was already tidy...')
            except BotInterrupt:
                self.logger.fatal('Giving up all hope of a safe exit')
            except BaseException:
                traceback.print_exc()
                self.logger.fatal('Giving up all hope of a safe exit')
            else:
                self.logger.info('Process is terminating NOW.')
            finally:
                # For some reason, keyboard interrupt still propagates out of
                # this try catch unless I do this.
                return
