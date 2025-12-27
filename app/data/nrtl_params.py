'''
Parametros NRTL para sistemas binarios e multicomponentes
tau_ij = a_ij / T (a_ij em Kelvin)
'''

# Sistemas binarios
NRTL_PARAMS = {
    # Alcool-Agua
    ('methanol', 'water'): {'a12': -39.56, 'a21': 196.24, 'alpha': 0.30},
    ('ethanol', 'water'): {'a12': -0.80, 'a21': 0.50, 'alpha': 0.30},
    ('1-propanol', 'water'): {'a12': 179.53, 'a21': 518.36, 'alpha': 0.30},
    ('2-propanol', 'water'): {'a12': 101.30, 'a21': 388.20, 'alpha': 0.30},
    ('1-butanol', 'water'): {'a12': 342.72, 'a21': 756.61, 'alpha': 0.30},
    ('water', 'tce'): {'a12': 5.98775, 'a21': 3.60977, 'alpha': 0.2485},
     ('tce', 'acetone'): {'a12': -0.19920, 'a21': -0.20102, 'alpha': 0.30},
    
    # Cetona-Agua
    ('acetone', 'water'): {'a12': 330.99, 'a21': -100.71, 'alpha': 0.30},
    ('methyl ethyl ketone', 'water'): {'a12': 444.04, 'a21': 13.52, 'alpha': 0.30},
    
    # Acido-Agua
    ('acetic acid', 'water'): {'a12': -54.87, 'a21': 190.36, 'alpha': 0.30},
    ('formic acid', 'water'): {'a12': -120.35, 'a21': 98.24, 'alpha': 0.30},
    
    # Alcanos-Aromaticos
    ('hexane', 'benzene'): {'a12': 0.0, 'a21': 0.0, 'alpha': 0.30},
    ('heptane', 'benzene'): {'a12': 0.0, 'a21': 0.0, 'alpha': 0.30},
    ('octane', 'benzene'): {'a12': -19.27, 'a21': 6.81, 'alpha': 0.30},
    ('hexane', 'toluene'): {'a12': 0.0, 'a21': 0.0, 'alpha': 0.30},
    
    # Alcool-Alcano
    ('ethanol', 'hexane'): {'a12': 626.42, 'a21': 282.67, 'alpha': 0.30},
    ('ethanol', 'heptane'): {'a12': 651.30, 'a21': 291.89, 'alpha': 0.30},
    ('ethanol', 'octane'): {'a12': -123.57, 'a21': 1354.92, 'alpha': 0.30},
    ('methanol', 'hexane'): {'a12': 1075.20, 'a21': 196.38, 'alpha': 0.30},
    ('methanol', 'octane'): {'a12': 379.31, 'a21': -108.42, 'alpha': 0.30},
    
    # Cetona-Alcano
    ('acetone', 'hexane'): {'a12': 122.34, 'a21': 136.53, 'alpha': 0.30},
    ('acetone', 'heptane'): {'a12': 134.56, 'a21': 145.23, 'alpha': 0.30},
    
    # Cetona-Alcool
    ('acetone', 'methanol'): {'a12': -39.76, 'a21': 237.69, 'alpha': 0.30},
    ('acetone', 'ethanol'): {'a12': 47.92, 'a21': 176.05, 'alpha': 0.30},
    
    # Clorados
    ('chloroform', 'acetone'): {'a12': -171.71, 'a21': 93.93, 'alpha': 0.30},
    ('chloroform', 'ethanol'): {'a12': -120.45, 'a21': 350.71, 'alpha': 0.30},
    ('chloroform', 'methanol'): {'a12': -58.87, 'a21': 301.24, 'alpha': 0.30},
    
    # Nitrilas
    ('acetonitrile', 'water'): {'a12': 116.21, 'a21': 398.79, 'alpha': 0.30},
    ('acetonitrile', 'benzene'): {'a12': -40.70, 'a21': 299.79, 'alpha': 0.30},
    
    # Benzeno
    ('benzene', 'ethanol'): {'a12': 471.08, 'a21': 38.28, 'alpha': 0.30},
    ('benzene', 'water'): {'a12': 1271.32, 'a21': 595.42, 'alpha': 0.20},
    ('toluene', 'water'): {'a12': 1346.59, 'a21': 623.27, 'alpha': 0.20},
    
    # Adicionais
    ('acetone', 'benzene'): {'a12': -25.45, 'a21': 89.32, 'alpha': 0.30},
    ('methanol', 'benzene'): {'a12': 523.71, 'a21': 151.83, 'alpha': 0.30},
    ('ethanol', 'benzene'): {'a12': 471.08, 'a21': 38.28, 'alpha': 0.30},
}

# Traducoes para portugues
COMPONENT_TRANSLATIONS = {
    'water': 'Água',
    'methanol': 'Metanol',
    'ethanol': 'Etanol',
    '1-propanol': '1-Propanol',
    '2-propanol': '2-Propanol',
    '1-butanol': '1-Butanol',
    'acetone': 'Acetona',
    'methyl ethyl ketone': 'Metil Etil Cetona',
    'acetic acid': 'Ácido Acético',
    'formic acid': 'Ácido Fórmico',
    'hexane': 'Hexano',
    'heptane': 'Heptano',
    'octane': 'Octano',
    'benzene': 'Benzeno',
    'toluene': 'Tolueno',
    'chloroform': 'Clorofórmio',
    'acetonitrile': 'Acetonitrila',
    'tce': '1,1,2-Tricloroetano',
}

def get_nrtl_params(comp1, comp2):
    '''Obter parametros NRTL para um par binario'''
    comp1_lower = comp1.lower()
    comp2_lower = comp2.lower()
    
    if (comp1_lower, comp2_lower) in NRTL_PARAMS:
        return NRTL_PARAMS[(comp1_lower, comp2_lower)]
    
    if (comp2_lower, comp1_lower) in NRTL_PARAMS:
        params = NRTL_PARAMS[(comp2_lower, comp1_lower)]
        return {'a12': params['a21'], 'a21': params['a12'], 'alpha': params['alpha']}
    
    return None

def get_available_components_nrtl():
    '''Retornar lista de componentes que tem parametros NRTL'''
    components = set()
    for (c1, c2) in NRTL_PARAMS.keys():
        components.add(c1)
        components.add(c2)
    
    # Retornar com nomes em portugues
    result = []
    for comp in sorted(components):
        result.append({
            'name': COMPONENT_TRANSLATIONS.get(comp, comp.title()),
            'name_en': comp
        })
    return result

# Sistemas ternarios comuns (todos os pares binarios)
# Etanol + Agua + Acetona
# (ethanol, water), (acetone, water), (acetone, ethanol) ja existem

# Metanol + Etanol + Agua
# (methanol, water), (ethanol, water) ja existem
NRTL_PARAMS[('methanol', 'ethanol')] = {'a12': -48.92, 'a21': 75.36, 'alpha': 0.30}

# Benzeno + Tolueno + Hexano
NRTL_PARAMS[('benzene', 'toluene')] = {'a12': 0.0, 'a21': 0.0, 'alpha': 0.30}

# Acetona + Metanol + Água (ja tem todos)
# Acetona + Cloroformio + Benzeno
NRTL_PARAMS[('chloroform', 'benzene')] = {'a12': -12.34, 'a21': 45.67, 'alpha': 0.30}
# adicione no final do NRTL_PARAMS
NRTL_PARAMS[('compa', 'compb')] = {'a12': 1000.0, 'a21': -1000.0, 'alpha': 0.30}

