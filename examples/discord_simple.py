from typing import Any, Optional

import discord
from discord import app_commands

import tixte


class MyClient(discord.Client):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.tixte: tixte.Client = tixte.Client('your-master-token', 'your-domain')


client = MyClient(intents=discord.Intents.all())
tree = app_commands.CommandTree(client=client)


@tree.command()
async def avatar(interaction: discord.Interaction, person: Optional[discord.Member] = None) -> None:
    await interaction.response.defer(ephemeral=True)

    target = person or interaction.user

    file = await client.tixte.url_to_file(target.display_avatar.url, filename='avatar.png')
    upload = await client.tixte.upload(file)

    await interaction.followup.send(f'Avatar: {upload}')


client.run('token')
