import tixte
import aiohttp
from typing import Union

import discord
from discord.ext import commands


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.all(),
        )

        self.session = aiohttp.ClientSession()
        self.tixte = tixte.Client(
            'your-master-token',
        )

    async def upload_file(self, file: Union[tixte.File, discord.File]) -> tixte.FileResponse:
        return await self.tixte.upload_file(file=file)

    async def delete_file(self, upload_id: Union[str, tixte.FileResponse]) -> None:
        if isinstance(upload_id, tixte.FileResponse):
            upload_id = upload_id.id
        return await self.tixte.delete_file(upload_id=upload_id)


bot = DiscordBot()
bot.run('token', reconnect=True)
