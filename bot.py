import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from dotenv import load_dotenv
import random
import aiohttp
import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# ─── SETUP DEL BOT ────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=',', intents=intents, case_insensitive=True, help_command=None)

# ─── LOADERS JSON ─────────────────────────────────────────────

def cargar_palabras():
    try:
        with open('words.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('palabras_malas', [])
    except Exception:
        return []

def cargar_chistes():
    try:
        with open('chistes.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('chistes', [])
    except Exception:
        return ["No hay chistes disponibles por ahora."]

def cargar_8ball():
    try:
        with open('8ball.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('respuestas', [])
    except Exception:
        return ["🟡 Sin respuesta disponible."]

def log_actividad(tipo: str, usuario: str, servidor: str, canal: str, contenido: str):
    """Escribe un evento al log de actividad (máx 200 entradas)."""
    try:
        with open('activity_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        logs = data.get('logs', [])
        logs.insert(0, {
            "timestamp": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "tipo": tipo,
            "usuario": usuario,
            "servidor": servidor,
            "canal": canal,
            "contenido": contenido[:200]
        })
        logs = logs[:200]
        with open('activity_log.json', 'w', encoding='utf-8') as f:
            json.dump({"logs": logs}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Log] Error al escribir actividad: {e}")

# ─── HELPERS ──────────────────────────────────────────────────

async def klipy_gif(query: str):
    klipy_key = os.getenv('KLIPY_API_KEY')
    url = f"https://api.klipy.com/api/v1/{klipy_key}/gifs/search"
    params = {'q': query, 'per_page': 20}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json(content_type=None)
        items = data.get('data', {}).get('data', [])
        if not items:
            return None
        gif = random.choice(items)
        return gif.get('file', {}).get('hd', {}).get('gif', {}).get('url')
    except Exception as e:
        print(f"[Klipy] Error con query '{query}': {e}")
        return None

def embed_error(texto: str):
    return discord.Embed(description=f"❌ {texto}", color=discord.Color.red())

async def send(ctx_or_int, **kwargs):
    if isinstance(ctx_or_int, discord.Interaction):
        if ctx_or_int.response.is_done():
            await ctx_or_int.followup.send(**kwargs)
        else:
            await ctx_or_int.response.send_message(**kwargs)
    else:
        await ctx_or_int.send(**kwargs)

# ─── EVENTOS ──────────────────────────────────────────────────

@bot.event
async def on_ready():
    await bot.tree.sync()
    activity = discord.Activity(type=discord.ActivityType.watching, name="el servidor 👀")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'Bot {bot.user} conectado a Discord')
    print(f'Slash commands sincronizados globalmente ✅')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    mensaje_lower = message.content.lower().strip()

    if 'mamañema' in mensaje_lower or 'mamnema' in mensaje_lower or 'mmñ' in mensaje_lower:
        log_actividad("mamañema", str(message.author), str(message.guild), str(message.channel), message.content)
        await message.channel.send("A usted le dijeron mamañema, mamese una ñemota")
        return

    palabras_malas = cargar_palabras()
    for palabra in palabras_malas:
        if palabra in mensaje_lower:
            log_actividad("mala_palabra", str(message.author), str(message.guild), str(message.channel), message.content)
            await message.channel.send("Oh, el diablo y te va a quedar así?")
            return

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=embed_error("No tienes permisos para usar este comando."))
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(embed=embed_error("No encontré ese usuario en el servidor."))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=embed_error(f"Falta: `{error.param.name}`. Usa `,ayuda` para ver el uso correcto."))
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=embed_error(f"Espera `{error.retry_after:.1f}s` antes de usar este comando de nuevo."))
    elif isinstance(error, commands.CommandNotFound):
        pass

# ─── SYNC (fix slash commands al instante) ────────────────────

@bot.command(name='sync')
@commands.is_owner()
async def sync_cmd(ctx):
    """Sincroniza slash commands al servidor actual de forma inmediata."""
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(embed=discord.Embed(
        description=f"✅ {len(synced)} slash commands sincronizados en **{ctx.guild.name}**.",
        color=discord.Color.green()
    ))

# ─── AYUDA ────────────────────────────────────────────────────

@bot.command(name='ayuda')
async def ayuda_prefix(ctx):
    await enviar_ayuda(ctx)

@bot.tree.command(name="ayuda", description="Muestra todos los comandos disponibles del bot")
async def ayuda_slash(interaction: discord.Interaction):
    await enviar_ayuda(interaction)

async def enviar_ayuda(ctx_or_int):
    e1 = discord.Embed(title="🛡️ Moderación", description="Requieren permisos del servidor.", color=discord.Color.red())
    e1.add_field(name="`,kick` / `/kick` @usuario [razón]", value="Expulsa a un miembro.", inline=False)
    e1.add_field(name="`,ban` / `/ban` @usuario [razón]", value="Banea permanentemente a un miembro.", inline=False)
    e1.add_field(name="`,unban` / `/unban` usuario#0000", value="Desbanea a un usuario.", inline=False)
    e1.add_field(name="`,timeout` / `/timeout` @usuario [minutos] [razón]", value="Silencia a un miembro por X minutos (por defecto 10).", inline=False)
    e1.add_field(name="`,clear` / `/clear` [cantidad]", value="Elimina mensajes del canal (por defecto 10, máx 100).", inline=False)
    e1.set_footer(text="Bot Ministro • Página 1/3")

    e2 = discord.Embed(title="ℹ️ Información & Utilidad", color=discord.Color.blue())
    e2.add_field(name="`,userinfo` / `/userinfo` [@usuario]", value="Info completa de un usuario: roles, fechas, etc.", inline=False)
    e2.add_field(name="`,serverinfo` / `/serverinfo`", value="Estadísticas del servidor.", inline=False)
    e2.add_field(name="`,avatar` / `/avatar` [@usuario]", value="Avatar en alta resolución.", inline=False)
    e2.add_field(name="`,ping` / `/ping`", value="Latencia del bot en milisegundos.", inline=False)
    e2.add_field(name="`,encuesta` / `/encuesta` pregunta", value="Crea una encuesta con reacciones ✅ y ❌.", inline=False)
    e2.add_field(name="`,decir` / `/decir` mensaje", value="El bot repite tu mensaje (solo admins).", inline=False)
    e2.set_footer(text="Bot Ministro • Página 2/3")

    e3 = discord.Embed(title="🎮 Diversión & GIFs", color=discord.Color.from_rgb(0, 255, 0))
    e3.add_field(name="`,8ball` / `/8ball` pregunta", value="La bola mágica 🎱 responde tu pregunta.", inline=False)
    e3.add_field(name="`,dado` / `/dado` [caras]", value="Tira un dado (por defecto 6, máx 100).", inline=False)
    e3.add_field(name="`,moneda` / `/moneda`", value="Cara o cruz 🪙.", inline=False)
    e3.add_field(name="`,chiste` / `/chiste`", value="Chiste dominicano al azar 😂.", inline=False)
    e3.add_field(name="`,gif` / `/gif` término", value="Busca cualquier GIF en Klipy.", inline=False)
    e3.add_field(name="`,pitola` / `/pitola`", value="GIF random de pistola 🔫.", inline=False)
    e3.add_field(name="`,sonata` / `/sonata`", value="GIF random de Hyundai Sonata 🚗.", inline=False)
    e3.add_field(name="🤖 Automático", value="Detecta malas palabras y variantes de *mamañema* automáticamente.", inline=False)
    e3.set_footer(text="Bot Ministro • Página 3/3 | Prefijo: , | También con /")

    await send(ctx_or_int, embeds=[e1, e2, e3])

# ─── MODERACIÓN ───────────────────────────────────────────────

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_prefix(ctx, miembro: discord.Member, *, razon="Sin razón especificada"):
    await miembro.kick(reason=razon)
    e = discord.Embed(title="👟 Miembro Expulsado", color=discord.Color.orange())
    e.add_field(name="Usuario", value=f"{miembro.mention} (`{miembro}`)")
    e.add_field(name="Razón", value=razon)
    e.add_field(name="Moderador", value=ctx.author.mention)
    e.set_thumbnail(url=miembro.display_avatar.url)
    await ctx.send(embed=e)

@bot.tree.command(name="kick", description="Expulsa a un miembro del servidor")
@app_commands.describe(miembro="El miembro a expulsar", razon="Razón del kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, miembro: discord.Member, razon: str = "Sin razón especificada"):
    await miembro.kick(reason=razon)
    e = discord.Embed(title="👟 Miembro Expulsado", color=discord.Color.orange())
    e.add_field(name="Usuario", value=f"{miembro.mention} (`{miembro}`)")
    e.add_field(name="Razón", value=razon)
    e.add_field(name="Moderador", value=interaction.user.mention)
    e.set_thumbnail(url=miembro.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_prefix(ctx, miembro: discord.Member, *, razon="Sin razón especificada"):
    await miembro.ban(reason=razon)
    e = discord.Embed(title="🔨 Miembro Baneado", color=discord.Color.dark_red())
    e.add_field(name="Usuario", value=f"{miembro.mention} (`{miembro}`)")
    e.add_field(name="Razón", value=razon)
    e.add_field(name="Moderador", value=ctx.author.mention)
    e.set_thumbnail(url=miembro.display_avatar.url)
    await ctx.send(embed=e)

@bot.tree.command(name="ban", description="Banea permanentemente a un miembro del servidor")
@app_commands.describe(miembro="El miembro a banear", razon="Razón del ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_slash(interaction: discord.Interaction, miembro: discord.Member, razon: str = "Sin razón especificada"):
    await miembro.ban(reason=razon)
    e = discord.Embed(title="🔨 Miembro Baneado", color=discord.Color.dark_red())
    e.add_field(name="Usuario", value=f"{miembro.mention} (`{miembro}`)")
    e.add_field(name="Razón", value=razon)
    e.add_field(name="Moderador", value=interaction.user.mention)
    e.set_thumbnail(url=miembro.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_prefix(ctx, *, usuario: str):
    bans = [entry async for entry in ctx.guild.bans()]
    for entry in bans:
        if str(entry.user) == usuario or str(entry.user.id) == usuario:
            await ctx.guild.unban(entry.user)
            await ctx.send(embed=discord.Embed(description=f"✅ {entry.user} desbaneado.", color=discord.Color.green()))
            return
    await ctx.send(embed=embed_error(f"No encontré ban para `{usuario}`. Usa el formato `Usuario#0000` o ID."))

@bot.tree.command(name="unban", description="Desbanea a un usuario del servidor")
@app_commands.describe(usuario="Tag del usuario (Usuario#0000) o su ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban_slash(interaction: discord.Interaction, usuario: str):
    await interaction.response.defer()
    bans = [entry async for entry in interaction.guild.bans()]
    for entry in bans:
        if str(entry.user) == usuario or str(entry.user.id) == usuario:
            await interaction.guild.unban(entry.user)
            await interaction.followup.send(embed=discord.Embed(description=f"✅ {entry.user} desbaneado.", color=discord.Color.green()))
            return
    await interaction.followup.send(embed=embed_error(f"No encontré ban para `{usuario}`."))

@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout_prefix(ctx, miembro: discord.Member, minutos: int = 10, *, razon="Sin razón especificada"):
    await miembro.timeout(datetime.timedelta(minutes=minutos), reason=razon)
    e = discord.Embed(title="🔇 Miembro Silenciado", color=discord.Color.dark_gray())
    e.add_field(name="Usuario", value=f"{miembro.mention} (`{miembro}`)")
    e.add_field(name="Duración", value=f"{minutos} minuto(s)")
    e.add_field(name="Razón", value=razon)
    e.add_field(name="Moderador", value=ctx.author.mention)
    e.set_thumbnail(url=miembro.display_avatar.url)
    await ctx.send(embed=e)

@bot.tree.command(name="timeout", description="Silencia a un miembro temporalmente")
@app_commands.describe(miembro="El miembro a silenciar", minutos="Duración en minutos (por defecto 10)", razon="Razón")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout_slash(interaction: discord.Interaction, miembro: discord.Member, minutos: int = 10, razon: str = "Sin razón especificada"):
    await miembro.timeout(datetime.timedelta(minutes=minutos), reason=razon)
    e = discord.Embed(title="🔇 Miembro Silenciado", color=discord.Color.dark_gray())
    e.add_field(name="Usuario", value=f"{miembro.mention} (`{miembro}`)")
    e.add_field(name="Duración", value=f"{minutos} minuto(s)")
    e.add_field(name="Razón", value=razon)
    e.add_field(name="Moderador", value=interaction.user.mention)
    e.set_thumbnail(url=miembro.display_avatar.url)
    await interaction.response.send_message(embed=e)

@bot.command(name='clear', aliases=['purge', 'limpiar'])
@commands.has_permissions(manage_messages=True)
async def clear_prefix(ctx, cantidad: int = 10):
    cantidad = min(cantidad, 100)
    await ctx.channel.purge(limit=cantidad + 1)
    msg = await ctx.send(embed=discord.Embed(description=f"🗑️ {cantidad} mensajes eliminados.", color=discord.Color.green()))
    await msg.delete(delay=3)

@bot.tree.command(name="clear", description="Elimina mensajes del canal")
@app_commands.describe(cantidad="Cantidad de mensajes a eliminar (máx 100, por defecto 10)")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_slash(interaction: discord.Interaction, cantidad: int = 10):
    cantidad = min(cantidad, 100)
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=cantidad)
    await interaction.followup.send(embed=discord.Embed(description=f"🗑️ {cantidad} mensajes eliminados.", color=discord.Color.green()), ephemeral=True)

# ─── INFORMACIÓN ──────────────────────────────────────────────

@bot.command(name='userinfo', aliases=['ui', 'usuario'])
async def userinfo_prefix(ctx, miembro: discord.Member = None):
    await enviar_userinfo(ctx, miembro or ctx.author)

@bot.tree.command(name="userinfo", description="Muestra información de un usuario")
@app_commands.describe(miembro="El usuario a consultar (por defecto tú)")
async def userinfo_slash(interaction: discord.Interaction, miembro: discord.Member = None):
    await enviar_userinfo(interaction, miembro or interaction.user)

async def enviar_userinfo(ctx_or_int, miembro: discord.Member):
    roles = [r.mention for r in miembro.roles if r.name != "@everyone"]
    e = discord.Embed(title=f"👤 {miembro.display_name}", color=miembro.color if miembro.color.value else discord.Color.blurple())
    e.set_thumbnail(url=miembro.display_avatar.url)
    e.add_field(name="Tag", value=str(miembro))
    e.add_field(name="ID", value=miembro.id)
    e.add_field(name="Cuenta creada", value=discord.utils.format_dt(miembro.created_at, 'D'))
    e.add_field(name="Entró al servidor", value=discord.utils.format_dt(miembro.joined_at, 'D') if miembro.joined_at else "N/A")
    e.add_field(name=f"Roles ({len(roles)})", value=", ".join(roles)[:1024] if roles else "Sin roles", inline=False)
    e.add_field(name="¿Bot?", value="Sí" if miembro.bot else "No")
    await send(ctx_or_int, embed=e)

@bot.command(name='serverinfo', aliases=['si', 'servidor'])
async def serverinfo_prefix(ctx):
    await enviar_serverinfo(ctx)

@bot.tree.command(name="serverinfo", description="Muestra información del servidor")
async def serverinfo_slash(interaction: discord.Interaction):
    await enviar_serverinfo(interaction)

async def enviar_serverinfo(ctx_or_int):
    g = ctx_or_int.guild if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.guild
    e = discord.Embed(title=f"🏠 {g.name}", color=discord.Color.blurple())
    if g.icon:
        e.set_thumbnail(url=g.icon.url)
    e.add_field(name="ID", value=g.id)
    e.add_field(name="Dueño", value=g.owner.mention if g.owner else "N/A")
    e.add_field(name="Creado", value=discord.utils.format_dt(g.created_at, 'D'))
    e.add_field(name="👥 Miembros", value=g.member_count)
    e.add_field(name="💬 Texto", value=len(g.text_channels))
    e.add_field(name="🔊 Voz", value=len(g.voice_channels))
    e.add_field(name="📁 Categorías", value=len(g.categories))
    e.add_field(name="🎭 Roles", value=len(g.roles))
    e.add_field(name="😀 Emojis", value=len(g.emojis))
    e.add_field(name="Verificación", value=str(g.verification_level).title())
    await send(ctx_or_int, embed=e)

@bot.command(name='avatar', aliases=['av', 'foto'])
async def avatar_prefix(ctx, miembro: discord.Member = None):
    await enviar_avatar(ctx, miembro or ctx.author)

@bot.tree.command(name="avatar", description="Muestra el avatar de un usuario en alta resolución")
@app_commands.describe(miembro="El usuario cuyo avatar quieres ver")
async def avatar_slash(interaction: discord.Interaction, miembro: discord.Member = None):
    await enviar_avatar(interaction, miembro or interaction.user)

async def enviar_avatar(ctx_or_int, miembro: discord.Member):
    e = discord.Embed(title=f"🖼️ Avatar de {miembro.display_name}", color=discord.Color.blurple())
    e.set_image(url=miembro.display_avatar.url)
    e.add_field(name="Enlace directo", value=f"[Click aquí]({miembro.display_avatar.url})")
    await send(ctx_or_int, embed=e)

@bot.command(name='ping')
async def ping_prefix(ctx):
    latencia = round(bot.latency * 1000)
    color = discord.Color.green() if latencia < 100 else discord.Color.orange() if latencia < 200 else discord.Color.red()
    await ctx.send(embed=discord.Embed(title="🏓 Pong!", description=f"Latencia: **{latencia}ms**", color=color))

@bot.tree.command(name="ping", description="Muestra la latencia actual del bot")
async def ping_slash(interaction: discord.Interaction):
    latencia = round(bot.latency * 1000)
    color = discord.Color.green() if latencia < 100 else discord.Color.orange() if latencia < 200 else discord.Color.red()
    await interaction.response.send_message(embed=discord.Embed(title="🏓 Pong!", description=f"Latencia: **{latencia}ms**", color=color))

# ─── UTILIDAD ─────────────────────────────────────────────────

@bot.command(name='encuesta', aliases=['poll'])
async def encuesta_prefix(ctx, *, pregunta: str):
    await ctx.message.delete()
    await enviar_encuesta(ctx, pregunta)

@bot.tree.command(name="encuesta", description="Crea una encuesta con ✅ y ❌")
@app_commands.describe(pregunta="La pregunta de tu encuesta")
async def encuesta_slash(interaction: discord.Interaction, pregunta: str):
    await enviar_encuesta(interaction, pregunta)

async def enviar_encuesta(ctx_or_int, pregunta: str):
    autor = ctx_or_int.user if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.author
    e = discord.Embed(title="📊 Encuesta", description=f"**{pregunta}**", color=discord.Color.gold(), timestamp=datetime.datetime.utcnow())
    e.set_footer(text=f"Encuesta de {autor.display_name}", icon_url=autor.display_avatar.url)
    e.add_field(name="✅ Sí", value="\u200b")
    e.add_field(name="❌ No", value="\u200b")
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.send_message(embed=e)
        msg = await ctx_or_int.original_response()
    else:
        msg = await ctx_or_int.send(embed=e)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

@bot.command(name='decir', aliases=['say'])
@commands.has_permissions(administrator=True)
async def decir_prefix(ctx, *, mensaje: str):
    await ctx.message.delete()
    await ctx.send(mensaje)

@bot.tree.command(name="decir", description="El bot repite tu mensaje (solo administradores)")
@app_commands.describe(mensaje="Lo que quieres que el bot diga")
@app_commands.checks.has_permissions(administrator=True)
async def decir_slash(interaction: discord.Interaction, mensaje: str):
    await interaction.response.send_message("✅ Enviado.", ephemeral=True)
    await interaction.channel.send(mensaje)

# ─── DIVERSIÓN ────────────────────────────────────────────────

@bot.command(name='8ball', aliases=['bola', 'pregunta'])
async def bola8_prefix(ctx, *, pregunta: str):
    await enviar_8ball(ctx, pregunta)

@bot.tree.command(name="8ball", description="La bola mágica responde cualquier pregunta")
@app_commands.describe(pregunta="Tu pregunta para la bola mágica")
async def bola8_slash(interaction: discord.Interaction, pregunta: str):
    await enviar_8ball(interaction, pregunta)

async def enviar_8ball(ctx_or_int, pregunta: str):
    respuestas = cargar_8ball()
    e = discord.Embed(title="🎱 Bola Mágica", color=discord.Color.purple())
    e.add_field(name="Pregunta", value=pregunta, inline=False)
    e.add_field(name="Respuesta", value=random.choice(respuestas), inline=False)
    await send(ctx_or_int, embed=e)

@bot.command(name='dado', aliases=['roll', 'dice'])
async def dado_prefix(ctx, caras: int = 6):
    await enviar_dado(ctx, caras)

@bot.tree.command(name="dado", description="Tira un dado de N caras")
@app_commands.describe(caras="Número de caras del dado (por defecto 6, máx 100)")
async def dado_slash(interaction: discord.Interaction, caras: int = 6):
    await enviar_dado(interaction, caras)

async def enviar_dado(ctx_or_int, caras: int):
    caras = max(2, min(caras, 100))
    resultado = random.randint(1, caras)
    e = discord.Embed(title="🎲 Dado tirado", description=f"Dado de **{caras}** caras → **{resultado}**", color=discord.Color.blurple())
    await send(ctx_or_int, embed=e)

@bot.command(name='moneda', aliases=['coin', 'flip'])
async def moneda_prefix(ctx):
    await enviar_moneda(ctx)

@bot.tree.command(name="moneda", description="Lanza una moneda: cara o cruz")
async def moneda_slash(interaction: discord.Interaction):
    await enviar_moneda(interaction)

async def enviar_moneda(ctx_or_int):
    resultado = random.choice(["🪙 ¡Cara!", "🪙 ¡Cruz!"])
    e = discord.Embed(title="Lanzando moneda...", description=resultado, color=discord.Color.gold())
    await send(ctx_or_int, embed=e)

@bot.command(name='chiste')
async def chiste_prefix(ctx):
    await enviar_chiste(ctx)

@bot.tree.command(name="chiste", description="Cuenta un chiste aleatorio")
async def chiste_slash(interaction: discord.Interaction):
    await enviar_chiste(interaction)

async def enviar_chiste(ctx_or_int):
    chistes = cargar_chistes()
    e = discord.Embed(title="😂 Chiste", description=random.choice(chistes), color=discord.Color.yellow())
    await send(ctx_or_int, embed=e)

# ─── GIFs ─────────────────────────────────────────────────────

@bot.command(name='gif')
async def gif_prefix(ctx, *, termino: str):
    await enviar_gif(ctx, termino)

@bot.tree.command(name="gif", description="Busca y muestra un GIF aleatorio de Klipy")
@app_commands.describe(termino="Lo que quieres buscar")
async def gif_slash(interaction: discord.Interaction, termino: str):
    await enviar_gif(interaction, termino)

async def enviar_gif(ctx_or_int, termino: str):
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.defer()
    gif_url = await klipy_gif(termino)
    if not gif_url:
        await send(ctx_or_int, embed=embed_error(f"No encontré GIF para `{termino}`."))
        return
    e = discord.Embed(title=f"🎞️ {termino}", color=discord.Color.blurple())
    e.set_image(url=gif_url)
    await send(ctx_or_int, embed=e)

@bot.command(name='pitola')
async def pitola_prefix(ctx):
    await enviar_klipy_embed(ctx, 'pistol gun', discord.Color.from_rgb(255, 50, 50))

@bot.tree.command(name="pitola", description="Muestra un GIF aleatorio de una pistola")
async def pitola_slash(interaction: discord.Interaction):
    await enviar_klipy_embed(interaction, 'pistol gun', discord.Color.from_rgb(255, 50, 50))

@bot.command(name='sonata')
async def sonata_prefix(ctx):
    await enviar_klipy_embed(ctx, 'Hyundai Sonata', discord.Color.from_rgb(0, 255, 0))

@bot.tree.command(name="sonata", description="Muestra un GIF aleatorio de un Hyundai Sonata")
async def sonata_slash(interaction: discord.Interaction):
    await enviar_klipy_embed(interaction, 'Hyundai Sonata', discord.Color.from_rgb(0, 255, 0))

async def enviar_klipy_embed(ctx_or_int, query: str, color):
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.defer()
    gif_url = await klipy_gif(query)
    if not gif_url:
        await send(ctx_or_int, embed=embed_error(f"No encontré gif para `{query}`."))
        return
    e = discord.Embed(color=color)
    e.set_image(url=gif_url)
    await send(ctx_or_int, embed=e)

# ─── MINECRAFT IP ─────────────────────────────────────────────

@bot.command(name='ip')
async def ip_prefix(ctx):
    await enviar_ip(ctx)

@bot.tree.command(name="ip", description="IP del servidor de Minecraft DawnCraft")
async def ip_slash(interaction: discord.Interaction):
    await enviar_ip(interaction)

async def enviar_ip(ctx_or_int):
    e = discord.Embed(
        title="🌍 Servidor de Minecraft — DawnCraft",
        color=discord.Color.from_rgb(34, 139, 34)
    )
    e.add_field(
        name="📡 IP del Servidor",
        value="`until-reid.gl.joinmc.link`",
        inline=False
    )
    e.add_field(
        name="🚀 Launcher",
        value="SKLauncher **4.0** (versión recomendada)",
        inline=True
    )
    e.add_field(
        name="🗺️ Modpack",
        value="DawnCraft (CurseForge)",
        inline=True
    )
    e.add_field(
        name="📖 ¿Cómo instalarlo? (SKLauncher + CurseForge)",
        value=(
            "**1.** Descarga **SKLauncher 4.0** desde [sklauncher.com](https://skmedix.pl/sklauncher)\n"
            "**2.** Abre SKLauncher → ve a **Installations** → clic en **New Installation**\n"
            "**3.** Selecciona la versión de Minecraft que usa DawnCraft *(Forge requerido)*\n"
            "**4.** Descarga el modpack **DawnCraft** desde [CurseForge](https://www.curseforge.com/minecraft/modpacks/dawn-craft)\n"
            "**5.** Extrae la carpeta de mods y cópiala a `.minecraft/mods` *(o usa la ruta de SKLauncher)*\n"
            "**6.** Inicia el juego con el perfil Forge → entra a **Multijugador** y pega la IP 👆"
        ),
        inline=False
    )
    e.set_footer(text="¡Nos vemos en el servidor! ⚔️")
    await send(ctx_or_int, embed=e)

# ─── ARRANQUE ─────────────────────────────────────────────────

def run_bot():
    bot.run(TOKEN)
