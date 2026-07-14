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

bot = commands.Bot(command_prefix=',', intents=intents, case_insensitive=True, help_command=None)

# ─── CHISTES DOMINICANOS ──────────────────────────────────────
CHISTES = [
    "¿Por qué el libro de matemáticas está triste? Porque tiene demasiados problemas, igualito que yo.",
    "¿Qué le dijo el semáforo al carro? No me mires que me estoy cambiando, diablo.",
    "¿Cómo se llama el campeón de buceo japonés? Tokofondo. El subcampeón: Kasitoko.",
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba! ¡Zum-ba!",
    "¿Por qué el espantapájaros ganó un premio? Porque era sobresaliente en su campo.",
    "¿Qué le dice un techo a otro techo? ¡Teja-vana!",
    "¿Por qué los pájaros vuelan al sur en invierno? Porque caminar sería demasiado lejos, fuiste.",
    "¿Qué le dijo el 0 al 8? ¡Buen cinturón, socio!",
    "¿Por qué el sol no fue a la escuela? Porque ya tenía miles de grados.",
    "¿Cómo se dice condón en chino? Paraná-Paraná-Paranaca.",
    "¿Qué hace un murciélago en una farmacia? Buscar pastillas pa' los virus.",
    "¿Por qué el fantasma fue al bar? Porque necesitaba levantarle el espíritu.",
    "¿Qué le dijo el café al azúcar? Sin ti, mi vida es amarga, mija.",
    "¿Cuál es el colmo de un electricista? Que su mujer lo deje y él no lo vea venir.",
    "¿Por qué el calendario estaba triste? Porque sus días estaban contados.",
]

RESPUESTAS_8BALL = [
    "🟢 Sí, definitivamente.",
    "🟢 Sin duda alguna.",
    "🟢 Puedes contar con ello.",
    "🟢 Las señales apuntan que sí.",
    "🟢 Claro que sí.",
    "🟡 Pregunta de nuevo más tarde.",
    "🟡 No puedo responder ahora mismo.",
    "🟡 Mejor no te lo digo ahora.",
    "🟡 Concéntrate y pregunta de nuevo.",
    "🔴 No creo que sea así.",
    "🔴 Mis fuentes dicen que no.",
    "🔴 Las señales apuntan que no.",
    "🔴 Definitivamente no.",
    "🔴 Ni lo pienses.",
]

# ─── FUNCIONES AUXILIARES ─────────────────────────────────────

def cargar_palabras():
    try:
        with open('words.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('palabras_malas', [])
    except Exception:
        return []

async def klipy_gif(query: str):
    """Busca un GIF en Klipy y devuelve la URL, o None si falla."""
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

def embed_ok(titulo: str, texto: str = None, color=discord.Color.green()):
    e = discord.Embed(title=titulo, color=color)
    if texto:
        e.description = texto
    return e

# ─── EVENTOS ──────────────────────────────────────────────────

@bot.event
async def on_ready():
    await bot.tree.sync()
    activity = discord.Activity(type=discord.ActivityType.watching, name="el servidor 👀")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'Bot {bot.user} conectado a Discord')
    print(f'Slash commands sincronizados ✅')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    mensaje_lower = message.content.lower().strip()

    if 'mamañema' in mensaje_lower or 'mamnema' in mensaje_lower or 'mmñ' in mensaje_lower:
        await message.channel.send("A usted le dijeron mamañema, mamese una ñemota")
        return

    palabras_malas = cargar_palabras()
    for palabra in palabras_malas:
        if palabra in mensaje_lower:
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
        await ctx.send(embed=embed_error(f"Falta un argumento: `{error.param.name}`. Usa `,ayuda` para ver el uso correcto."))
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=embed_error(f"Espera `{error.retry_after:.1f}s` antes de usar este comando de nuevo."))

async def slash_error(interaction: discord.Interaction, error):
    msg = "Ocurrió un error."
    if isinstance(error, app_commands.MissingPermissions):
        msg = "No tienes permisos para usar este comando."
    await interaction.response.send_message(embed=embed_error(msg), ephemeral=True)

# ─── AYUDA ────────────────────────────────────────────────────

@bot.command(name='ayuda')
async def ayuda_prefix(ctx):
    await enviar_ayuda(ctx)

@bot.tree.command(name="ayuda", description="Muestra todos los comandos disponibles del bot")
async def ayuda_slash(interaction: discord.Interaction):
    await enviar_ayuda(interaction)

async def enviar_ayuda(ctx_or_interaction):
    embeds = []

    # ── Página 1: Moderación ──
    e1 = discord.Embed(
        title="🛡️ Moderación",
        description="Comandos para mantener el orden en el servidor.",
        color=discord.Color.red()
    )
    e1.add_field(name="`,kick` / `/kick` @usuario [razón]", value="Expulsa a un miembro del servidor.", inline=False)
    e1.add_field(name="`,ban` / `/ban` @usuario [razón]", value="Banea permanentemente a un miembro.", inline=False)
    e1.add_field(name="`,unban` / `/unban` usuario#0000", value="Desbanea a un usuario por su tag.", inline=False)
    e1.add_field(name="`,timeout` / `/timeout` @usuario [minutos] [razón]", value="Silencia a un miembro por X minutos (por defecto 10).", inline=False)
    e1.add_field(name="`,clear` / `/clear` [cantidad]", value="Elimina mensajes del canal (por defecto 10, máx 100).", inline=False)
    e1.set_footer(text="Bot Ministro • 📄 Página 1/3 — usa ,ayuda para ver todo")
    embeds.append(e1)

    # ── Página 2: Información & Utilidad ──
    e2 = discord.Embed(
        title="ℹ️ Información & Utilidad",
        description="Comandos para obtener información y herramientas útiles.",
        color=discord.Color.blue()
    )
    e2.add_field(name="`,userinfo` / `/userinfo` [@usuario]", value="Muestra información completa de un usuario (nombre, roles, fecha de entrada, etc).", inline=False)
    e2.add_field(name="`,serverinfo` / `/serverinfo`", value="Muestra estadísticas del servidor (miembros, canales, roles, etc).", inline=False)
    e2.add_field(name="`,avatar` / `/avatar` [@usuario]", value="Muestra el avatar en alta resolución de un usuario.", inline=False)
    e2.add_field(name="`,ping` / `/ping`", value="Muestra la latencia del bot en milisegundos.", inline=False)
    e2.add_field(name="`,encuesta` / `/encuesta` pregunta", value="Crea una encuesta con reacciones ✅ y ❌.", inline=False)
    e2.add_field(name="`,decir` / `/decir` mensaje", value="El bot repite tu mensaje en el canal (solo admins).", inline=False)
    e2.set_footer(text="Bot Ministro • 📄 Página 2/3")
    embeds.append(e2)

    # ── Página 3: Diversión & GIFs ──
    e3 = discord.Embed(
        title="🎮 Diversión & GIFs",
        description="Comandos para entretenerte en el servidor.",
        color=discord.Color.from_rgb(0, 255, 0)
    )
    e3.add_field(name="`,8ball` / `/8ball` pregunta", value="La bola mágica responde cualquier pregunta con sí, no o tal vez.", inline=False)
    e3.add_field(name="`,dado` / `/dado` [caras]", value="Tira un dado. Por defecto 6 caras, puedes poner hasta 100.", inline=False)
    e3.add_field(name="`,moneda` / `/moneda`", value="Lanza una moneda: cara o cruz.", inline=False)
    e3.add_field(name="`,chiste` / `/chiste`", value="Te cuenta un chiste dominicano al azar.", inline=False)
    e3.add_field(name="`,gif` / `/gif` término", value="Busca y muestra un GIF aleatorio de Klipy con el término que pongas.", inline=False)
    e3.add_field(name="`,pitola` / `/pitola`", value="Muestra un GIF random de una pistola.", inline=False)
    e3.add_field(name="`,sonata` / `/sonata`", value="Muestra un GIF random de un Hyundai Sonata.", inline=False)
    e3.add_field(name="🤖 Detección automática", value="El bot detecta malas palabras dominicanas y responde automáticamente.\nTambién detecta variantes de *mamañema* con respuesta especial.", inline=False)
    e3.set_footer(text="Bot Ministro • 📄 Página 3/3 | Prefijo: , | También disponibles con /")
    embeds.append(e3)

    if isinstance(ctx_or_interaction, discord.Interaction):
        await ctx_or_interaction.response.send_message(embeds=embeds)
    else:
        await ctx_or_interaction.send(embeds=embeds)

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
            e = embed_ok(f"✅ {entry.user} ha sido desbaneado.")
            await ctx.send(embed=e)
            return
    await ctx.send(embed=embed_error(f"No encontré ningún ban para `{usuario}`. Usa el formato `Usuario#0000` o el ID."))

@bot.tree.command(name="unban", description="Desbanea a un usuario del servidor")
@app_commands.describe(usuario="Tag del usuario (Usuario#0000) o su ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban_slash(interaction: discord.Interaction, usuario: str):
    await interaction.response.defer()
    bans = [entry async for entry in interaction.guild.bans()]
    for entry in bans:
        if str(entry.user) == usuario or str(entry.user.id) == usuario:
            await interaction.guild.unban(entry.user)
            await interaction.followup.send(embed=embed_ok(f"✅ {entry.user} ha sido desbaneado."))
            return
    await interaction.followup.send(embed=embed_error(f"No encontré ningún ban para `{usuario}`."))

@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout_prefix(ctx, miembro: discord.Member, minutos: int = 10, *, razon="Sin razón especificada"):
    duracion = datetime.timedelta(minutes=minutos)
    await miembro.timeout(duracion, reason=razon)
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
    duracion = datetime.timedelta(minutes=minutos)
    await miembro.timeout(duracion, reason=razon)
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
    msg = await ctx.send(embed=embed_ok(f"🗑️ {cantidad} mensajes eliminados."))
    await msg.delete(delay=3)

@bot.tree.command(name="clear", description="Elimina mensajes del canal")
@app_commands.describe(cantidad="Cantidad de mensajes a eliminar (máx 100, por defecto 10)")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_slash(interaction: discord.Interaction, cantidad: int = 10):
    cantidad = min(cantidad, 100)
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=cantidad)
    await interaction.followup.send(embed=embed_ok(f"🗑️ {cantidad} mensajes eliminados."), ephemeral=True)

# ─── INFORMACIÓN ──────────────────────────────────────────────

@bot.command(name='userinfo', aliases=['ui', 'usuario'])
async def userinfo_prefix(ctx, miembro: discord.Member = None):
    miembro = miembro or ctx.author
    await enviar_userinfo(ctx, miembro)

@bot.tree.command(name="userinfo", description="Muestra información de un usuario")
@app_commands.describe(miembro="El usuario a consultar (por defecto tú)")
async def userinfo_slash(interaction: discord.Interaction, miembro: discord.Member = None):
    miembro = miembro or interaction.user
    await enviar_userinfo(interaction, miembro)

async def enviar_userinfo(ctx_or_int, miembro: discord.Member):
    roles = [r.mention for r in miembro.roles if r.name != "@everyone"]
    roles_str = ", ".join(roles) if roles else "Sin roles"
    created = discord.utils.format_dt(miembro.created_at, style='D')
    joined = discord.utils.format_dt(miembro.joined_at, style='D') if miembro.joined_at else "Desconocido"
    e = discord.Embed(title=f"👤 {miembro.display_name}", color=miembro.color if miembro.color.value else discord.Color.blurple())
    e.set_thumbnail(url=miembro.display_avatar.url)
    e.add_field(name="Tag completo", value=str(miembro))
    e.add_field(name="ID", value=miembro.id)
    e.add_field(name="Cuenta creada", value=created)
    e.add_field(name="Entró al servidor", value=joined)
    e.add_field(name=f"Roles ({len(roles)})", value=roles_str[:1024], inline=False)
    e.add_field(name="¿Bot?", value="Sí" if miembro.bot else "No")
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.send_message(embed=e)
    else:
        await ctx_or_int.send(embed=e)

@bot.command(name='serverinfo', aliases=['si', 'servidor'])
async def serverinfo_prefix(ctx):
    await enviar_serverinfo(ctx)

@bot.tree.command(name="serverinfo", description="Muestra información del servidor")
async def serverinfo_slash(interaction: discord.Interaction):
    await enviar_serverinfo(interaction)

async def enviar_serverinfo(ctx_or_int):
    g = ctx_or_int.guild if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.guild
    created = discord.utils.format_dt(g.created_at, style='D')
    e = discord.Embed(title=f"🏠 {g.name}", color=discord.Color.blurple())
    if g.icon:
        e.set_thumbnail(url=g.icon.url)
    e.add_field(name="ID", value=g.id)
    e.add_field(name="Dueño", value=g.owner.mention if g.owner else "Desconocido")
    e.add_field(name="Creado", value=created)
    e.add_field(name="👥 Miembros", value=g.member_count)
    e.add_field(name="💬 Canales de texto", value=len(g.text_channels))
    e.add_field(name="🔊 Canales de voz", value=len(g.voice_channels))
    e.add_field(name="📁 Categorías", value=len(g.categories))
    e.add_field(name="🎭 Roles", value=len(g.roles))
    e.add_field(name="😀 Emojis", value=len(g.emojis))
    e.add_field(name="Nivel de verificación", value=str(g.verification_level).title())
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.send_message(embed=e)
    else:
        await ctx_or_int.send(embed=e)

@bot.command(name='avatar', aliases=['av', 'foto'])
async def avatar_prefix(ctx, miembro: discord.Member = None):
    miembro = miembro or ctx.author
    await enviar_avatar(ctx, miembro)

@bot.tree.command(name="avatar", description="Muestra el avatar de un usuario en alta resolución")
@app_commands.describe(miembro="El usuario cuyo avatar quieres ver")
async def avatar_slash(interaction: discord.Interaction, miembro: discord.Member = None):
    miembro = miembro or interaction.user
    await enviar_avatar(interaction, miembro)

async def enviar_avatar(ctx_or_int, miembro: discord.Member):
    e = discord.Embed(title=f"🖼️ Avatar de {miembro.display_name}", color=discord.Color.blurple())
    e.set_image(url=miembro.display_avatar.url)
    e.add_field(name="Enlace directo", value=f"[Click aquí]({miembro.display_avatar.url})")
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.send_message(embed=e)
    else:
        await ctx_or_int.send(embed=e)

@bot.command(name='ping')
async def ping_prefix(ctx):
    latencia = round(bot.latency * 1000)
    color = discord.Color.green() if latencia < 100 else discord.Color.orange() if latencia < 200 else discord.Color.red()
    e = discord.Embed(title="🏓 Pong!", description=f"Latencia: **{latencia}ms**", color=color)
    await ctx.send(embed=e)

@bot.tree.command(name="ping", description="Muestra la latencia actual del bot")
async def ping_slash(interaction: discord.Interaction):
    latencia = round(bot.latency * 1000)
    color = discord.Color.green() if latencia < 100 else discord.Color.orange() if latencia < 200 else discord.Color.red()
    e = discord.Embed(title="🏓 Pong!", description=f"Latencia: **{latencia}ms**", color=color)
    await interaction.response.send_message(embed=e)

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
    e = discord.Embed(
        title="📊 Encuesta",
        description=f"**{pregunta}**",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    e.set_footer(text=f"Encuesta creada por {autor.display_name}", icon_url=autor.display_avatar.url)
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
    await interaction.response.send_message("✅ Mensaje enviado.", ephemeral=True)
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
    respuesta = random.choice(RESPUESTAS_8BALL)
    e = discord.Embed(title="🎱 Bola Mágica", color=discord.Color.purple())
    e.add_field(name="Pregunta", value=pregunta, inline=False)
    e.add_field(name="Respuesta", value=respuesta, inline=False)
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.send_message(embed=e)
    else:
        await ctx_or_int.send(embed=e)

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
    e = discord.Embed(
        title="🎲 Dado tirado",
        description=f"Dado de **{caras}** caras → **{resultado}**",
        color=discord.Color.blurple()
    )
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.send_message(embed=e)
    else:
        await ctx_or_int.send(embed=e)

@bot.command(name='moneda', aliases=['coin', 'flip'])
async def moneda_prefix(ctx):
    await enviar_moneda(ctx)

@bot.tree.command(name="moneda", description="Lanza una moneda: cara o cruz")
async def moneda_slash(interaction: discord.Interaction):
    await enviar_moneda(interaction)

async def enviar_moneda(ctx_or_int):
    resultado = random.choice(["🪙 ¡Cara!", "🪙 ¡Cruz!"])
    e = discord.Embed(title="Lanzando moneda...", description=resultado, color=discord.Color.gold())
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.send_message(embed=e)
    else:
        await ctx_or_int.send(embed=e)

@bot.command(name='chiste')
async def chiste_prefix(ctx):
    await enviar_chiste(ctx)

@bot.tree.command(name="chiste", description="Cuenta un chiste aleatorio")
async def chiste_slash(interaction: discord.Interaction):
    await enviar_chiste(interaction)

async def enviar_chiste(ctx_or_int):
    e = discord.Embed(title="😂 Chiste", description=random.choice(CHISTES), color=discord.Color.yellow())
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.response.send_message(embed=e)
    else:
        await ctx_or_int.send(embed=e)

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
        msg = f"No encontré ningún GIF para `{termino}`."
        if isinstance(ctx_or_int, discord.Interaction):
            await ctx_or_int.followup.send(embed=embed_error(msg))
        else:
            await ctx_or_int.send(embed=embed_error(msg))
        return
    e = discord.Embed(title=f"🎞️ GIF: {termino}", color=discord.Color.blurple())
    e.set_image(url=gif_url)
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.followup.send(embed=e)
    else:
        await ctx_or_int.send(embed=e)

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
        msg = f"No encontré ningún gif para `{query}` en este momento."
        if isinstance(ctx_or_int, discord.Interaction):
            await ctx_or_int.followup.send(embed=embed_error(msg))
        else:
            await ctx_or_int.send(embed=embed_error(msg))
        return
    e = discord.Embed(color=color)
    e.set_image(url=gif_url)
    if isinstance(ctx_or_int, discord.Interaction):
        await ctx_or_int.followup.send(embed=e)
    else:
        await ctx_or_int.send(embed=e)

# ─── ARRANQUE ─────────────────────────────────────────────────

def run_bot():
    bot.run(TOKEN)
