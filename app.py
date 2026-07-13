from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', 'fallback-secret')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

WORDS_FILE = 'words.json'

def cargar_palabras():
    with open(WORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_palabras(data):
    with open(WORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Contraseña incorrecta', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/health')
def health():
    return 'ok', 200

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    data = cargar_palabras()
    palabras = sorted(data.get('palabras_malas', []))
    return render_template('index.html', palabras=palabras, total=len(palabras))

@app.route('/agregar', methods=['POST'])
def agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    nueva = request.form.get('palabra', '').strip().lower()
    if nueva:
        data = cargar_palabras()
        if nueva not in data['palabras_malas']:
            data['palabras_malas'].append(nueva)
            guardar_palabras(data)
            flash(f'✅ Palabra "{nueva}" agregada correctamente.', 'success')
        else:
            flash(f'⚠️ La palabra "{nueva}" ya existe en la lista.', 'warning')
    return redirect(url_for('index'))

@app.route('/eliminar', methods=['POST'])
def eliminar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    palabra = request.form.get('palabra', '').strip()
    if palabra:
        data = cargar_palabras()
        if palabra in data['palabras_malas']:
            data['palabras_malas'].remove(palabra)
            guardar_palabras(data)
            flash(f'🗑️ Palabra "{palabra}" eliminada.', 'success')
    return redirect(url_for('index'))
