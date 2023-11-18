import discord
from discord.ext import commands
import asyncio
import pygame
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

SOUND_FILE_PATH = 'timersound.mp3'

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.bans = True
intents.dm_messages = True
intents.dm_reactions = True
intents.dm_typing = True
intents.emojis = True
intents.emojis_and_stickers = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_scheduled_events = True
intents.guild_typing = True
intents.guilds = True
intents.integrations = True
intents.invites = True
intents.messages = True # `message_content` is required to get the content of the messages
intents.reactions = True
intents.typing = True
intents.voice_states = True
intents.webhooks = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')


WORK_TIME = 1 * 60  # 25 minutes
BREAK_TIME = 1 * 60  # 5 minutes

current_timer = None

def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f'{minutes:02}:{seconds:02}'

def play_sound():
    pygame.mixer.init()
    pygame.mixer.music.load(SOUND_FILE_PATH)
    pygame.mixer.music.play()

# Timer task
async def timer_task(ctx, duration, message):
    global current_timer

    await ctx.send(f'Timer: {format_time(duration)}')

    for remaining_time in range(duration, 0, -1):
        await asyncio.sleep(1)
        await message.edit(content=f'Timer: {format_time(remaining_time)}')

    play_sound()
    await ctx.send('Time is up!')

    current_timer = None  # Reset the current timer

# Command to start the Pomodoro timer
@bot.command(name='startpomodoro')
async def start_pomodoro(ctx, work_time=WORK_TIME, break_time=BREAK_TIME):
    global current_timer

    if current_timer is not None:
        await ctx.send('A timer is already running!')
        return

    await ctx.send(f'Starting Pomodoro timer with {format_time(work_time)} work and {format_time(break_time)} break.')

    # Start the work timer
    message = await ctx.send(f'Timer: {format_time(work_time)}')
    current_timer = bot.loop.create_task(timer_task(ctx, work_time, message))

    # Wait for the work timer to finish
    await current_timer

    # Start the break timer
    await asyncio.sleep(1)  # Give a small delay between work and break
    message = await ctx.send(f'Timer: {format_time(break_time)}')
    current_timer = bot.loop.create_task(timer_task(ctx, break_time, message))

@bot.command(name='stop')
async def stop(ctx):
    await ctx.send("Pomodoro timer stopped! ⏹️")
    bot.loop.stop()

bot.run(BOT_TOKEN)