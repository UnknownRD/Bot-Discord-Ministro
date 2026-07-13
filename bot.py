import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
import random

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Crear el bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=',', intents=intents)

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
    embed.add_field(name=",sonata", value="Muestra una imagen aleatoria del Sonata dominicano", inline=False)
    embed.add_field(name=",pitola", value="Muestra un gif de una pistola", inline=False)
    embed.add_field(name=",ayuda", value="Muestra este menu de ayuda", inline=False)
    embed.add_field(name="Funciones Automaticas", value="El bot detecta automaticamente malas palabras dominicanas y responde.", inline=False)
    embed.set_footer(text="Bot Ministro v1.0")
    await ctx.send(embed=embed)

@bot.command(name='pitola')
async def pitola_command(ctx):
    """Muestra un gif de una pistola"""
    gifs = [
        "https://media.tenor.com/yCxXMIAmyMIAAAAC/gun-pistol.gif",
        "https://media.tenor.com/Yxnt3YZgjPEAAAAC/gun.gif",
        "https://media.tenor.com/9XHx08CfXtcAAAAC/pistol-gun.gif"
    ]
    embed = discord.Embed(color=discord.Color.from_rgb(255, 50, 50))
    embed.set_image(url=random.choice(gifs))
    await ctx.send(embed=embed)

@bot.command(name='sonata')
async def sonata_command(ctx):
    sonatas = [
        {"imagen": "https://drive.google.com/uc?export=view&id=1a_h6XgEKvof0y9Bp2tE70w92Y5OGUU-y"},
        {"imagen": "https://drive.google.com/uc?export=view&id=1XWNMH8tXHKdXZhEE01bkyqmLgAhEyDGo"},
        {"imagen": "https://drive.google.com/uc?export=view&id=1utRlmQ4ZKqB-sEPBZ0C0Xys3aZZ1wf2_"}
    ]
    sonata = random.choice(sonatas)
    embed = discord.Embed()
    embed.set_image(url=sonata["imagen"])
    await ctx.send(embed=embed)

def run_bot():
    bot.run(TOKEN)
