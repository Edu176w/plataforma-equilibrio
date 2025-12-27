import os
import sys

# Adicionar o diretorio raiz ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f'Servidor iniciando em http://localhost:{port}')
    print(f'Modo debug: {debug}')
    
    app.run(host='0.0.0.0', port=port, debug=debug)
