from flask import Blueprint, request, jsonify, render_template, redirect, url_for, send_file, make_response
from app.calculators.elv_calculator import ELVCalculator
from app.utils.ai_elv import log_elv_simulation, recommend_model_for_elv
from flask_login import current_user, login_required  # ✅ ADICIONAR login_required
import pandas as pd
import io
import time
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

bp = Blueprint('elv', __name__, url_prefix='/elv')

# ============================================
# DEFINIÇÃO DE PRESETS DE CASOS DE ESTUDO
# ============================================

CASE_PRESETS = {
    'ethanol-water': {
        'id': 'ethanol-water',
        'title': 'Etanol-Água (Caso de Estudo)',
        'components': ['Ethanol', 'Water'],
        'model': 'NRTL',
        'calc_type': 'txy',
        'pressure': 101.325,
        'pressure_unit': 'kPa',
        'composition': 0.5
    },
    'benzene-toluene': {
        'id': 'benzene-toluene',
        'title': 'Benzeno-Tolueno (Caso de Estudo)',
        'components': ['Benzene', 'Toluene'],
        'model': 'Ideal',
        'calc_type': 'txy',
        'pressure': 101.325,
        'pressure_unit': 'kPa',
        'composition': 0.5
    },
    'acetone-water': {
        'id': 'acetone-water',
        'title': 'Acetona-Água (Caso de Estudo)',
        'components': ['Acetone', 'Water'],
        'model': 'NRTL',
        'calc_type': 'txy',
        'pressure': 101.325,
        'pressure_unit': 'kPa',
        'composition': 0.5
    },
    'methanol-benzene': {
        'id': 'methanol-benzene',
        'title': 'Metanol-Benzeno (Caso de Estudo)',
        'components': ['Methanol', 'Benzene'],
        'model': 'NRTL',
        'calc_type': 'txy',
        'pressure': 101.325,
        'pressure_unit': 'kPa',
        'composition': 0.395
    }
}

@bp.route('/')
def index():
    return redirect(url_for('elv.calculator'))

@bp.route('/calculator')
@login_required  # ✅ ADICIONAR ESTA LINHA
def calculator():
    """
    Renderiza a página do calculador ELV
    Suporta query parameters para carregar presets de casos de estudo
    
    Query params:
        preset: ID do caso de estudo (ex: 'ethanol-water')
    
    Returns:
        Template renderizado com dados do preset (se aplicável)
    """
    # Verificar se há preset de caso de estudo
    preset_id = request.args.get('preset')
    preset_data = None
    
    if preset_id:
        if preset_id in CASE_PRESETS:
            preset_data = CASE_PRESETS[preset_id]
            print(f'[ELV] 📚 Carregando preset: {preset_id} - {preset_data["title"]}')
        else:
            print(f'[ELV] ⚠️  Preset não encontrado: {preset_id}')
    
    return render_template('elv_calculator.html', preset=preset_data)

# [RESTO DO CÓDIGO PERMANECE IGUAL]



# ============================================================================
# ==================== CÁLCULOS PONTUAIS =====================================
# ============================================================================

@bp.route('/calculate/bubble', methods=['POST'])
def calculate_bubble_point():
    start_time = time.time()
    try:
        data = request.get_json()

        components = data['components']
        x = data['compositions']
        model = data.get('model', 'Ideal')

        temp_value = data['temperature']
        temp_unit = data.get('temperature_unit', 'C')
        if temp_unit == 'K':
            temperature_C = temp_value - 273.15
        else:
            temperature_C = temp_value

        calc = ELVCalculator()
        results = calc.bubble_point(components, temperature_C, x, model)

        # IA: sugestão de modelo para este sistema / tipo de cálculo
        ai_suggestion = recommend_model_for_elv(components, 'bubble')

        # Log da simulação
        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'temperature_C': temperature_C,
            'temperature_unit': temp_unit,
            'compositions': x,
        }
        log_elv_simulation(
            user_id=user_id,
            calculation_type='bubble',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )

        return jsonify({'success': True, 'results': results, 'calc_type': 'bubble', 'ai_suggestion': ai_suggestion})

    except Exception as e:
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'temperature': data.get('temperature'),
                'temperature_unit': data.get('temperature_unit', 'C'),
                'compositions': data.get('compositions', []),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_elv_simulation(
                user_id=user_id,
                calculation_type='bubble',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except Exception:
            pass

        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/calculate/bubble_t', methods=['POST'])
def calculate_bubble_temperature():
    start_time = time.time()
    try:
        data = request.get_json()

        components = data['components']
        x = data['compositions']
        model = data.get('model', 'Ideal')

        press_value = data['pressure']
        press_unit = data.get('pressure_unit', 'kPa')

        if press_unit == 'Pa':
            pressure_kPa = press_value / 1000
        elif press_unit == 'bar':
            pressure_kPa = press_value * 100
        elif press_unit == 'atm':
            pressure_kPa = press_value * 101.325
        else:
            pressure_kPa = press_value

        calc = ELVCalculator()
        results = calc.bubble_temperature(components, pressure_kPa, x, model)

        ai_suggestion = recommend_model_for_elv(components, 'bubble_t')

        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'pressure_kPa': pressure_kPa,
            'pressure_unit': press_unit,
            'compositions': x,
        }
        log_elv_simulation(
            user_id=user_id,
            calculation_type='bubble_t',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )

        return jsonify({'success': True, 'results': results, 'calc_type': 'bubble_t', 'ai_suggestion': ai_suggestion})

    except Exception as e:
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'pressure': data.get('pressure'),
                'pressure_unit': data.get('pressure_unit', 'kPa'),
                'compositions': data.get('compositions', []),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_elv_simulation(
                user_id=user_id,
                calculation_type='bubble_t',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except Exception:
            pass

        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/calculate/dew', methods=['POST'])
def calculate_dew_point():
    start_time = time.time()
    try:
        data = request.get_json()

        components = data['components']
        y = data['compositions']
        model = data.get('model', 'Ideal')

        temp_value = data['temperature']
        temp_unit = data.get('temperature_unit', 'C')
        if temp_unit == 'K':
            temperature_C = temp_value - 273.15
        else:
            temperature_C = temp_value

        calc = ELVCalculator()
        results = calc.dew_point(components, temperature_C, y, model)

        # adicionar Psat
        from thermo.chemical import Chemical
        T = temperature_C + 273.15
        for i, comp in enumerate(components):
            chem = Chemical(comp)
            P_sat = chem.VaporPressure(T)
            results[f'P{i+1}_sat (kPa)'] = round(P_sat / 1000, 2)

        ai_suggestion = recommend_model_for_elv(components, 'dew')

        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'temperature_C': temperature_C,
            'temperature_unit': temp_unit,
            'compositions': y,
        }
        log_elv_simulation(
            user_id=user_id,
            calculation_type='dew',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )

        return jsonify({'success': True, 'results': results, 'calc_type': 'dew', 'ai_suggestion': ai_suggestion})

    except Exception as e:
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'temperature': data.get('temperature'),
                'temperature_unit': data.get('temperature_unit', 'C'),
                'compositions': data.get('compositions', []),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_elv_simulation(
                user_id=user_id,
                calculation_type='dew',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except Exception:
            pass

        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/calculate/dew_t', methods=['POST'])
def calculate_dew_temperature():
    start_time = time.time()
    try:
        data = request.get_json()

        components = data['components']
        y = data['compositions']
        model = data.get('model', 'Ideal')

        press_value = data['pressure']
        press_unit = data.get('pressure_unit', 'kPa')

        if press_unit == 'Pa':
            pressure_kPa = press_value / 1000
        elif press_unit == 'bar':
            pressure_kPa = press_value * 100
        elif press_unit == 'atm':
            pressure_kPa = press_value * 101.325
        else:
            pressure_kPa = press_value

        calc = ELVCalculator()
        results = calc.dew_temperature(components, pressure_kPa, y, model)

        from thermo.chemical import Chemical
        T_K = results['T (K)']
        for i, comp in enumerate(components):
            chem = Chemical(comp)
            P_sat = chem.VaporPressure(T_K)
            results[f'P{i+1}_sat (kPa)'] = round(P_sat / 1000, 2)

        ai_suggestion = recommend_model_for_elv(components, 'dew_t')

        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'pressure_kPa': pressure_kPa,
            'pressure_unit': press_unit,
            'compositions': y,
        }
        log_elv_simulation(
            user_id=user_id,
            calculation_type='dew_t',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )

        return jsonify({'success': True, 'results': results, 'calc_type': 'dew_t', 'ai_suggestion': ai_suggestion})

    except Exception as e:
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'pressure': data.get('pressure'),
                'pressure_unit': data.get('pressure_unit', 'kPa'),
                'compositions': data.get('compositions', []),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_elv_simulation(
                user_id=user_id,
                calculation_type='dew_t',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except Exception:
            pass

        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/calculate/flash', methods=['POST'])
def calculate_flash():
    start_time = time.time()
    try:
        data = request.get_json()

        components = data['components']
        z = data['compositions']
        model = data.get('model', 'Ideal')

        temp_value = data['temperature']
        temp_unit = data.get('temperature_unit', 'C')
        if temp_unit == 'K':
            temperature_C = temp_value - 273.15
        else:
            temperature_C = temp_value

        press_value = data['pressure']
        press_unit = data.get('pressure_unit', 'kPa')

        if press_unit == 'Pa':
            pressure_kPa = press_value / 1000
        elif press_unit == 'bar':
            pressure_kPa = press_value * 100
        elif press_unit == 'atm':
            pressure_kPa = press_value * 101.325
        else:
            pressure_kPa = press_value

        calc = ELVCalculator()
        results = calc.flash_calculation(components, temperature_C, pressure_kPa, z, model)

        from thermo.chemical import Chemical
        T = temperature_C + 273.15
        for i, comp in enumerate(components):
            chem = Chemical(comp)
            P_sat = chem.VaporPressure(T)
            results[f'P{i+1}_sat (kPa)'] = round(P_sat / 1000, 2)

        ai_suggestion = recommend_model_for_elv(components, 'flash')

        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'temperature_C': temperature_C,
            'temperature_unit': temp_unit,
            'pressure_kPa': pressure_kPa,
            'pressure_unit': press_unit,
            'compositions': z,
        }
        log_elv_simulation(
            user_id=user_id,
            calculation_type='flash',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )

        return jsonify({'success': True, 'results': results, 'calc_type': 'flash', 'ai_suggestion': ai_suggestion})

    except Exception as e:
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'temperature': data.get('temperature'),
                'temperature_unit': data.get('temperature_unit', 'C'),
                'pressure': data.get('pressure'),
                'pressure_unit': data.get('pressure_unit', 'kPa'),
                'compositions': data.get('compositions', []),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_elv_simulation(
                user_id=user_id,
                calculation_type='flash',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except Exception:
            pass

        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ==================== DIAGRAMAS BINÁRIOS ====================================
# ============================================================================

@bp.route('/diagram/pxy', methods=['POST'])
def generate_pxy_diagram():
    start_time = time.time()
    try:
        data = request.get_json()

        components = data['components']
        model = data.get('model', 'Ideal')

        temp_value = data['temperature']
        temp_unit = data.get('temperature_unit', 'C')
        if temp_unit == 'K':
            temperature_C = temp_value - 273.15
        else:
            temperature_C = temp_value

        calc = ELVCalculator()
        results = calc.generate_pxy_diagram(components, temperature_C, model)

        ai_suggestion = recommend_model_for_elv(components, 'pxy')

        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'temperature_C': temperature_C,
            'temperature_unit': temp_unit,
        }
        log_elv_simulation(
            user_id=user_id,
            calculation_type='pxy',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )

        return jsonify({'success': True, 'results': results, 'ai_suggestion': ai_suggestion})

    except Exception as e:
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'temperature': data.get('temperature'),
                'temperature_unit': data.get('temperature_unit', 'C'),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_elv_simulation(
                user_id=user_id,
                calculation_type='pxy',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except Exception:
            pass

        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/diagram/txy', methods=['POST'])
def generate_txy_diagram():
    start_time = time.time()
    try:
        data = request.get_json()

        components = data['components']
        model = data.get('model', 'Ideal')

        press_value = data['pressure']
        press_unit = data.get('pressure_unit', 'kPa')

        if press_unit == 'Pa':
            pressure_kPa = press_value / 1000
        elif press_unit == 'bar':
            pressure_kPa = press_value * 100
        elif press_unit == 'atm':
            pressure_kPa = press_value * 101.325
        else:
            pressure_kPa = press_value

        calc = ELVCalculator()
        results = calc.generate_txy_diagram(components, pressure_kPa, model)

        ai_suggestion = recommend_model_for_elv(components, 'txy')

        user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
        conditions = {
            'pressure_kPa': pressure_kPa,
            'pressure_unit': press_unit,
        }
        log_elv_simulation(
            user_id=user_id,
            calculation_type='txy',
            model=model,
            components=components,
            conditions=conditions,
            results=results,
            success=True,
            error_message=None,
            start_time=start_time,
        )

        return jsonify({'success': True, 'results': results, 'ai_suggestion': ai_suggestion})

    except Exception as e:
        try:
            data = request.get_json() or {}
            components = data.get('components', [])
            model = data.get('model', 'Ideal')
            conditions = {
                'pressure': data.get('pressure'),
                'pressure_unit': data.get('pressure_unit', 'kPa'),
            }
            user_id = current_user.id if getattr(current_user, 'is_authenticated', False) else None
            log_elv_simulation(
                user_id=user_id,
                calculation_type='txy',
                model=model,
                components=components,
                conditions=conditions,
                results={},
                success=False,
                error_message=str(e),
                start_time=start_time,
            )
        except Exception:
            pass

        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ==================== EXPORTAÇÃO CSV/PDF DIAGRAMAS ==========================
# ============================================================================

@bp.route('/export/csv', methods=['POST'])
def export_csv():
    """Exportar dados do diagrama T-x-y ou P-x-y para CSV"""
    try:
        data = request.get_json()

        diagram_type = data.get('diagram_type', 'txy')
        components = data.get('components', [])
        model = data.get('model', 'Ideal')
        diagram_data = data.get('data', {})

        if diagram_type == 'txy':
            df_bubble = pd.DataFrame({
                f'x1 ({components[0]})': diagram_data.get('x_bubble', []),
                'T_bubble (°C)': diagram_data.get('T_bubble', []),
                f'y1 ({components[0]})': diagram_data.get('y_bubble', []),
            })

            df_dew = pd.DataFrame({
                f'y1 ({components[0]})': diagram_data.get('y_dew', []),
                'T_dew (°C)': diagram_data.get('T_dew', []),
                f'x1 ({components[0]})': diagram_data.get('x_dew', []),
            })

            df = pd.concat(
                [df_bubble.add_prefix('Bubble_'), df_dew.add_prefix('Dew_')],
                axis=1,
            )

            pressure_kPa = data.get('pressure', 101.325)
            filename = f"TXY_{components[0]}_{components[1]}_{model}_{pressure_kPa}kPa.csv"

        else:
            df_bubble = pd.DataFrame({
                f'x1 ({components[0]})': diagram_data.get('x_bubble', []),
                'P_bubble (kPa)': diagram_data.get('P_bubble', []),
                f'y1 ({components[0]})': diagram_data.get('y_bubble', []),
            })

            df_dew = pd.DataFrame({
                f'y1 ({components[0]})': diagram_data.get('y_dew', []),
                'P_dew (kPa)': diagram_data.get('P_dew', []),
                f'x1 ({components[0]})': diagram_data.get('x_dew', []),
            })

            df = pd.concat(
                [df_bubble.add_prefix('Bubble_'), df_dew.add_prefix('Dew_')],
                axis=1,
            )

            temperature_C = data.get('temperature', 60)
            filename = f"PXY_{components[0]}_{components[1]}_{model}_{temperature_C}C.csv"

        metadata = (
            f"# Plataforma Termodinâmica - Módulo ELV\n"
            f"# Data de exportação: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# Componentes: {components[0]} (1) + {components[1]} (2)\n"
            f"# Modelo termodinâmico: {model}\n"
            f"# Diagrama: {diagram_type.upper()}\n"
        )
        if diagram_type == 'txy':
            metadata += f"# Pressão: {pressure_kPa} kPa\n"
        else:
            metadata += f"# Temperatura: {temperature_C} °C\n"
        metadata += "#\n"

        output = io.StringIO()
        output.write(metadata)
        df.to_csv(output, index=False)
        output.seek(0)

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-Type"] = "text/csv; charset=utf-8"

        return response

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/export/pdf', methods=['POST'])
def export_pdf():
    """Exportar diagrama + dados em PDF"""
    try:
        data = request.get_json()

        diagram_type = data.get('diagram_type', 'txy')
        components = data.get('components', [])
        model = data.get('model', 'Ideal')
        diagram_data = data.get('data', {})

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
        )

        title = Paragraph(
            f"Diagrama {diagram_type.upper()} - {components[0].title()} / {components[1].title()}",
            title_style,
        )
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        if diagram_type == 'txy':
            pressure_kPa = data.get('pressure', 101.325)
            info_text = f"""
            <b>Modelo termodinâmico:</b> {model}<br/>
            <b>Pressão:</b> {pressure_kPa} kPa<br/>
            <b>Componente 1:</b> {components[0].title()}<br/>
            <b>Componente 2:</b> {components[1].title()}<br/>
            <b>Data:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        else:
            temperature_C = data.get('temperature', 60)
            info_text = f"""
            <b>Modelo termodinâmico:</b> {model}<br/>
            <b>Temperatura:</b> {temperature_C} °C<br/>
            <b>Componente 1:</b> {components[0].title()}<br/>
            <b>Componente 2:</b> {components[1].title()}<br/>
            <b>Data:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        if diagram_type == 'txy':
            table_data = [['x1', 'T_bubble (°C)', 'y1', 'y1', 'T_dew (°C)', 'x1']]

            x_bubble = diagram_data.get('x_bubble', [])[:20]
            T_bubble = diagram_data.get('T_bubble', [])[:20]
            y_bubble = diagram_data.get('y_bubble', [])[:20]
            y_dew = diagram_data.get('y_dew', [])[:20]
            T_dew = diagram_data.get('T_dew', [])[:20]
            x_dew = diagram_data.get('x_dew', [])[:20]

            n = min(len(x_bubble), len(y_dew))
            for i in range(n):
                table_data.append(
                    [
                        f"{x_bubble[i]:.4f}" if i < len(x_bubble) else "",
                        f"{T_bubble[i]:.2f}" if i < len(T_bubble) else "",
                        f"{y_bubble[i]:.4f}" if i < len(y_bubble) else "",
                        f"{y_dew[i]:.4f}" if i < len(y_dew) else "",
                        f"{T_dew[i]:.2f}" if i < len(T_dew) else "",
                        f"{x_dew[i]:.4f}" if i < len(x_dew) else "",
                    ]
                )
        else:
            table_data = [['x1', 'P_bubble (kPa)', 'y1', 'y1', 'P_dew (kPa)', 'x1']]

            x_bubble = diagram_data.get('x_bubble', [])[:20]
            P_bubble = diagram_data.get('P_bubble', [])[:20]
            y_bubble = diagram_data.get('y_bubble', [])[:20]
            y_dew = diagram_data.get('y_dew', [])[:20]
            P_dew = diagram_data.get('P_dew', [])[:20]
            x_dew = diagram_data.get('x_dew', [])[:20]

            n = min(len(x_bubble), len(y_dew))
            for i in range(n):
                table_data.append(
                    [
                        f"{x_bubble[i]:.4f}" if i < len(x_bubble) else "",
                        f"{P_bubble[i]:.2f}" if i < len(P_bubble) else "",
                        f"{y_bubble[i]:.4f}" if i < len(y_bubble) else "",
                        f"{y_dew[i]:.4f}" if i < len(y_dew) else "",
                        f"{P_dew[i]:.2f}" if i < len(P_dew) else "",
                        f"{x_dew[i]:.4f}" if i < len(x_dew) else "",
                    ]
                )

        t = Table(table_data, colWidths=[1 * inch] * 6)
        t.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        story.append(t)
        story.append(Spacer(1, 0.2 * inch))
        story.append(
            Paragraph(
                "<i>Tabela limitada a 20 pontos. Dados completos disponíveis no CSV.</i>",
                styles['Italic'],
            )
        )
        story.append(Spacer(1, 0.5 * inch))
        story.append(
            Paragraph(
                "<i>Gerado por Plataforma Termodinâmica - Módulo ELV</i>",
                styles['Italic'],
            )
        )

        doc.build(story)
        buffer.seek(0)

        filename = f"{diagram_type.upper()}_{components[0]}_{components[1]}_{model}.pdf"

        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ==================== EXPORTAÇÃO PDF RESULTADO PONTUAL ======================
# ============================================================================

@bp.route('/export/point_pdf', methods=['POST'])
def export_point_pdf():
    """Exportar resultado pontual em PDF"""
    try:
        data = request.get_json()
        calc_type = data.get('calc_type', 'bubble')
        results = data.get('results', {})
        components = data.get('components', [])
        model = data.get('model', 'Ideal')

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=12,
        )
        story.append(Paragraph('Módulo ELV - Resultado Pontual', title_style))
        story.append(Spacer(1, 0.3 * cm))

        info_data = [
            ['Tipo de Cálculo:', calc_type.replace('_', ' ').title()],
            ['Modelo:', model],
            ['Componentes:', ', '.join(components)],
            ['Data:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
        ]

        info_table = Table(info_data, colWidths=[5 * cm, 10 * cm])
        info_table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(info_table)
        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph('Resultados', styles['Heading2']))
        story.append(Spacer(1, 0.2 * cm))

        results_data = [['Parâmetro', 'Valor']]
        for key, value in results.items():
            if isinstance(value, (int, float)):
                results_data.append([key, f'{value:.4f}'])
            else:
                results_data.append([key, str(value)])

        results_table = Table(results_data, colWidths=[8 * cm, 7 * cm])
        results_table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]
            )
        )
        story.append(results_table)

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'ELV_{calc_type}_resultado.pdf',
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ==================== COMPARAÇÃO DE MODELOS =================================
# ============================================================================

@bp.route('/diagram/compare', methods=['POST'])
def compare_models():
    """Gerar dados de múltiplos modelos para comparação visual em diagramas"""
    try:
        data = request.get_json()

        diagram_type = data.get('diagram_type', 'txy')
        components = data.get('components', [])
        models = data.get('models', ['Ideal'])

        calc = ELVCalculator()
        results = {}

        for model in models:
            try:
                if diagram_type == 'txy':
                    press_value = data['pressure']
                    press_unit = data.get('pressure_unit', 'kPa')

                    if press_unit == 'Pa':
                        pressure_kPa = press_value / 1000
                    elif press_unit == 'bar':
                        pressure_kPa = press_value * 100
                    elif press_unit == 'atm':
                        pressure_kPa = press_value * 101.325
                    else:
                        pressure_kPa = press_value

                    results[model] = calc.generate_txy_diagram(components, pressure_kPa, model)

                else:
                    temp_value = data['temperature']
                    temp_unit = data.get('temperature_unit', 'C')
                    if temp_unit == 'K':
                        temperature_C = temp_value - 273.15
                    else:
                        temperature_C = temp_value

                    results[model] = calc.generate_pxy_diagram(components, temperature_C, model)

            except Exception as e:
                results[model] = {'error': str(e)}

        return jsonify({'success': True, 'results': results})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/calculate/compare', methods=['POST'])
def compare_point_calculations():
    """Comparar múltiplos modelos em um cálculo pontual"""
    try:
        data = request.get_json()
        calc_type = data.get('calc_type')
        components = data.get('components')
        models = data.get('models', ['Ideal'])
        temperature = data.get('temperature')
        temperature_unit = data.get('temperature_unit', 'C')
        pressure = data.get('pressure')
        pressure_unit = data.get('pressure_unit', 'kPa')
        compositions = data.get('compositions', [])

        # converter unidades para formato esperado pelo ELVCalculator
        if temperature is not None and temperature_unit == 'K':
            temperature_C = temperature - 273.15
        else:
            temperature_C = temperature

        if pressure is not None:
            if pressure_unit == 'Pa':
                pressure_kPa = pressure / 1000
            elif pressure_unit == 'bar':
                pressure_kPa = pressure * 100
            elif pressure_unit == 'atm':
                pressure_kPa = pressure * 101.325
            else:
                pressure_kPa = pressure
        else:
            pressure_kPa = None

        calc = ELVCalculator()
        results = {}

        for model in models:
            try:
                if calc_type == 'bubble':
                    res = calc.bubble_point(components, temperature_C, compositions, model)
                elif calc_type == 'bubble_t':
                    res = calc.bubble_temperature(components, pressure_kPa, compositions, model)
                elif calc_type == 'dew':
                    res = calc.dew_point(components, temperature_C, compositions, model)
                elif calc_type == 'dew_t':
                    res = calc.dew_temperature(components, pressure_kPa, compositions, model)
                elif calc_type == 'flash':
                    res = calc.flash_calculation(components, temperature_C, pressure_kPa, compositions, model)
                else:
                    res = {'error': 'Tipo de cálculo inválido'}

                results[model] = res

            except Exception as e:
                results[model] = {'error': str(e)}

        return jsonify({'success': True, 'results': results, 'calc_type': calc_type})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
