import tixte
import discord

client = discord.Client(intents=discord.Intents.all(), command_prefix='!')
client.tixte = tixte.Client('your-master-token')

@client.event
async def on_member_join(member):
    if member.id == 146348630926819328:  # Specific user
        file = discord.File("my_image.png")
        url = await client.tixte.upload_image(file=file)  # Upload image
        return await member.send(str(url))  # Send them the image url.