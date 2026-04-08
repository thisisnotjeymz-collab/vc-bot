import os
import asyncio
import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("DISCORD_TOKEN")
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID", "0"))
GUILD_ID = 1490249414667927592  # server id mo

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    activity=discord.Game("Elevated 〆"),
    status=discord.Status.online
)

async def connect_to_vc():
    if VC_CHANNEL_ID == 0:
        return

    channel = bot.get_channel(VC_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(VC_CHANNEL_ID)
        except:
            return

    if not isinstance(channel, discord.VoiceChannel):
        return

    voice_client = channel.guild.voice_client

    try:
        if voice_client and voice_client.is_connected():
            if voice_client.channel.id != channel.id:
                await voice_client.move_to(channel)
            return

        await channel.connect()
    except:
        pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)  # instant commands

    await connect_to_vc()

    if not keep_vc_alive.is_running():
        keep_vc_alive.start()

@tasks.loop(seconds=60)
async def keep_vc_alive():
    await connect_to_vc()

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and after.channel is None:
        await asyncio.sleep(3)
        await connect_to_vc()

# 🔥 COMMANDS

@bot.tree.command(name="join", description="Join VC")
async def join(interaction: discord.Interaction):
    await connect_to_vc()
    await interaction.response.send_message("Joined VC", ephemeral=True)

@bot.tree.command(name="leave", description="Leave VC")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("Left VC", ephemeral=True)
    else:
        await interaction.response.send_message("Not in VC", ephemeral=True)

@bot.tree.command(name="ping", description="Check bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Bot is alive", ephemeral=True)

bot.run(TOKEN)
