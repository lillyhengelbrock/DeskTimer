import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env
load_dotenv()

# Retrieve the bot token from the environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Set your default work and break times in seconds
WORK_TIME = 25
BREAK_TIME = 5
DEFAULT_ROUNDS = 4 # timer repeats 4 times

# Create a dictionary to store voice channel IDs per server
voice_channel_ids = {}
timer_running = False
# Create intents and enable the necessary ones
intents = discord.Intents.default()
intents.messages = True  # Enable message content intent
intents.message_content = True
intents.guilds = True    # Enable guilds intent
intents.voice_states = True  # Enable voice states intent

# Create a bot instance with a command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f'{minutes:02}:{seconds:02}'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="!timer"))

# Function to play the sound in a voice channel
async def play_sound_vc(channel):
    if channel.guild.voice_client is None:
        vc = await channel.connect()
    else:
        vc = channel.guild.voice_client
    source = discord.FFmpegPCMAudio('timersound.mp3')
    vc.play(source)


# Timer task with dynamic message update
async def timer_work_vc(ctx, duration):
    global timer_running
    global voice_channel_ids
    channel_id = voice_channel_ids.get(ctx.guild.id)
    if not timer_running:
        return
    if channel_id:
        channel = ctx.guild.get_channel(channel_id)
        if channel:
            message = await ctx.send(f'Work: {format_time(duration)}')

            for remaining_time in range(duration, 0, -1):
                if not timer_running:
                    await ctx.send('Timer interrupted.')
                    return
                time.sleep(1)
                await message.edit(content=f'Work: {format_time(remaining_time)}')

            await play_sound_vc(channel)
        else:
            await ctx.send('The voice channel no longer exists.')
    else:
        await ctx.send('The voice channel ID is not set. Use !setvoicechannel command to set it.')

async def timer_break_vc(ctx, duration):
    global timer_running
    global voice_channel_ids
    channel_id = voice_channel_ids.get(ctx.guild.id)
    if not timer_running:
        return
    if channel_id:
        channel = ctx.guild.get_channel(channel_id)
        if channel:
            message = await ctx.send(f'Break: {format_time(duration)}')

            for remaining_time in range(duration, 0, -1):
                if not timer_running:
                    return
                time.sleep(1)
                await message.edit(content=f'Break: {format_time(remaining_time)}')

            await play_sound_vc(channel)
        else:
            await ctx.send('The voice channel no longer exists.')
    else:
        await ctx.send('The voice channel ID is not set. Use !setvoicechannel command to set it.')

# Command to set the voice channel ID for the server
@bot.command(name='setvoicechannel')
async def set_voice_channel(ctx, channel_id: int):
    voice_channel_ids[ctx.guild.id] = channel_id
    await ctx.send(f'Voice channel ID set to {channel_id} for this server.')

# Command to start the Pomodoro timer with sound in the configured voice channel
@bot.command(name='timer')
async def start_pomodoro_vc(ctx, rounds: int =DEFAULT_ROUNDS, work_time_minutes: int =WORK_TIME, break_time_minutes: int =BREAK_TIME):
    global timer_running
    global voice_channel_ids
    work_time = work_time_minutes * 60
    break_time = break_time_minutes * 60
    timer_running = True
    await ctx.send("Timer started - Let's go!")
    for _ in range(rounds):
        await timer_work_vc(ctx, work_time)
        await timer_break_vc(ctx, break_time)
    if timer_running:
        await ctx.send('Good job! You finished your pomodoro session!')
    timer_running = False
    await asyncio.sleep(5)
    if ctx.guild.voice_client is not None:
        await ctx.guild.voice_client.disconnect()

# Command to stop the timer and disconnect from the voice channel
@bot.command(name='stop')
async def stop_timer(ctx):
    global timer_running

    if timer_running:
        timer_running = False
        if ctx.guild.voice_client is not None:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send('No voice channel to disconnect from.')
    else:
        await ctx.send('No timer is currently running.')

# Run the bot with your token
bot.run(BOT_TOKEN)
