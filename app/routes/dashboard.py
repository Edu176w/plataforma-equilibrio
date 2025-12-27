from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
from datetime import datetime
from io import StringIO
import csv

from app import db
from app.models import Simulation

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/')
@login_required  # ✅ ADICIONAR
def index():
    """Renderiza página do dashboard (apenas usuários logados)"""
    return render_template('dashboard.html')

@bp.route('/simulations', methods=['GET'])
@login_required  # ✅ ADICIONAR
def get_simulations():
    """
    Obter histórico de simulações do usuário logado
    
    Query params:
        module: Filtrar por módulo (elv, ell, esl)
        limit: Limite de resultados (padrão: 1000)
    """
    try:
        module = request.args.get('module')
        limit = request.args.get('limit', type=int) or 1000

        # ✅ FILTRAR POR USUÁRIO LOGADO
        query = Simulation.query.filter_by(user_id=current_user.id)
        
        if module:
            query = query.filter_by(module=module)

        sims = (
            query
            .order_by(Simulation.created_at.desc())
            .limit(limit)
            .all()
        )

        simulations = []
        for s in sims:
            simulations.append({
                'id': s.id,
                'timestamp': s.created_at.isoformat() if s.created_at else None,
                'module': s.module,
                'calculation_type': s.calculation_type,
                'model': s.model,
                'components': s.components,
                'conditions': s.conditions,
                'results': None,  # não enviar payload pesado na listagem
                'execution_time': s.execution_time,
                'success': s.success,
                'error_message': s.error_message,
            })

        return jsonify({'success': True, 'simulations': simulations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/save', methods=['POST'])
@login_required  # ✅ ADICIONAR
def save_simulation():
    """
    Endpoint descontinuado - gravação feita diretamente pelos módulos
    """
    return jsonify({
        'success': False,
        'error': 'Endpoint /save descontinuado; gravação é feita diretamente na tabela Simulation.'
    }), 410

@bp.route('/<int:simulation_id>', methods=['GET'])
@login_required  # ✅ ADICIONAR
def get_simulation(simulation_id):
    """
    Obter uma simulação específica do usuário logado
    """
    try:
        # ✅ VERIFICAR SE A SIMULAÇÃO PERTENCE AO USUÁRIO
        s = Simulation.query.filter_by(
            id=simulation_id,
            user_id=current_user.id
        ).first()
        
        if not s:
            return jsonify({
                'success': False, 
                'error': 'Simulação não encontrada ou você não tem permissão'
            }), 404

        sim = s.to_dict()
        sim['error_message'] = s.error_message

        return jsonify({'success': True, 'simulation': sim})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:simulation_id>', methods=['DELETE'])
@login_required  # ✅ ADICIONAR
def delete_simulation(simulation_id):
    """
    Deletar uma simulação do usuário logado
    """
    try:
        # ✅ VERIFICAR SE A SIMULAÇÃO PERTENCE AO USUÁRIO
        s = Simulation.query.filter_by(
            id=simulation_id,
            user_id=current_user.id
        ).first()
        
        if not s:
            return jsonify({
                'success': False, 
                'error': 'Simulação não encontrada ou você não tem permissão'
            }), 404

        db.session.delete(s)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@login_required  # ✅ ADICIONAR
def get_stats():
    """
    Obter estatísticas do dashboard do usuário logado
    """
    try:
        # ✅ FILTRAR POR USUÁRIO LOGADO
        sims = Simulation.query.filter_by(user_id=current_user.id).all()

        total = len(sims)
        successful = len([s for s in sims if s.success])
        failed = total - successful

        by_module = {}
        for s in sims:
            mod = (s.module or 'unknown').lower()
            by_module[mod] = by_module.get(mod, 0) + 1

        by_model = {}
        for s in sims:
            m = s.model or 'unknown'
            by_model[m] = by_model.get(m, 0) + 1

        exec_times = [s.execution_time for s in sims if s.execution_time is not None]
        avg_time = sum(exec_times) / len(exec_times) if exec_times else 0.0

        stats = {
            'total_simulations': total,
            'successful': successful,
            'failed': failed,
            'by_module': by_module,
            'by_model': by_model,
            'avg_execution_time': round(avg_time, 3),
        }

        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/export', methods=['GET'])
@login_required  # ✅ ADICIONAR
def export_history():
    """
    Exportar histórico de simulações do usuário logado em CSV
    """
    try:
        # ✅ FILTRAR POR USUÁRIO LOGADO
        sims = Simulation.query.filter_by(
            user_id=current_user.id
        ).order_by(Simulation.created_at.desc()).all()

        si = StringIO()
        writer = csv.writer(si, delimiter=';')

        writer.writerow([
            'id',
            'timestamp',
            'module',
            'calculation_type',
            'model',
            'components',
            'conditions',
            'results',
            'execution_time',
            'success',
            'error_message',
        ])

        for s in sims:
            writer.writerow([
                s.id,
                s.created_at.isoformat() if s.created_at else '',
                s.module or '',
                s.calculation_type or '',
                s.model or '',
                s.components or '',
                s.conditions or '',
                s.results or '',
                s.execution_time if s.execution_time is not None else '',
                1 if s.success else 0,
                (s.error_message or '').replace('\n', ' ').replace('\r', ' '),
            ])

        output = si.getvalue()
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=historico_{current_user.username}.csv'}
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
