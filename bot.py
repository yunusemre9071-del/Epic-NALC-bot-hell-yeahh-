
import os 
import random
import discord
from discord.ext import tasks, commands
from discord import app_commands

import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

status_message = None
goal_announced = False

IRS_MESSAGES = [
    "The IRS found us.",
    "The IRS is typing...",
    "Good news: I am alive. Bad news: I owe taxes.",
    "The member count keeps increasing. So does my tax liability.",
    "I accidentally claimed the member count as a dependent.",
    "I have legal representation.",
    "The IRS has better legal representation.",
    "Please do not tell the IRS about the member count."
]

# ----------------------------
# READY EVENT
# ----------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    update_goal.start()



# ----------------------------
# /LOG COMMAND
# ----------------------------
@bot.tree.command(name="log", description="Log an ended event")
@app_commands.describe(
    host="Event host",
    attendees="Mention attendees (space separated)",
    picture="Event screenshot"
)
async def log(
    interaction: discord.Interaction,
    host: discord.Member,
    attendees: str,
    picture: discord.Attachment
):
    attendee_list = attendees.split()

    embed = discord.Embed(
        title="Event Log",
        color=0x00FFAA
    )

    embed.description = (
        f"**Host:** {host.mention}\n"
        f"**Attendees:** {' '.join(attendee_list) if attendee_list else 'None'}"
    )

    if picture:
        embed.set_image(url=picture.url)

    await interaction.response.send_message(embed=embed)

# ----------------------------
# /PING COMMAND
# ----------------------------
@bot.tree.command(
    name="ping",
    description="Check bot latency"
)
async def ping(interaction: discord.Interaction):

    latency = round(bot.latency * 1000)

    await interaction.response.send_message(
        f"🏓 Pong!\nLatency: `{latency}ms`"
    )


# ----------------------------
# /IRSLOG COMMAND (JOKE)
# ----------------------------
@bot.tree.command(
    name="logs",
    description="Log"
)
async def irslog(interaction: discord.Interaction):

    file = discord.File(
        "images/log.jpeg",
        filename="log.jpeg"
    )

    await interaction.response.send_message(
        "📋 Official Log report:",
        file=file
    )

# ----------------------------
# MUSIC BOT
# ----------------------------

MUSIC_FOLDER = "music"


def get_songs():
    songs = {}

    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)

    for file in os.listdir(MUSIC_FOLDER):
        if file.lower().endswith(".mp3"):
            name = os.path.splitext(file)[0]
            songs[name] = os.path.join(MUSIC_FOLDER, file)

    return songs


@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message(
            "❌ You need to join a voice channel first.",
            ephemeral=True
        )
        return

    vc = interaction.guild.voice_client

    if vc:
        await vc.move_to(interaction.user.voice.channel)
    else:
        await interaction.user.voice.channel.connect()

    await interaction.response.send_message("✅ Joined your voice channel.")


@app_commands.describe(song="Name of the song (without .mp3)")
@bot.tree.command(name="play", description="Play a song from the music folder")
async def play(interaction: discord.Interaction, song: str):

    songs = get_songs()

    if song not in songs:
        await interaction.response.send_message(
            "❌ Song not found.\nAvailable songs:\n" +
            "\n".join(f"• {s}" for s in songs.keys()),
            ephemeral=True
        )
        return

    vc = interaction.guild.voice_client

    if vc is None:
        if interaction.user.voice is None:
            await interaction.response.send_message(
                "❌ Join a voice channel first.",
                ephemeral=True
            )
            return

        vc = await interaction.user.voice.channel.connect()

    if vc.is_playing():
        vc.stop()

    source = discord.FFmpegPCMAudio(songs[song])
    vc.play(source)

    await interaction.response.send_message(f"▶️ Now playing **{song}**")


@bot.tree.command(name="stop", description="Stop the current song")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏹️ Music stopped.")
    else:
        await interaction.response.send_message(
            "Nothing is playing.",
            ephemeral=True
        )


@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if vc:
        await vc.disconnect()
        await interaction.response.send_message("👋 Left the voice channel.")
    else:
        await interaction.response.send_message(
            "I'm not in a voice channel.",
            ephemeral=True
        )


@bot.tree.command(name="songs", description="List all available songs")
async def songs(interaction: discord.Interaction):

    song_list = sorted(get_songs().keys())

    if not song_list:
        await interaction.response.send_message(
            "No songs found in the `music` folder.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "**Available Songs:**\n" +
        "\n".join(f"🎵 {song}" for song in song_list)
    )

# ----------------------------
# RUN BOT
# ----------------------------
import os

TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)
