from typing import Union

import tixte
import aiohttp

import discord
from discord.ext import commands


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.all(),
        )

        self.session = aiohttp.ClientSession()
        self.tixte = tixte.Client('your-master-token', 'your-domain', session=self.session)

    async def upload_file(self, file: Union[tixte.File, discord.File]) -> tixte.Upload:
        return await self.tixte.upload_file(file)

    async def delete_file(self, id: str) -> None:
        partial = self.tixte.get_partial_upload(id)
        await partial.delete()

bot = DiscordBot()
bot.run('token')
