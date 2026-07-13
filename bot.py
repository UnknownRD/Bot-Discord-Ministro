import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
import random
import aiohttp

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Crear el bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=',', intents=intents, case_insensitive=True)

def cargar_palabras():
    try:
        with open('words.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('palabras_malas', [])
    except Exception:
        return []

@bot.event
async def on_ready():
    print(f'Bot {bot.user} se ha conectado a Discord')
    print(f'El bot está listo para detectar malas palabras dominicanas')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    mensaje_lower = message.content.lower().strip()

    # Detectar "mamañema" o "mmñ"
    if 'mamañema' in mensaje_lower or 'mamnema' in mensaje_lower or 'mmñ' in mensaje_lower:
        await message.channel.send("A usted le dijeron mamañema, mamese una ñemota")
        return

    # Cargar palabras desde el archivo (se actualiza en tiempo real)
    palabras_malas = cargar_palabras()

    for palabra in palabras_malas:
        if palabra in mensaje_lower:
            await message.channel.send("Oh, el diablo y te va a quedar así?")
            return

    await bot.process_commands(message)

@bot.command(name='ayuda')
async def ayuda_command(ctx):
    embed = discord.Embed(
        title="Comandos Disponibles",
        description="Aqui estan todos los comandos del bot",
        color=discord.Color.from_rgb(0, 255, 0)
    )
    embed.add_field(name=",sonata", value="Muestra un gif del Hyundai Sonata", inline=False)
    embed.add_field(name=",pitola", value="Muestra un gif de una pistola", inline=False)
    embed.add_field(name=",ayuda", value="Muestra este menu de ayuda", inline=False)
    embed.add_field(name="Funciones Automaticas", value="El bot detecta automaticamente malas palabras dominicanas y responde.", inline=False)
    embed.set_footer(text="Bot Ministro v1.0")
    await ctx.send(embed=embed)

@bot.command(name='pitola')
async def pitola_command(ctx):
    """Muestra un gif de una pistola usando la API de Klipy"""
    klipy_key = os.getenv('KLIPY_API_KEY')
    url = f"https://api.klipy.com/api/v1/{klipy_key}/gifs/search"
    params = {'q': 'pistol gun', 'per_page': 20}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json(content_type=None)

        # Estructura de Klipy: data.data.data[].file.hd.gif.url
        items = data.get('data', {}).get('data', [])

        if not items:
            await ctx.send("No encontré ningún gif de pistola en este momento.")
            return

        gif = random.choice(items)
        gif_url = gif.get('file', {}).get('hd', {}).get('gif', {}).get('url')

        if not gif_url:
            await ctx.send("No pude obtener el gif. Intenta de nuevo.")
            return

        embed = discord.Embed(color=discord.Color.from_rgb(255, 50, 50))
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"[Klipy] Error completo: {type(e).__name__}: {e}")
        await ctx.send(f"Error al conectar con Klipy: {type(e).__name__}: {e}")

@bot.command(name='sonata')
async def sonata_command(ctx):
    """Muestra un gif de Hyundai Sonata usando la API de Klipy"""
    klipy_key = os.getenv('KLIPY_API_KEY')
    url = f"https://api.klipy.com/api/v1/{klipy_key}/gifs/search"
    params = {'q': 'Hyundai Sonata', 'per_page': 20}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json(content_type=None)

        items = data.get('data', {}).get('data', [])

        if not items:
            await ctx.send("No encontré ningún gif del Hyundai Sonata en este momento.")
            return

        gif = random.choice(items)
        gif_url = gif.get('file', {}).get('hd', {}).get('gif', {}).get('url')

        if not gif_url:
            await ctx.send("No pude obtener el gif. Intenta de nuevo.")
            return

        embed = discord.Embed(color=discord.Color.from_rgb(0, 255, 0))
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"[Klipy Sonata] Error: {type(e).__name__}: {e}")
        await ctx.send(f"Error al conectar con Klipy: {type(e).__name__}: {e}")

def run_bot():
    bot.run(TOKEN)
