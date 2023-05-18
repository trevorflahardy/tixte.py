from __future__ import annotations
from typing import Optional

import aiohttp
import discord
import asyncio
from discord.ext import commands
from discord import app_commands

import tixte


class DiscordBot(commands.Bot):
    def __init__(self, session: aiohttp.ClientSession) -> None:
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.all(),
        )

        self.session: aiohttp.ClientSession = session
        self.tixte: tixte.Client = tixte.Client('your-master-token', 'your-domain', session=self.session)


@app_commands.command(name='attachment-to-url', description='Upload any attachment to a URL.')
@app_commands.describe(
    attachment='The attachment you want to turn into a URL.',
    tixte_user_id='An optional tixte user ID to make the attachment privately available to.',
)
async def attachment_to_url(
    interaction: discord.Interaction[DiscordBot], attachment: discord.Attachment, tixte_user_id: Optional[str] = None
) -> None:
    await interaction.response.defer(ephemeral=True)

    tixte_user: Optional[tixte.User] = None
    upload_type = tixte.UploadType.public
    if tixte_user_id is not None:
        try:
            tixte_user = await interaction.client.tixte.fetch_user(tixte_user_id)
        except tixte.NotFound:
            return await interaction.followup.send(f'Tixte user with ID {tixte_user_id} does not exist.')
        else:
            upload_type = tixte.UploadType.private

    file = await attachment.to_file(filename=attachment.filename)
    upload = await interaction.client.tixte.upload(file, upload_type=upload_type)  # pyright: ignore[reportGeneralTypeIssues]

    if tixte_user is not None:
        permissions = upload.permissions
        await permissions.add(tixte_user, level=tixte.UploadPermissionLevel.viewer, message="Image requested from Discord.")

    return await interaction.followup.send(f'Your attachment is now available at {upload.url}!')


async def main() -> None:
    discord.utils.setup_logging()

    session = aiohttp.ClientSession()

    async with aiohttp.ClientSession() as session:
        bot = DiscordBot(session=session)
        async with bot:
            await bot.start('token')

    # NOTE: We do not need to "await bot.tixte.cleanup()" becuase the session will close itself


asyncio.run(main())
