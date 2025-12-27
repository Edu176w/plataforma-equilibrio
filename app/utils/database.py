import json
import os
import numpy as np

def load_components():
    '''Carregar componentes do arquivo JSON'''
    file_path = os.path.join('data', 'components.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['components']

def get_component_by_name(name):
    '''Buscar componente por nome'''
    components = load_components()
    for comp in components:
        if comp['name'].lower() == name.lower():
            return comp
    return None

def get_component_by_id(component_id):
    '''Buscar componente por ID'''
    components = load_components()
    for comp in components:
        if comp['id'] == component_id:
            return comp
    return None

def load_nrtl_parameters():
    '''Carregar parâmetros NRTL'''
    file_path = os.path.join('data', 'nrtl_parameters.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['binary_pairs']

def get_nrtl_parameters(comp1_name, comp2_name):
    '''Buscar parâmetros NRTL para par binário'''
    params = load_nrtl_parameters()
    
    for pair in params:
        if (pair['component1'] == comp1_name and pair['component2'] == comp2_name):
            return {
                'tau12': pair['tau12'],
                'tau21': pair['tau21'],
                'alpha12': pair['alpha12']
            }
        elif (pair['component1'] == comp2_name and pair['component2'] == comp1_name):
            return {
                'tau12': pair['tau21'],
                'tau21': pair['tau12'],
                'alpha12': pair['alpha12']
            }
    
    return None

def load_uniquac_parameters():
    '''Carregar parâmetros UNIQUAC'''
    file_path = os.path.join('data', 'uniquac_parameters.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['binary_pairs']

def get_uniquac_parameters(comp1_name, comp2_name):
    '''Buscar parâmetros UNIQUAC para par binário'''
    params = load_uniquac_parameters()
    
    for pair in params:
        if (pair['component1'] == comp1_name and pair['component2'] == comp2_name):
            return {
                'a12': pair['a12'],
                'a21': pair['a21']
            }
        elif (pair['component1'] == comp2_name and pair['component2'] == comp1_name):
            return {
                'a12': pair['a21'],
                'a21': pair['a12']
            }
    
    return None

def load_unifac_groups():
    '''Carregar grupos UNIFAC'''
    file_path = os.path.join('data', 'unifac_groups.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_antoine_params(components_list):
    '''Extrair parâmetros de Antoine de lista de componentes'''
    antoine_params = []
    for comp_name in components_list:
        comp = get_component_by_name(comp_name)
        if comp:
            antoine_params.append((
                comp['antoine_a'],
                comp['antoine_b'],
                comp['antoine_c']
            ))
        else:
            raise ValueError(f'Componente {comp_name} não encontrado')
    
    return antoine_params

def build_nrtl_matrices(components_list):
    '''Construir matrizes tau e alpha para NRTL'''
    n = len(components_list)
    tau = np.zeros((n, n))
    alpha = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i == j:
                tau[i, j] = 0.0
                alpha[i, j] = 0.0
            else:
                params = get_nrtl_parameters(components_list[i], components_list[j])
                if params:
                    tau[i, j] = params['tau12']
                    alpha[i, j] = params['alpha12']
                else:
                    # Valores padrão se não houver parâmetros
                    tau[i, j] = 0.0
                    alpha[i, j] = 0.3
    
    return tau, alpha

def build_uniquac_matrices(components_list):
    '''Construir matrizes r, q e tau para UNIQUAC'''
    n = len(components_list)
    r = np.zeros(n)
    q = np.zeros(n)
    tau = np.zeros((n, n))
    
    for i, comp_name in enumerate(components_list):
        comp = get_component_by_name(comp_name)
        if comp:
            r[i] = comp['uniquac_r']
            q[i] = comp['uniquac_q']
    
    for i in range(n):
        for j in range(n):
            if i == j:
                tau[i, j] = 1.0
            else:
                params = get_uniquac_parameters(components_list[i], components_list[j])
                if params:
                    # tau_ij = exp(-a_ij/T), usando T = 298.15 K como referência
                    tau[i, j] = np.exp(-params['a12'] / 298.15)
                else:
                    tau[i, j] = 1.0
    
    return r, q, tau
