'''
app/__init__.py
VERSÃO 3.0 - Com autenticação Flask-Login


Inicialização da aplicação Flask
Módulos: ELV, ELL, ESL, Dashboard, Educational, Auth
'''


# ============================================================================
# COMPATIBILIDADE COM NUMPY 2.0+ (DEVE SER A PRIMEIRA COISA)
# ============================================================================


import numpy as np
import sys


print(f"[NumPy Compat] Detectado NumPy {np.__version__}")


# Restaurar aliases removidos no NumPy 2.0
if not hasattr(np, 'float_'):
    np.float_ = np.float64
    print("[NumPy Compat] ✅ np.float_ -> np.float64")


if not hasattr(np, 'int_'):
    np.int_ = np.int64
    print("[NumPy Compat] ✅ np.int_ -> np.int64")


if not hasattr(np, 'complex_'):
    np.complex_ = np.complex128
    print("[NumPy Compat] ✅ np.complex_ -> np.complex128")


if not hasattr(np, 'bool_'):
    np.bool_ = bool
    print("[NumPy Compat] ✅ np.bool_ -> bool")


print("[NumPy Compat] Compatibilidade NumPy 2.x ativada ✅")


# ============================================================================
# IMPORTAÇÕES FLASK
# ============================================================================


from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os


# Instância global do banco
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    CORS(app)


    # Configurações básicas
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['JSON_SORT_KEYS'] = False


    # ========================================================================
    # CONFIGURAÇÃO DO BANCO DE DADOS (MODIFICADO PARA PRODUÇÃO)
    # ========================================================================
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Produção (Render/PostgreSQL)
        print('[INIT] 🔵 Usando PostgreSQL (produção)')
        # Fix: Render usa postgres:// mas SQLAlchemy precisa de postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    else:
        # Desenvolvimento (SQLite local)
        print('[INIT] 🟡 Usando SQLite (desenvolvimento)')
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, 'instance', 'plataforma_equilibrio.db')
        os.makedirs(os.path.join(base_dir, 'instance'), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Inicializar SQLAlchemy
    db.init_app(app)


    # ========================================================================
    # CONFIGURAR FLASK-LOGIN
    # ========================================================================
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta página'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    print("[INIT] ✅ Flask-Login configurado")


    # Importar modelos para registrar as tabelas (User, Simulation, etc.)
    from app import models  # noqa: F401


    # ========================================================================
    # REGISTRAR BLUEPRINTS
    # ========================================================================
    # Nota: A ordem de registro importa para rotas com prefixos sobrepostos
    
    print("[INIT] Registrando blueprints...")
    
    # ✅ Blueprint de autenticação (PRIMEIRO)
    from app.routes import auth
    app.register_blueprint(auth.bp)
    print("[INIT] ✅ Blueprint 'auth' registrado (/auth/*)")
    
    # Blueprints principais
    from app.routes import main, api_components, elv, dashboard, educational
    from app.routes.ell import ell_bp  # Blueprint ELL
    from app.routes import esl
    
    app.register_blueprint(main.bp)
    print("[INIT] ✅ Blueprint 'main' registrado")
    
    app.register_blueprint(api_components.bp)
    print("[INIT] ✅ Blueprint 'api_components' registrado")
    
    # Módulos de cálculo
    app.register_blueprint(elv.bp)
    print("[INIT] ✅ Blueprint 'elv' registrado (/elv/*)")
    
    app.register_blueprint(ell_bp)
    print("[INIT] ✅ Blueprint 'ell' registrado (/ell/*)")
    
    app.register_blueprint(esl.bp)
    print("[INIT] ✅ Blueprint 'esl' registrado (/esl/*)")
    
    # Outros módulos
    app.register_blueprint(dashboard.bp)
    print("[INIT] ✅ Blueprint 'dashboard' registrado")
    
    app.register_blueprint(educational.bp)
    print("[INIT] ✅ Blueprint 'educational' registrado")
    
    # API de componentes ELL (se existir separado)
    try:
        from app.routes.api_ell_components import bp as api_ell_components_bp
        app.register_blueprint(api_ell_components_bp)
        print('[INIT] ✅ Blueprint api_ell_components registrado')
    except ImportError:
        print('[INIT] ⚠️ api_ell_components não encontrado (opcional)')


    # ========================================================================
    # CRIAR TABELAS E PRÉ-CARREGAR COMPONENTES
    # ========================================================================
    
    with app.app_context():
        try:
            db.create_all()
            print('[INIT] ✅ Tabelas do banco criadas/atualizadas')
        except Exception as e:
            print(f'[INIT] ❌ Erro ao criar tabelas: {e}')


        try:
            from app.utils.component_database import ComponentDatabase
            comp_db = ComponentDatabase()
            all_comps = comp_db.list_all_components()
            print(f'[INIT] ✅ {len(all_comps)} componentes pré-carregados')
        except Exception as e:
            print(f'[INIT] ⚠️ Erro ao pré-carregar componentes: {e}')


    print('='*70)
    print('[INIT] 🚀 Aplicação Flask inicializada com sucesso!')
    print('[INIT] 📦 Módulos disponíveis: ELV, ELL, ESL, Dashboard, Educational, Auth')
    print('[INIT] 🔢 NumPy:', np.__version__, '(compatível)')
    print('[INIT] 🔐 Autenticação: Ativada (Flask-Login)')
    print('='*70)
    
    return app
