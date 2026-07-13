import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Crear el bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=',', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} se ha conectado a Discord')
    print(f'El bot está listo para detectar malas palabras dominicanas')

# Evento para detectar mensajes
@bot.event
async def on_message(message):
    # No responder a sí mismo
    if message.author.bot:
        return
    
    mensaje_lower = message.content.lower().strip()
    
    # Detectar "mamañema" o "mmñ"
    if 'mamañema' in mensaje_lower or 'mamnema' in mensaje_lower or 'mmñ' in mensaje_lower:
        await message.channel.send("A usted le dijeron mamañema, mamese una ñemota")
        return
    
    # Palabras malas dominicanas
    palabras_malas = [
        'coño', 'cono', 'coñazo', 'conazo', 'coñaso', 'conaso', 'recoño', 'recono',
        'diablo', 'diabloo', 'diablazo', 'diablaso',
        'mierda', 'mielda', 'comemierda', 'comemielda', 'hablamierda', 'ablamierda', 'hablamielda', 'ablamielda', 'buenamierda', 'buenamielda',
        'singar', 'singal', 'singa', 'singón', 'singon', 'singaputa',
        'rapar', 'rapal', 'rapa', 'rapón', 'rapon',
        'mamagüevo', 'mamaguevo', 'mamahuevo', 'mamawebo', 'mamawevo', 'mamaguebo', 'mamagwebo',
        'mamaculo',
        'güevo', 'guevo', 'huevo', 'webo', 'wevo', 'guebo', 'gwebo',
        'pinga', 'toto', 'ripio', 'culo', 'culazo', 'culaso', 'fundillo', 'fundiyo',
        'puta', 'putísima', 'putisima', 'hijueputa', 'hijoeputa', 'hiueputa', 'jioeputa', 'joputa', 'yueputa',
        'cabrón', 'cabron', 'cabronazo', 'cabronaso',
        'cuero', 'cuelo', 'cuerazo', 'cueraso',
        'azaroso', 'asaroso', 'azarón', 'azaron', 'asaron',
        'maldito', 'mardito', 'madito', 'malparido', 'marparido',
        'desgraciado', 'degraciao', 'desgraciao', 'degraciado',
        'rastrero', 'ratrero', 'ratrelo',
        'lambón', 'lambon', 'lambiscón', 'lambiscon', 'lambeñema', 'lambenema',
        'palomo', 'parigüayo', 'pariguayo', 'paliguayo', 'paligüayo',
        'baboso', 'asqueroso', 'aqueroso',
        'chopo', 'chopoputa', 'chopazo', 'chopaso',
        'cagón', 'cagon', 'cagaíto', 'cagaito',
        'mojón', 'mojon', 'singaíto', 'singaito',
        'desabrío', 'desabrio', 'desabrido',
        'cuernú', 'cuernu', 'cuernudo',
        'venao', 'venado', 'chivato', 'grajoso',
        'jediondo', 'hediondo', 'gediondo',
        'freco', 'fresco', 'frecomierda', 'frecomielda', 'frescomierda',
        'pendejo', 'pendejazo', 'pendejaso',
        'presentao', 'presentado',
        'safao', 'safado', 'zafao', 'zafado',
        'lambeculo', 'gallaloca', 'gayaloca',
        'puerco', 'puelco',
        'charlatán', 'charlatan',
        'relambío', 'relambio', 'relambido',
        'cuerero', 'rapaso', 'rapazo',
        'totico', 'pingazo', 'pingaso', 'totazo', 'totaso',
        'ñemazo', 'nemazo', 'ñemaso', 'nemaso',
        'guevazo', 'guevaso', 'webaso', 'webazo', 'wevaso', 'wevazo',
        'carajo', 'carajazo', 'carajaso', 'recarajo',
        'careculo', 'careñema', 'carenema',
        'lambetoto', 'malnacido', 'marnacido',
        'singapur', 'singapul',
        'desgrañao', 'desgranao', 'degrañao', 'degranao',
        'deguañangao', 'deguanangao',
        'arrastrao', 'arrastrado', 'rastrao',
        'rabandola', 'sacomierda', 'sacomielda', 'sacoemierda',
        'mamón', 'mamon',
        'buchemierda', 'buchemielda', 'bucheemierda',
        'rompeculo', 'pajuil', 'chapeadora', 'sabandija', 'tollo', 'toyo',
        'mmg', 'perra', 'sucia',
        'hijo de perra', 'hijoeperra', 'hijodeperra'
    ]
    
    for palabra in palabras_malas:
        if palabra in mensaje_lower:
            await message.channel.send("Oh, el diablo y te va a quedar así?")
            return
    
    # Procesar comandos
    await bot.process_commands(message)

# Comando Ayuda
@bot.command(name='ayuda')
async def ayuda_command(ctx):
    """Muestra los comandos disponibles"""
    embed = discord.Embed(
        title="Comandos Disponibles",
        description="Aqui estan todos los comandos del bot",
        color=discord.Color.from_rgb(0, 255, 0)
    )
    
    embed.add_field(
        name=",sonata",
        value="Muestra una imagen aleatoria del Sonata dominicano",
        inline=False
    )
    
    embed.add_field(
        name=",ayuda",
        value="Muestra este menu de ayuda",
        inline=False
    )
    
    embed.add_field(
        name="Funciones Automaticas",
        value="El bot detecta automaticamente malas palabras dominicanas y responde.",
        inline=False
    )
    
    embed.set_footer(text="Bot Dominicano v1.0")
    
    await ctx.send(embed=embed)

# Comando Sonata (mantener el original)
@bot.command(name='sonata')
async def sonata_command(ctx):
    """Muestra una imagen aleatoria del Sonata LF 2017"""
    # Datos del Sonata LF 2017 con imágenes
    sonatas = [
        {
            "imagen": "https://drive.google.com/uc?export=view&id=1a_h6XgEKvof0y9Bp2tE70w92Y5OGUU-y"
        },
        {
            "imagen": "https://drive.google.com/uc?export=view&id=1XWNMH8tXHKdXZhEE01bkyqmLgAhEyDGo"
        },
        {
            "imagen": "https://drive.google.com/uc?export=view&id=1utRlmQ4ZKqB-sEPBZ0C0Xys3aZZ1wf2_"
        }
    ]
    
    sonata = random.choice(sonatas)
    embed = discord.Embed()
    embed.set_image(url=sonata["imagen"])
    
    await ctx.send(embed=embed)

# Ejecutar el bot
bot.run(TOKEN)
