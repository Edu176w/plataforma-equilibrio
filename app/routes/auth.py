"""
app/routes/auth.py
Sistema de autenticação - Login, Registro, Logout
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Login realizado com sucesso!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    
    return render_template('auth/login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validações
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios!', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Usuário já existe!', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'danger')
        elif password != password_confirm:
            flash('Senhas não conferem!', 'danger')
        elif len(password) < 6:
            flash('Senha deve ter no mínimo 6 caracteres!', 'danger')
        else:
            # Criar usuário
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@bp.route('/logout')
@login_required
def logout():
    """Fazer logout"""
    logout_user()
    flash('Você saiu da sua conta', 'info')
    return redirect(url_for('main.index'))


@bp.route('/profile')
@login_required
def profile():
    """Perfil do usuário"""
    total_sims = len(current_user.simulations)
    return render_template('auth/profile.html', total_simulations=total_sims)
