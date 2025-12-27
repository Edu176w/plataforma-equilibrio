from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required

bp = Blueprint('educational', __name__, url_prefix='/educational')

# ============================================
# ROTAS DE PÁGINAS
# ============================================

@bp.route('/')
@login_required
def index():
    """Página principal da seção educacional"""
    return render_template('educational.html')

@bp.route('/fundamentals')
@login_required
def fundamentals():
    """Fundamentos de equilíbrio de fases"""
    return render_template('educational_fundamentals.html')

@bp.route('/cases')
@login_required
def cases():
    """Casos de estudo validados"""
    return render_template('educational_cases.html')

@bp.route('/tutorials')
@login_required
def tutorials():
    """Tutoriais guiados passo a passo"""
    return render_template('educational_tutorials.html')

@bp.route('/glossary')
@login_required
def glossary():
    """Página do glossário técnico"""
    from app.utils.glossary_data import GLOSSARY_TERMS
    return render_template('educational_glossary.html', glossary_terms=GLOSSARY_TERMS)

@bp.route('/references')
@login_required
def references():
    """Referências bibliográficas"""
    return render_template('educational_references.html')

@bp.route('/equations')
@login_required
def equations():
    """Equações implementadas"""
    return render_template('educational_equations.html')

# ============================================
# SISTEMA DE PRESETS PARA CASOS DE ESTUDO
# ============================================

CASE_PRESETS = {
    # ========== CASOS ELV ==========
    'ethanol-water': {
        'module': 'elv',
        'title': 'Etanol-Água',
        'components': ['Ethanol', 'Water'],
        'conditions': {
            'pressure': 101.325,
            'temperature': 78.2,
            'composition': 0.5
        },
        'model': 'NRTL',
        'calc_type': 'txy',
        'parameters': {
            'NRTL': {
                'tau12': 0.8009,
                'tau21': -0.1771,
                'alpha': 0.3009
            }
        }
    },
    
    'flash-ethanol-water': {
        'module': 'elv',
        'title': 'Flash Etanol-Água (Tutorial)',
        'components': ['Ethanol', 'Water'],
        'conditions': {
            'pressure': 101.325,
            'temperature': 78.2,
            'composition': 0.5
        },
        'model': 'NRTL',
        'calc_type': 'flash',
        'parameters': {
            'NRTL': {
                'tau12': 0.8009,
                'tau21': -0.1771,
                'alpha': 0.3009
            }
        }
    },
    
    'benzene-toluene': {
        'module': 'elv',
        'title': 'Benzeno-Tolueno',
        'components': ['Benzene', 'Toluene'],
        'conditions': {
            'pressure': 101.325,
            'temperature': 90.0,
            'composition': 0.5
        },
        'model': 'Ideal',
        'calc_type': 'pxy',  # ✅ P-x-y para tutorial 2
        'parameters': None
    },
    
    'acetone-water': {
        'module': 'elv',
        'title': 'Acetona-Água',
        'components': ['Acetone', 'Water'],
        'conditions': {
            'pressure': 101.325,
            'temperature': 70.0,
            'composition': 0.5
        },
        'model': 'NRTL',
        'calc_type': 'txy',
        'parameters': {
            'NRTL': {
                'tau12': 1.6744,
                'tau21': 0.7831,
                'alpha': 0.3020
            }
        }
    },
    
    'methanol-benzene': {
        'module': 'elv',
        'title': 'Metanol-Benzeno',
        'components': ['Methanol', 'Benzene'],
        'conditions': {
            'pressure': 101.325,
            'temperature': 58.3,
            'composition': 0.395
        },
        'model': 'NRTL',
        'calc_type': 'txy',
        'parameters': {
            'NRTL': {
                'tau12': 2.3891,
                'tau21': 0.9534,
                'alpha': 0.2987
            }
        }
    },
    
    # ========== CASOS ELL ==========
    'water-butanol-acetone': {
        'module': 'ell',
        'title': 'Água-1-Butanol-Acetona',
        'components': ['Water', '1-Butanol', 'Acetone'],
        'conditions': {
            'temperature': 25.0,
            'feed_composition': [0.4, 0.3, 0.3]
        },
        'model': 'NRTL',
        'calc_type': 'extraction',  # ✅ Extração para tutorial 5
        'parameters': {
            'NRTL': {
                'tau12': 5.1234,
                'tau21': 1.9876,
                'tau13': 1.2345,
                'tau31': 0.5678,
                'tau23': 0.3456,
                'tau32': 0.7890,
                'alpha': 0.2
            }
        }
    },
    
    'water-chloroform-aceticacid': {
        'module': 'ell',
        'title': 'Água-Clorofórmio-Ácido Acético',
        'components': ['Water', 'Chloroform', 'Acetic Acid'],
        'conditions': {
            'temperature': 25.0,
            'feed_composition': [0.5, 0.3, 0.2]
        },
        'model': 'UNIQUAC',
        'calc_type': 'ternary',
        'parameters': None
    },
    
    'water-toluene-aniline': {
        'module': 'ell',
        'title': 'Água-Tolueno-Anilina',
        'components': ['Water', 'Toluene', 'Aniline'],
        'conditions': {
            'temperature': 25.0,
            'feed_composition': [0.45, 0.35, 0.2]
        },
        'model': 'NRTL',
        'calc_type': 'ternary',  # ✅ Diagrama ternário para tutorial 6
        'parameters': None
    },
    
    # ========== CASOS ESL ==========
    'naphthalene-benzene': {
        'module': 'esl',
        'title': 'Naftaleno-Benzeno',
        'components': ['Naphthalene', 'Benzene'],
        'conditions': {
            'temperature': 0.0,
            'composition': 0.5
        },
        'model': 'Ideal',
        'calc_type': 'tx',  # ✅ Diagrama T-x para tutorial 7
        'parameters': None
    },
    
    'water-nacl': {
        'module': 'esl',
        'title': 'Água-Cloreto de Sódio',
        'components': ['Water', 'Sodium Chloride'],
        'conditions': {
            'temperature': 25.0,
            'composition': 0.233
        },
        'model': 'van\'t Hoff',
        'calc_type': 'binary',
        'parameters': None
    },
    
    'phenol-water': {
        'module': 'esl',
        'title': 'Fenol-Água',
        'components': ['Phenol', 'Water'],
        'conditions': {
            'temperature': 20.0,
            'composition': 0.5
        },
        'model': 'NRTL',
        'calc_type': 'tx',  # ✅ Diagrama T-x para tutorial 8
        'parameters': {
            'NRTL': {
                'tau12': 3.4567,
                'tau21': 1.2345,
                'alpha': 0.3
            }
        }
    }
}

@bp.route('/cases/load/<case_id>')
def load_case(case_id):
    """Carrega um caso de estudo e redireciona para o módulo apropriado"""
    if case_id not in CASE_PRESETS:
        print(f'[EDUCATIONAL] Caso não encontrado: {case_id}')
        return redirect(url_for('educational.cases'))
    
    case = CASE_PRESETS[case_id]
    module = case['module']
    
    print(f'[EDUCATIONAL] Carregando caso: {case_id} → módulo {module}')
    
    return redirect(url_for(f'{module}.calculator', preset=case_id))

@bp.route('/api/cases/<case_id>')
def api_get_case(case_id):
    """API para obter dados completos de um caso específico"""
    if case_id not in CASE_PRESETS:
        return jsonify({
            'success': False,
            'error': 'Caso não encontrado'
        }), 404
    
    case = CASE_PRESETS[case_id]
    
    return jsonify({
        'success': True,
        'case_id': case_id,
        'data': case
    })

@bp.route('/api/cases')
def api_list_cases():
    """API para listar todos os casos disponíveis"""
    cases_list = []
    
    for case_id, case_data in CASE_PRESETS.items():
        cases_list.append({
            'id': case_id,
            'title': case_data['title'],
            'module': case_data['module'],
            'components': case_data['components'],
            'model': case_data['model'],
            'calc_type': case_data.get('calc_type', 'unknown')
        })
    
    return jsonify({
        'success': True,
        'count': len(cases_list),
        'cases': cases_list
    })

# ============================================
# API PARA BUSCA NO GLOSSÁRIO
# ============================================

@bp.route('/api/glossary/search')
def api_glossary_search():
    """API para buscar termos no glossário"""
    query = request.args.get('q', '').lower()
    
    from app.utils.glossary_data import get_all_terms, search_terms
    
    if query:
        results = search_terms(query)
    else:
        results = get_all_terms()
    
    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    })


# ============================================
# SISTEMA DE TUTORIAIS INTERATIVOS
# ============================================


# ============================================
# SISTEMA DE TUTORIAIS INTERATIVOS
# ============================================

TUTORIALS = {
    # ========== TUTORIAL 01: FLASH ELV ==========
    'flash-ethanol-water': {
        'id': 'flash-ethanol-water',
        'title': 'Flash Isotérmico de Etanol-Água',
        'module': 'elv',
        'preset': 'flash-ethanol-water',
        'duration': 15,
        'level': 'Iniciante',
        'description': 'Aprenda a calcular separação flash de uma mistura etanol-água usando o módulo ELV.',
        'objectives': [
            'Compreender o conceito de separação flash',
            'Aplicar o algoritmo de Rachford-Rice',
            'Interpretar resultados de fração vaporizada',
            'Analisar sensibilidade T-P'
        ],
        'prerequisites': [
            'Equilíbrio líquido-vapor básico',
            'Conceito de frações molares',
            'Lei de Raoult'
        ],
        'steps': [
            {
                'id': 1,
                'title': 'Adicionar Etanol',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Digite "Ethanol" na caixa de busca e clique no componente para adicioná-lo.',
                'action': 'Digite "Ethanol" e clique para adicionar',
                'validation': {'type': 'component_added'},
                'hint': 'Use a barra de busca para encontrar componentes rapidamente.'
            },
            {
                'id': 2,
                'title': 'Adicionar Água',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Agora adicione "Water" como segundo componente. Flash isotérmico requer pelo menos 2 componentes.',
                'action': 'Digite "Water" e clique para adicionar',
                'validation': {'type': 'component_added'},
                'hint': 'A água é o segundo componente da mistura etanol-água.'
            },
            {
                'id': 3,
                'title': 'Selecionar Modelo NRTL',
                'target': '#model',
                'position': 'bottom',
                'content': 'Selecione o modelo termodinâmico "NRTL" para sistemas não-ideais.',
                'action': 'Selecione "NRTL" no menu suspenso',
                'validation': {'type': 'select_value', 'element': '#model', 'value': 'NRTL'},
                'hint': 'NRTL é adequado para sistemas altamente não-ideais como etanol-água.'
            },
            {
                'id': 4,
                'title': 'Escolher Flash Isotérmico',
                'target': '#calcType',
                'position': 'bottom',
                'content': 'Selecione "Flash" no tipo de cálculo.',
                'action': 'Selecione "Flash" no menu suspenso',
                'validation': {'type': 'select_value', 'element': '#calcType', 'value': 'flash'},
                'hint': 'Flash isotérmico mantém temperatura constante.'
            },
            {
                'id': 5,
                'title': 'Definir Temperatura',
                'target': '#temperature',
                'position': 'right',
                'content': 'Digite a temperatura de operação: 78.2°C (próximo ao azeótropo).',
                'action': 'Digite "78.2" no campo de temperatura',
                'validation': {'type': 'input_value', 'element': '#temperature', 'min': 70, 'max': 85},
                'hint': 'O azeótropo etanol-água ocorre em ~78.2°C a 1 atm.'
            },
            {
                'id': 6,
                'title': 'Definir Pressão',
                'target': '#dynamicFields',
                'position': 'right',
                'content': 'Digite a pressão de operação: 101.325 kPa (1 atmosfera).',
                'action': 'Digite "101.325" no campo de pressão',
                'validation': {'type': 'input_value', 'element': '#pressure', 'min': 90, 'max': 110},
                'hint': 'Pressão atmosférica padrão é 101.325 kPa.'
            },
            {
                'id': 7,
                'title': 'Definir Composição de Alimentação',
                'target': '#dynamicFields',
                'position': 'right',
                'content': 'Digite a fração molar do etanol: 0.5 (mistura equimolar).',
                'action': 'Digite "0.5" para fração de etanol',
                'validation': {'type': 'composition_filled', 'min': 0.4, 'max': 0.6},
                'hint': 'A soma das frações molares deve ser 1.0.'
            },
            {
                'id': 8,
                'title': 'Calcular Resultados',
                'target': '.btn-sim-primary',
                'position': 'top',
                'content': 'Clique em "Calcular" para executar o cálculo de flash.',
                'action': 'Clique no botão "Calcular"',
                'validation': {'type': 'button_click', 'element': '.btn-sim-primary'},
                'hint': 'O algoritmo de Rachford-Rice será aplicado.'
            },
            {
                'id': 9,
                'title': 'Analisar Resultados',
                'target': '#results',
                'position': 'left',
                'content': 'Analise os resultados: fração vaporizada (β), composições x e y, coeficientes γ.',
                'action': 'Revise os resultados exibidos',
                'validation': {'type': 'element_visible', 'element': '#results .results-card'},
                'hint': 'β = 0 significa todo líquido, β = 1 significa todo vapor.'
            }
        ]
    },
    
    # ========== TUTORIAL 02: DIAGRAMA P-X-Y ✅ CORRIGIDO ==========
    'diagram-pxy': {
        'id': 'diagram-pxy',
        'title': 'Construção de Diagrama P-x-y',
        'module': 'elv',
        'preset': 'benzene-toluene',
        'duration': 20,
        'level': 'Iniciante',
        'description': 'Construa um diagrama de equilíbrio P-x-y para o sistema benzeno-tolueno a temperatura constante.',
        'objectives': [
            'Compreender comportamento ideal (Lei de Raoult)',
            'Calcular curvas de bolha e orvalho isotérmicas',
            'Interpretar diagrama P-x-y',
            'Analisar volatilidade relativa'
        ],
        'prerequisites': [
            'Equilíbrio de fases básico',
            'Conceito de ponto de bolha e orvalho',
            'Pressão de vapor'
        ],
        'steps': [
            {
                'id': 1,
                'title': 'Adicionar Benzeno',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Digite "Benzene" e adicione o primeiro componente.',
                'action': 'Digite "Benzene" e clique para adicionar',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 2,
                'title': 'Adicionar Tolueno',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione "Toluene" como segundo componente.',
                'action': 'Digite "Toluene" e clique para adicionar',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 3,
                'title': 'Modelo Ideal',
                'target': '#model',
                'position': 'bottom',
                'content': 'Mantenha o modelo "Ideal" selecionado. Benzeno e tolueno apresentam comportamento próximo ao ideal.',
                'action': 'Verifique se "Ideal" está selecionado',
                'validation': {'type': 'select_value', 'element': '#model', 'value': 'Ideal'}
            },
            {
                'id': 4,
                'title': 'Selecionar Diagrama P-x-y',
                'target': '#calcType',
                'position': 'bottom',
                'content': 'Selecione "Diagrama P-x-y (2 componentes)" para gerar curvas isotérmicas de equilíbrio.',
                'action': 'Selecione "Diagrama P-x-y"',
                'validation': {'type': 'select_value', 'element': '#calcType', 'value': 'pxy'}
            },
            {
                'id': 5,
                'title': 'Definir Temperatura',
                'target': '#temperature',
                'position': 'bottom',
                'content': 'Digite 90°C (temperatura intermediária entre os pontos de ebulição).',
                'action': 'Digite "90"',
                'validation': {'type': 'input_value', 'element': '#temperature', 'min': 80, 'max': 100}
            },
            {
                'id': 6,
                'title': 'Gerar Diagrama',
                'target': '.btn-sim-primary',
                'position': 'top',
                'content': 'Clique em "Calcular" para gerar o diagrama P-x-y completo.',
                'action': 'Clique em "Calcular"',
                'validation': {'type': 'button_click', 'element': '.btn-sim-primary'}
            },
            {
                'id': 7,
                'title': 'Interpretar Diagrama',
                'target': '#results',
                'position': 'left',
                'content': 'Observe as curvas de bolha (superior) e orvalho (inferior). A pressão aumenta com a fração de benzeno (mais volátil).',
                'action': 'Analise o gráfico gerado',
                'validation': {'type': 'element_visible', 'element': '#results .panel'}
            }
        ]
    },
    
    # ========== TUTORIAL 03: AZEOTROPIA ✅ CORRIGIDO ==========
    'azeotrope-detection': {
        'id': 'azeotrope-detection',
        'title': 'Identificação de Azeótropos',
        'module': 'elv',
        'preset': 'methanol-benzene',
        'duration': 25,
        'level': 'Intermediário',
        'description': 'Detecte e caracterize o azeótropo de mínimo do sistema metanol-benzeno usando NRTL.',
        'objectives': [
            'Identificar azeótropo em diagrama P-x-y',
            'Entender desvios da Lei de Raoult',
            'Compreender limitações da destilação',
            'Analisar coeficientes de atividade'
        ],
        'prerequisites': [
            'Diagramas P-x-y',
            'Modelos não-ideais (NRTL)',
            'Conceito de azeotropia'
        ],
        'steps': [
            {
                'id': 1,
                'title': 'Adicionar Metanol',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione "Methanol" como primeiro componente.',
                'action': 'Digite "Methanol" e clique para adicionar',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 2,
                'title': 'Adicionar Benzeno',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione "Benzene" como segundo componente.',
                'action': 'Digite "Benzene" e clique para adicionar',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 3,
                'title': 'Modelo NRTL',
                'target': '#model',
                'position': 'bottom',
                'content': 'Selecione NRTL para capturar não-idealidade forte deste sistema.',
                'action': 'Selecione "NRTL"',
                'validation': {'type': 'select_value', 'element': '#model', 'value': 'NRTL'}
            },
            {
                'id': 4,
                'title': 'Gerar Diagrama P-x-y',
                'target': '#calcType',
                'position': 'bottom',
                'content': 'Selecione "Diagrama P-x-y" para visualizar o azeótropo.',
                'action': 'Selecione "Diagrama P-x-y"',
                'validation': {'type': 'select_value', 'element': '#calcType', 'value': 'pxy'}
            },
            {
                'id': 5,
                'title': 'Definir Temperatura',
                'target': '#dynamicFields',
                'position': 'bottom',
                'content': 'Digite 80 °C (celsius).',
                'action': 'Digite "80"',
                'validation': {'type': 'input_value', 'element': '#temperature', 'min': 90, 'max': 110}
            },
            {
                'id': 6,
                'title': 'Calcular',
                'target': '.btn-sim-primary',
                'position': 'top',
                'content': 'Gere o diagrama.',
                'action': 'Clique em "Calcular"',
                'validation': {'type': 'button_click', 'element': '.btn-sim-primary'}
            },
            {
                'id': 7,
                'title': 'Localizar Azeótropo',
                'target': '#results',
                'position': 'left',
                'content': 'Observe o ponto onde as curvas se tocam (x ≈ 0.820, P ≈ 215 Kpa). Este é o azeótropo de mínimo!',
                'action': 'Analise o gráfico',
                'validation': {'type': 'element_visible', 'element': '#results .panel'}
            }
        ]
    },
    
    # ========== TUTORIAL 04: COMPARAÇÃO DE MODELOS ✅ CORRIGIDO ==========
    'model-comparison': {
        'id': 'model-comparison',
        'title': 'Comparação Ideal vs NRTL vs UNIQUAC',
        'module': 'elv',
        'preset': 'acetone-water',
        'duration': 30,
        'level': 'Intermediário',
        'description': 'Compare predições de diferentes modelos termodinâmicos para acetona-água.',
        'objectives': [
            'Comparar múltiplos modelos',
            'Entender quando usar cada modelo',
            'Avaliar qualidade das predições',
            'Analisar coeficientes de atividade'
        ],
        'prerequisites': [
            'Modelos termodinâmicos',
            'Não-idealidade',
            'Interpretação de diagramas'
        ],
        'steps': [
            {
                'id': 1,
                'title': 'Adicionar Acetona',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione "Acetone" como primeiro componente.',
                'action': 'Digite "Acetone" e clique para adicionar',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 2,
                'title': 'Adicionar Água',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione "Water" como segundo componente.',
                'action': 'Digite "Water" e clique para adicionar',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 3,
                'title': 'Diagrama T-x-y',
                'target': '#calcType',
                'position': 'bottom',
                'content': 'Selecione diagrama T-x-y.',
                'action': 'Selecione "Diagrama T-x-y"',
                'validation': {'type': 'select_value', 'element': '#calcType', 'value': 'txy'}
            },
            {
                'id': 4,
                'title': 'Calcular com Modelo Ideal',
                'target': '#model',
                'position': 'bottom',
                'content': 'Primeiro, use modelo Ideal para ver as limitações.',
                'action': 'Selecione "Ideal"',
                'validation': {'type': 'select_value', 'element': '#model', 'value': 'Ideal'}
            },
            {
                'id': 5,
                'title': 'Definir Pressão',
                'target': '#dynamicFields',
                'position': 'bottom',
                'content': 'Digite 101.325 kPa.',
                'action': 'Digite "101.325"',
                'validation': {'type': 'input_value', 'element': '#pressure', 'min': 90, 'max': 110}
            },
            {
                'id': 6,
                'title': 'Gerar Diagrama Ideal',
                'target': '.btn-sim-primary',
                'position': 'top',
                'content': 'Calcule o primeiro diagrama com modelo Ideal.',
                'action': 'Clique em "Calcular"',
                'validation': {'type': 'button_click', 'element': '.btn-sim-primary'}
            },
            {
                'id': 7,
                'title': 'Analisar Resultados',
                'target': '#results',
                'position': 'left',
                'content': 'Observe o diagrama gerado. Agora você pode testar outros modelos (NRTL, UNIQUAC) mudando o modelo e recalculando para comparar.',
                'action': 'Revise o diagrama',
                'validation': {'type': 'element_visible', 'element': '#results .panel'}
            }
        ]
    },
    
    # ========== TUTORIAL 05: EXTRAÇÃO LLE ✅ CORRIGIDO ==========
    'lle-extraction': {
        'id': 'lle-extraction',
        'title': 'Extração de Acetona com 1-Butanol',
        'module': 'ell',
        'preset': 'water-butanol-acetone',
        'duration': 35,
        'level': 'Avançado',
        'description': 'Projete uma extração líquido-líquido multi-estágios para recuperar acetona de solução aquosa.',
        'objectives': [
            'Compreender extração líquido-líquido',
            'Calcular número de estágios teóricos',
            'Interpretar coeficientes de distribuição',
            'Analisar eficiência e seletividade'
        ],
        'prerequisites': [
            'Equilíbrio líquido-líquido',
            'Balanço material',
            'Equação de Kremser-Souders-Brown'
        ],
        'steps': [
            {
                'id': 1,
                'title': 'Adicionar Água',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Water como diluente (componente que fica preferencialmente no rafinado).',
                'action': 'Digite Water e clique para adicionar',
                'validation': {'type': 'component_added'},
                'hint': 'A água é o diluente da alimentação.'
            },
            {
                'id': 2,
                'title': 'Adicionar 1-Butanol',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione 1-Butanol como solvente (componente que extrai o soluto).',
                'action': 'Digite 1-Butanol e clique para adicionar',
                'validation': {'type': 'component_added'},
                'hint': '1-Butanol é imiscível com água e extrai acetona.'
            },
            {
                'id': 3,
                'title': 'Adicionar Acetona',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Acetone como soluto (componente a ser extraído).',
                'action': 'Digite Acetone e clique para adicionar',
                'validation': {'type': 'component_added'},
                'hint': 'Acetona é o soluto que será transferido para o solvente.'
            },
            {
                'id': 4,
                'title': 'Selecionar Modelo NRTL',
                'target': '#model',
                'position': 'bottom',
                'content': 'Selecione NRTL para sistemas ternários com duas fases líquidas.',
                'action': 'Selecione NRTL',
                'validation': {'type': 'select_value', 'element': '#model', 'value': 'NRTL'},
                'hint': 'NRTL é robusto para sistemas com imiscibilidade parcial.'
            },
            # ✅ ADICIONAR ESTES NOVOS PASSOS:
            {
                'id': 5,
                'title': 'Selecionar Flash L1-L2',
                'target': '#calcType',
                'position': 'bottom',
                'content': 'Selecione "Flash L1-L2" para calcular o equilíbrio líquido-líquido.',
                'action': 'Selecione Flash L1-L2',
                'validation': {'type': 'select_value', 'element': '#calcType', 'value': 'ellflash'}
            },
            {
                'id': 6,
                'title': 'Definir Temperatura',
                'target': '#temperature',
                'position': 'right',
                'content': 'Digite 25°C como temperatura de operação.',
                'action': 'Digite 25',
                'validation': {'type': 'input_value', 'element': '#temperature', 'min': 20, 'max': 30}
            },
            {
                'id': 7,
                'title': 'Definir Composição Global',
                'target': '#dynamicFields',
                'position': 'right',
                'content': 'Digite a composição global da alimentação. Use z(Water)=0.4, z(1-Butanol)=0.3, z(Acetone)=0.3.',
                'action': 'Preencha as composições',
                'validation': {'type': 'composition_filled', 'min': 0.2, 'max': 0.5},
                'hint': 'A soma das frações molares deve ser 1.0.'
            },
            {
                'id': 8,
                'title': 'Calcular Equilíbrio',
                'target': '.btn-sim-primary',
                'position': 'top',
                'content': 'Clique em Calcular para resolver o equilíbrio líquido-líquido.',
                'action': 'Clique em Calcular',
                'validation': {'type': 'button_click', 'element': '.btn-sim-primary'}
            },
            {
                'id': 9,
                'title': 'Analisar Resultados da Extração',
                'target': '#results',
                'position': 'left',
                'content': 'Excelente! Observe as composições das fases L1 (rafinado) e L2 (extrato), os coeficientes de distribuição K e a fração de cada fase.',
                'action': 'Analise os resultados',
                'validation': {'type': 'element_visible', 'element': '#results .results-card'},
                'hint': 'O coeficiente de distribuição K = x_L2/x_L1 indica a preferência do soluto pela fase extrato.'
            }
        ]
    },

    
    # ========== TUTORIAL 06: DIAGRAMA TERNÁRIO ✅ CORRIGIDO ==========
    'ternary-diagram': {
        'id': 'ternary-diagram',
        'title': 'Construção de Diagrama Ternário',
        'module': 'ell',
        'preset': 'water-toluene-aniline',
        'duration': 30,
        'level': 'Intermediário',
        'description': 'Construa e interprete um diagrama ternário completo para água-tolueno-anilina.',
        'objectives': [
            'Compreender diagramas ternários',
            'Calcular curva binodal',
            'Determinar tie-lines',
            'Identificar plait point'
        ],
        'prerequisites': [
            'Equilíbrio líquido-líquido',
            'Coordenadas ternárias',
            'Regra da alavanca'
        ],
        'steps': [
            {
                'id': 1,
                'title': 'Adicionar Água',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Water como primeiro componente.',
                'action': 'Digite Water e clique',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 2,
                'title': 'Adicionar Tolueno',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Toluene como segundo componente.',
                'action': 'Digite Toluene e clique',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 3,
                'title': 'Adicionar Anilina',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Aniline como terceiro componente.',
                'action': 'Digite Aniline e clique',
                'validation': {'type': 'component_added'}
            },
            {
                'id': 4,
                'title': 'Modelo NRTL',
                'target': '#model',
                'position': 'bottom',
                'content': 'Selecione NRTL.',
                'action': 'Selecione NRTL',
                'validation': {'type': 'select_value', 'element': '#model', 'value': 'NRTL'}
            },
            # ✅ ADICIONAR ESTES NOVOS PASSOS:
            {
                'id': 5,
                'title': 'Selecionar Diagrama Ternário',
                'target': '#calcType',
                'position': 'bottom',
                'content': 'Selecione "Diagrama Ternário Completo" para gerar a curva binodal e tie-lines.',
                'action': 'Selecione Diagrama Ternário',
                'validation': {'type': 'select_value', 'element': '#calcType', 'value': 'ternary_diagram'}
            },
            {
                'id': 6,
                'title': 'Definir Temperatura',
                'target': '#temperature',
                'position': 'right',
                'content': 'Digite a temperatura de 25°C para o cálculo do equilíbrio.',
                'action': 'Digite 25',
                'validation': {'type': 'input_value', 'element': '#temperature', 'min': 20, 'max': 30}
            },
            {
                'id': 7,
                'title': 'Calcular Diagrama',
                'target': '.btn-sim-primary',
                'position': 'top',
                'content': 'Clique em Calcular para gerar o diagrama ternário completo com binodal e tie-lines.',
                'action': 'Clique em Calcular',
                'validation': {'type': 'button_click', 'element': '.btn-sim-primary'},
                'hint': 'O cálculo pode levar alguns segundos.'
            },
            {
                'id': 8,
                'title': 'Analisar Diagrama Ternário',
                'target': '#results',
                'position': 'left',
                'content': 'Parabéns! Observe o diagrama ternário gerado: a curva binodal delimita a região de duas fases, e as tie-lines conectam composições em equilíbrio.',
                'action': 'Analise o diagrama gerado',
                'validation': {'type': 'element_visible', 'element': '#results .panel'},
                'hint': 'O plait point é onde a tie-line tem comprimento zero.'
            }
        ]
    },

    
    # ========== TUTORIAL 07: CRISTALIZAÇÃO ESL ✅ CORRIGIDO ==========
    'crystallization': {
        'id': 'crystallization',
        'title': 'Cristalização de Naftaleno',
        'module': 'esl',
        'preset': 'naphthalene-benzene',
        'duration': 25,
        'level': 'Iniciante',
        'description': 'Calcule a solubilidade de naftaleno em benzeno e projete um processo de cristalização.',
        'objectives': [
            'Compreender equilíbrio sólido-líquido',
            'Calcular solubilidade vs temperatura',
            'Determinar rendimento de cristalização',
            'Analisar pureza do cristal'
        ],
        'prerequisites': [
            'Termodinâmica de fases',
            'Entalpia de fusão',
            'Balanço material'
        ],
        'steps': [
            {
                'id': 1,
                'title': 'Adicionar Naftaleno',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Naphthalene (soluto que será cristalizado).',
                'action': 'Digite Naphthalene e clique',
                'validation': {'type': 'component_added'},
                'hint': 'Naftaleno tem Tm = 80.3°C e ΔHfus = 18.6 kJ/mol.'
            },
            {
                'id': 2,
                'title': 'Adicionar Benzeno',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Benzene (solvente).',
                'action': 'Digite Benzene e clique',
                'validation': {'type': 'component_added'},
                'hint': 'Benzeno permanece líquido e dissolve naftaleno.'
            },
            {
                'id': 3,
                'title': 'Modelo Ideal',
                'target': '#model',
                'position': 'bottom',
                'content': 'Mantenha Ideal selecionado. Naftaleno-benzeno apresenta comportamento próximo ao ideal.',
                'action': 'Verifique Ideal',
                'validation': {'type': 'select_value', 'element': '#model', 'value': 'Ideal'}
            },
            # ✅ ADICIONAR ESTES NOVOS PASSOS:
            {
                'id': 4,
                'title': 'Selecionar Cristalização',
                'target': '#calcType',
                'position': 'bottom',
                'content': 'Selecione "Cristalização" para visualizar a solubilidade.',
                'action': 'Cristalização',
                'validation': {'type': 'select_value', 'element': '#calcType', 'value': 'crystallization'}
            },
            {
                'id': 5,
                'title': 'Calcular Cristalização',
                'target': '.btn-sim-primary',
                'position': 'top',
                'content': 'Clique em Calcular para gerar a cristalização.',
                'action': 'Clique em Calcular',
                'validation': {'type': 'button_click', 'element': '.btn-sim-primary'},
                'hint': 'O cálculo usa a equação de Schröder-van Laar.'
            },
            {
                'id': 6,
                'title': 'Analisar Cristalização',
                'target': '#results',
                'position': 'left',
                'content': 'Perfeito! Observe a cristalização do naftaleno.',
                'action': 'Analise a cristalização',
                'validation': {'type': 'element_visible', 'element': '#results .panel'},
                'hint': '.'
            }
        ]
    },

    
    # ========== TUTORIAL 08: PONTO EUTÉTICO ✅ CORRIGIDO ==========
    'eutectic-point': {
        'id': 'eutectic-point',
        'title': 'Determinação de Ponto Eutético',
        'module': 'esl',
        'preset': 'naphthalene-benzene',  # ✅ MUDADO PARA SISTEMA IDEAL
        'duration': 25,
        'level': 'Iniciante',  # ✅ MUDADO PARA INICIANTE
        'description': 'Identifique o ponto eutético do sistema naftaleno-benzeno e aprenda sobre diagramas T-x com eutético.',
        'objectives': [
            'Compreender ponto eutético',
            'Identificar temperatura eutética',
            'Interpretar diagrama T-x binário',
            'Calcular composição eutética'
        ],
        'prerequisites': [
            'Equilíbrio sólido-líquido',
            'Diagramas de fases',
            'Lei de Raoult para sólidos'
        ],
        'steps': [
            {
                'id': 1,
                'title': 'Adicionar Naftaleno',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Naphthalene como primeiro componente (Tm = 80.3°C).',
                'action': 'Digite Naphthalene e clique',
                'validation': {'type': 'component_added'},
                'hint': 'Naftaleno é um sólido aromático com alto ponto de fusão.'
            },
            {
                'id': 2,
                'title': 'Adicionar Benzeno',
                'target': '#componentSearch',
                'position': 'right',
                'content': 'Adicione Benzene como segundo componente (Tm = 5.5°C).',
                'action': 'Digite Benzene e clique',
                'validation': {'type': 'component_added'},
                'hint': 'Benzeno tem ponto de fusão muito mais baixo que naftaleno.'
            },
            {
                'id': 3,
                'title': 'Modelo Ideal',
                'target': '#model',
                'position': 'bottom',
                'content': 'Mantenha o modelo Ideal (Schrӧder-van Laar). Naftaleno e benzeno são aromáticos similares e formam solução quase ideal.',
                'action': 'Verifique se Ideal está selecionado',
                'validation': {'type': 'select_value', 'element': '#model', 'value': 'Ideal'},
                'hint': 'A equação de Schrӧder-van Laar é perfeita para sistemas ideais.'
            },
            {
                'id': 4,
                'title': 'Selecionar Diagrama T-x',
                'target': '#calcType',
                'position': 'bottom',
                'content': 'Selecione "Diagrama T-x binário" para visualizar as curvas de liquidus e o ponto eutético.',
                'action': 'Selecione Diagrama T-x',
                'validation': {'type': 'select_value', 'element': '#calcType', 'value': 'tx'},
                'hint': 'O diagrama T-x mostra temperatura vs composição.'
            },
            {
                'id': 5,
                'title': 'Calcular Diagrama',
                'target': '.btn-sim-primary',
                'position': 'top',
                'content': 'Clique em Calcular para gerar o diagrama T-x completo com as curvas de liquidus e o ponto eutético.',
                'action': 'Clique em Calcular',
                'validation': {'type': 'button_click', 'element': '.btn-sim-primary'},
                'hint': 'O cálculo resolve a equação de solubilidade para múltiplas temperaturas.'
            },
            {
                'id': 6,
                'title': 'Identificar Ponto Eutético',
                'target': '#results',
                'position': 'left',
                'content': 'Perfeito! Observe o diagrama T-x: as duas curvas de liquidus (uma partindo de 80.3°C para naftaleno, outra de 5.5°C para benzeno) se encontram no PONTO EUTÉTICO. Neste ponto, ambos os componentes cristalizam simultaneamente. Veja a temperatura eutética (Te) e composição eutética (xe) nos resultados.',
                'action': 'Analise o diagrama e identifique Te e xe',
                'validation': {'type': 'element_visible', 'element': '#results .panel'},
                'hint': 'O ponto eutético é a temperatura mínima de cristalização do sistema. Abaixo dele, o sistema é 100% sólido.'
            }
        ]
    },


}

@bp.route('/tutorials/<tutorial_id>/start')
def start_tutorial(tutorial_id):
    """Inicia tutorial interativo"""
    if tutorial_id not in TUTORIALS:
        return redirect(url_for('educational.tutorials'))
    
    tutorial = TUTORIALS[tutorial_id]
    preset_id = tutorial.get('preset')
    module = tutorial['module']
    
    print(f'[EDUCATIONAL] Iniciando tutorial: {tutorial_id} → módulo {module}')
    
    # ✅ CORREÇÃO: endpoints corretos para cada módulo
    endpoint_map = {
        'elv': 'elv.calculator',
        'ell': 'ell.ell_calculator',  # ← CORRIGIDO
        'esl': 'esl.calculator'        # ← CORRIGIDO
    }
    
    endpoint = endpoint_map.get(module)
    
    if not endpoint:
        print(f'[EDUCATIONAL] ❌ Endpoint não encontrado para módulo: {module}')
        return redirect(url_for('educational.tutorials'))
    
    try:
        return redirect(url_for(
            endpoint,
            preset=preset_id,
            tutorial=tutorial_id
        ))
    except Exception as e:
        print(f'[EDUCATIONAL] ❌ Erro ao redirecionar: {e}')
        # Fallback: redirecionar para URL direta
        module_urls = {
            'elv': '/elv',
            'ell': '/ell',
            'esl': '/esl'
        }
        base_url = module_urls.get(module, f'/{module}')
        url = f"{base_url}?preset={preset_id}&tutorial={tutorial_id}"
        return redirect(url)

@bp.route('/api/tutorials/<tutorial_id>')
def api_get_tutorial(tutorial_id):
    """API para obter dados completos do tutorial"""
    if tutorial_id not in TUTORIALS:
        return jsonify({'success': False, 'error': 'Tutorial não encontrado'}), 404
    
    return jsonify({
        'success': True,
        'tutorial': TUTORIALS[tutorial_id]
    })

@bp.route('/api/tutorials')
def api_list_tutorials():
    """API para listar todos os tutoriais disponíveis"""
    tutorials_list = []
    
    for tutorial_id, tutorial_data in TUTORIALS.items():
        tutorials_list.append({
            'id': tutorial_id,
            'title': tutorial_data['title'],
            'module': tutorial_data['module'],
            'duration': tutorial_data['duration'],
            'level': tutorial_data['level'],
            'description': tutorial_data['description']
        })
    
    return jsonify({
        'success': True,
        'count': len(tutorials_list),
        'tutorials': tutorials_list
    })
