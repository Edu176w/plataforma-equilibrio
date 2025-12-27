"""
app/routes/ell.py

Rotas Flask para o módulo ELL (Equilíbrio Líquido-Líquido)
VERSÃO 4.0 - Com extração multi-estágios (Kremser-Souders-Brown)

MUDANÇAS CRÍTICAS (v4.0):
=========================
- ✅ Novo endpoint: /ell/calculate/extraction (extração multi-estágios)
- ✅ Novo endpoint: /ell/calculate/extraction-fixed (N estágios fixos)
- ✅ Integração com log_ell_simulation() para Dashboard
- ✅ Suporte a Flask-Login (user_id)
- ✅ Logs de flash, diagrama ternário e extração
- ✅ Compatível com minimização de Gibbs

FUNDAMENTAÇÃO TEÓRICA:
======================
Baseado em:
    [1] Prausnitz et al. (1999), Chapter 12 & Appendix E
    [2] Michelsen (1982) - Stability analysis
    [3] Baker et al. (1982) - Gibbs energy minimization
    [4] Perry's Handbook, 8th Ed., Section 15 - Liquid-Liquid Extraction
        - Eq. 15-48 a 15-52: Kremser-Souders-Brown

ENDPOINTS DISPONÍVEIS:
======================
- GET  /ell                          -> Página da calculadora ELL
- POST /ell/calculate/flash          -> Flash isotérmico L1-L2
- POST /ell/calculate/extraction     -> Extração multi-estágios (Kremser) ⭐ NOVO
- POST /ell/calculate/extraction-fixed -> Extração com N estágios fixos ⭐ NOVO
- POST /ell/diagram/ternary          -> Diagrama ternário completo
- POST /ell/compare                  -> Comparação NRTL vs UNIQUAC
- POST /ell/export/csv               -> Exportar resultados CSV
- POST /ell/export/pdf               -> Exportar resultados PDF
- GET  /ell/api/components           -> Componentes disponíveis

Autor: Desenvolvido para TCC
Data: Dezembro 2024
Versão: 4.0 (Com extração multi-estágios)
"""

import time
import json
import numpy as np
from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import current_user, login_required
import io
import csv

# Importar funções de interface do novo calculator
# ADICIONAR ESSAS LINHAS após: from app.calculators.ell_calculator import ...
from app.calculators.ell_calculator import (
    calculate_ell_flash,
    generate_ternary_diagram_ell,
    ELLCalculator,
    # ⭐ ADICIONAR ESTAS 3 NOVAS FUNÇÕES:
    get_available_components_for_ell,
    get_available_models_for_components,
    check_ell_parameters_available
)


# Importar funções de dados
from app.data.ell_nrtl_params import (
    get_available_components_ell_nrtl,
    get_complete_ternary_systems as get_complete_nrtl
)
from app.data.ell_uniquac_params import (
    get_available_components_ell_uniquac,
    get_complete_ternary_systems as get_complete_uniquac
)

# Importar funções de AI
from app.utils.ai_ell import (
    log_ell_simulation,
    recommend_model_for_ell
)
HAS_AI = True

ell_bp = Blueprint('ell', __name__, url_prefix='/ell')

# ============================================================================
# FUNÇÕES AUXILIARES PARA CONVERSÃO DE TIPOS
# ============================================================================

def convert_to_python_native(obj):
    """
    Converte tipos NumPy para tipos nativos Python para serialização JSON
    
    Args:
        obj: Valor a ser convertido (pode ser NumPy type, list, dict, etc.)
    
    Returns:
        Valor convertido para tipo nativo Python
    """
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return [convert_to_python_native(item) for item in obj.tolist()]
    elif isinstance(obj, dict):
        return {key: convert_to_python_native(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_python_native(item) for item in obj]
    else:
        return obj

def safe_float(value, default=0.0):
    """Conversão segura para float nativo Python"""
    try:
        if isinstance(value, (np.floating, np.integer)):
            return float(value)
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False):
    """Conversão segura para bool nativo Python"""
    try:
        if isinstance(value, np.bool_):
            return bool(value)
        return bool(value)
    except (ValueError, TypeError):
        return default

def safe_array_to_list(arr):
    """Converte array NumPy para lista Python nativa"""
    if isinstance(arr, np.ndarray):
        return [safe_float(x) for x in arr]
    elif isinstance(arr, (list, tuple)):
        return [safe_float(x) for x in arr]
    else:
        return []

# ============================================
# DEFINIÇÃO DE PRESETS DE CASOS DE ESTUDO
# ============================================

CASE_PRESETS = {
    'water-butanol-acetone': {
        'id': 'water-butanol-acetone',
        'title': 'Água-1-Butanol-Acetona (Caso de Estudo)',
        'components': ['Water', '1-Butanol', 'Acetone'],
        'model': 'NRTL',
        'calc_type': 'ternary_diagram',
        'temperature': 25,
        'temperature_unit': 'C',
        'ntielines': 5
    },
    'water-chloroform-aceticacid': {
        'id': 'water-chloroform-aceticacid',
        'title': 'Água-Clorofórmio-Ácido Acético (Caso de Estudo)',
        'components': ['Water', 'Chloroform', 'Acetic Acid'],
        'model': 'UNIQUAC',
        'calc_type': 'ternary_diagram',
        'temperature': 25,
        'temperature_unit': 'C',
        'ntielines': 5
    },
    'water-toluene-aniline': {
        'id': 'water-toluene-aniline',
        'title': 'Água-Tolueno-Anilina (Caso de Estudo)',
        'components': ['Water', 'Toluene', 'Aniline'],
        'model': 'NRTL',
        'calc_type': 'ternary_diagram',
        'temperature': 25,
        'temperature_unit': 'C',
        'ntielines': 5
    }
}


# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================

@ell_bp.route('/', methods=['GET'])
@login_required
def ell_calculator():
    """
    Renderiza a página da calculadora ELL
    Suporta query parameters para carregar presets de casos de estudo
    
    Query params:
        preset: ID do caso de estudo (ex: 'water-butanol-acetone')
    
    Returns:
        Template renderizado com dados do preset (se aplicável)
    """
    # Verificar se há preset de caso de estudo
    preset_id = request.args.get('preset')
    preset_data = None
    
    if preset_id:
        if preset_id in CASE_PRESETS:
            preset_data = CASE_PRESETS[preset_id]
            print(f'[ELL] 📚 Carregando preset: {preset_id} - {preset_data["title"]}')
        else:
            print(f'[ELL] ⚠️  Preset não encontrado: {preset_id}')
    
    return render_template('ell_calculator.html', preset=preset_data)


# ✅ ADICIONE ESTA ROTA AQUI ✅
@ell_bp.route('/calculator', methods=['GET'])
@login_required
def ell_calculator_alt():
    """
    Rota alternativa /calculator - mantém compatibilidade com educational.js
    Redireciona para a mesma função principal
    
    Query params:
        preset: ID do caso de estudo (ex: 'water-butanol-acetone')
    
    Returns:
        Template renderizado com dados do preset (se aplicável)
    """
    preset_id = request.args.get('preset')
    preset_data = None
    
    if preset_id:
        if preset_id in CASE_PRESETS:
            preset_data = CASE_PRESETS[preset_id]
            print(f'[ELL] 📚 Carregando preset (via /calculator): {preset_id} - {preset_data["title"]}')
        else:
            print(f'[ELL] ⚠️  Preset não encontrado: {preset_id}')
    
    return render_template('ell_calculator.html', preset=preset_data)


# ============================================================================
# CÁLCULO: FLASH ISOTÉRMICO
# ============================================================================

@ell_bp.route('/calculate/flash', methods=['POST'])
def calculate_flash():
    """
    Flash isotérmico L1-L2 usando novo algoritmo de minimização de Gibbs
    
    Request JSON:
        {
            "components": ["Water", "1,1,2-Trichloroethane", "Acetone"],
            "z_feed": [0.3, 0.4, 0.3],
            "temperature": 25.0,
            "temperature_unit": "C",
            "model": "NRTL"
        }
    
    Response JSON:
        {
            "success": true,
            "results": {
                "converged": true,
                "two_phase": true,
                "beta": 0.636,
                "x_L1": [0.586, 0.132, 0.282],
                "x_L2": [0.137, 0.553, 0.310],
                "K": [4.26, 0.24, 0.91],
                "gamma_L1": [2.81, 1.86, 0.97],
                "gamma_L2": [11.93, 1.09, 1.20],
                "residual": 0.000123,
                "iterations": 119,
                "warning": null
            }
        }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        components = data.get('components', [])
        z_feed = data.get('z_feed', [])
        temperature = float(data.get('temperature', 25.0))
        temp_unit = data.get('temperature_unit', 'C')
        model = data.get('model', 'NRTL')
        
        # Converter temperatura para °C
        if temp_unit == 'K':
            temperature = temperature - 273.15
        elif temp_unit == 'F':
            temperature = (temperature - 32.0) * 5.0 / 9.0
        
        # Validar número de componentes
        if len(components) != 3:
            return jsonify({
                'success': False,
                'error': 'ELL requer exatamente 3 componentes'
            }), 400
        
        if len(z_feed) != 3:
            return jsonify({
                'success': False,
                'error': 'Composição global deve ter 3 valores'
            }), 400
        
        # Validar soma das composições
        z_sum = sum(z_feed)
        if abs(z_sum - 1.0) > 0.01:
            return jsonify({
                'success': False,
                'error': f'Soma das frações molares deve ser 1.0 (recebido: {z_sum:.4f})'
            }), 400
        
        # Executar cálculo usando NOVA função de interface
        print(f"\n{'='*70}")
        print(f"[ELL FLASH] Iniciando cálculo")
        print(f"  Componentes: {components}")
        print(f"  z_feed: {z_feed}")
        print(f"  Temperatura: {temperature}°C")
        print(f"  Modelo: {model}")
        print(f"{'='*70}\n")
        
        result = calculate_ell_flash(components, z_feed, temperature, model)
        
        if not result['success']:
            print(f"[ELL FLASH] ❌ Erro: {result.get('error')}")
            
            # Log do erro no banco
            if HAS_AI:
                try:
                    user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                    conditions_log = {
                        'z_feed': z_feed,
                        'temperature_C': temperature,
                        'temperature_unit': temp_unit
                    }
                    log_ell_simulation(
                        user_id=user_id,
                        calculation_type='flash',
                        model=model,
                        components=components,
                        conditions=conditions_log,
                        results={},
                        success=False,
                        error_message=result.get('error'),
                        start_time=start_time
                    )
                except Exception as log_err:
                    print(f"[ELL FLASH] ⚠️ Erro ao fazer log: {log_err}")
            
            return jsonify(result), 400
        
        # Extrair resultados
        res = result['results']
        
        # Log do resultado
        if res['two_phase']:
            print(f"\n{'='*70}")
            print(f"[ELL FLASH] ✅ SISTEMA BIFÁSICO")
            print(f"  Convergiu: {res['converged']}")
            print(f"  β = {res['beta']:.6f}")
            print(f"  x_L1 = {res['x_L1']}")
            print(f"  x_L2 = {res['x_L2']}")
            print(f"  Iterações: {res['iterations']}")
            print(f"{'='*70}\n")
        else:
            print(f"\n{'='*70}")
            print(f"[ELL FLASH] ⚠️ SISTEMA MONOFÁSICO")
            print(f"  {res.get('warning', 'Composição fora da região binodal')}")
            print(f"{'='*70}\n")
        
        # Converter para tipos Python nativos
        response_data = {
            'success': True,
            'results': convert_to_python_native(res),
            'ai_suggestion': convert_to_python_native(result.get('ai_suggestion'))
        }
        
        # ✅ LOG DA SIMULAÇÃO NO BANCO DE DADOS
        if HAS_AI:
            try:
                user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                conditions_log = {
                    'z_feed': z_feed,
                    'temperature_C': temperature,
                    'temperature_unit': temp_unit
                }
                log_ell_simulation(
                    user_id=user_id,
                    calculation_type='flash',
                    model=model,
                    components=components,
                    conditions=conditions_log,
                    results=res,
                    success=True,
                    error_message=None,
                    start_time=start_time
                )
            except Exception as log_err:
                print(f"[ELL FLASH] ⚠️ Erro ao fazer log: {log_err}")
        
        print(f"[ELL FLASH] ✅ Cálculo concluído em {time.time() - start_time:.2f}s")
        return jsonify(response_data)
        
    except ValueError as e:
        print(f"[ELL FLASH] ❌ Erro de validação: {str(e)}")
        
        # Log do erro
        if HAS_AI:
            try:
                user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                data = request.get_json()
                log_ell_simulation(
                    user_id=user_id,
                    calculation_type='flash',
                    model=data.get('model', 'NRTL'),
                    components=data.get('components', []),
                    conditions={'temperature': data.get('temperature'), 'z_feed': data.get('z_feed')},
                    results={},
                    success=False,
                    error_message=str(e),
                    start_time=start_time
                )
            except:
                pass
        
        return jsonify({
            'success': False,
            'error': f'Erro nos dados de entrada: {str(e)}'
        }), 400
    except Exception as e:
        print(f"[ELL FLASH] ❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Log do erro
        if HAS_AI:
            try:
                user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                data = request.get_json()
                log_ell_simulation(
                    user_id=user_id,
                    calculation_type='flash',
                    model=data.get('model', 'NRTL'),
                    components=data.get('components', []),
                    conditions={'temperature': data.get('temperature'), 'z_feed': data.get('z_feed')},
                    results={},
                    success=False,
                    error_message=str(e),
                    start_time=start_time
                )
            except:
                pass
        
        return jsonify({
            'success': False,
            'error': f'Erro no cálculo: {str(e)}'
        }), 500

# ============================================================================
# ⭐ NOVO: EXTRAÇÃO MULTI-ESTÁGIOS (KREMSER-SOUDERS-BROWN)
# ============================================================================

@ell_bp.route('/calculate/extraction', methods=['POST'])
def calculate_extraction():
    """
    Extração líquido-líquido multi-estágios usando equação de Kremser-Souders-Brown
    
    Referência: Perry's Handbook, 8th Ed., Section 15, Eq. 15-48 a 15-52
    
    Request JSON:
        {
            "components": ["Water", "Acetic Acid", "Ethyl Acetate"],
            "z_feed": [0.9, 0.1, 0.0],
            "temperature": 25.0,
            "temperature_unit": "C",
            "model": "NRTL",
            "S_F_ratio": 2.0,
            "target_recovery": 0.95,
            "efficiency": 0.7,
            "solute_index": 1
        }
    
    Response JSON:
        {
            "success": true,
            "results": {
                "converged": true,
                "N_theoretical": 4.23,
                "N_actual": 6.04,
                "N_rounded": 7,
                "extraction_factor": 2.45,
                "K_distribution": 1.225,
                "recovery_achieved": 0.95,
                "x_raffinate": [0.91, 0.005, 0.085],
                "x_extract": [0.05, 0.095, 0.855],
                "warnings": null
            }
        }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        components = data.get('components', [])
        z_feed = data.get('z_feed', [])
        temperature = float(data.get('temperature', 25.0))
        temp_unit = data.get('temperature_unit', 'C')
        model = data.get('model', 'NRTL')
        S_F_ratio = float(data.get('S_F_ratio', 2.0))
        target_recovery = float(data.get('target_recovery', 0.95))
        efficiency = float(data.get('efficiency', 1.0))
        solute_index = int(data.get('solute_index', 1))
        
        # Converter temperatura para °C
        if temp_unit == 'K':
            temperature = temperature - 273.15
        elif temp_unit == 'F':
            temperature = (temperature - 32.0) * 5.0 / 9.0
        
        # Validações
        if len(components) != 3:
            return jsonify({
                'success': False,
                'error': 'ELL requer exatamente 3 componentes'
            }), 400
        
        if len(z_feed) != 3:
            return jsonify({
                'success': False,
                'error': 'Composição global deve ter 3 valores'
            }), 400
        
        if not (0 < target_recovery < 1):
            return jsonify({
                'success': False,
                'error': f'Recuperação deve estar entre 0 e 1 (recebido: {target_recovery})'
            }), 400
        
        if not (0 < efficiency <= 1):
            return jsonify({
                'success': False,
                'error': f'Eficiência deve estar entre 0 e 1 (recebido: {efficiency})'
            }), 400
        
        if S_F_ratio <= 0:
            return jsonify({
                'success': False,
                'error': f'Razão S/F deve ser positiva (recebido: {S_F_ratio})'
            }), 400
        
        print(f"\n{'='*70}")
        print(f"[ELL EXTRAÇÃO] Iniciando cálculo de extração multi-estágios")
        print(f"  Componentes: {components}")
        print(f"  Soluto: {components[solute_index]}")
        print(f"  z_feed: {z_feed}")
        print(f"  Temperatura: {temperature}°C")
        print(f"  Modelo: {model}")
        print(f"  S/F: {S_F_ratio}")
        print(f"  Recuperação alvo: {target_recovery*100:.1f}%")
        print(f"  Eficiência: {efficiency*100:.0f}%")
        print(f"{'='*70}\n")
        
        # Criar calculadora ELL
        calc = ELLCalculator(
            components=components,
            temperature_C=temperature,
            model=model
        )
        
        # Executar cálculo de extração
        result = calc.calculate_multistage_extraction(
            z_feed=np.array(z_feed),
            S_F_ratio=S_F_ratio,
            target_recovery=target_recovery,
            efficiency=efficiency,
            solute_index=solute_index
        )
        
        if not result.get('converged', False):
            print(f"[ELL EXTRAÇÃO] ❌ Erro: {result.get('warning', 'Não convergiu')}")
            
            # Log do erro
            if HAS_AI:
                try:
                    user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                    conditions_log = {
                        'z_feed': z_feed,
                        'temperature_C': temperature,
                        'S_F_ratio': S_F_ratio,
                        'target_recovery': target_recovery,
                        'efficiency': efficiency,
                        'solute_index': solute_index
                    }
                    log_ell_simulation(
                        user_id=user_id,
                        calculation_type='extraction',
                        model=model,
                        components=components,
                        conditions=conditions_log,
                        results={},
                        success=False,
                        error_message=result.get('warning', 'Não convergiu'),
                        start_time=start_time
                    )
                except Exception as log_err:
                    print(f"[ELL EXTRAÇÃO] ⚠️ Erro ao fazer log: {log_err}")
            
            return jsonify({
                'success': False,
                'error': result.get('warning', 'Cálculo não convergiu')
            }), 400
        
        # Log do resultado
        print(f"\n{'='*70}")
        print(f"[ELL EXTRAÇÃO] ✅ CÁLCULO CONCLUÍDO")
        print(f"  N_teórico: {result['N_theoretical']:.2f} estágios")
        print(f"  N_real: {result['N_actual']:.2f} estágios")
        print(f"  N_arredondado: {result['N_rounded']} estágios")
        print(f"  Fator de extração: {result['extraction_factor']:.4f}")
        print(f"  Recuperação: {result['recovery_achieved']*100:.1f}%")
        print(f"{'='*70}\n")
        
        # Converter para tipos Python nativos
        response_data = {
            'success': True,
            'results': convert_to_python_native(result)
        }
        
        # ✅ LOG DA SIMULAÇÃO NO BANCO DE DADOS
        if HAS_AI:
            try:
                user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                conditions_log = {
                    'z_feed': z_feed,
                    'temperature_C': temperature,
                    'S_F_ratio': S_F_ratio,
                    'target_recovery': target_recovery,
                    'efficiency': efficiency,
                    'solute_index': solute_index
                }
                log_ell_simulation(
                    user_id=user_id,
                    calculation_type='extraction',
                    model=model,
                    components=components,
                    conditions=conditions_log,
                    results=result,
                    success=True,
                    error_message=None,
                    start_time=start_time
                )
            except Exception as log_err:
                print(f"[ELL EXTRAÇÃO] ⚠️ Erro ao fazer log: {log_err}")
        
        print(f"[ELL EXTRAÇÃO] ✅ Cálculo concluído em {time.time() - start_time:.2f}s")
        return jsonify(response_data)
        
    except ValueError as e:
        print(f"[ELL EXTRAÇÃO] ❌ Erro de validação: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro nos dados de entrada: {str(e)}'
        }), 400
    except Exception as e:
        print(f"[ELL EXTRAÇÃO] ❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro no cálculo: {str(e)}'
        }), 500

# ============================================================================
# ⭐ NOVO: EXTRAÇÃO COM NÚMERO FIXO DE ESTÁGIOS
# ============================================================================

@ell_bp.route('/calculate/extraction-fixed', methods=['POST'])
def calculate_extraction_fixed_stages():
    """
    Calcula recuperação alcançada com número FIXO de estágios
    
    Request JSON:
        {
            "components": ["Water", "Acetic Acid", "Ethyl Acetate"],
            "z_feed": [0.9, 0.1, 0.0],
            "temperature": 25.0,
            "model": "NRTL",
            "S_F_ratio": 2.0,
            "N_stages": 5,
            "efficiency": 0.7,
            "solute_index": 1
        }
    
    Response JSON:
        {
            "success": true,
            "results": {
                "converged": true,
                "N_stages": 5,
                "N_theoretical": 3.5,
                "extraction_factor": 2.45,
                "recovery_achieved": 0.92
            }
        }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        components = data.get('components', [])
        z_feed = data.get('z_feed', [])
        temperature = float(data.get('temperature', 25.0))
        temp_unit = data.get('temperature_unit', 'C')
        model = data.get('model', 'NRTL')
        S_F_ratio = float(data.get('S_F_ratio', 2.0))
        N_stages = int(data.get('N_stages', 5))
        efficiency = float(data.get('efficiency', 1.0))
        solute_index = int(data.get('solute_index', 1))
        
        # Converter temperatura
        if temp_unit == 'K':
            temperature = temperature - 273.15
        elif temp_unit == 'F':
            temperature = (temperature - 32.0) * 5.0 / 9.0
        
        print(f"\n[ELL EXTRAÇÃO-FIXED] {N_stages} estágios, S/F={S_F_ratio}, η={efficiency*100:.0f}%")
        
        # Criar calculadora
        calc = ELLCalculator(
            components=components,
            temperature_C=temperature,
            model=model
        )
        
        # Executar cálculo
        result = calc.calculate_extraction_with_fixed_stages(
            z_feed=np.array(z_feed),
            S_F_ratio=S_F_ratio,
            N_stages=N_stages,
            efficiency=efficiency,
            solute_index=solute_index
        )
        
        if not result.get('converged', False):
            return jsonify({
                'success': False,
                'error': result.get('warning', 'Não convergiu')
            }), 400
        
        print(f"[ELL EXTRAÇÃO-FIXED] ✅ Recuperação alcançada: {result['recovery_achieved']*100:.1f}%")
        
        response_data = {
            'success': True,
            'results': convert_to_python_native(result)
        }
        
        # Log
        if HAS_AI:
            try:
                user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                conditions_log = {
                    'z_feed': z_feed,
                    'temperature_C': temperature,
                    'S_F_ratio': S_F_ratio,
                    'N_stages': N_stages,
                    'efficiency': efficiency,
                    'solute_index': solute_index
                }
                log_ell_simulation(
                    user_id=user_id,
                    calculation_type='extraction_fixed',
                    model=model,
                    components=components,
                    conditions=conditions_log,
                    results=result,
                    success=True,
                    error_message=None,
                    start_time=start_time
                )
            except Exception as log_err:
                print(f"[ELL EXTRAÇÃO-FIXED] ⚠️ Erro ao fazer log: {log_err}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[ELL EXTRAÇÃO-FIXED] ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro no cálculo: {str(e)}'
        }), 500

# ============================================================================
# DIAGRAMA: TERNÁRIO COMPLETO (BINODAL + TIE-LINES)
# ============================================================================

@ell_bp.route('/diagram/ternary', methods=['POST'])
def generate_ternary_diagram():
    """
    Gera diagrama ternário completo com binodal e tie-lines
    
    Request JSON:
        {
            "components": ["Water", "1,1,2-Trichloroethane", "Acetone"],
            "temperature": 25.0,
            "temperature_unit": "C",
            "model": "NRTL",
            "n_tie_lines": 5
        }
    
    Response JSON:
        {
            "success": true,
            "results": {
                "T_C": 25.0,
                "T_K": 298.15,
                "model": "NRTL",
                "components": [...],
                "binodal_L1": [[x1, x2, x3], ...],
                "binodal_L2": [[x1, x2, x3], ...],
                "tie_lines": [{"x_L1": [...], "x_L2": [...], "beta": 0.5}, ...],
                "n_binodal_points": 16,
                "n_tie_lines": 5
            }
        }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        components = data.get('components', [])
        temperature = float(data.get('temperature', 25.0))
        temp_unit = data.get('temperature_unit', 'C')
        model = data.get('model', 'NRTL')
        n_tie_lines = int(data.get('n_tie_lines', 5))
        
        # Converter temperatura para °C
        if temp_unit == 'K':
            temperature = temperature - 273.15
        elif temp_unit == 'F':
            temperature = (temperature - 32.0) * 5.0 / 9.0
        
        # Validar número de componentes
        if len(components) != 3:
            return jsonify({
                'success': False,
                'error': 'ELL requer exatamente 3 componentes'
            }), 400
        
        print(f"\n{'='*70}")
        print(f"[ELL DIAGRAMA] Gerando diagrama ternário")
        print(f"  Componentes: {components}")
        print(f"  Temperatura: {temperature}°C")
        print(f"  Modelo: {model}")
        print(f"  n_tie_lines: {n_tie_lines}")
        print(f"{'='*70}\n")
        
        # Executar cálculo usando NOVA função de interface
        result = generate_ternary_diagram_ell(
            components=components,
            temperature_C=temperature,
            model=model,
            n_tie_lines=n_tie_lines
        )
        
        if not result['success']:
            print(f"[ELL DIAGRAMA] ❌ Erro: {result.get('error')}")
            
            # Log do erro
            if HAS_AI:
                try:
                    user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                    conditions_log = {
                        'temperature_C': temperature,
                        'temperature_unit': temp_unit,
                        'n_tie_lines': n_tie_lines
                    }
                    log_ell_simulation(
                        user_id=user_id,
                        calculation_type='ternary',
                        model=model,
                        components=components,
                        conditions=conditions_log,
                        results={},
                        success=False,
                        error_message=result.get('error'),
                        start_time=start_time
                    )
                except Exception as log_err:
                    print(f"[ELL DIAGRAMA] ⚠️ Erro ao fazer log: {log_err}")
            
            return jsonify(result), 400
        
        # Log do resultado
        res = result['results']
        print(f"\n{'='*70}")
        print(f"[ELL DIAGRAMA] ✅ DIAGRAMA GERADO")
        print(f"  Binodal: {res['n_binodal_points']} pontos")
        print(f"  Tie-lines: {res['n_tie_lines']} linhas")
        print(f"{'='*70}\n")
        
        # Converter para tipos Python nativos
        response_data = {
            'success': True,
            'results': convert_to_python_native(res),
            'ai_suggestion': convert_to_python_native(result.get('ai_suggestion'))
        }
        
        # ✅ LOG DA SIMULAÇÃO NO BANCO DE DADOS
        if HAS_AI:
            try:
                user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                conditions_log = {
                    'temperature_C': temperature,
                    'temperature_unit': temp_unit,
                    'n_tie_lines': n_tie_lines
                }
                log_ell_simulation(
                    user_id=user_id,
                    calculation_type='ternary',
                    model=model,
                    components=components,
                    conditions=conditions_log,
                    results={
                        'n_binodal_points': res['n_binodal_points'],
                        'n_tie_lines': res['n_tie_lines'],
                        'binodal_L1': res.get('binodal_L1', []),
                        'binodal_L2': res.get('binodal_L2', []),
                        'tie_lines': res.get('tie_lines', [])
                    },
                    success=True,
                    error_message=None,
                    start_time=start_time
                )
            except Exception as log_err:
                print(f"[ELL DIAGRAMA] ⚠️ Erro ao fazer log: {log_err}")
        
        print(f"[ELL DIAGRAMA] ✅ Diagrama gerado em {time.time() - start_time:.2f}s")
        return jsonify(response_data)
        
    except ValueError as e:
        print(f"[ELL DIAGRAMA] ❌ Erro de validação: {str(e)}")
        
        # Log do erro
        if HAS_AI:
            try:
                user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                data = request.get_json()
                log_ell_simulation(
                    user_id=user_id,
                    calculation_type='ternary',
                    model=data.get('model', 'NRTL'),
                    components=data.get('components', []),
                    conditions={'temperature': data.get('temperature')},
                    results={},
                    success=False,
                    error_message=str(e),
                    start_time=start_time
                )
            except:
                pass
        
        return jsonify({
            'success': False,
            'error': f'Erro nos dados de entrada: {str(e)}'
        }), 400
    except Exception as e:
        print(f"[ELL DIAGRAMA] ❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Log do erro
        if HAS_AI:
            try:
                user_id = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
                data = request.get_json()
                log_ell_simulation(
                    user_id=user_id,
                    calculation_type='ternary',
                    model=data.get('model', 'NRTL'),
                    components=data.get('components', []),
                    conditions={'temperature': data.get('temperature')},
                    results={},
                    success=False,
                    error_message=str(e),
                    start_time=start_time
                )
            except:
                pass
        
        return jsonify({
            'success': False,
            'error': f'Erro ao gerar diagrama: {str(e)}'
        }), 500

# ============================================================================
# COMPARAÇÃO DE MODELOS
# ============================================================================

@ell_bp.route('/compare', methods=['POST'])
def compare_models():
    """
    Compara resultados entre NRTL e UNIQUAC
    """
    try:
        data = request.get_json()
        
        components = data.get('components', [])
        z_feed = data.get('z_feed', [])
        temperature = float(data.get('temperature', 25.0))
        temp_unit = data.get('temperature_unit', 'C')
        
        # Converter temperatura para °C
        if temp_unit == 'K':
            temperature = temperature - 273.15
        elif temp_unit == 'F':
            temperature = (temperature - 32.0) * 5.0 / 9.0
        
        print(f"\n{'='*70}")
        print(f"[ELL COMPARAÇÃO] Comparando NRTL vs UNIQUAC")
        print(f"  Componentes: {components}")
        print(f"  z_feed: {z_feed}")
        print(f"  Temperatura: {temperature}°C")
        print(f"{'='*70}\n")
        
        results = {}
        
        # Calcular com NRTL
        try:
            print("[ELL COMPARAÇÃO] Calculando com NRTL...")
            result_nrtl = calculate_ell_flash(components, z_feed, temperature, 'NRTL')
            if result_nrtl['success']:
                results['NRTL'] = convert_to_python_native(result_nrtl['results'])
                print(f"[ELL COMPARAÇÃO] ✅ NRTL: β={results['NRTL']['beta']:.4f}")
            else:
                results['NRTL'] = {'error': result_nrtl.get('error')}
                print(f"[ELL COMPARAÇÃO] ❌ NRTL: {results['NRTL']['error']}")
        except Exception as e:
            results['NRTL'] = {'error': str(e)}
            print(f"[ELL COMPARAÇÃO] ❌ NRTL exception: {str(e)}")
        
        # Calcular com UNIQUAC
        try:
            print("[ELL COMPARAÇÃO] Calculando com UNIQUAC...")
            result_uniquac = calculate_ell_flash(components, z_feed, temperature, 'UNIQUAC')
            if result_uniquac['success']:
                results['UNIQUAC'] = convert_to_python_native(result_uniquac['results'])
                print(f"[ELL COMPARAÇÃO] ✅ UNIQUAC: β={results['UNIQUAC']['beta']:.4f}")
            else:
                results['UNIQUAC'] = {'error': result_uniquac.get('error')}
                print(f"[ELL COMPARAÇÃO] ❌ UNIQUAC: {results['UNIQUAC']['error']}")
        except Exception as e:
            results['UNIQUAC'] = {'error': str(e)}
            print(f"[ELL COMPARAÇÃO] ❌ UNIQUAC exception: {str(e)}")
        
        # Análise comparativa
        comparison = {}
        if ('error' not in results.get('NRTL', {}) and 
            'error' not in results.get('UNIQUAC', {})):
            
            nrtl = results['NRTL']
            uniquac = results['UNIQUAC']
            
            comparison['beta_difference'] = abs(nrtl['beta'] - uniquac['beta'])
            comparison['both_two_phase'] = (nrtl['two_phase'] and uniquac['two_phase'])
            
            if comparison['both_two_phase']:
                x_L1_nrtl = np.array(nrtl['x_L1'])
                x_L1_uniquac = np.array(uniquac['x_L1'])
                x_L2_nrtl = np.array(nrtl['x_L2'])
                x_L2_uniquac = np.array(uniquac['x_L2'])
                
                comparison['composition_difference_L1'] = float(np.linalg.norm(x_L1_nrtl - x_L1_uniquac))
                comparison['composition_difference_L2'] = float(np.linalg.norm(x_L2_nrtl - x_L2_uniquac))
        
        print(f"[ELL COMPARAÇÃO] ✅ Comparação concluída\n")
        
        return jsonify({
            'success': True,
            'results': results,
            'comparison': comparison
        })
        
    except Exception as e:
        print(f"[ELL COMPARAÇÃO] ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro na comparação: {str(e)}'
        }), 500

# ============================================================================
# EXPORTAÇÃO: CSV
# ============================================================================

@ell_bp.route('/export/csv', methods=['POST'])
def export_csv():
    """Exporta resultados em formato CSV"""
    try:
        data = request.get_json()
        
        diagram_type = data.get('diagram_type', 'flash')
        components = data.get('components', [])
        model = data.get('model', 'NRTL')
        temperature = data.get('temperature', 25.0)
        results_data = data.get('data', {})
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['# Equilíbrio Líquido-Líquido (ELL)'])
        writer.writerow(['# Componentes:', ', '.join(components)])
        writer.writerow(['# Modelo:', model])
        writer.writerow(['# Temperatura (°C):', temperature])
        writer.writerow(['# Baseado em: Prausnitz et al., Appendix E'])
        writer.writerow([])
        
        if diagram_type == 'flash':
            # Exportar flash
            writer.writerow(['# FLASH ISOTÉRMICO L1-L2'])
            writer.writerow([])
            writer.writerow(['Propriedade', 'Valor'])
            writer.writerow(['Fração L2 (β)', results_data.get('beta')])
            writer.writerow(['Bifásico', results_data.get('two_phase')])
            writer.writerow(['Convergiu', results_data.get('converged')])
            writer.writerow([])
            
            writer.writerow(['Componente', 'z_feed', 'x_L1', 'x_L2', 'K', 'γ_L1', 'γ_L2'])
            for i, comp in enumerate(components):
                writer.writerow([
                    comp,
                    results_data.get('z_feed', [None]*3)[i],
                    results_data.get('x_L1', [None]*3)[i],
                    results_data.get('x_L2', [None]*3)[i],
                    results_data.get('K', [None]*3)[i],
                    results_data.get('gamma_L1', [None]*3)[i],
                    results_data.get('gamma_L2', [None]*3)[i]
                ])
        
        elif diagram_type == 'ternary':
            # Exportar binodal
            writer.writerow(['# CURVA BINODAL - FASE L1'])
            writer.writerow([f'x_{components[0]}', f'x_{components[1]}', f'x_{components[2]}'])
            for point in results_data.get('binodal_L1', []):
                writer.writerow(point)
            
            writer.writerow([])
            writer.writerow(['# CURVA BINODAL - FASE L2'])
            writer.writerow([f'x_{components[0]}', f'x_{components[1]}', f'x_{components[2]}'])
            for point in results_data.get('binodal_L2', []):
                writer.writerow(point)
            
            writer.writerow([])
            writer.writerow(['# TIE-LINES'])
            for idx, tie_line in enumerate(results_data.get('tie_lines', [])):
                writer.writerow([])
                writer.writerow([f'# Tie-line {idx+1}'])
                writer.writerow(['Fase', f'x_{components[0]}', f'x_{components[1]}', f'x_{components[2]}'])
                writer.writerow(['L1'] + tie_line['x_L1'])
                writer.writerow(['L2'] + tie_line['x_L2'])
        
        elif diagram_type == 'extraction':
            # Exportar extração
            writer.writerow(['# EXTRAÇÃO MULTI-ESTÁGIOS'])
            writer.writerow([])
            writer.writerow(['Propriedade', 'Valor'])
            writer.writerow(['Estágios teóricos', results_data.get('N_theoretical')])
            writer.writerow(['Estágios reais', results_data.get('N_actual')])
            writer.writerow(['Estágios arredondados', results_data.get('N_rounded')])
            writer.writerow(['Fator de extração (E)', results_data.get('extraction_factor')])
            writer.writerow(['Coef. distribuição (K)', results_data.get('K_distribution')])
            writer.writerow(['Recuperação alcançada', results_data.get('recovery_achieved')])
            writer.writerow([])
            
            writer.writerow(['Componente', 'x_feed', 'x_raffinate', 'x_extract'])
            for i, comp in enumerate(components):
                writer.writerow([
                    comp,
                    results_data.get('x_feed', [None]*3)[i],
                    results_data.get('x_raffinate', [None]*3)[i],
                    results_data.get('x_extract', [None]*3)[i]
                ])
        
        # Preparar download
        output.seek(0)
        bytes_output = io.BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        
        filename = f'ell_{diagram_type}_{model}_{temperature}C.csv'
        
        return send_file(
            bytes_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"[ELL EXPORT] ❌ Erro: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro ao exportar CSV: {str(e)}'
        }), 500


# ============================================================================
# EXPORTAÇÃO: PDF
# ============================================================================

@ell_bp.route('/export/pdf', methods=['POST'])
def export_pdf():
    """
    Exporta resultados em PDF profissional com gráficos, tabelas e fundamentação teórica
    
    Requer: pip install reportlab matplotlib pillow numpy
    
    Request JSON:
        {
            "diagram_type": "flash|ternary|extraction|extraction_fixed",
            "components": ["Water", "1,1,2-Trichloroethane", "Acetone"],
            "model": "NRTL",
            "temperature": 25.0,
            "results": {...},
            "include_equations": true,
            "include_methodology": true
        }
    
    Response: PDF binary file
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
            PageBreak, Image, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
        from datetime import datetime
        import io
        
        data = request.get_json()
        
        diagram_type = data.get('diagram_type', 'flash')
        components = data.get('components', [])
        model = data.get('model', 'NRTL')
        temperature = float(data.get('temperature', 25.0))
        results = data.get('results', {})
        include_equations = data.get('include_equations', True)
        include_methodology = data.get('include_methodology', True)
        
        print(f"\n{'='*70}")
        print(f"[ELL PDF] Gerando relatório PDF")
        print(f"  Tipo: {diagram_type}")
        print(f"  Componentes: {components}")
        print(f"  Modelo: {model}")
        print(f"  Temperatura: {temperature}°C")
        print(f"{'='*70}\n")
        
        # Criar PDF em memória
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=0.8*inch,
            leftMargin=0.8*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
            title=f"ELL Analysis - {diagram_type.upper()}",
            author="UFAL - ResTIC16",
            subject="Liquid-Liquid Equilibrium Calculation"
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#003366'),
            borderWidth=1,
            borderPadding=4
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=12
        )
        
        # Conteúdo
        story = []
        
        # ============ PÁGINA 1: CAPA E RESUMO ============
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            f"ANÁLISE DE EQUILÍBRIO LÍQUIDO-LÍQUIDO (ELL)",
            title_style
        ))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"Cálculo: {diagram_type.upper()}",
            styles['Heading2']
        ))
        story.append(Spacer(1, 0.5*inch))
        
        # Resumo executivo
        story.append(Paragraph("RESUMO EXECUTIVO", heading2_style))
        
        summary_text = f"""
        <b>Componentes:</b> {', '.join(components)}<br/>
        <b>Modelo Termodinâmico:</b> {model}<br/>
        <b>Temperatura:</b> {temperature}°C ({temperature + 273.15:.2f} K)<br/>
        <b>Data do Cálculo:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>
        <b>Instituição:</b> UFAL - Universidade Federal de Alagoas<br/>
        <b>Grupo:</b> ResTIC16 - Thermodynamic Engineering<br/>
        """
        
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # ============ DADOS CALCULADOS ============
        
        story.append(Paragraph("RESULTADOS PRINCIPAIS", heading2_style))
        
        # ========================================================================
        # SEÇÃO: FLASH
        # ========================================================================
        if diagram_type == 'flash':
            results_data = [
                ['Propriedade', 'Valor'],
                ['Convergência', 'Sim ✓' if results.get('converged') else 'Não ✗'],
                ['Sistema Bifásico', 'Sim ✓' if results.get('two_phase') else 'Não ✗'],
                ['Fração Molar de L2 (β)', f"{results.get('beta', 0):.6f}"],
                ['Resíduo Final', f"{results.get('residual', 0):.2e}"],
                ['Iterações Necessárias', f"{results.get('iterations', 0)}"]
            ]
            
            story.append(Spacer(1, 0.15*inch))
            table = Table(results_data, colWidths=[2.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            story.append(table)
            
            # Composições detalhadas
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("COMPOSIÇÕES DETALHADAS", heading2_style))
            
            comp_data = [['Componente', 'z_feed', 'x_L1', 'x_L2', 'K']]
            for i, comp in enumerate(components):
                comp_data.append([
                    comp,
                    f"{results.get('z_feed', [0]*3)[i]:.4f}",
                    f"{results.get('x_L1', [0]*3)[i]:.4f}",
                    f"{results.get('x_L2', [0]*3)[i]:.4f}",
                    f"{results.get('K', [0]*3)[i]:.4f}"
                ])
            
            comp_table = Table(comp_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            story.append(comp_table)
            
            # Coeficientes de atividade
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("COEFICIENTES DE ATIVIDADE", heading2_style))
            
            gamma_data = [['Componente', 'γ_L1', 'γ_L2', 'Razão (γ_L1/γ_L2)']]
            for i, comp in enumerate(components):
                gamma_L1 = results.get('gamma_L1', [1]*3)[i]
                gamma_L2 = results.get('gamma_L2', [1]*3)[i]
                ratio = gamma_L1 / gamma_L2 if gamma_L2 != 0 else 0
                gamma_data.append([
                    comp,
                    f"{gamma_L1:.4f}",
                    f"{gamma_L2:.4f}",
                    f"{ratio:.4f}"
                ])
            
            gamma_table = Table(gamma_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.6*inch])
            gamma_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            story.append(gamma_table)
        
        # ========================================================================
        # SEÇÃO: TERNÁRIO (COMPLETA)
        # ========================================================================
        elif diagram_type == 'ternary':
            binodal_L1 = results.get('binodal_L1', [])
            binodal_L2 = results.get('binodal_L2', [])
            tie_lines = results.get('tie_lines', [])
            n_binodal = results.get('n_binodal_points', len(binodal_L1))
            n_tie_lines = results.get('n_tie_lines', len(tie_lines))
            
            # Resumo executivo
            ternary_summary = f"""
            <b>Pontos na Curva Binodal:</b> {n_binodal}<br/>
            <b>Tie-lines Geradas:</b> {n_tie_lines}<br/>
            <b>Temperatura:</b> {temperature}°C ({temperature + 273.15:.2f} K)<br/>
            <b>Modelo:</b> {model}<br/>
            """
            story.append(Paragraph(ternary_summary, body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # ============ TABELA: CURVA BINODAL ============
            
            story.append(Paragraph("CURVA BINODAL (PRIMEIROS 10 PONTOS)", heading2_style))
            
            binodal_all = binodal_L1 if len(binodal_L1) > 0 else binodal_L2
            binodal_display = binodal_all[:10]
            
            binodal_table_data = [['#', components[0], components[1], components[2]]]
            for i, point in enumerate(binodal_display, 1):
                if isinstance(point, (list, tuple)) and len(point) >= 3:
                    binodal_table_data.append([
                        str(i),
                        f"{float(point[0]):.4f}",
                        f"{float(point[1]):.4f}",
                        f"{float(point[2]):.4f}"
                    ])
            
            binodal_table = Table(binodal_table_data, colWidths=[0.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            binodal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            story.append(binodal_table)
            
            if len(binodal_all) > 10:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(
                    f"<i>... e mais {len(binodal_all) - 10} pontos (exportar CSV para dados completos)</i>",
                    body_style
                ))
            
            # ============ TABELA: TIE-LINES ============
            
            if len(tie_lines) > 0:
                story.append(Spacer(1, 0.3*inch))
                story.append(Paragraph("TIE-LINES (LINHAS DE EQUILÍBRIO)", heading2_style))
                
                tie_table_data = [['#', 'Fase', components[0], components[1], components[2], 'β', 'Distância']]
                
                for i, tie in enumerate(tie_lines, 1):
                    x_L1 = tie.get('x_L1', [0, 0, 0])
                    x_L2 = tie.get('x_L2', [0, 0, 0])
                    beta = tie.get('beta', 0.5)
                    distance = tie.get('distance', 0.0)
                    
                    # Linha L1
                    tie_table_data.append([
                        str(i),
                        'L1',
                        f"{float(x_L1[0]):.4f}",
                        f"{float(x_L1[1]):.4f}",
                        f"{float(x_L1[2]):.4f}",
                        f"{1-beta:.3f}",
                        f"{distance:.3f}"
                    ])
                    
                    # Linha L2
                    tie_table_data.append([
                        '',
                        'L2',
                        f"{float(x_L2[0]):.4f}",
                        f"{float(x_L2[1]):.4f}",
                        f"{float(x_L2[2]):.4f}",
                        f"{beta:.3f}",
                        ''
                    ])
                
                tie_table = Table(tie_table_data, colWidths=[0.3*inch, 0.5*inch, 1*inch, 1*inch, 1*inch, 0.6*inch, 0.8*inch])
                tie_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
                ]))
                story.append(tie_table)
            
            # ============ GRÁFICO TERNÁRIO ============
            
            story.append(PageBreak())
            story.append(Paragraph("DIAGRAMA TERNÁRIO", heading2_style))
            
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                from matplotlib.patches import Polygon
                import tempfile
                import numpy as np
                
                fig, ax = plt.subplots(figsize=(8, 7))
                
                # Triângulo de referência
                triangle = Polygon([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]], 
                                  fill=False, edgecolor='gray', linewidth=2, linestyle='--')
                ax.add_patch(triangle)
                
                # Função para converter coordenadas ternárias
                def ternary_to_cartesian(x1, x2, x3):
                    x = x2 + 0.5 * x3
                    y = (np.sqrt(3) / 2) * x3
                    return x, y
                
                # Plotar binodal
                binodal_all = binodal_L1 + binodal_L2
                if len(binodal_all) > 0:
                    x_coords = []
                    y_coords = []
                    for point in binodal_all:
                        if isinstance(point, (list, tuple)) and len(point) >= 3:
                            x, y = ternary_to_cartesian(float(point[0]), float(point[1]), float(point[2]))
                            x_coords.append(x)
                            y_coords.append(y)
                    
                    if len(x_coords) > 0:
                        ax.plot(x_coords, y_coords, 'b-', linewidth=2.5, label='Binodal', zorder=2)
                        ax.scatter(x_coords, y_coords, c='dodgerblue', s=40, zorder=3, edgecolors='navy', linewidths=0.5)
                
                # Plotar tie-lines
                if len(tie_lines) > 0:
                    for idx, tie in enumerate(tie_lines):
                        x_L1 = tie.get('x_L1', [0, 0, 0])
                        x_L2 = tie.get('x_L2', [0, 0, 0])
                        
                        x1, y1 = ternary_to_cartesian(float(x_L1[0]), float(x_L1[1]), float(x_L1[2]))
                        x2, y2 = ternary_to_cartesian(float(x_L2[0]), float(x_L2[1]), float(x_L2[2]))
                        
                        label = 'Tie-lines' if idx == 0 else None
                        ax.plot([x1, x2], [y1, y2], 'r--', linewidth=1.5, alpha=0.8, label=label, zorder=1)
                        ax.scatter([x1, x2], [y1, y2], c='red', s=60, marker='o', zorder=4, edgecolors='darkred', linewidths=1)
                
                # Rótulos dos vértices
                offset = 0.08
                ax.text(-offset, -offset, components[0], fontsize=13, fontweight='bold', ha='right', va='top')
                ax.text(1+offset, -offset, components[1], fontsize=13, fontweight='bold', ha='left', va='top')
                ax.text(0.5, np.sqrt(3)/2 + offset, components[2], fontsize=13, fontweight='bold', ha='center', va='bottom')
                
                ax.set_xlim(-0.15, 1.15)
                ax.set_ylim(-0.15, np.sqrt(3)/2 + 0.15)
                ax.set_aspect('equal')
                ax.axis('off')
                ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
                ax.set_title(f'Diagrama Ternário - {model} - {temperature}°C', 
                           fontsize=15, fontweight='bold', pad=20)
                
                # Salvar em arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    plt.savefig(tmp.name, dpi=150, bbox_inches='tight', facecolor='white')
                    plt.close()
                    
                    # Adicionar ao PDF
                    img = Image(tmp.name, width=6*inch, height=5.5*inch)
                    story.append(img)
                    
                    # Remover arquivo temporário
                    import os
                    os.unlink(tmp.name)
                
                print("[ELL PDF] ✅ Gráfico ternário adicionado ao PDF")
                
            except Exception as e:
                print(f"[ELL PDF] ⚠️ Erro ao gerar gráfico: {str(e)}")
                import traceback
                traceback.print_exc()
                story.append(Paragraph(
                    f"<i>⚠️ Não foi possível gerar o gráfico: {str(e)}</i>",
                    body_style
                ))
        
        # ========================================================================
        # SEÇÃO: EXTRAÇÃO
        # ========================================================================
        elif diagram_type in ['extraction', 'extraction_fixed']:
            extraction_data = [
                ['Parâmetro', 'Valor'],
                ['Soluto', components[results.get('solute_index', 1)] if results.get('solute_index', 1) < len(components) else 'N/A'],
                ['Razão S/F', f"{results.get('S_F_ratio', 0):.2f}"],
                ['N° Estágios (Teórico)', f"{results.get('N_theoretical', 0):.2f}"],
                ['N° Estágios (Real)', f"{results.get('N_actual', 0):.2f}"],
                ['N° Estágios (Arredondado)', f"{results.get('N_rounded', 0)}"],
                ['Fator de Extração', f"{results.get('extraction_factor', 0):.4f}"],
                ['Recuperação Alcançada', f"{results.get('recovery_achieved', 0)*100:.2f}%"],
                ['Eficiência da Coluna', f"{results.get('efficiency', 1)*100:.0f}%"]
            ]
            
            story.append(Spacer(1, 0.15*inch))
            table = Table(extraction_data, colWidths=[2.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            story.append(table)
        
        # ========================================================================
        # FUNDAMENTAÇÃO TEÓRICA
        # ========================================================================
        
        if include_methodology:
            story.append(PageBreak())
            story.append(Paragraph("FUNDAMENTAÇÃO TEÓRICA", heading2_style))
            
            if diagram_type == 'flash':
                theory_text = """
                <b>FLASH ISOTÉRMICO LÍQUIDO-LÍQUIDO (ELL)</b><br/><br/>
                
                O cálculo de flash L1-L2 determina se uma mistura em condições dadas irá separar 
                em duas fases líquidas imiscíveis e suas respectivas composições.<br/><br/>
                
                <b>Critério de Estabilidade (Michelsen, 1982):</b><br/>
                Uma mistura é estável (monofásica) se e somente se a matriz Hessiana da energia 
                de Gibbs for positiva definida em todas as direções.<br/><br/>
                
                <b>Minimização de Energia de Gibbs:</b><br/>
                Para sistemas bifásicos, resolve-se:<br/>
                <i>min G = n<sup>L1</sup>·g<sup>L1</sup> + n<sup>L2</sup>·g<sup>L2</sup></i><br/>
                Sujeito a:<br/>
                - Balanço material: Σx<sup>L1</sup> = Σx<sup>L2</sup> = 1<br/>
                - Restrição: β ∈ [0, 1] (fração molar de L2)<br/><br/>
                
                <b>Equações de Equilíbrio:</b><br/>
                μ<sub>i</sub><sup>L1</sup> = μ<sub>i</sub><sup>L2</sup>  ∀i<br/>
                Ou equivalentemente:<br/>
                <i>γ<sub>i</sub><sup>L1</sup> · x<sub>i</sub><sup>L1</sup> = γ<sub>i</sub><sup>L2</sup> · x<sub>i</sub><sup>L2</sup></i><br/><br/>
                
                <b>Modelos Termodinâmicos:</b><br/>
                """
                
                if model == 'NRTL':
                    theory_text += """
                    <b>NRTL (Non-Random Two-Liquid):</b> [Renon & Prausnitz, 1968]<br/>
                    Validade: -20°C a 200°C<br/>
                    Aplicável para: Diversos pares de solventes, alcoóis + hidrocarbonetos, 
                    água + solventes orgânicos<br/>
                    Parâmetros: τ<sub>ij</sub>, τ<sub>ji</sub>, α<sub>ij</sub><br/>
                    """
                elif model == 'UNIQUAC':
                    theory_text += """
                    <b>UNIQUAC (UNIquac Quasichemical):</b> [Abrams & Prausnitz, 1975]<br/>
                    Validade: -20°C a 150°C<br/>
                    Aplicável para: Sistemas polares e apolares, em especial com água<br/>
                    Parâmetros: τ<sub>ij</sub>, τ<sub>ji</sub> (energias de interação)<br/>
                    """
                
                theory_text += """
                <br/><b>Referências:</b><br/>
                [1] Prausnitz, J.M., Lichtenthaler, R.N., & de Azevedo, E.G. (1999). 
                    <i>Molecular Thermodynamics of Fluid-Phase Equilibria</i>. 3rd ed., Prentice Hall.<br/>
                [2] Michelsen, M.L. (1982). The isothermal flash problem. Part I. Stability. 
                    <i>Fluid Phase Equilibria</i>, 9, 1-19.<br/>
                [3] Baker, L.E., Pierce, A.C., & Luks, K.D. (1982). Gibbs energy analysis of phase equilibria. 
                    <i>Soc. Pet. Eng. J.</i>, 22, 731-742.
                """
                
                story.append(Paragraph(theory_text, body_style))
            
            elif diagram_type == 'ternary':
                theory_text = """
                <b>DIAGRAMA TERNÁRIO LÍQUIDO-LÍQUIDO (ELL)</b><br/><br/>
                
                O diagrama ternário representa o equilíbrio líquido-líquido de sistemas com três componentes,
                mostrando a curva binodal (limite da região bifásica) e as tie-lines (linhas de equilíbrio).<br/><br/>
                
                <b>Curva Binodal:</b><br/>
                Delimita a região onde o sistema é instável e se separa em duas fases líquidas. 
                Composições fora da binodal são estáveis (monofásicas). Composições dentro da binodal 
                são bifásicas.<br/><br/>
                
                <b>Tie-lines (Linhas de Equilíbrio):</b><br/>
                Conectam as composições das duas fases líquidas em equilíbrio (L1 e L2) a uma dada temperatura. 
                A regra da alavanca determina as quantidades relativas de cada fase.<br/><br/>
                
                <b>Algoritmo de Geração da Binodal:</b><br/>
                1. Varredura de composições no diagrama ternário<br/>
                2. Teste de estabilidade (TPD - Tangent Plane Distance)<br/>
                3. Flash L1-L2 para pontos instáveis<br/>
                4. Convex Hull ou setores radiais para extrair borda<br/>
                5. Ordenação nearest-neighbor (TSP greedy)<br/><br/>
                
                <b>Referências:</b><br/>
                [1] Prausnitz et al. (1999). Molecular Thermodynamics. 3rd ed., Cap. 11.<br/>
                [2] Michelsen, M.L. & Mollerup, J.M. (2007). Thermodynamic Models: Fundamentals & Computational Aspects.<br/>
                [3] Sørensen, J.M. & Arlt, W. (1980). Liquid-Liquid Equilibrium Data Collection. DECHEMA.
                """
                
                story.append(Paragraph(theory_text, body_style))
            
            elif diagram_type in ['extraction', 'extraction_fixed']:
                theory_text = """
                <b>EXTRAÇÃO LÍQUIDO-LÍQUIDO MULTI-ESTÁGIOS</b><br/><br/>
                
                <b>Equação de Kremser-Souders-Brown:</b> [Perry's Handbook, 8th Ed., Section 15]<br/>
                Define o número teórico de estágios ideais necessários para alcançar uma determinada 
                recuperação do soluto em processo de extração em contracorrente.<br/><br/>
                
                <b>Fator de Extração (E):</b><br/>
                <i>E = K · (S/F)</i><br/>
                Onde:<br/>
                - K = coeficiente de distribuição do soluto = [x<sub>s</sub><sup>L2</sup>]/[x<sub>s</sub><sup>L1</sup>]<br/>
                - S = vazão molar de solvente (L2)<br/>
                - F = vazão molar de alimentação (L1)<br/><br/>
                
                <b>Número de Estágios Teóricos (N<sub>t</sub>):</b><br/>
                Para E ≠ 1:<br/>
                <i>N<sub>t</sub> = ln[(1-R)·(1-E) + E] / ln(E)</i><br/>
                Onde: R = recuperação do soluto (fração)<br/><br/>
                
                Para E = 1 (caso limite):<br/>
                <i>N<sub>t</sub> = R / (1-R)</i><br/><br/>
                
                <b>Número de Estágios Reais (N<sub>real</sub>):</b><br/>
                <i>N<sub>real</sub> = N<sub>t</sub> / η</i><br/>
                Onde: η = eficiência de Murphree ou eficiência global (0 < η ≤ 1)<br/><br/>
                
                <b>Recuperação Alcançada:</b><br/>
                <i>R = 1 - [(1-E)^(N<sub>real</sub>)] / (E-1)</i><br/><br/>
                
                <b>Condições de Operação:</b><br/>
                - Razão S/F: Tipicamente 1-5 (quanto maior, melhor a extração, maior custo)<br/>
                - Eficiência: 50-90% (escada teórica vs real)<br/>
                - Contracorrente: padrão industrial (maior eficiência que cocorrente)<br/><br/>
                
                <b>Referência:</b><br/>
                Perry's Chemical Engineers' Handbook (8th Edition). McGraw-Hill, Section 15: 
                Liquid-Liquid Extraction, Equations 15-48 to 15-52.
                """
                
                story.append(Paragraph(theory_text, body_style))
        
        # ========================================================================
        # EQUAÇÕES
        # ========================================================================
        
        if include_equations:
            story.append(PageBreak())
            story.append(Paragraph("EQUAÇÕES FUNDAMENTAIS", heading2_style))
            
            equations_text = """
            <b>1. EQUILÍBRIO TERMODINÂMICO</b><br/>
            μ<sub>i</sub><sup>L1</sup> = μ<sub>i</sub><sup>L2</sup>  →  
            γ<sub>i</sub><sup>L1</sup>·x<sub>i</sub><sup>L1</sup> = γ<sub>i</sub><sup>L2</sup>·x<sub>i</sub><sup>L2</sup><br/><br/>
            
            <b>2. RESTRIÇÕES DE BALANÇO</b><br/>
            Σ<sub>i</sub> x<sub>i</sub><sup>L1</sup> = 1,  Σ<sub>i</sub> x<sub>i</sub><sup>L2</sup> = 1<br/>
            β·x<sub>i</sub><sup>L2</sup> + (1-β)·x<sub>i</sub><sup>L1</sup> = z<sub>i</sub><br/><br/>
            
            <b>3. ENERGIA DE GIBBS (Residual)</b><br/>
            G<sup>R</sup> = Σ<sub>i</sub> n<sub>i</sub>·[RT·ln(γ<sub>i</sub>) + (Δh<sub>i</sub> - h<sub>i,ideal</sub>)]<br/><br/>
            
            <b>4. MODELO NRTL</b><br/>
            ln γ<sub>i</sub> = x<sub>j</sub>² · [τ<sub>ji</sub>·G<sub>ji</sub> / (x<sub>i</sub> + x<sub>j</sub>·G<sub>ji</sub>)² + 
            τ<sub>ij</sub>·G<sub>ij</sub> / (x<sub>j</sub> + x<sub>i</sub>·G<sub>ij</sub>)²]<br/>
            τ<sub>ij</sub> = A<sub>ij</sub> / T,  G<sub>ij</sub> = exp(-α<sub>ij</sub>·τ<sub>ij</sub>)<br/><br/>
            
            <b>5. CRITÉRIO DE ESTABILIDADE (Tangente)</b><br/>
            ∇<sup>2</sup>G > 0  ∀ direções  →  Sistema estável<br/>
            ∃ direção com ∇<sup>2</sup>G < 0  →  Sistema instável (bifásico)<br/><br/>
            
            <b>6. COEFICIENTE DE DISTRIBUIÇÃO</b><br/>
            K<sub>i</sub> = x<sub>i</sub><sup>L2</sup> / x<sub>i</sub><sup>L1</sup><br/><br/>
            
            <b>7. FATOR DE EXTRAÇÃO (KREMSER)</b><br/>
            E = K·(S/F),  com R = 1 - [(1-E)^N] / (E-1) se E ≠ 1<br/><br/>
            """
            
            story.append(Paragraph(equations_text, body_style))
        
        # ========================================================================
        # RODAPÉ
        # ========================================================================
        
        story.append(PageBreak())
        story.append(Paragraph("INFORMAÇÕES DO CÁLCULO", heading2_style))
        
        footer_text = f"""
        <b>Sistema Calculado:</b> {', '.join(components)}<br/>
        <b>Temperatura:</b> {temperature}°C ({temperature + 273.15:.2f} K)<br/>
        <b>Modelo Termodinâmico:</b> {model}<br/>
        <b>Tipo de Cálculo:</b> {diagram_type.upper()}<br/>
        <b>Data/Hora:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>
        <b>Plataforma:</b> Thermodynamic Equilibrium Calculator v4.0<br/>
        <b>Instituição:</b> UFAL - Universidade Federal de Alagoas<br/>
        <b>Grupo de Pesquisa:</b> ResTIC16 - Thermodynamic Engineering Group<br/><br/>
        
        <b>Base de Dados Utilizada:</b><br/>
        - NRTL Parameters: Prausnitz et al. (1999), Appendix E<br/>
        - UNIQUAC Parameters: Abrams & Prausnitz (1975)<br/>
        - Extraction Theory: Perry's Handbook, 8th Ed., Section 15<br/><br/>
        
        <b>Validação e Precisão:</b><br/>
        - Testes de convergência automáticos ✓<br/>
        - Verificação de estabilidade termodinâmica ✓<br/>
        - Minimização de Gibbs com tolerância 1e-8 ✓<br/>
        - Critério de parada: residual < 1e-10 ou 1000 iterações<br/><br/>
        
        <i>Este documento foi gerado automaticamente. 
        Consulte as referências para validação de precisão em aplicações críticas.</i>
        """
        
        story.append(Paragraph(footer_text, body_style))
        
        # ========================================================================
        # CONSTRUIR PDF
        # ========================================================================
        
        doc.build(story)
        pdf_buffer.seek(0)
        
        filename = f'ell_{diagram_type}_{model}_{temperature}C_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        print(f"[ELL PDF] ✅ PDF gerado com sucesso: {filename}")
        print(f"{'='*70}\n")
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except ImportError as e:
        print(f"[ELL PDF] ❌ Dependência faltante: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Dependência faltante. Instale com: pip install reportlab matplotlib pillow numpy',
            'details': str(e)
        }), 501
    except Exception as e:
        print(f"[ELL PDF] ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro ao gerar PDF: {str(e)}'
        }), 500



# ============================================================================
# API: COMPONENTES DISPONÍVEIS
# ============================================================================

# ============================================================================
# API: COMPONENTES DISPONÍVEIS (VERSÃO 2.0 - COM FILTRO POR TIPO DE CÁLCULO)
# ============================================================================

@ell_bp.route('/api/components', methods=['GET'])
def get_available_components():
    """
    Retorna componentes disponíveis para ELL

    VERSÃO 2.0: Suporte a filtros por calc_type

    Query params:
        ?model=NRTL ou ?model=UNIQUAC ou ?model=UNIFAC  (obrigatório)
        ?calc_type=extraction          (opcional - filtra apenas componentes com parâmetros)

    Examples:
        GET /ell/api/components?model=NRTL
        GET /ell/api/components?model=UNIQUAC&calc_type=extraction
        GET /ell/api/components?model=UNIFAC
    """
    try:
        model = request.args.get('model', 'NRTL')
        calc_type = request.args.get('calc_type', None)  # ⭐ NOVO

        print(f"[ELL API] Solicitação de componentes: model={model}, calc_type={calc_type}")

        # ====================================================================
        # CASO 1: Extração (filtrar apenas componentes com parâmetros)
        # ====================================================================
        if calc_type == 'extraction':
            print(f"[ELL API] 🔍 Filtrando componentes para EXTRAÇÃO")

            # Usar função nova do ell_calculator.py
            components = get_available_components_for_ell(model)

            # Obter sistemas completos
            if model == 'NRTL':
                complete_systems = get_complete_nrtl()
            elif model == 'UNIQUAC':
                complete_systems = get_complete_uniquac()
            elif model == 'UNIFAC':
                complete_systems = []  # ✅ UNIFAC não tem sistemas pré-definidos
            else:
                return jsonify({
                    'success': False,
                    'error': f'Modelo {model} não suportado'
                }), 400

        # ====================================================================
        # CASO 2: Flash / Diagrama (componentes padrão)
        # ====================================================================
        else:
            if model == 'NRTL':
                components = get_available_components_ell_nrtl()
                complete_systems = get_complete_nrtl()
            elif model == 'UNIQUAC':
                components = get_available_components_ell_uniquac()
                complete_systems = get_complete_uniquac()
            elif model == 'UNIFAC':
                # ✅ UNIFAC PREDITIVO - Carregar componentes disponíveis
                components = get_available_components_for_ell('UNIFAC')
                complete_systems = []  # UNIFAC não tem sistemas pré-definidos
            else:
                return jsonify({
                    'success': False,
                    'error': f'Modelo {model} não suportado'
                }), 400

        # Converter para tipos Python nativos
        components = convert_to_python_native(components)
        complete_systems = convert_to_python_native(complete_systems)

        print(f"[ELL API] ✅ Retornando {len(components)} componentes para {model} (calc_type={calc_type})")

        return jsonify({
            'success': True,
            'model': model,
            'calc_type': calc_type,
            'components': components,
            'complete_systems': complete_systems,
            'count': len(components)
        })

    except Exception as e:
        print(f"[ELL API] ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro ao obter componentes: {str(e)}'
        }), 500


# ============================================================================
# ⭐ NOVA ROTA: VERIFICAR MODELOS DISPONÍVEIS PARA COMPONENTES SELECIONADOS
# ============================================================================

@ell_bp.route('/api/models/available', methods=['POST'])
def check_models_available():
    """
    Verifica quais modelos (NRTL, UNIQUAC) têm parâmetros disponíveis
    para os 3 componentes selecionados.
    
    Request JSON:
        {
            "components": ["Water", "1,1,2-Trichloroethane", "Acetone"]
        }
    
    Response JSON:
        {
            "success": true,
            "components": ["Water", "1,1,2-Trichloroethane", "Acetone"],
            "available_models": ["NRTL"],
            "details": {
                "NRTL": {
                    "available": true,
                    "message": "✅ Parâmetros NRTL disponíveis...",
                    "reference": "Prausnitz Table E-5, Bender & Block (1975)"
                },
                "UNIQUAC": {
                    "available": false,
                    "message": "❌ Parâmetros UNIQUAC não encontrados..."
                }
            }
        }
    
    Example:
        POST /ell/api/models/available
        Body: {"components": ["Water", "1,1,2-Trichloroethane", "Acetone"]}
    """
    try:
        data = request.get_json()
        components = data.get('components', [])
        
        # Validar entrada
        if len(components) != 3:
            return jsonify({
                'success': False,
                'error': 'São necessários exatamente 3 componentes',
                'received': len(components)
            }), 400
        
        print(f"[ELL API] 🔍 Verificando modelos disponíveis para: {components}")
        
        # Usar função do ell_calculator.py
        available_models = get_available_models_for_components(components)
        
        # Obter detalhes de cada modelo
        details = {}
        
        for model in ['NRTL', 'UNIQUAC']:
            result = check_ell_parameters_available(components, model, 25.0)
            details[model] = {
                'available': result.get('available', False),
                'message': result.get('message', 'Não verificado'),
                'reference': result.get('reference', None),
                'temperature_warning': result.get('temperature_warning', None)
            }
        
        print(f"[ELL API] ✅ Modelos disponíveis: {available_models}")
        
        return jsonify({
            'success': True,
            'components': components,
            'available_models': available_models,
            'details': details
        })
        
    except Exception as e:
        print(f"[ELL API] ❌ Erro ao verificar modelos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erro ao verificar modelos disponíveis: {str(e)}'
        }), 500
