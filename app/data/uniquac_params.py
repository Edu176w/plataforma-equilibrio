'''
Parâmetros UNIQUAC para sistemas binários
tau_ij = exp(-a_ij / T) onde a_ij está em Kelvin
Fonte: Prausnitz et al. (1986), DECHEMA Chemistry Data Series
'''

# Parâmetros estruturais r e q (Table 6-9)
UNIQUAC_R_Q = {
    'water': {'r': 0.92, 'q': 1.40},
    'methanol': {'r': 1.43, 'q': 1.43},
    'ethanol': {'r': 2.11, 'q': 1.97},
    '1-propanol': {'r': 2.78, 'q': 2.51},
    '2-propanol': {'r': 2.78, 'q': 2.51},
    '1-butanol': {'r': 3.45, 'q': 3.05},
    'acetone': {'r': 2.57, 'q': 2.34},
    'methyl ethyl ketone': {'r': 3.25, 'q': 2.88},
    'methyl isobutyl ketone': {'r': 4.60, 'q': 4.03},
    'acetonitrile': {'r': 1.87, 'q': 1.72},
    'acetic acid': {'r': 1.90, 'q': 1.80},
    'formic acid': {'r': 1.54, 'q': 1.48},
    'benzene': {'r': 3.19, 'q': 2.40},
    'toluene': {'r': 3.92, 'q': 2.97},
    'hexane': {'r': 4.50, 'q': 3.86},
    'n-hexane': {'r': 4.50, 'q': 3.86},
    'heptane': {'r': 5.17, 'q': 4.40},
    'n-heptane': {'r': 5.17, 'q': 4.40},
    'octane': {'r': 5.85, 'q': 4.94},
    'n-octane': {'r': 5.85, 'q': 4.94},
    'chloroform': {'r': 2.70, 'q': 2.34},
    'carbon tetrachloride': {'r': 3.33, 'q': 2.82},
    'nitroethane': {'r': 2.68, 'q': 2.41},
    'nitromethane': {'r': 2.01, 'q': 1.87},
    'ethyl acetate': {'r': 3.48, 'q': 3.12},
    'diethylamine': {'r': 3.68, 'q': 3.17},
    'methylcyclopentane': {'r': 3.97, 'q': 3.01},
    'ethanol/carbon tetrachloride': {'r': 0, 'q': 0},  # placeholder para pares
}

# Parâmetros binários de energia (Table 6-10 e literatura)
UNIQUAC_PARAMS = {
    # Álcoois com água
    ('methanol', 'water'): {'a12': -122.89, 'a21': 305.26},
    ('ethanol', 'water'): {'a12': -83.27, 'a21': 256.07},
    ('1-propanol', 'water'): {'a12': 39.13, 'a21': 393.70},
    ('2-propanol', 'water'): {'a12': -14.02, 'a21': 373.81},
    ('1-butanol', 'water'): {'a12': 171.77, 'a21': 546.52},
    
    # Cetonas com água
    ('acetone', 'water'): {'a12': 330.99, 'a21': -100.71},
    ('methyl ethyl ketone', 'water'): {'a12': 422.69, 'a21': 22.96},
    
    # Ácidos com água
    ('acetic acid', 'water'): {'a12': -165.76, 'a21': 320.43},
    ('formic acid', 'water'): {'a12': -144.58, 'a21': 241.64},
    
    # Aromáticos com alcanos
    ('hexane', 'benzene'): {'a12': -7.97, 'a21': 6.27},
    ('heptane', 'benzene'): {'a12': -9.42, 'a21': 7.53},
    ('octane', 'benzene'): {'a12': -11.03, 'a21': 8.96},
    ('hexane', 'toluene'): {'a12': -7.22, 'a21': 5.88},
    
    # Álcoois com alcanos
    ('ethanol', 'hexane'): {'a12': 406.05, 'a21': 93.54},
    ('ethanol', 'octane'): {'a12': -80.16, 'a21': 872.18},
    ('ethanol', 'heptane'): {'a12': 279.26, 'a21': 38.40},
    ('methanol', 'hexane'): {'a12': 713.95, 'a21': 27.82},
    ('methanol', 'octane'): {'a12': 238.18, 'a21': -109.87},
    
    # Cetonas com alcanos e álcoois
    ('acetone', 'hexane'): {'a12': 75.82, 'a21': 74.76},
    ('acetone', 'methanol'): {'a12': -28.50, 'a21': 165.31},
    ('acetone', 'ethanol'): {'a12': 25.09, 'a21': 113.27},
    ('acetone', 'benzene'): {'a12': -19.35, 'a21': 62.78},
    
    # Halogenados
    ('chloroform', 'acetone'): {'a12': -171.71, 'a21': 93.93},
    ('chloroform', 'ethanol'): {'a12': -86.77, 'a21': 243.39},
    ('chloroform', 'methanol'): {'a12': -75.13, 'a21': 242.53},
    ('ethanol', 'carbon tetrachloride'): {'a12': -138.90, 'a21': 947.20},
    ('carbon tetrachloride', 'benzene'): {'a12': -95.13, 'a21': 242.53},
    
    # Nitrocompostos
    ('acetonitrile', 'benzene'): {'a12': -40.70, 'a21': 299.79},
    ('acetonitrile', 'water'): {'a12': 378.89, 'a21': 136.46},
    ('hexane', 'nitromethane'): {'a12': 230.64, 'a21': -5.86},
    ('hexane', 'nitroethane'): {'a12': 230.64, 'a21': -5.86},

    
    # Aromáticos com água e álcoois
    ('benzene', 'ethanol'): {'a12': 332.68, 'a21': -9.09},
    ('benzene', 'water'): {'a12': 844.03, 'a21': 352.09},
    ('toluene', 'water'): {'a12': 891.76, 'a21': 367.42},
    
    # Ésteres
    ('ethyl acetate', 'ethanol'): {'a12': -121.57, 'a21': 1354.92},
    ('ethyl acetate', 'water'): {'a12': 591.71, 'a21': -25.08},
    ('methanol', 'ethyl acetate'): {'a12': -56.35, 'a21': 972.09},
    #('methanol', 'diethylamine'): {'a12': 350.0, 'a21': 280.0},

    
    # Outros binários da Tabela 6-10
    ('methylcyclopentane', 'ethanol'): {'a12': 1383.93, 'a21': -118.27},
    ('methylcyclopentane', 'benzene'): {'a12': 56.47, 'a21': -6.47},
    ('formic acid','acetic acid'):{'a12':-144.58,'a21':241.64},
}

COMPONENT_TRANSLATIONS = {
    'water': 'Água',
    'methanol': 'Metanol',
    'ethanol': 'Etanol',
    '1-propanol': '1-Propanol',
    '2-propanol': '2-Propanol',
    '1-butanol': '1-Butanol',
    'acetone': 'Acetona',
    'methyl ethyl ketone': 'Metil Etil Cetona',
    'methyl isobutyl ketone': 'Metil Isobutil Cetona',
    'acetic acid': 'Ácido Acético',
    'formic acid': 'Ácido Fórmico',
    'hexane': 'Hexano',
    'n-hexane': 'n-Hexano',
    'heptane': 'Heptano',
    'n-heptane': 'n-Heptano',
    'octane': 'Octano',
    'n-octane': 'n-Octano',
    'benzene': 'Benzeno',
    'toluene': 'Tolueno',
    'chloroform': 'Clorofórmio',
    'acetonitrile': 'Acetonitrila',
    'carbon tetrachloride': 'Tetracloreto de Carbono',
    'nitromethane': 'Nitrometano',
    'nitroethane': 'Nitroetano',
    'ethyl acetate': 'Acetato de Etila',
    'diethylamine': 'Dietilamina',
    'methylcyclopentane': 'Metilciclopentano',
}


def get_uniquac_params(comp1, comp2):
    comp1_lower = comp1.lower()
    comp2_lower = comp2.lower()
    
    if (comp1_lower, comp2_lower) in UNIQUAC_PARAMS:
        return UNIQUAC_PARAMS[(comp1_lower, comp2_lower)]
    
    if (comp2_lower, comp1_lower) in UNIQUAC_PARAMS:
        params = UNIQUAC_PARAMS[(comp2_lower, comp1_lower)]
        return {'a12': params['a21'], 'a21': params['a12']}
    
    return None


def get_uniquac_r_q(comp):
    return UNIQUAC_R_Q.get(comp.lower())


def get_available_components_uniquac():
    '''Retornar componentes com parâmetros UNIQUAC'''
    components = set()
    for (c1, c2) in UNIQUAC_PARAMS.keys():
        components.add(c1)
        components.add(c2)
    
    result = []
    for comp in sorted(components):
        result.append({
            'name': COMPONENT_TRANSLATIONS.get(comp, comp.title()),
            'name_en': comp
        })
    return result
