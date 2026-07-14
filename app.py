from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', 'fallback-secret')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

# ─── ARCHIVOS DE DATOS ────────────────────────────────────────
WORDS_FILE       = 'words.json'
CHISTES_FILE     = 'chistes.json'
BOLA8_FILE       = '8ball.json'
ACTIVITY_FILE    = 'activity_log.json'

COMANDOS = [
    {"categoria": "🛡️ Moderación", "nombre": "kick",      "uso": ",kick @usuario [razón]",          "slash": True,  "descripcion": "Expulsa a un miembro del servidor.", "permisos": "Expulsar miembros"},
    {"categoria": "🛡️ Moderación", "nombre": "ban",       "uso": ",ban @usuario [razón]",           "slash": True,  "descripcion": "Banea permanentemente a un miembro.", "permisos": "Banear miembros"},
    {"categoria": "🛡️ Moderación", "nombre": "unban",     "uso": ",unban Usuario#0000",              "slash": True,  "descripcion": "Desbanea a un usuario por tag o ID.", "permisos": "Banear miembros"},
    {"categoria": "🛡️ Moderación", "nombre": "timeout",   "uso": ",timeout @usuario [min] [razón]", "slash": True,  "descripcion": "Silencia a un miembro por X minutos.", "permisos": "Moderar miembros"},
    {"categoria": "🛡️ Moderación", "nombre": "clear",     "uso": ",clear [cantidad]",               "slash": True,  "descripcion": "Elimina mensajes del canal (máx 100).", "permisos": "Gestionar mensajes"},
    {"categoria": "ℹ️ Información", "nombre": "userinfo",  "uso": ",userinfo [@usuario]",            "slash": True,  "descripcion": "Info completa de un usuario.", "permisos": "—"},
    {"categoria": "ℹ️ Información", "nombre": "serverinfo","uso": ",serverinfo",                     "slash": True,  "descripcion": "Estadísticas del servidor.", "permisos": "—"},
    {"categoria": "ℹ️ Información", "nombre": "avatar",    "uso": ",avatar [@usuario]",              "slash": True,  "descripcion": "Avatar en alta resolución.", "permisos": "—"},
    {"categoria": "ℹ️ Información", "nombre": "ping",      "uso": ",ping",                          "slash": True,  "descripcion": "Latencia del bot en ms.", "permisos": "—"},
    {"categoria": "🔧 Utilidad",    "nombre": "encuesta",  "uso": ",encuesta ¿Pregunta?",            "slash": True,  "descripcion": "Crea una encuesta con ✅ y ❌.", "permisos": "—"},
    {"categoria": "🔧 Utilidad",    "nombre": "decir",     "uso": ",decir mensaje",                  "slash": True,  "descripcion": "El bot repite tu mensaje.", "permisos": "Administrador"},
    {"categoria": "🎮 Diversión",   "nombre": "8ball",     "uso": ",8ball ¿Pregunta?",               "slash": True,  "descripcion": "La bola mágica 🎱 responde tu pregunta.", "permisos": "—"},
    {"categoria": "🎮 Diversión",   "nombre": "dado",      "uso": ",dado [caras]",                   "slash": True,  "descripcion": "Tira un dado de N caras (máx 100).", "permisos": "—"},
    {"categoria": "🎮 Diversión",   "nombre": "moneda",    "uso": ",moneda",                         "slash": True,  "descripcion": "Lanza una moneda: cara o cruz.", "permisos": "—"},
    {"categoria": "🎮 Diversión",   "nombre": "chiste",    "uso": ",chiste",                         "slash": True,  "descripcion": "Chiste dominicano al azar.", "permisos": "—"},
    {"categoria": "🎞️ GIFs",       "nombre": "gif",       "uso": ",gif término",                    "slash": True,  "descripcion": "Busca cualquier GIF en Klipy.", "permisos": "—"},
    {"categoria": "🎞️ GIFs",       "nombre": "pitola",    "uso": ",pitola",                         "slash": True,  "descripcion": "GIF aleatorio de pistola.", "permisos": "—"},
    {"categoria": "🎞️ GIFs",       "nombre": "sonata",    "uso": ",sonata",                         "slash": True,  "descripcion": "GIF aleatorio de Hyundai Sonata.", "permisos": "—"},
    {"categoria": "🎮 Minecraft",   "nombre": "ip",        "uso": ",ip",                             "slash": True,  "descripcion": "IP y tutorial de instalación del servidor DawnCraft.", "permisos": "—"},
    {"categoria": "ℹ️ Información", "nombre": "status",    "uso": ",status",                         "slash": True,  "descripcion": "Estado en vivo del bot: latencia WebSocket, API, uptime y stats.", "permisos": "—"},
]

# ─── HELPERS ──────────────────────────────────────────────────

def leer_json(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default

def escribir_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─── AUTH ─────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password', '') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Contraseña incorrecta', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/health')
def health():
    return 'ok', 200

# ─── DASHBOARD ────────────────────────────────────────────────

@app.route('/')
@login_required
def dashboard():
    palabras = leer_json(WORDS_FILE, {'palabras_malas': []}).get('palabras_malas', [])
    chistes  = leer_json(CHISTES_FILE, {'chistes': []}).get('chistes', [])
    bola8    = leer_json(BOLA8_FILE, {'respuestas': []}).get('respuestas', [])
    logs     = leer_json(ACTIVITY_FILE, {'logs': []}).get('logs', [])
    return render_template('dashboard.html',
        total_palabras=len(palabras),
        total_chistes=len(chistes),
        total_8ball=len(bola8),
        total_logs=len(logs),
        ultimos_logs=logs[:5],
        total_comandos=len(COMANDOS)
    )

# ─── PALABRAS ─────────────────────────────────────────────────

@app.route('/palabras')
@login_required
def palabras():
    data = leer_json(WORDS_FILE, {'palabras_malas': []})
    lista = sorted(data.get('palabras_malas', []))
    return render_template('palabras.html', palabras=lista, total=len(lista))

@app.route('/palabras/agregar', methods=['POST'])
@login_required
def palabras_agregar():
    nueva = request.form.get('palabra', '').strip().lower()
    if nueva:
        data = leer_json(WORDS_FILE, {'palabras_malas': []})
        if nueva not in data['palabras_malas']:
            data['palabras_malas'].append(nueva)
            escribir_json(WORDS_FILE, data)
            flash(f'✅ Palabra "{nueva}" agregada.', 'success')
        else:
            flash(f'⚠️ "{nueva}" ya existe.', 'warning')
    return redirect(url_for('palabras'))

@app.route('/palabras/eliminar', methods=['POST'])
@login_required
def palabras_eliminar():
    palabra = request.form.get('palabra', '').strip()
    if palabra:
        data = leer_json(WORDS_FILE, {'palabras_malas': []})
        if palabra in data['palabras_malas']:
            data['palabras_malas'].remove(palabra)
            escribir_json(WORDS_FILE, data)
            flash(f'🗑️ Palabra "{palabra}" eliminada.', 'success')
    return redirect(url_for('palabras'))

# ─── CHISTES ──────────────────────────────────────────────────

@app.route('/chistes')
@login_required
def chistes():
    data = leer_json(CHISTES_FILE, {'chistes': []})
    return render_template('chistes.html', chistes=data.get('chistes', []))

@app.route('/chistes/agregar', methods=['POST'])
@login_required
def chistes_agregar():
    nuevo = request.form.get('chiste', '').strip()
    if nuevo:
        data = leer_json(CHISTES_FILE, {'chistes': []})
        data['chistes'].append(nuevo)
        escribir_json(CHISTES_FILE, data)
        flash('✅ Chiste agregado.', 'success')
    return redirect(url_for('chistes'))

@app.route('/chistes/eliminar', methods=['POST'])
@login_required
def chistes_eliminar():
    idx = int(request.form.get('idx', -1))
    data = leer_json(CHISTES_FILE, {'chistes': []})
    if 0 <= idx < len(data['chistes']):
        eliminado = data['chistes'].pop(idx)
        escribir_json(CHISTES_FILE, data)
        flash(f'🗑️ Chiste eliminado.', 'success')
    return redirect(url_for('chistes'))

# ─── 8BALL ────────────────────────────────────────────────────

@app.route('/8ball')
@login_required
def bola8():
    data = leer_json(BOLA8_FILE, {'respuestas': []})
    return render_template('bola8.html', respuestas=data.get('respuestas', []))

@app.route('/8ball/agregar', methods=['POST'])
@login_required
def bola8_agregar():
    nueva = request.form.get('respuesta', '').strip()
    if nueva:
        data = leer_json(BOLA8_FILE, {'respuestas': []})
        data['respuestas'].append(nueva)
        escribir_json(BOLA8_FILE, data)
        flash('✅ Respuesta agregada.', 'success')
    return redirect(url_for('bola8'))

@app.route('/8ball/eliminar', methods=['POST'])
@login_required
def bola8_eliminar():
    idx = int(request.form.get('idx', -1))
    data = leer_json(BOLA8_FILE, {'respuestas': []})
    if 0 <= idx < len(data['respuestas']):
        data['respuestas'].pop(idx)
        escribir_json(BOLA8_FILE, data)
        flash('🗑️ Respuesta eliminada.', 'success')
    return redirect(url_for('bola8'))

# ─── COMANDOS ─────────────────────────────────────────────────

@app.route('/comandos')
@login_required
def comandos():
    categorias = {}
    for cmd in COMANDOS:
        cat = cmd['categoria']
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(cmd)
    return render_template('comandos.html', categorias=categorias, total=len(COMANDOS))

# ─── ACTIVIDAD ────────────────────────────────────────────────

@app.route('/actividad')
@login_required
def actividad():
    data = leer_json(ACTIVITY_FILE, {'logs': []})
    return render_template('actividad.html', logs=data.get('logs', []))

@app.route('/actividad/limpiar', methods=['POST'])
@login_required
def actividad_limpiar():
    escribir_json(ACTIVITY_FILE, {'logs': []})
    flash('🗑️ Log de actividad limpiado.', 'success')
    return redirect(url_for('actividad'))

# ─── SYNC API ─────────────────────────────────────────────────

@app.route('/sync', methods=['POST'])
@login_required
def sync():
    try:
        data = leer_json(WORDS_FILE, {'palabras_malas': []})
        return jsonify({'ok': True, 'total': len(data.get('palabras_malas', []))})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
