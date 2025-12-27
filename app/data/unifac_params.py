import json

# Tabela G.2 - Parametros de interacao UNIFAC (a_nm em K)
UNIFAC_INTERACTION_PARAMS = {
    # Formato: (grupo_n, grupo_m): a_nm
    (1, 3): 61.13, (1, 4): 76.50, (1, 5): 986.50, (1, 7): 1318.00, (1, 9): 476.40, (1, 13): 251.50, (1, 15): 255.70, (1, 19): 597.00,
    (3, 1): -11.12, (3, 4): 167.00, (3, 5): 636.10, (3, 7): 903.80, (3, 9): 25.77, (3, 13): 32.14, (3, 15): 122.80, (3, 19): 212.50,
    (4, 1): -69.70, (4, 3): -146.80, (4, 5): 803.20, (4, 7): 5695.00, (4, 9): -52.10, (4, 13): 213.10, (4, 15): -49.29, (4, 19): 6096.00,
    (5, 1): 156.40, (5, 3): 89.60, (5, 4): 25.82, (5, 7): 353.50, (5, 9): 84.00, (5, 13): 28.06, (5, 15): 42.70, (5, 19): 6.712,
    (7, 1): 300.00, (7, 3): 362.30, (7, 4): 377.60, (7, 5): -229.10, (7, 9): -195.40, (7, 13): 540.50, (7, 15): 168.00, (7, 19): 112.60,
    (9, 1): 26.76, (9, 3): 140.10, (9, 4): 365.80, (9, 5): 164.50, (9, 7): 472.50, (9, 13): -103.60, (9, 15): -174.20, (9, 19): 481.70,
    (13, 1): 83.36, (13, 3): 52.13, (13, 4): 65.69, (13, 5): 237.70, (13, 7): -114.70, (13, 9): 191.10, (13, 15): 251.50, (13, 19): -18.51,
    (15, 1): 65.33, (15, 3): -22.31, (15, 4): 223.00, (15, 5): -150.00, (15, 7): -448.20, (15, 9): 394.60, (15, 13): -56.08, (15, 19): 147.10,
    (19, 1): 24.82, (19, 3): -22.97, (19, 4): -138.40, (19, 5): 185.40, (19, 7): 242.80, (19, 9): -287.50, (19, 13): 38.81, (19, 15): -108.50,
}

# Tabela G.1 - Parametros de subgrupos UNIFAC-ELV
UNIFAC_SUBGROUP_PARAMS = {
    # Formato: subgroup_id: {'main_group': int, 'Rk': float, 'Qk': float}
    1: {'main_group': 1, 'name': 'CH3', 'Rk': 0.9011, 'Qk': 0.848},
    2: {'main_group': 1, 'name': 'CH2', 'Rk': 0.6744, 'Qk': 0.540},
    3: {'main_group': 1, 'name': 'CH', 'Rk': 0.4469, 'Qk': 0.228},
    4: {'main_group': 1, 'name': 'C', 'Rk': 0.2195, 'Qk': 0.000},
    
    10: {'main_group': 3, 'name': 'ACH', 'Rk': 0.5313, 'Qk': 0.400},
    
    12: {'main_group': 4, 'name': 'ACCH3', 'Rk': 1.2663, 'Qk': 0.968},
    13: {'main_group': 4, 'name': 'ACCH2', 'Rk': 1.0396, 'Qk': 0.660},
    
    15: {'main_group': 5, 'name': 'OH', 'Rk': 1.0000, 'Qk': 1.200},
    
    17: {'main_group': 7, 'name': 'H2O', 'Rk': 0.9200, 'Qk': 1.400},
    
    19: {'main_group': 9, 'name': 'CH3CO', 'Rk': 1.6724, 'Qk': 1.488},
    20: {'main_group': 9, 'name': 'CH2CO', 'Rk': 1.4457, 'Qk': 1.180},
    
    25: {'main_group': 13, 'name': 'CH3O', 'Rk': 1.1450, 'Qk': 1.088},
    26: {'main_group': 13, 'name': 'CH2O', 'Rk': 0.9183, 'Qk': 0.780},
    27: {'main_group': 13, 'name': 'CH-O', 'Rk': 0.6908, 'Qk': 0.468},
    
    32: {'main_group': 15, 'name': 'CH3NH', 'Rk': 1.4337, 'Qk': 1.244},
    33: {'main_group': 15, 'name': 'CH2NH', 'Rk': 1.2070, 'Qk': 0.936},
    34: {'main_group': 15, 'name': 'CHNH', 'Rk': 0.9795, 'Qk': 0.624},
}

# Composicao de subgrupos por molecula
MOLECULE_UNIFAC_GROUPS = {
    # ===== ALCOOIS =====
    'methanol': [(1, 1), (15, 1)],  # 1 CH3 + 1 OH
    'ethanol': [(1, 1), (2, 1), (15, 1)],  # 1 CH3 + 1 CH2 + 1 OH
    'propanol': [(1, 1), (2, 2), (15, 1)],
    '1-propanol': [(1, 1), (2, 2), (15, 1)],
    '2-propanol': [(1, 2), (3, 1), (15, 1)],  # 2 CH3 + 1 CH + 1 OH
    'butanol': [(1, 1), (2, 3), (15, 1)],
    '1-butanol': [(1, 1), (2, 3), (15, 1)],
    '2-butanol': [(1, 2), (2, 1), (3, 1), (15, 1)],
    'tert-butanol': [(1, 3), (4, 1), (15, 1)],  # 3 CH3 + 1 C + 1 OH
    
    # ===== AGUA =====
    'water': [(17, 1)],  # 1 H2O
    
    # ===== CETONAS =====
    'acetone': [(1, 2), (19, 1)],  # 2 CH3 + 1 CH3CO
    'methyl ethyl ketone': [(1, 2), (2, 1), (19, 1)],
    'methyl isobutyl ketone': [(1, 3), (2, 1), (19, 1)],
    
    # ===== AROMATICOS =====
    'benzene': [(10, 6)],  # 6 ACH (aromático)
    'toluene': [(10, 5), (12, 1)],  # 5 ACH + 1 ACCH3
    'xylene': [(10, 4), (12, 2)],
    'ethylbenzene': [(10, 5), (13, 1)],  # 5 ACH + 1 ACCH2
    
    # ===== ALCANOS =====
    'hexane': [(1, 2), (2, 4)],  # 2 CH3 + 4 CH2
    'heptane': [(1, 2), (2, 5)],
    'octane': [(1, 2), (2, 6)],
    'pentane': [(1, 2), (2, 3)],
    'butane': [(1, 2), (2, 2)],
    'propane': [(1, 2), (2, 1)],
    'cyclohexane': [(2, 6)],  # 6 CH2 em ciclo
    
    # ===== ACIDOS =====
    'acetic acid': [(1, 1), (20, 1)],  # 1 CH3 + 1 COOH
    'formic acid': [(20, 1)],  # 1 COOH
    'propionic acid': [(1, 1), (2, 1), (20, 1)],
    
    # ===== ACETATOS =====
    'ethyl acetate': [(1, 2), (2, 1), (22, 1)],  # 2 CH3 + 1 CH2 + 1 COO
    'methyl acetate': [(1, 2), (22, 1)],
    'butyl acetate': [(1, 2), (2, 3), (22, 1)],
    
    # ===== CLORADOS =====
    'chloroform': [(23, 1)],  # CHCl3
    'dichloromethane': [(24, 1)],  # CH2Cl2
    'carbon tetrachloride': [(25, 1)],  # CCl4
    'chlorobenzene': [(10, 5), (26, 1)],  # 5 ACH + 1 ACCl
    
    # ===== NITROGENADOS =====
    'acetonitrile': [(1, 1), (28, 1)],  # 1 CH3 + 1 CH3CN
    'diethylamine': [(1, 2), (2, 2), (33, 1)],  # 2 CH3 + 2 CH2 + 1 amine
    'pyridine': [(30, 5)],  # 5 ACNH (aromatic N)
    
    # ===== ETERES =====
    'diethyl ether': [(1, 2), (2, 2), (27, 1)],  # 2 CH3 + 2 CH2 + 1 O
    'tetrahydrofuran': [(2, 4), (27, 1)],  # 4 CH2 + 1 O (cyclic)
    
    # ===== ALDEIDOS =====
    'acetaldehyde': [(1, 1), (21, 1)],  # 1 CH3 + 1 CHO
    'formaldehyde': [(21, 1)],  # 1 CHO
}

def get_unifac_groups(component_name):
    '''Obter grupos UNIFAC para um componente'''
    name_lower = component_name.lower()
    return MOLECULE_UNIFAC_GROUPS.get(name_lower, [])

def get_interaction_param(main_group_n, main_group_m):
    '''Obter parametro de interacao a_nm'''
    return UNIFAC_INTERACTION_PARAMS.get((main_group_n, main_group_m), 0.0)

def get_subgroup_params(subgroup_id):
    '''Obter parametros R e Q de um subgrupo'''
    return UNIFAC_SUBGROUP_PARAMS.get(subgroup_id, {'Rk': 1.0, 'Qk': 1.0, 'main_group': 1})

