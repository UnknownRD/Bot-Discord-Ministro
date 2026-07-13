# Bot de Discord para mensajes y Sonata

Este proyecto es un bot de Discord hecho en Python con discord.py. El bot tiene dos funciones principales:

- Detecta palabras consideradas ofensivas o inapropiadas en el chat y responde con un mensaje configurable.
- Responde al comando ,sonata con una imagen aleatoria del Hyundai Sonata LF 2017.
- Incluye un comando ,ayuda para ver los comandos disponibles.

## Archivos importantes

- discord_bot.py: lógica principal del bot.
- .env: archivo con el token del bot de Discord.
- local.py: ejemplo simple de Python que se usó al inicio.
- README.md: esta documentación.

## Requisitos

- Python 3.10 o superior.
- Acceso a Internet para que el bot pueda conectarse a Discord.
- Una cuenta de Discord.
- Una aplicación de bot creada en Discord Developer Portal.

## Instalación

1. Abre la terminal en la carpeta del proyecto.
2. Instala las librerías necesarias:

```powershell
pip install discord.py python-dotenv
```

## Configuración del token

1. Crea una aplicación en Discord Developer Portal.
2. Ve a la sección Bot.
3. Crea un bot y copia el token.
4. Crea un archivo .env en la carpeta del proyecto con este contenido:

```env
DISCORD_TOKEN=tu_token_aqui
```

5. Guarda el archivo.

## Activar permisos del bot en Discord

1. En Discord Developer Portal entra a OAuth2 > URL Generator.
2. Marca el scope bot.
3. En permisos del bot marca:
   - Send Messages
   - Read Messages/View Channels
   - Embed Links
4. Usa la URL generada para invitar el bot a tu servidor.

## Ejecutar el bot

En la terminal ejecuta:

```powershell
python discord_bot.py
```

Si todo está bien, verás un mensaje indicando que el bot se conectó.

## Comandos del bot

- ,sonata: muestra una imagen aleatoria del Sonata LF 2017.
- ,ayuda: muestra una lista de comandos disponibles.

## Cómo personalizar el bot

### Cambiar las palabras que detecta

Abre discord_bot.py y busca la lista llamada palabras_malas. Agrega o quita palabras según lo que quieras.

### Cambiar el mensaje de respuesta

En el bloque del evento on_message, cambia los textos que se envían al canal.

### Cambiar las imágenes del comando ,sonata

En el comando sonata_command cambia las URLs de las imágenes que están dentro de la lista sonatas.

### Cambiar el prefijo del bot

En discord_bot.py cambia este valor:

```python
bot = commands.Bot(command_prefix=',', intents=intents)
```

### Cambiar el nombre del bot

En Discord Developer Portal ve a General Information y cambia el nombre de la aplicación.

## Recomendaciones

- Nunca compartas el token del bot.
- Reinicia el bot cada vez que hagas cambios en el código.
- Mantén el bot corriendo en una terminal abierta o en un servicio de hosting si lo quieres activo las 24 horas.

## Subir cambios a GitHub

Si quieres guardar tus cambios en GitHub, usa:

```powershell
git add .
git commit -m "Describe tus cambios"
git push origin main
```

Si Git te pide autenticación, usa un Personal Access Token de GitHub en lugar de la contraseña.
