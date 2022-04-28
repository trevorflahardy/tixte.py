from typing import Any

import tixte
import discord


class MyClient(discord.Client):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.tixte: tixte.Client = tixte.Client('your-master-token', 'your-domain')


client = MyClient(intents=discord.Intents.all())


@client.event
async def on_member_join(member: discord.Member) -> None:
    if member.id != 146348630926819328:  # Specific user
        return

    file = discord.File('my_image.png')
    upload = await client.tixte.upload_image(file=file)
    await member.send(upload.url)


client.run('token')
