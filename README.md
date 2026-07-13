# 🤖 Bot Ministro — Bot de Discord Dominicano

Bot de Discord con detección de malas palabras dominicanas y panel web de administración.

---

## ✨ Funciones principales

### 🔍 Detección automática de malas palabras
- Monitorea todos los mensajes del servidor.
- Compara contra una lista de **214 términos** dominicanos cargada desde `words.json`.
- Si detecta una mala palabra, responde: *"Oh, el diablo y te va a quedar así?"*
- Detecta variantes de **"mamañema"** (`mamnema`, `mmñ`) con una respuesta especial.
- La lista se recarga en tiempo real sin reiniciar el bot.

### 📋 Comandos disponibles (prefijo: `,`)

| Comando | Descripción |
|---------|-------------|
| `,ayuda` | Muestra todos los comandos disponibles y funciones del bot |
| `,pitola` | Muestra un GIF aleatorio de pistola usando la API de Klipy |
| `,sonata` | Muestra un GIF aleatorio de Hyundai Sonata usando la API de Klipy |

---

## 🖥️ Panel de Administración Web

Interfaz web protegida con contraseña para gestionar la lista de malas palabras.

**URL:** `http://localhost:5000` (o el dominio de Replit)

### Rutas disponibles

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/login` | GET / POST | Inicio de sesión con contraseña de administrador |
| `/logout` | GET | Cierra la sesión |
| `/` | GET | Dashboard principal — lista de palabras monitoreadas |
| `/agregar` | POST | Agrega una nueva palabra a la lista |
| `/eliminar` | POST | Elimina una palabra de la lista |
| `/sync` | POST | Devuelve el total de palabras activas (JSON) |
| `/health` | GET | Health check — devuelve `ok` |

---

## ⚙️ Arquitectura

```
main.py          → Punto de entrada: lanza Flask en hilo daemon + bot en hilo principal
bot.py           → Lógica del bot de Discord (comandos, detección de palabras)
app.py           → Panel web Flask
words.json       → Lista de malas palabras (fuente compartida entre bot y panel)
templates/
  login.html     → Página de inicio de sesión
  index.html     → Dashboard del panel
```

**Inicio del sistema (`main.py`):**
- `flask_thread` — hilo daemon que sirve el panel en `0.0.0.0:5000`
- `run_bot()` — corre el bot de Discord en el hilo principal

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

```
python main.py
```

Esto inicia tanto el bot de Discord como el panel web simultáneamente.

---

## 🌐 APIs externas

### Klipy
- Endpoint: `https://api.klipy.com/api/v1/{API_KEY}/gifs/search`
- Usada por: `,pitola` y `,sonata`
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
