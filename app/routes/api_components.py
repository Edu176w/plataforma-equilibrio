from flask import Blueprint, request, jsonify, render_template
from app.utils.component_database import ComponentDatabase

bp = Blueprint('api_components', __name__)

component_db = ComponentDatabase()

# ==================== PÁGINA HTML ====================

@bp.route('/components/')
@bp.route('/components/list')
def components_page():
    '''Renderizar página HTML de componentes'''
    return render_template('components.html')

# ==================== API - LISTAR TODOS ====================

@bp.route('/api/components/list', methods=['GET'])
def list_components():
    '''Listar TODOS os componentes com nomes em português'''
    try:
        components_raw = component_db.list_all_components()

        formatted_components = []
        for comp in components_raw:
            formatted_components.append({
                'name': comp['name'],
                'name_en': comp.get('name_en', comp['name']),
                'formula': comp['formula'],
                'cas': comp['cas'],
                'MW': comp['MW'],
                'Tb': comp['Tb'],
                'Tm': comp['Tm'],
                'Tc': comp['Tc'],
                'Pc': comp['Pc'],
                'Vc': comp.get('Vc'),
                'omega': comp['omega'],
                'dipole': comp.get('dipole'),
                'UNIFAC_R': comp.get('UNIFAC_R'),
                'UNIFAC_Q': comp.get('UNIFAC_Q')
            })

        return jsonify({
            'success': True,
            'components': formatted_components,
            'total': len(formatted_components)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== API - FILTRAR POR MODELO ====================

@bp.route('/api/components/by-model/<model>', methods=['GET'])
def get_components_by_model(model):
    '''Listar componentes disponíveis para um modelo específico'''
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
    
    try:
        model = model.upper()
        
        if model == 'IDEAL':
            # Modelo ideal funciona para TODOS os componentes
            return list_components()
        
        elif model == 'NRTL':
            # Importar parâmetros NRTL
            from nrtl_params import NRTL_PARAMS
            
            # Extrair componentes únicos dos pares
            nrtl_components = set()
            for (comp1, comp2) in NRTL_PARAMS.keys():
                nrtl_components.add(comp1)
                nrtl_components.add(comp2)
            
            # Buscar dados completos dos componentes
            all_comps = component_db.list_all_components()
            filtered = []
            
            for comp in all_comps:
                name_en = comp.get('name_en', comp['name']).lower()
                if name_en in nrtl_components:
                    filtered.append({
                        'name': comp['name'],
                        'name_en': comp.get('name_en', comp['name']),
                        'formula': comp['formula'],
                        'cas': comp['cas'],
                        'MW': comp['MW'],
                        'Tb': comp['Tb'],
                        'Tm': comp['Tm'],
                        'Tc': comp['Tc'],
                        'Pc': comp['Pc'],
                        'Vc': comp.get('Vc'),
                        'omega': comp['omega'],
                        'dipole': comp.get('dipole'),
                        'UNIFAC_R': comp.get('UNIFAC_R'),
                        'UNIFAC_Q': comp.get('UNIFAC_Q')
                    })
            
            return jsonify({
                'success': True,
                'model': model,
                'components': filtered,
                'count': len(filtered)
            })
        
        elif model == 'UNIQUAC':
            # Importar parâmetros UNIQUAC
            from uniquac_params import UNIQUAC_PARAMS, UNIQUAC_R_Q
            
            # Extrair componentes únicos
            uniquac_components = set()
            for (comp1, comp2) in UNIQUAC_PARAMS.keys():
                uniquac_components.add(comp1)
                uniquac_components.add(comp2)
            
            # Adicionar componentes que têm R e Q definidos
            uniquac_components.update(UNIQUAC_R_Q.keys())
            
            # Buscar dados completos
            all_comps = component_db.list_all_components()
            filtered = []
            
            for comp in all_comps:
                name_en = comp.get('name_en', comp['name']).lower()
                if name_en in uniquac_components:
                    filtered.append({
                        'name': comp['name'],
                        'name_en': comp.get('name_en', comp['name']),
                        'formula': comp['formula'],
                        'cas': comp['cas'],
                        'MW': comp['MW'],
                        'Tb': comp['Tb'],
                        'Tm': comp['Tm'],
                        'Tc': comp['Tc'],
                        'Pc': comp['Pc'],
                        'Vc': comp.get('Vc'),
                        'omega': comp['omega'],
                        'dipole': comp.get('dipole'),
                        'UNIFAC_R': comp.get('UNIFAC_R'),
                        'UNIFAC_Q': comp.get('UNIFAC_Q')
                    })
            
            return jsonify({
                'success': True,
                'model': model,
                'components': filtered,
                'count': len(filtered)
            })
        
        elif model == 'UNIFAC':
            # Importar grupos UNIFAC
            from unifac_params import UNIFAC_GROUPS
            
            # Extrair componentes que têm grupos definidos
            unifac_components = set(UNIFAC_GROUPS.keys())
            
            # Buscar dados completos
            all_comps = component_db.list_all_components()
            filtered = []
            
            for comp in all_comps:
                name_en = comp.get('name_en', comp['name']).lower()
                # Verificar se tem grupos UNIFAC ou R/Q definidos
                if (name_en in unifac_components or 
                    (comp.get('UNIFAC_R') is not None and comp.get('UNIFAC_Q') is not None)):
                    filtered.append({
                        'name': comp['name'],
                        'name_en': comp.get('name_en', comp['name']),
                        'formula': comp['formula'],
                        'cas': comp['cas'],
                        'MW': comp['MW'],
                        'Tb': comp['Tb'],
                        'Tm': comp['Tm'],
                        'Tc': comp['Tc'],
                        'Pc': comp['Pc'],
                        'Vc': comp.get('Vc'),
                        'omega': comp['omega'],
                        'dipole': comp.get('dipole'),
                        'UNIFAC_R': comp.get('UNIFAC_R'),
                        'UNIFAC_Q': comp.get('UNIFAC_Q')
                    })
            
            return jsonify({
                'success': True,
                'model': model,
                'components': filtered,
                'count': len(filtered)
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Modelo inválido. Use: IDEAL, NRTL, UNIQUAC ou UNIFAC'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== API - DETALHES ====================

@bp.route('/api/components/details/<cas>', methods=['GET'])
def component_details(cas):
    '''Obter detalhes completos de um componente por CAS'''
    try:
        properties = component_db.get_component_properties(cas)
        return jsonify({
            'success': True,
            'component': properties
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== API - BUSCA ====================

@bp.route('/api/components/search', methods=['POST', 'GET'])
def search_components():
    '''Buscar componentes por nome, fórmula ou CAS'''
    try:
        if request.method == 'POST':
            data = request.get_json()
            search_term = data.get('search', '').lower()
        else:
            search_term = request.args.get('q', '').lower()

        if not search_term:
            components = component_db.list_all_components()
            return jsonify({
                'success': True,
                'components': components,
                'total': len(components)
            })

        components = component_db.list_all_components()
        results = []
        
        for comp in components:
            if (search_term in comp['name'].lower() or
                search_term in comp.get('name_en', '').lower() or
                search_term in comp['formula'].lower() or
                search_term in comp['cas'].lower()):
                results.append(comp)

        return jsonify({
            'success': True,
            'components': results,
            'total': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== API - CATEGORIAS ====================

@bp.route('/api/components/categories', methods=['GET'])
def get_categories():
    '''Obter categorias de componentes'''
    categories = {
        'common': ['Water', 'Ethanol', 'Methanol', 'Acetone', 'Benzene', 'Toluene'],
        'alcohols': ['Methanol', 'Ethanol', 'Propanol', 'Butanol'],
        'aromatics': ['Benzene', 'Toluene', 'Xylene', 'Naphthalene'],
        'ketones': ['Acetone', 'Methyl ethyl ketone'],
        'alkanes': ['Hexane', 'Heptane', 'Octane'],
        'acids': ['Acetic acid']
    }

    return jsonify({
        'success': True,
        'categories': categories
    })

# ==================== API - RELOAD ====================

@bp.route('/api/components/reload', methods=['GET'])
def reload_database():
    '''Forçar reload do banco de dados'''
    component_db._all_components = None
    component_db.cache = {}
    component_db._translations = component_db._load_translations()
    components = component_db.list_all_components()

    return jsonify({
        'success': True,
        'message': 'Banco de dados recarregado',
        'total': len(components)
    })
