# app/routes/esl.py
"""
ESL Routes - Rotas Flask para Equilíbrio Sólido-Líquido
===============================================================================

Endpoints REST para cálculos de ESL baseados em Prausnitz et al.

Rotas disponíveis:
------------------
1. Cálculos pontuais:
   - POST /esl/calculate/solubility - Calcula solubilidade a T fixa
   - POST /esl/calculate/crystallization - Calcula T de cristalização
   
2. Diagramas:
   - POST /esl/diagram/tx - Diagrama binário T-x (liquidus)
   - POST /esl/diagram/ternary - Diagrama ternário isotérmico
   
3. Comparação de modelos:
   - POST /esl/calculate/compare - Compara modelos em cálculo pontual
   - POST /esl/diagram/compare - Compara modelos em diagramas
   
4. Dados e propriedades:
   - GET /esl/components - Lista componentes disponíveis
   - GET /esl/component/<name> - Propriedades de um componente
   - GET /esl/eutectic_systems - Sistemas eutéticos conhecidos
   
5. Exportação:
   - POST /esl/export/csv - Exporta dados em CSV
   - POST /esl/export/pdf - Exporta em PDF
   - POST /esl/export/point_csv - Exporta cálculo pontual em CSV
   - POST /esl/export/point_pdf - Exporta cálculo pontual em PDF

Autor: Plataforma de Equilíbrio de Fases
Data: 2025-12-20
"""

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    send_file,
    make_response,
)
from flask_login import current_user, login_required  # ✅ ADICIONAR login_required
from datetime import datetime
import pandas as pd
import numpy as np
import io
import time

from app.calculators.esl_calculator import ESLCalculator
from app.utils.ai_esl import log_esl_simulation, recommend_model_for_esl

# Importar funções de dados ESL
try:
    from app.data.esl_data import (
        get_component_data,
        list_available_components,
        get_eutectic_systems,
        validate_component_data,
        print_component_summary
    )
    HAS_ESL_DATA = True
except ImportError:
    HAS_ESL_DATA = False
    def get_component_data(name): return None
    def list_available_components(): return []
    def get_eutectic_systems(): return []
    def validate_component_data(name): return {'valid': True, 'warnings': [], 'errors': []}
    def print_component_summary(name): pass

bp = Blueprint('esl', __name__, url_prefix='/esl')

# ============================================================================
# PRESETS DE CASOS DE ESTUDO ESL
# ============================================================================

CASE_PRESETS = {
    'naphthalene-benzene': {
        'id': 'naphthalene-benzene',
        'title': 'Naftaleno-Benzeno (Caso de Estudo)',
        'components': ['Naphthalene', 'Benzene'],
        'model': 'Ideal',
        'calc_type': 'solubility',
        'temperature': 0,
        'temperature_unit': 'C'
    },
    
    'phenol-water': {
        'id': 'phenol-water',
        'title': 'Fenol-Água (Caso de Estudo)',
        'components': ['Phenol', 'Water'],
        'model': 'NRTL',
        'calc_type': 'solubility',
        'temperature': 20,
        'temperature_unit': 'C'
    }
}



# =============================================================================
# ROTAS PRINCIPAIS
# =============================================================================

@bp.route('/')
def index():
    """Redireciona para calculadora ESL."""
    return redirect(url_for('esl.calculator'))


@bp.route('/calculator')
@login_required
def calculator():
    """
    Renderiza a página da calculadora ESL
    Suporta query parameters para carregar presets de casos de estudo
    
    Query params:
        preset: ID do caso de estudo (ex: 'naphthalene-benzene')
    
    Returns:
        Template renderizado com dados do preset (se aplicável)
    """
    preset_id = request.args.get('preset')
    preset_data = None
    
    if preset_id:
        if preset_id in CASE_PRESETS:
            preset_data = CASE_PRESETS[preset_id]
            print(f'[ESL] 📚 Carregando preset: {preset_id} - {preset_data["title"]}')
        else:
            print(f'[ESL] ⚠️  Preset não encontrado: {preset_id}')
    
    return render_template('esl_calculator.html', preset=preset_data)



# =============================================================================
# ROTAS DE DADOS E PROPRIEDADES
# =============================================================================

@bp.route('/components', methods=['GET'])
def get_components_list():
    """
    Lista componentes ESL disponíveis, FILTRANDO por modelo termodinâmico.
    
    Query Parameters:
        model (str): 'Ideal', 'NRTL', 'UNIQUAC', 'UNIFAC' (default: 'Ideal')
    
    Example:
        GET /esl/components?model=NRTL
    
    Returns:
        JSON com componentes que têm parâmetros para o modelo
    """
    try:
        if not HAS_ESL_DATA:
            return jsonify({
                'success': False,
                'error': 'Base de dados ESL não disponível'
            }), 500
        
        # Obter modelo da query string
        model = request.args.get('model', 'Ideal')
        
        print(f"[ESL] Carregando componentes para modelo: {model}")  # Debug
        
        # Importar dados necessários
        from app.data.esl_data import (
            ESL_DATA,
            NRTL_PARAMETERS,
            UNIQUAC_PURE_PROPERTIES,
            UNIFAC_GROUPS
        )
        
        filtered_components = []
        
        # Iterar sobre todos os componentes ESL
        for key, data in ESL_DATA.items():
            comp_name = data.get('name')  # Nome em português
            
            # Criar dicionário do componente
            comp_dict = {
                'key': key,
                'name': comp_name,
                'name_en': data.get('name_en'),
                'formula': data.get('formula'),
                'CAS': data.get('CAS'),
                'MW': data.get('MW'),
                'Tm': data.get('Tm'),
                'Tm_C': data.get('Tm_C'),
                'Hfus': data.get('Hfus'),
                'Hfus_kJ_mol': data.get('Hfus_kJ_mol'),
                'Sfus': data.get('Sfus'),
                'applications': data.get('applications', '')
            }
            
            # Filtrar por modelo
            if model == 'Ideal':
                # Ideal: todos os componentes
                filtered_components.append(comp_dict)
            
            elif model == 'NRTL':
                # NRTL: verificar se tem parâmetros com ALGUM outro componente
                has_nrtl = False
                
                for (comp1, comp2) in NRTL_PARAMETERS.keys():
                    if comp1 == comp_name or comp2 == comp_name:
                        has_nrtl = True
                        break
                
                if has_nrtl:
                    filtered_components.append(comp_dict)
            
            elif model == 'UNIQUAC':
                # UNIQUAC: verificar se tem propriedades r, q
                if comp_name in UNIQUAC_PURE_PROPERTIES:
                    filtered_components.append(comp_dict)
            
            elif model == 'UNIFAC':
                # UNIFAC: verificar se tem grupos funcionais
                if comp_name in UNIFAC_GROUPS:
                    filtered_components.append(comp_dict)
        
        print(f"[ESL] Componentes filtrados para {model}: {len(filtered_components)}")  # Debug
        
        return jsonify({
            'success': True,
            'components': filtered_components,
            'total': len(filtered_components),
            'model': model,
            'source': 'NIST WebBook + Literatura + Prausnitz'
        })
    
    except Exception as e:
        print(f"[ESL] ERRO: {str(e)}")  # Debug
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/component/<component_name>', methods=['GET'])
def get_component_properties(component_name):
    """
    Retorna propriedades termodinâmicas de um componente específico.
    
    Parameters:
        component_name (str): Nome do componente (URL parameter)
        
    Returns:
        JSON com propriedades completas do componente
        
    Example:
        GET /esl/component/naphthalene
    """
    try:
        if not HAS_ESL_DATA:
            return jsonify({
                'success': False,
                'error': 'Base de dados ESL não disponível'
            }), 500
        
        data = get_component_data(component_name)
        
        if data is None:
            return jsonify({
                'success': False,
                'error': f'Componente "{component_name}" não encontrado'
            }), 404
        
        # Validar dados
        validation = validate_component_data(component_name)
        
        return jsonify({
            'success': True,
            'component': data,
            'validation': validation
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/eutectic_systems', methods=['GET'])
def get_eutectic_systems_list():
    """
    Lista sistemas eutéticos binários conhecidos da literatura.
    
    Returns:
        JSON com sistemas eutéticos documentados
        
    Example:
        GET /esl/eutectic_systems
    """
    try:
        if not HAS_ESL_DATA:
            return jsonify({
                'success': False,
                'error': 'Base de dados ESL não disponível'
            }), 500
        
        systems = get_eutectic_systems()
        
        return jsonify({
            'success': True,
            'eutectic_systems': systems,
            'total': len(systems)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/validate_components', methods=['POST'])
def validate_components():
    """
    Valida se componentes são compatíveis com modelo selecionado.
    
    Request JSON:
        {
            "components": ["naphthalene", "benzene"],
            "model": "NRTL"
        }
        
    Returns:
        JSON com status de validação e avisos
    """
    try:
        data = request.get_json() or {}
        components = data.get('components', [])
        model = data.get('model', 'Ideal')
        
        calc = ESLCalculator()
        
        # Validar modelo/componentes
        try:
            calc.validate_model_components(components, model)
            is_valid = True
            error_message = None
        except ValueError as e:
            is_valid = False
            error_message = str(e)
        
        # Validar dados termodinâmicos individuais
        component_validations = {}
        if HAS_ESL_DATA:
            for comp in components:
                validation = validate_component_data(comp)
                component_validations[comp] = validation
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'error_message': error_message,
            'component_validations': component_validations,
            'warnings': calc.warnings
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# CÁLCULOS PONTUAIS
# =============================================================================

@bp.route('/calculate/solubility', methods=['POST'])
def calculate_solubility():
    """
    Calcula solubilidade de sólidos em líquido a temperatura fixa.
    
    Baseado em Prausnitz Eq. 11-5, 11-13, 11-15:
    x₂ × γ₂ = f₂^L / f₂^S
    
    Request JSON:
        {
            "components": ["naphthalene", "benzene"],
            "temperature": 25.0,
            "temperature_unit": "C",  // "C" ou "K"
            "model": "NRTL",  // "Ideal", "Wilson", "NRTL", "UNIQUAC", "UNIFAC"
            "use_complete_equation": false  // true: Eq. 11-13, false: Eq. 11-15
        }
        
    Returns:
        JSON com composições de saturação e coeficientes de atividade
    """
    start_time = time.time()
    
    try:
        data = request.get_json() or {}
        
        # Parâmetros obrigatórios
        components = data.get('components')
        if not components:
            return jsonify({'success': False, 'error': 'Componentes não especificados'}), 400
        
        model = data.get('model', 'Ideal')
        
        # Temperatura
        temp_value = data.get('temperature')
        if temp_value is None:
            return jsonify({'success': False, 'error': 'Temperatura não especificada'}), 400
        
        temp_unit = data.get('temperature_unit', 'C')
        if temp_unit == 'K':
            temperature_C = temp_value - 273.15
        else:
            temperature_C = temp_value
        
        # Parâmetros opcionais
        use_complete_equation = data.get('use_complete_equation', False)
        
        # Executar cálculo
        calc = ESLCalculator()
        results = calc.solubility(
            components=components,
            temperature_C=temperature_C,
            model=model,
            use_complete_equation=use_complete_equation
        )
        
        # Sugestão de IA
        ai_suggestion = recommend_model_for_esl(components, 'solubility')
        
        # Logging
        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'temperature_C': temperature_C,
            'temperature_unit': temp_unit,
            'use_complete_equation': use_complete_equation
        }
        log_esl_simulation(
            user_id=user_id,
            calculation_type='solubility',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'calc_type': 'solubility',
            'ai_suggestion': ai_suggestion,
            'execution_time': round(time.time() - start_time, 3)
        })
    
    except ValueError as e:
        # Erro de validação
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'validation'
        }), 400
    
    except Exception as e:
        # Erro inesperado - logging
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'temperature': data.get('temperature'),
                'temperature_unit': data.get('temperature_unit', 'C'),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_esl_simulation(
                user_id=user_id,
                calculation_type='solubility',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'calculation'
        }), 500


@bp.route('/calculate/crystallization', methods=['POST'])
def calculate_crystallization():
    """
    Calcula temperatura de início de cristalização para composição fixa.
    
    Resolve para T onde: xᵢ × γᵢ(x,T) = exp[-(ΔHfus/R)(Tm/T - 1)]
    
    Request JSON:
        {
            "components": ["naphthalene", "benzene"],
            "compositions": [0.3, 0.7],  // Frações molares
            "model": "NRTL",
            "use_complete_equation": false
        }
        
    Returns:
        JSON com temperatura de cristalização
    """
    start_time = time.time()
    
    try:
        data = request.get_json() or {}
        
        # Parâmetros obrigatórios
        components = data.get('components')
        compositions = data.get('compositions')
        
        if not components:
            return jsonify({'success': False, 'error': 'Componentes não especificados'}), 400
        if not compositions:
            return jsonify({'success': False, 'error': 'Composições não especificadas'}), 400
        if len(components) != len(compositions):
            return jsonify({'success': False, 'error': 'Número de componentes e composições não correspondem'}), 400
        
        model = data.get('model', 'Ideal')
        use_complete_equation = data.get('use_complete_equation', False)
        
        # Executar cálculo
        calc = ESLCalculator()
        results = calc.crystallization(
            components=components,
            compositions=compositions,
            model=model,
            use_complete_equation=use_complete_equation
        )
        
        # Sugestão de IA
        ai_suggestion = recommend_model_for_esl(components, 'crystallization')
        
        # Logging
        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'compositions': compositions,
            'use_complete_equation': use_complete_equation
        }
        log_esl_simulation(
            user_id=user_id,
            calculation_type='crystallization',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'calc_type': 'crystallization',
            'ai_suggestion': ai_suggestion,
            'execution_time': round(time.time() - start_time, 3)
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'validation'
        }), 400
    
    except Exception as e:
        # Logging
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {'compositions': data.get('compositions', [])}
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_esl_simulation(
                user_id=user_id,
                calculation_type='crystallization',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'calculation'
        }), 500


# =============================================================================
# DIAGRAMAS DE FASES
# =============================================================================

@bp.route('/diagram/tx', methods=['POST'])
def generate_tx_diagram():
    """
    Gera diagrama de fases binário T-x (curva liquidus).
    
    Prausnitz Fig. 11-5, 11-17, 11-20, 11-21.
    
    Request JSON:
        {
            "components": ["naphthalene", "benzene"],  // Exatamente 2
            "model": "NRTL",
            "n_points": 50,  // Resolução da curva
            "use_complete_equation": false
        }
        
    Returns:
        JSON com arrays x1, T_liquidus, ponto eutético
    """
    start_time = time.time()
    
    try:
        data = request.get_json() or {}
        
        # Parâmetros
        components = data.get('components')
        if not components:
            return jsonify({'success': False, 'error': 'Componentes não especificados'}), 400
        if len(components) != 2:
            return jsonify({'success': False, 'error': 'Diagrama T-x requer exatamente 2 componentes'}), 400
        
        model = data.get('model', 'Ideal')
        n_points = data.get('n_points', 50)
        use_complete_equation = data.get('use_complete_equation', False)
        
        # Executar cálculo
        calc = ESLCalculator()
        results = calc.generate_tx_diagram(
            components=components,
            model=model,
            n_points=n_points,
            use_complete_equation=use_complete_equation
        )
        
        # Sugestão de IA
        ai_suggestion = recommend_model_for_esl(components, 'tx')
        
        # Logging
        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'n_points': n_points,
            'use_complete_equation': use_complete_equation
        }
        log_esl_simulation(
            user_id=user_id,
            calculation_type='tx',
            model=model,
            components=components,
            conditions=conditions,
            results=results,  # ✅ SALVAR TUDO! (x1, T_liquidus_C, T_eutectic_C, x_eutectic)
            success=True,
            error_message=None,
            start_time=start_time,
        )

        
        return jsonify({
            'success': True,
            'results': results,
            'ai_suggestion': ai_suggestion,
            'execution_time': round(time.time() - start_time, 3)
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'validation'
        }), 400
    
    except Exception as e:
        # Logging
        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'n_points': n_points,
            'use_complete_equation': use_complete_equation
        }
        log_esl_simulation(
            user_id=user_id,
            calculation_type='tx',
            model=model,
            components=components,
            conditions=conditions,
            results=results,  # ✅ SALVAR TUDO (x1, T_liquidus_C, etc.)
            success=True,
            error_message=None,
            start_time=start_time,
        )
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'calculation'
        }), 500


@bp.route('/diagram/ternary', methods=['POST'])
def generate_ternary_diagram():
    """
    Gera diagrama ternário de solubilidade isotérmico.
    
    Prausnitz Fig. 11-21, 11-23 (sistemas ternários).
    
    Request JSON:
    {
        "components": ["naphthalene", "anthracene", "benzene"],  # Exatamente 3
        "temperature": 25.0,
        "temperature_unit": "C",
        "model": "UNIFAC",
        "n_points": 20,  # ✅ CORRIGIDO: era grid_resolution
        "use_complete_equation": false
    }
    
    Returns:
        JSON com pontos {x1, x2, x3, phase} para plotagem triangular
    """
    start_time = time.time()
    
    try:
        data = request.get_json() or {}
        
        # Parâmetros obrigatórios
        components = data.get('components')
        if not components:
            return jsonify(success=False, error='Componentes não especificados'), 400
        
        if len(components) != 3:
            return jsonify(success=False, error='Diagrama ternário requer exatamente 3 componentes'), 400
        
        model = data.get('model', 'Ideal')
        
        # Temperatura
        temp_value = data.get('temperature')
        if temp_value is None:
            return jsonify(success=False, error='Temperatura não especificada'), 400
        
        temp_unit = data.get('temperature_unit', 'C')
        if temp_unit == 'K':
            temperature_C = temp_value - 273.15
        else:
            temperature_C = temp_value
        
        # ✅ CORREÇÃO 1: Receber n_points (não grid_resolution)
        n_points = data.get('n_points', 20)
        
        use_complete_equation = data.get('use_complete_equation', False)
        
        # Executar cálculo
        calc = ESLCalculator()
        
        # ✅ CORREÇÃO 2: Passar n_points (não grid_resolution)
        results = calc.generate_ternary_diagram(
            components=components,
            temperature_C=temperature_C,
            model=model,
            n_points=n_points,  # ✅ CORRIGIDO!
            use_complete_equation=use_complete_equation
        )
        
        # Suggestão de IA
        ai_suggestion = recommend_model_for_esl(components, 'ternary')
        
        # Logging
        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'temperature_C': temperature_C,
            'temperature_unit': temp_unit,
            'n_points': n_points,
            'use_complete_equation': use_complete_equation
        }
        log_esl_simulation(
            user_id=user_id,
            calculation_type='ternary',
            model=model,
            components=components,
            conditions=conditions,
            results=results,  # ✅ SALVAR TUDO (points, etc.)
            success=True,
            error_message=None,
            start_time=start_time,
        )

        
        return jsonify({
            'success': True,
            'results': results,
            'ai_suggestion': ai_suggestion,
            'execution_time': round(time.time() - start_time, 3)
        })
        
    except ValueError as e:
        return jsonify(success=False, error=str(e), error_type='validation'), 400
    
    except Exception as e:
        # Logging
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'temperature': data.get('temperature'),
                'temperature_unit': data.get('temperature_unit', 'C'),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_esl_simulation(
                user_id=user_id,
                calculation_type='ternary',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except:
            pass
        
        return jsonify(success=False, error=str(e), error_type='calculation'), 500

# =============================================================================
# COMPARAÇÃO DE MODELOS
# =============================================================================

@bp.route('/diagram/compare', methods=['POST'])
def esl_compare_diagrams():
    """
    Compara múltiplos modelos em um diagrama T-x ou ternário.
    
    Request JSON:
        {
            "diagram_type": "tx",  // "tx" ou "ternary"
            "components": ["naphthalene", "benzene"],
            "models": ["Ideal", "NRTL", "UNIFAC"],  // 2-4 modelos
            "temperature": 25.0,  // Apenas para ternary
            "temperature_unit": "C",
            "n_points": 50,  // ✅ CORREÇÃO: único parâmetro para ambos os tipos
            "use_complete_equation": false
        }
        
    Returns:
        JSON com resultados para cada modelo
    """
    try:
        data = request.get_json() or {}
        diagram_type = data.get('diagram_type')
        components = data.get('components', [])
        models = data.get('models', [])
        
        if not diagram_type:
            return jsonify({'success': False, 'error': 'Tipo de diagrama não especificado'}), 400
        if not components:
            return jsonify({'success': False, 'error': 'Componentes não especificados'}), 400
        if not models or len(models) < 2:
            return jsonify({'success': False, 'error': 'Selecione pelo menos 2 modelos para comparar'}), 400
        if len(models) > 4:
            return jsonify({'success': False, 'error': 'Máximo 4 modelos para comparação'}), 400
        
        results = {}
        calc = ESLCalculator()
        
        use_complete_equation = data.get('use_complete_equation', False)
        
        for model in models:
            try:
                if diagram_type == 'tx':
                    if len(components) != 2:
                        results[model] = {'error': 'T-x requer 2 componentes'}
                        continue
                    
                    n_points = data.get('n_points', 50)
                    model_result = calc.generate_tx_diagram(
                        components=components,
                        model=model,
                        n_points=n_points,
                        use_complete_equation=use_complete_equation
                    )
                
                elif diagram_type == 'ternary':
                    if len(components) != 3:
                        results[model] = {'error': 'Ternário requer 3 componentes'}
                        continue
                    
                    temp_value = data.get('temperature')
                    if temp_value is None:
                        results[model] = {'error': 'Temperatura não especificada'}
                        continue
                    
                    temp_unit = data.get('temperature_unit', 'C')
                    if temp_unit == 'K':
                        temperature_C = temp_value - 273.15
                    else:
                        temperature_C = temp_value
                    
                    # ✅ CORREÇÃO: usar n_points em vez de grid_resolution
                    n_points = data.get('n_points', 20)
                    
                    model_result = calc.generate_ternary_diagram(
                        components=components,
                        temperature_C=temperature_C,
                        model=model,
                        n_points=n_points,  # ✅ CORRIGIDO!
                        use_complete_equation=use_complete_equation
                    )
                
                else:
                    model_result = {'error': f'Tipo de diagrama "{diagram_type}" desconhecido'}
                
                results[model] = model_result
            
            except Exception as e:
                results[model] = {'error': str(e)}
        
        # Estatísticas de comparação
        comparison_stats = _calculate_comparison_stats(results, diagram_type)
        
        return jsonify({
            'success': True,
            'results': results,
            'comparison_stats': comparison_stats
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@bp.route('/calculate/compare', methods=['POST'])
def esl_compare_point_calculations():
    """
    Compara múltiplos modelos em um cálculo pontual.
    
    Request JSON:
        {
            "calc_type": "solubility",  // "solubility" ou "crystallization"
            "components": ["naphthalene", "benzene"],
            "models": ["Ideal", "NRTL", "UNIFAC"],
            "temperature": 25.0,  // Para solubility
            "temperature_unit": "C",
            "compositions": [0.3, 0.7],  // Para crystallization
            "use_complete_equation": false
        }
        
    Returns:
        JSON com resultados para cada modelo + análise comparativa
    """
    try:
        data = request.get_json() or {}
        calc_type = data.get('calc_type')
        components = data.get('components', [])
        models = data.get('models', [])
        
        if not calc_type:
            return jsonify({'success': False, 'error': 'Tipo de cálculo não especificado'}), 400
        if not components:
            return jsonify({'success': False, 'error': 'Componentes não especificados'}), 400
        if not models or len(models) < 2:
            return jsonify({'success': False, 'error': 'Selecione pelo menos 2 modelos para comparar'}), 400
        
        results = {}
        calc = ESLCalculator()
        
        use_complete_equation = data.get('use_complete_equation', False)
        
        for model in models:
            try:
                if calc_type == 'solubility':
                    temp_value = data.get('temperature')
                    if temp_value is None:
                        results[model] = {'error': 'Temperatura não especificada'}
                        continue
                    
                    temp_unit = data.get('temperature_unit', 'C')
                    if temp_unit == 'K':
                        temperature_C = temp_value - 273.15
                    else:
                        temperature_C = temp_value
                    
                    model_result = calc.solubility(
                        components=components,
                        temperature_C=temperature_C,
                        model=model,
                        use_complete_equation=use_complete_equation
                    )
                
                elif calc_type == 'crystallization':
                    compositions = data.get('compositions')
                    if not compositions:
                        results[model] = {'error': 'Composições não especificadas'}
                        continue
                    
                    model_result = calc.crystallization(
                        components=components,
                        compositions=compositions,
                        model=model,
                        use_complete_equation=use_complete_equation
                    )
                
                else:
                    model_result = {'error': f'Tipo de cálculo "{calc_type}" desconhecido'}
                
                results[model] = model_result
            
            except Exception as e:
                results[model] = {'error': str(e)}
        
        # Análise comparativa
        comparison_analysis = _analyze_point_comparison(results, calc_type, components)
        
        return jsonify({
            'success': True,
            'results': results,
            'comparison_analysis': comparison_analysis
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# FUNÇÕES AUXILIARES PARA COMPARAÇÃO
# =============================================================================

def _calculate_comparison_stats(results, diagram_type):
    """
    Calcula estatísticas comparativas entre modelos.
    
    Para T-x: compara temperaturas eutéticas
    Para ternário: compara extensão das regiões sólido-líquido
    """
    stats = {}
    
    if diagram_type == 'tx':
        # Comparar temperaturas eutéticas
        eutectic_temps = {}
        eutectic_comps = {}
        
        for model, data in results.items():
            if 'error' not in data:
                eutectic_temps[model] = data.get('T_eutectic_C')
                eutectic_comps[model] = data.get('x_eutectic')
        
        if len(eutectic_temps) >= 2:
            temps = list(eutectic_temps.values())
            stats['T_eutectic_mean'] = round(np.mean(temps), 2)
            stats['T_eutectic_std'] = round(np.std(temps), 2)
            stats['T_eutectic_range'] = [round(min(temps), 2), round(max(temps), 2)]
            stats['eutectic_data'] = {
                'temperatures': eutectic_temps,
                'compositions': eutectic_comps
            }
    
    elif diagram_type == 'ternary':
        # Comparar proporção de pontos líquidos vs sólido-líquido
        phase_stats = {}
        
        for model, data in results.items():
            if 'error' not in data and 'points' in data:
                points = data['points']
                total = len(points)
                liquid = sum(1 for p in points if p['phase'] == 'liquid')
                phase_stats[model] = {
                    'total_points': total,
                    'liquid_points': liquid,
                    'solid_liquid_points': total - liquid,
                    'liquid_fraction': round(liquid / total, 3) if total > 0 else 0
                }
        
        stats['phase_statistics'] = phase_stats
    
    return stats


def _analyze_point_comparison(results, calc_type, components):
    """
    Análise comparativa para cálculos pontuais.
    
    Compara composições (solubility) ou temperaturas (crystallization).
    """
    analysis = {
        'calc_type': calc_type,
        'models_compared': list(results.keys()),
        'successful_models': []
    }
    
    if calc_type == 'solubility':
        # Comparar frações molares calculadas
        compositions = {}
        gammas = {}
        
        for model, data in results.items():
            if 'error' not in data:
                analysis['successful_models'].append(model)
                for key, value in data.items():
                    if key.startswith('x') and '(' in key:
                        # Extrair componente: x1 (naphthalene) -> naphthalene
                        comp_name = key.split('(')[1].split(')')[0]
                        if comp_name not in compositions:
                            compositions[comp_name] = {}
                        compositions[comp_name][model] = value
                    elif key.startswith('gamma'):
                        if model not in gammas:
                            gammas[model] = {}
                        gammas[model][key] = value
        
        analysis['compositions'] = compositions
        analysis['activity_coefficients'] = gammas
        
        # Estatísticas por componente
        for comp, model_values in compositions.items():
            if len(model_values) >= 2:
                values = list(model_values.values())
                analysis[f'{comp}_stats'] = {
                    'mean': round(np.mean(values), 6),
                    'std': round(np.std(values), 6),
                    'range': [round(min(values), 6), round(max(values), 6)],
                    'by_model': model_values
                }
    
    elif calc_type == 'crystallization':
        # Comparar temperaturas de cristalização
        temps_C = {}
        temps_K = {}
        
        for model, data in results.items():
            if 'error' not in data:
                analysis['successful_models'].append(model)
                if 'T_cryst_C' in data:
                    temps_C[model] = data['T_cryst_C']
                if 'T_cryst_K' in data:
                    temps_K[model] = data['T_cryst_K']
        
        if len(temps_C) >= 2:
            values = list(temps_C.values())
            analysis['T_cryst_stats'] = {
                'mean_C': round(np.mean(values), 2),
                'std_C': round(np.std(values), 2),
                'range_C': [round(min(values), 2), round(max(values), 2)],
                'by_model': temps_C
            }
    
    return analysis


# =============================================================================
# EXPORTAÇÃO - CSV
# =============================================================================

@bp.route('/export/csv', methods=['POST'])
def export_esl_csv():
    """
    Exporta dados de diagrama T-x ou ternário em CSV.
    
    Request JSON:
        {
            "diagram_type": "tx",
            "data": { ... },  // Resultado do diagrama
            "components": ["naphthalene", "benzene"],
            "model": "NRTL"
        }
    """
    try:
        data = request.get_json() or {}
        diagram_type = data.get('diagram_type')
        diagram_data = data.get('data')
        components = data.get('components', [])
        model = data.get('model', 'Ideal')
        
        if not diagram_data:
            return jsonify({'success': False, 'error': 'Dados do diagrama não fornecidos'}), 400
        
        if diagram_type == 'tx':
            # Diagrama T-x: x1, T_liquidus
            df = pd.DataFrame({
                f'x1 ({components[0]})': diagram_data.get('x1', []),
                'T_liquidus_C': diagram_data.get('T_liquidus_C', []),
            })
            
            # Adicionar linha do ponto eutético
            if 'T_eutectic_C' in diagram_data and 'x_eutectic' in diagram_data:
                eutectic_row = pd.DataFrame({
                    f'x1 ({components[0]})': [diagram_data['x_eutectic']],
                    'T_liquidus_C': [diagram_data['T_eutectic_C']]
                })
                df = pd.concat([df, eutectic_row], ignore_index=True)
                df = df.sort_values(f'x1 ({components[0]})')
            
            filename = f"ESL_TX_{components[0]}_{components[1]}_{model}.csv"
        
        elif diagram_type == 'ternary':
            # Diagrama ternário: x1, x2, x3, phase
            points = diagram_data.get('points', [])
            rows = []
            for pt in points:
                rows.append({
                    f'x1 ({components[0]})': pt['x1'],
                    f'x2 ({components[1]})': pt['x2'],
                    f'x3 ({components[2]})': pt['x3'],
                    'phase': pt['phase']
                })
            df = pd.DataFrame(rows)
            
            T_C = diagram_data.get('T_C', 'unknown')
            filename = f"ESL_Ternary_{T_C}C_{model}.csv"
        
        else:
            return jsonify({'success': False, 'error': 'Tipo de diagrama desconhecido'}), 400
        
        # Converter para CSV
        output = io.StringIO()
        
        # Adicionar metadados no cabeçalho
        output.write(f"# ESL Diagram Export\n")
        output.write(f"# Type: {diagram_type}\n")
        output.write(f"# Model: {model}\n")
        output.write(f"# Components: {', '.join(components)}\n")
        output.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write(f"# Source: Prausnitz ESL Calculator\n")
        output.write("#\n")
        
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/export/point_csv', methods=['POST'])
def export_esl_point_csv():
    """
    Exporta resultados de cálculo pontual (solubility/crystallization) em CSV.
    """
    try:
        data = request.get_json() or {}
        calc_type = data.get('calc_type')
        components = data.get('components', [])
        model = data.get('model', 'Ideal')
        results = data.get('results', {})
        
        # Converter resultados em DataFrame
        rows = []
        for key, value in results.items():
            if key != 'warnings':  # Pular warnings
                rows.append({'Property': key, 'Value': value})
        
        df = pd.DataFrame(rows)
        filename = f"ESL_{calc_type}_{model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Converter para CSV com metadados
        output = io.StringIO()
        output.write(f"# ESL Point Calculation Export\n")
        output.write(f"# Calculation Type: {calc_type}\n")
        output.write(f"# Model: {model}\n")
        output.write(f"# Components: {', '.join(components)}\n")
        output.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("#\n")
        
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# EXPORTAÇÃO - PDF
# =============================================================================

@bp.route('/export/pdf', methods=['POST'])
def export_esl_pdf():
    """
    Exporta diagrama ESL em PDF (usando reportlab).
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib.units import cm
        
        data = request.get_json() or {}
        diagram_type = data.get('diagram_type')
        diagram_data = data.get('data')
        components = data.get('components', [])
        model = data.get('model', 'Ideal')
        
        buffer = io.BytesIO()
        c = pdf_canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 18)
        c.drawString(2*cm, height - 2.5*cm, f"ESL Diagram - {diagram_type.upper()}")
        
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, height - 3.5*cm, f"Components: {', '.join(components)}")
        c.drawString(2*cm, height - 4.2*cm, f"Model: {model}")
        c.drawString(2*cm, height - 4.9*cm, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(2*cm, height - 5.6*cm, f"Reference: Prausnitz et al., Molecular Thermodynamics")
        
        # Linha divisória
        c.line(2*cm, height - 6*cm, width - 2*cm, height - 6*cm)
        
        # Dados resumidos
        y_pos = height - 7*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y_pos, "Summary:")
        y_pos -= 1*cm
        
        c.setFont("Helvetica", 10)
        
        if diagram_type == 'tx':
            x1_vals = diagram_data.get('x1', [])
            T_vals = diagram_data.get('T_liquidus_C', [])
            
            c.drawString(2*cm, y_pos, f"• Data points: {len(x1_vals)}")
            y_pos -= 0.6*cm
            
            if T_vals:
                c.drawString(2*cm, y_pos, f"• Temperature range: {min(T_vals):.2f} – {max(T_vals):.2f} °C")
                y_pos -= 0.6*cm
            
            if 'T_eutectic_C' in diagram_data:
                c.drawString(2*cm, y_pos, f"• Eutectic temperature: {diagram_data['T_eutectic_C']:.2f} °C")
                y_pos -= 0.6*cm
                c.drawString(2*cm, y_pos, f"• Eutectic composition: x₁ = {diagram_data['x_eutectic']:.4f}")
                y_pos -= 0.6*cm
            
            # Temperaturas de fusão
            if 'Tm1_C' in diagram_data:
                c.drawString(2*cm, y_pos, f"• Tm({components[0]}): {diagram_data['Tm1_C']:.2f} °C")
                y_pos -= 0.6*cm
            if 'Tm2_C' in diagram_data:
                c.drawString(2*cm, y_pos, f"• Tm({components[1]}): {diagram_data['Tm2_C']:.2f} °C")
                y_pos -= 0.6*cm
        
        elif diagram_type == 'ternary':
            points = diagram_data.get('points', [])
            c.drawString(2*cm, y_pos, f"• Calculated points: {len(points)}")
            y_pos -= 0.6*cm
            
            T_C = diagram_data.get('T_C')
            if T_C is not None:
                c.drawString(2*cm, y_pos, f"• Temperature: {T_C:.2f} °C ({T_C+273.15:.2f} K)")
                y_pos -= 0.6*cm
            
            # Contagem de fases
            liquid_count = sum(1 for p in points if p['phase'] == 'liquid')
            solid_liquid_count = len(points) - liquid_count
            
            c.drawString(2*cm, y_pos, f"• Liquid region points: {liquid_count} ({liquid_count/len(points)*100:.1f}%)")
            y_pos -= 0.6*cm
            c.drawString(2*cm, y_pos, f"• Solid-liquid region points: {solid_liquid_count} ({solid_liquid_count/len(points)*100:.1f}%)")
            y_pos -= 0.6*cm
        
        # Avisos termodinâmicos
        y_pos -= 1*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y_pos, "Thermodynamic Assumptions:")
        y_pos -= 0.7*cm
        
        c.setFont("Helvetica", 9)
        assumptions = [
            "• Pure solid phase (no solid solutions)",
            "• Low to moderate pressure (~1 atm)",
            "• Poynting correction neglected",
            "• ΔCp ≈ 0 (simplified equation) or complete equation used",
            "• Parameters from ELV data (may require adjustment for SLE)"
        ]
        
        for assumption in assumptions:
            c.drawString(2*cm, y_pos, assumption)
            y_pos -= 0.5*cm
        
        # Rodapé
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(2*cm, 2*cm, "Generated by Prausnitz ESL Calculator - Phase Equilibrium Platform")
        c.drawString(2*cm, 1.5*cm, "For educational and research purposes")
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        filename = f"ESL_{diagram_type}_{model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/export/point_pdf', methods=['POST'])
def export_esl_point_pdf():
    """
    Exporta resultados de cálculo pontual em PDF.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib.units import cm
        
        data = request.get_json() or {}
        calc_type = data.get('calc_type')
        components = data.get('components', [])
        model = data.get('model', 'Ideal')
        results = data.get('results', {})
        
        buffer = io.BytesIO()
        c = pdf_canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 18)
        title = "Solubility Calculation" if calc_type == 'solubility' else "Crystallization Temperature"
        c.drawString(2*cm, height - 2.5*cm, f"ESL - {title}")
        
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, height - 3.5*cm, f"Components: {', '.join(components)}")
        c.drawString(2*cm, height - 4.2*cm, f"Model: {model}")
        c.drawString(2*cm, height - 4.9*cm, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Linha divisória
        c.line(2*cm, height - 5.3*cm, width - 2*cm, height - 5.3*cm)
        
        # Resultados
        y_pos = height - 6.5*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y_pos, "Results:")
        y_pos -= 1*cm
        
        c.setFont("Courier", 10)
        for key, value in results.items():
            if key == 'warnings':
                continue
            
            if isinstance(value, (int, float)):
                line = f"{key:40s} = {value:.6f}"
            else:
                line = f"{key:40s} = {value}"
            
            c.drawString(2*cm, y_pos, line)
            y_pos -= 0.5*cm
            
            if y_pos < 3*cm:
                c.showPage()
                y_pos = height - 3*cm
        
        # Avisos
        if 'warnings' in results:
            y_pos -= 0.5*cm
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2*cm, y_pos, "Warnings:")
            y_pos -= 0.7*cm
            
            c.setFont("Helvetica", 9)
            for warning_key, warning_text in results['warnings'].items():
                c.drawString(2*cm, y_pos, f"• {warning_text}")
                y_pos -= 0.5*cm
        
        # Rodapé
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(2*cm, 2*cm, "Generated by Prausnitz ESL Calculator")
        c.drawString(2*cm, 1.5*cm, "Reference: Prausnitz et al., Molecular Thermodynamics of Fluid-Phase Equilibria, 3rd Ed.")
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        filename = f"ESL_{calc_type}_{model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# ADICIONAR ANTES DO FINAL DO ARQUIVO esl.py (antes dos error handlers)
# =============================================================================

@bp.route('/parameters/nrtl', methods=['POST'])
def get_nrtl_params():
    """
    Retorna parâmetros NRTL para um par binário.
    
    Request JSON:
        {
            "component1": "Naftaleno",
            "component2": "Benzeno"
        }
    
    Returns:
        JSON: Parâmetros NRTL (tau12, tau21, alpha, etc.)
    """
    try:
        if not HAS_ESL_DATA:
            return jsonify({
                'success': False,
                'error': 'Base de dados ESL não disponível'
            }), 500
        
        # Importar função específica
        from app.data.esl_data import get_nrtl_parameters
        
        data = request.get_json()
        comp1 = data.get('component1')
        comp2 = data.get('component2')
        
        if not comp1 or not comp2:
            return jsonify({
                'success': False,
                'error': 'Componentes não especificados'
            }), 400
        
        params = get_nrtl_parameters(comp1, comp2)
        
        if params is None:
            return jsonify({
                'success': False,
                'error': f'Parâmetros NRTL não disponíveis para {comp1} + {comp2}',
                'available': False
            })
        
        return jsonify({
            'success': True,
            'parameters': params,
            'available': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar parâmetros NRTL: {str(e)}',
            'details': str(e)
        }), 500


@bp.route('/parameters/uniquac', methods=['POST'])
def get_uniquac_params():
    """
    Retorna parâmetros UNIQUAC para um par binário.
    
    Request JSON:
        {
            "component1": "Naftaleno",
            "component2": "Benzeno"
        }
    
    Returns:
        JSON: Parâmetros UNIQUAC (u12, u21) + propriedades r, q
    """
    try:
        if not HAS_ESL_DATA:
            return jsonify({
                'success': False,
                'error': 'Base de dados ESL não disponível'
            }), 500
        
        # Importar funções específicas
        from app.data.esl_data import get_uniquac_parameters, get_uniquac_properties
        
        data = request.get_json()
        comp1 = data.get('component1')
        comp2 = data.get('component2')
        
        if not comp1 or not comp2:
            return jsonify({
                'success': False,
                'error': 'Componentes não especificados'
            }), 400
        
        # Buscar parâmetros de interação binária
        params = get_uniquac_parameters(comp1, comp2)
        
        # Buscar propriedades estruturais
        props1 = get_uniquac_properties(comp1)
        props2 = get_uniquac_properties(comp2)
        
        if params is None:
            return jsonify({
                'success': False,
                'error': f'Parâmetros UNIQUAC não disponíveis para {comp1} + {comp2}',
                'available': False
            })
        
        if props1 is None or props2 is None:
            return jsonify({
                'success': False,
                'error': f'Propriedades r/q não disponíveis para um dos componentes',
                'available': False
            })
        
        return jsonify({
            'success': True,
            'parameters': params,
            'properties': {
                comp1: props1,
                comp2: props2
            },
            'available': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar parâmetros UNIQUAC: {str(e)}',
            'details': str(e)
        }), 500


@bp.route('/parameters/unifac', methods=['POST'])
def get_unifac_params():
    """
    Retorna grupos funcionais UNIFAC e parâmetros de interação.
    
    Request JSON:
        {
            "components": ["Naftaleno", "Benzeno"]
        }
    
    Returns:
        JSON: Grupos funcionais de cada componente + matriz de interações
    """
    try:
        if not HAS_ESL_DATA:
            return jsonify({
                'success': False,
                'error': 'Base de dados ESL não disponível'
            }), 500
        
        # Importar funções e dados
        from app.data.esl_data import (
            get_unifac_groups,
            UNIFAC_GROUP_R_Q,
            UNIFAC_GROUP_INTERACTIONS
        )
        
        data = request.get_json()
        components = data.get('components', [])
        
        if not components:
            return jsonify({
                'success': False,
                'error': 'Componentes não especificados'
            }), 400
        
        result = {
            'success': True,
            'groups': {},
            'group_properties': {},
            'interactions': {},
            'available': True
        }
        
        # Buscar grupos de cada componente
        missing = []
        for comp in components:
            groups = get_unifac_groups(comp)
            if groups is None:
                missing.append(comp)
                result['available'] = False
            else:
                result['groups'][comp] = groups
        
        if missing:
            return jsonify({
                'success': False,
                'error': f'Grupos UNIFAC não disponíveis para: {", ".join(missing)}',
                'available': False
            })
        
        # Coletar todos os grupos únicos
        all_groups = set()
        for groups in result['groups'].values():
            all_groups.update(groups.keys())
        
        # Buscar propriedades R e Q dos grupos
        for group in all_groups:
            if group in UNIFAC_GROUP_R_Q:
                result['group_properties'][group] = UNIFAC_GROUP_R_Q[group]
        
        # Buscar parâmetros de interação entre grupos
        for g1 in all_groups:
            for g2 in all_groups:
                if g1 != g2:
                    key = (g1, g2)
                    reverse_key = (g2, g1)
                    
                    if key in UNIFAC_GROUP_INTERACTIONS:
                        result['interactions'][f"{g1}-{g2}"] = UNIFAC_GROUP_INTERACTIONS[key]
                    elif reverse_key in UNIFAC_GROUP_INTERACTIONS:
                        params = UNIFAC_GROUP_INTERACTIONS[reverse_key]
                        result['interactions'][f"{g1}-{g2}"] = {
                            'a12': params['a21'],
                            'a21': params['a12']
                        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar parâmetros UNIFAC: {str(e)}',
            'details': str(e)
        }), 500


@bp.route('/status', methods=['GET'])
def esl_status():
    """
    Retorna status da base de dados ESL.
    """
    try:
        if not HAS_ESL_DATA:
            return jsonify({
                'success': False,
                'error': 'Base de dados ESL não disponível'
            }), 500
        
        from app.data.esl_data import (
            ESL_DATA,
            NRTL_PARAMETERS,
            UNIQUAC_PARAMETERS,
            UNIQUAC_PURE_PROPERTIES,
            UNIFAC_GROUPS,
            UNIFAC_GROUP_INTERACTIONS
        )
        
        return jsonify({
            'success': True,
            'module': 'ESL - Equilíbrio Sólido-Líquido',
            'version': '2.1',
            'database': {
                'components': len(ESL_DATA),
                'nrtl_pairs': len(NRTL_PARAMETERS),
                'uniquac_pairs': len(UNIQUAC_PARAMETERS),
                'uniquac_components': len(UNIQUAC_PURE_PROPERTIES),
                'unifac_components': len(UNIFAC_GROUPS),
                'unifac_interactions': len(UNIFAC_GROUP_INTERACTIONS)
            },
            'models_available': ['Ideal', 'NRTL', 'UNIQUAC', 'UNIFAC']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao verificar status: {str(e)}'
        }), 500


# =============================================================================
# FIM DAS NOVAS ROTAS
# =============================================================================


# =============================================================================
# TRATAMENTO DE ERROS
# =============================================================================

@bp.errorhandler(404)
def not_found_error(error):
    """Handler para erros 404."""
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado',
        'available_endpoints': [
            '/esl/calculator',
            '/esl/components',
            '/esl/calculate/solubility',
            '/esl/calculate/crystallization',
            '/esl/diagram/tx',
            '/esl/diagram/ternary'
        ]
    }), 404


@bp.errorhandler(500)
def internal_error(error):
    """Handler para erros 500."""
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor',
        'message': str(error)
    }), 500

