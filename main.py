import threading
import os
from app import app
from bot import run_bot

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Correr Flask en un hilo separado
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"Panel web iniciado en puerto {os.environ.get('PORT', 5000)}")

    # Correr el bot de Discord en el hilo principal
    run_bot()
