# 🤖 Bot Ministro — Bot de Discord Dominicano

Bot de Discord multifunción con prefijo `,` y slash commands `/`. Incluye moderación, información, diversión, GIFs y detección automática de malas palabras dominicanas.

---

## ✨ Funciones automáticas

| Función | Descripción |
|---------|-------------|
| 🤬 Detección de malas palabras | Monitorea todos los mensajes. Si detecta uno de los 214 términos dominicanos del `words.json`, responde automáticamente. |
| 💬 Mamañema especial | Si alguien escribe `mamañema`, `mamnema` o `mmñ`, el bot responde con frase especial. |
| 🔄 Recarga en vivo | La lista de palabras se recarga en tiempo real sin reiniciar el bot. |

---

## 📋 Comandos

> Todos los comandos funcionan con el prefijo `,` y también como slash command `/`.

---

### 🛡️ Moderación
> Requieren permisos del servidor para usarse.

| Comando | Uso | Descripción |
|---------|-----|-------------|
| `kick` | `,kick @usuario [razón]` | Expulsa a un miembro del servidor. Requiere: **Expulsar miembros**. |
| `ban` | `,ban @usuario [razón]` | Banea permanentemente a un miembro. Requiere: **Banear miembros**. |
| `unban` | `,unban Usuario#0000` | Desbanea a un usuario por su tag o ID. Requiere: **Banear miembros**. |
| `timeout` | `,timeout @usuario [minutos] [razón]` | Silencia a un miembro por X minutos (por defecto 10). Requiere: **Moderar miembros**. |
| `clear` | `,clear [cantidad]` | Elimina mensajes del canal (por defecto 10, máx 100). Aliases: `purge`, `limpiar`. Requiere: **Gestionar mensajes**. |

---

### ℹ️ Información

| Comando | Uso | Descripción |
|---------|-----|-------------|
| `userinfo` | `,userinfo [@usuario]` | Muestra info completa de un usuario: roles, fecha de creación, fecha de entrada. Si no mencionas a nadie, te muestra tu propia info. Aliases: `ui`, `usuario`. |
| `serverinfo` | `,serverinfo` | Estadísticas del servidor: miembros, canales de texto, canales de voz, categorías, roles, emojis y nivel de verificación. Aliases: `si`, `servidor`. |
| `avatar` | `,avatar [@usuario]` | Muestra el avatar en alta resolución. Incluye enlace directo. Aliases: `av`, `foto`. |
| `ping` | `,ping` | Muestra la latencia del bot en milisegundos. Verde < 100ms, naranja < 200ms, rojo ≥ 200ms. |

---

### 🔧 Utilidad

| Comando | Uso | Descripción |
|---------|-----|-------------|
| `encuesta` | `,encuesta ¿Pregunta?` | Crea una encuesta con reacciones ✅ y ❌. Alias: `poll`. |
| `decir` | `,decir mensaje` | El bot repite el mensaje en el canal y borra el original. Solo administradores. Alias: `say`. |

---

### 🎮 Diversión

| Comando | Uso | Descripción |
|---------|-----|-------------|
| `8ball` | `,8ball ¿Pregunta?` | La bola mágica 🎱 responde con sí, no o tal vez. Aliases: `bola`, `pregunta`. |
| `dado` | `,dado [caras]` | Tira un dado de N caras (por defecto 6, máx 100). Aliases: `roll`, `dice`. |
| `moneda` | `,moneda` | Lanza una moneda: cara o cruz 🪙. Aliases: `coin`, `flip`. |
| `chiste` | `,chiste` | Cuenta un chiste dominicano al azar 😂. |

---

### 🎞️ GIFs (Klipy)

| Comando | Uso | Descripción |
|---------|-----|-------------|
| `gif` | `,gif término` | Busca y muestra un GIF aleatorio de Klipy con el término que pongas. |
| `pitola` | `,pitola` | GIF aleatorio de una pistola 🔫. |
| `sonata` | `,sonata` | GIF aleatorio de un Hyundai Sonata 🚗. |

---

## 🖥️ Panel de Administración Web

Interfaz web protegida con contraseña para gestionar la lista de malas palabras.

**URL:** Puerto 5000 (o el dominio de Replit)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/login` | GET / POST | Inicio de sesión con contraseña de administrador |
| `/logout` | GET | Cierra la sesión |
| `/` | GET | Dashboard — lista de palabras monitoreadas |
| `/agregar` | POST | Agrega una nueva palabra a la lista |
| `/eliminar` | POST | Elimina una palabra de la lista |
| `/sync` | POST | Devuelve el total de palabras activas (JSON) |
| `/health` | GET | Health check — devuelve `ok` |

---

## ⚙️ Arquitectura

```
main.py          → Punto de entrada: lanza Flask en hilo daemon + bot en hilo principal
bot.py           → Lógica del bot (slash commands + prefix commands)
app.py           → Panel web Flask
words.json       → Lista de 214 malas palabras (compartida entre bot y panel)
templates/
  login.html     → Página de inicio de sesión
  index.html     → Dashboard del panel
```

**Inicio del sistema (`main.py`):**
- `flask_thread` — hilo daemon que sirve el panel en `0.0.0.0:5000`
- `run_bot()` — corre el bot de Discord en el hilo principal con sincronización automática de slash commands

---

## 🔐 Secrets requeridos

Configurados como variables de entorno en Replit:

| Secret | Descripción |
|--------|-------------|
| `DISCORD_TOKEN` | Token del bot de Discord |
| `ADMIN_PASSWORD` | Contraseña para el panel web |
| `KLIPY_API_KEY` | API key de Klipy para búsqueda de GIFs |
| `SESSION_SECRET` | Clave secreta para las sesiones de Flask |

---

## 🚀 Cómo correrlo

El proyecto corre en **Replit** usando el workflow **Discord Bot**:

```bash
python main.py
```

Esto inicia tanto el bot de Discord como el panel web. Los slash commands se sincronizan automáticamente al arrancar.

---

## 🌐 APIs externas

### Klipy
- Endpoint: `https://api.klipy.com/api/v1/{API_KEY}/gifs/search`
- Usada por: `gif`, `pitola`, `sonata`
- Estructura de respuesta: `data.data.data[].file.hd.gif.url`

---

## 📦 Dependencias

```
discord.py
python-dotenv
flask
gunicorn
aiohttp
```

---

## 🔗 Repositorio

[https://github.com/UnknownRD/Bot-Discord-Ministro](https://github.com/UnknownRD/Bot-Discord-Ministro)
