# app/models.py (ATUALIZADO)
from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com simulações
    simulations = db.relationship('Simulation', backref='user', lazy=True)
    
    def set_password(self, password):
        """Define senha com hash seguro (Werkzeug)"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Simulation(db.Model):
    __tablename__ = 'simulations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Informações da simulação
    module = db.Column(db.String(20), nullable=False)  # elv, ell, esl
    calculation_type = db.Column(db.String(50), nullable=False)  # bubble, flash, etc
    model = db.Column(db.String(20), nullable=False)  # PR, NRTL, etc
    
    # Componentes e condições (JSON)
    components = db.Column(db.Text, nullable=False)  # Lista de componentes
    conditions = db.Column(db.Text, nullable=False)  # Temperatura, pressão, composição
    
    # Resultados (JSON)
    results = db.Column(db.Text, nullable=False)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    execution_time = db.Column(db.Float)  # Tempo de execução em segundos
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Simulation {self.id} - {self.module} - {self.calculation_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'module': self.module,
            'calculation_type': self.calculation_type,
            'model': self.model,
            'components': json.loads(self.components),
            'conditions': json.loads(self.conditions),
            'results': json.loads(self.results),
            'created_at': self.created_at.isoformat(),
            'execution_time': self.execution_time,
            'success': self.success
        }
