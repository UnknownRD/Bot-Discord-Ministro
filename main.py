import threading
from app import app
from bot import run_bot

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Correr Flask en un hilo separado
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Panel web iniciado en puerto 5000")

    # Correr el bot de Discord en el hilo principal
    run_bot()
