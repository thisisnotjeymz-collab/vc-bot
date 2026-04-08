import os
import asyncio
import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("DISCORD_TOKEN")
VC_CHANNEL_ID = int(os.getenv("VC_CHANNEL_ID", "0"))
GUILD_ID = 1490249414667927592

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    activity=discord.Game("Join Veloriax 〆"),
    status=discord.Status.online
)

async def connect_to_vc():
    if VC_CHANNEL_ID == 0:
        print("VC_CHANNEL_ID is missing.")
        return

    channel = bot.get_channel(VC_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(VC_CHANNEL_ID)
        except Exception as e:
            print(f"Failed to fetch channel: {e}")
            return

    if not isinstance(channel, discord.VoiceChannel):
        print("Selected channel is not a voice channel.")
        return

    voice_client = channel.guild.voice_client

    try:
        if voice_client and voice_client.is_connected():
            if voice_client.channel.id != channel.id:
                await voice_client.move_to(channel)
            return

        await channel.connect()
        print(f"Connected to VC: {channel.name}")

    except Exception as e:
        print(f"Error connecting to VC: {e}")

@bot.tree.command(name="join", description="Make the bot join the VC")
async def join(interaction: discord.Interaction):
    await connect_to_vc()
    await interaction.response.send_message("Joined VC", ephemeral=True)

@bot.tree.command(name="leave", description="Make the bot leave the VC")
async def leave(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Server only command.", ephemeral=True)
        return

    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        await vc.disconnect()
        await interaction.response.send_message("Left VC", ephemeral=True)
    else:
        await interaction.response.send_message("Bot is not in a VC", ephemeral=True)

@bot.tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Bot is alive", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    guild = discord.Object(id=GUILD_ID)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synced {len(synced)} commands")

    await connect_to_vc()

    if not keep_vc_alive.is_running():
        keep_vc_alive.start()

@tasks.loop(seconds=60)
async def keep_vc_alive():
    await connect_to_vc()

@bot.event
async def on_voice_state_update(member, before, after):
    if bot.user and member.id == bot.user.id and after.channel is None:
        await asyncio.sleep(3)
        await connect_to_vc()

bot.run(TOKEN)
