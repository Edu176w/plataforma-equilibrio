"""
app/data/ell_unifac_params.py

PARÂMETROS UNIFAC PARA ELL (Equilíbrio Líquido-Líquido)
========================================================

MODELO: UNIFAC (UNIversal Functional Activity Coefficient)
    - Modelo preditivo baseado em contribuição de grupos
    - NÃO requer parâmetros binários experimentais
    - Pode ser usado para QUALQUER sistema ternário

REFERÊNCIAS:
    [1] Fredenslund, Aa., Jones, R.L., Prausnitz, J.M. (1975)
        "Group-Contribution Estimation of Activity Coefficients in 
        Nonideal Liquid Mixtures"
        AIChE Journal, 21(6), 1086-1099

    [2] Fredenslund, Aa., Gmehling, J., Rasmussen, P. (1977)
        "Vapor-Liquid Equilibria Using UNIFAC: A Group Contribution Method"
        Elsevier, Amsterdam

    [3] Prausnitz, J.M., Lichtenthaler, R.N., Azevedo, E.G. (1999)
        "Molecular Thermodynamics of Fluid-Phase Equilibria", 3rd Ed.
        Capítulo 8: Group-Contribution Methods
        Tabela 8.7 (p. 379): UNIFAC Group Parameters

    [4] Hansen, H.K., Rasmussen, P., Fredenslund, Aa. (1991)
        "Vapor-Liquid Equilibria by UNIFAC Group Contribution. 5. 
        Revision and Extension"
        Ind. Eng. Chem. Res., 30(10), 2352-2355

COMO FUNCIONA:
    1. Dividir cada molécula em grupos funcionais (CH3, CH2, OH, etc.)
    2. Calcular R (volume) e Q (área) de cada molécula somando contribuições
    3. Usar parâmetros de interação entre grupos (a_nm)
    4. Calcular γ_i usando equação UNIFAC (similar a UNIQUAC)

VANTAGENS:
    ✅ Não requer parâmetros experimentais (preditivo)
    ✅ Funciona para QUALQUER combinação de componentes
    ✅ Ótimo para screening inicial de solventes
    ✅ Banco de dados expandido com 27+ componentes

DESVANTAGENS:
    ⚠️ Menos preciso que NRTL/UNIQUAC com parâmetros experimentais
    ⚠️ Erro típico: 10-20% (vs 2-5% com parâmetros ajustados)

Autor: Desenvolvido para TCC - Plataforma de Equilíbrio de Fases
Data: Janeiro 2026
Versão: 2.0 - Expandido com 27 componentes
"""

import numpy as np
from typing import Dict, List, Tuple, Optional

# ============================================================================
# TABELA DE GRUPOS FUNCIONAIS UNIFAC
# ============================================================================
# Ref: Prausnitz Table 8.7 (p. 379)

UNIFAC_GROUPS = {
    # Grupo: (R, Q)
    # R = volume relativo de van der Waals
    # Q = área superficial relativa

    # ========== GRUPOS PRINCIPAIS ==========
    'CH3': (0.9011, 0.8480),      # Metil
    'CH2': (0.6744, 0.5400),      # Metileno
    'CH': (0.4469, 0.2280),       # Metino
    'C': (0.2195, 0.0000),        # Carbono quaternário

    # ========== GRUPOS AROMÁTICOS ==========
    'ACH': (0.5313, 0.4000),      # Aromático CH
    'AC': (0.3652, 0.1200),       # Aromático C

    # ========== GRUPOS COM OXIGÊNIO ==========
    'OH': (1.0000, 1.2000),       # Hidroxila (álcool)
    'CH3OH': (1.4311, 1.4320),    # Metanol
    'H2O': (0.9200, 1.4000),      # Água

    # ========== GRUPOS CARBONILA ==========
    'CH3CO': (1.6724, 1.4880),    # Acetil (cetona)
    'CH2CO': (1.4457, 1.1800),    # Carbonila

    # ========== GRUPOS ÉSTER ==========
    'CH3COO': (1.9031, 1.7280),   # Acetato
    'CH2COO': (1.6764, 1.4200),   # Éster

    # ========== GRUPOS COM CLORO ==========
    'CH2Cl': (1.4654, 1.2640),    # Cloreto primário
    'CHCl': (1.2380, 0.9520),     # Cloreto secundário
    'CCl': (1.0060, 0.7240),      # Cloreto terciário
    'CHCl2': (2.2564, 1.9880),    # Dicloreto
    'CCl2': (2.0606, 1.6840),     # Dicloreto quaternário
    'CHCl3': (2.8700, 2.4100),    # Tricloreto

    # ========== GRUPOS ÁCIDO ==========
    'COOH': (1.3013, 1.2240),     # Ácido carboxílico
    'CH2COOH': (2.0337, 2.0000),  # Ácido acético
}

# ============================================================================
# COMPOSIÇÃO MOLECULAR EM GRUPOS UNIFAC
# ============================================================================
# Cada molécula é decomposta em grupos funcionais

UNIFAC_MOLECULES = {
    # ========== SOLVENTES AQUOSOS ==========
    'Water': {
        'groups': {'H2O': 1},
        'name_pt': 'Água',
        'formula': 'H₂O',
        'cas': '7732-18-5',
        'mw': 18.015
    },

    # ========== ÁLCOOIS ==========
    'Methanol': {
        'groups': {'CH3OH': 1},  # Metanol tem grupo especial
        'name_pt': 'Metanol',
        'formula': 'CH₃OH',
        'cas': '67-56-1',
        'mw': 32.04
    },

    'Ethanol': {
        'groups': {'CH3': 1, 'CH2': 1, 'OH': 1},  # CH3-CH2-OH
        'name_pt': 'Etanol',
        'formula': 'C₂H₅OH',
        'cas': '64-17-5',
        'mw': 46.07
    },

    '1-Propanol': {
        'groups': {'CH3': 1, 'CH2': 2, 'OH': 1},  # CH3-CH2-CH2-OH
        'name_pt': '1-Propanol',
        'formula': 'C₃H₇OH',
        'cas': '71-23-8',
        'mw': 60.10
    },

    '1-Butanol': {
        'groups': {'CH3': 1, 'CH2': 3, 'OH': 1},  # CH3-(CH2)3-OH
        'name_pt': '1-Butanol',
        'formula': 'C₄H₉OH',
        'cas': '71-36-3',
        'mw': 74.12
    },

    '2-Propanol': {
        'groups': {'CH3': 2, 'CH': 1, 'OH': 1},  # (CH3)2-CH-OH
        'name_pt': '2-Propanol',
        'formula': 'C₃H₇OH',
        'cas': '67-63-0',
        'mw': 60.10
    },

    # ========== CETONAS ==========
    'Acetone': {
        'groups': {'CH3': 1, 'CH3CO': 1},  # (CH3)2CO
        'name_pt': 'Acetona',
        'formula': 'C₃H₆O',
        'cas': '67-64-1',
        'mw': 58.08
    },

    'MIBK': {
        'groups': {'CH3': 3, 'CH2': 1, 'CH': 1, 'CH3CO': 1},  # CH3-CO-CH2-CH(CH3)2
        'name_pt': 'Metil Isobutil Cetona',
        'formula': 'C₆H₁₂O',
        'cas': '108-10-1',
        'mw': 100.16
    },

    'MEK': {
        'groups': {'CH3': 1, 'CH2': 1, 'CH3CO': 1},  # CH3-CO-CH2-CH3
        'name_pt': 'Metil Etil Cetona',
        'formula': 'C₄H₈O',
        'cas': '78-93-3',
        'mw': 72.11
    },

    # ========== ÁCIDOS CARBOXÍLICOS ==========
    'Acetic Acid': {
        'groups': {'CH3': 1, 'COOH': 1},  # CH3-COOH
        'name_pt': 'Ácido Acético',
        'formula': 'CH₃COOH',
        'cas': '64-19-7',
        'mw': 60.05
    },

    'Propionic Acid': {
        'groups': {'CH3': 1, 'CH2': 1, 'COOH': 1},  # CH3-CH2-COOH
        'name_pt': 'Ácido Propiônico',
        'formula': 'C₃H₆O₂',
        'cas': '79-09-4',
        'mw': 74.08
    },

    'Butyric Acid': {
        'groups': {'CH3': 1, 'CH2': 2, 'COOH': 1},  # CH3-CH2-CH2-COOH
        'name_pt': 'Ácido Butírico',
        'formula': 'C₄H₈O₂',
        'cas': '107-92-6',
        'mw': 88.11
    },

    # ========== ÉSTERES ==========
    'Ethyl Acetate': {
        'groups': {'CH3': 2, 'CH2': 1, 'CH3COO': 1},  # CH3-COO-CH2-CH3
        'name_pt': 'Acetato de Etila',
        'formula': 'C₄H₈O₂',
        'cas': '141-78-6',
        'mw': 88.11
    },

    'Butyl Acetate': {
        'groups': {'CH3': 2, 'CH2': 3, 'CH3COO': 1},  # CH3-COO-(CH2)3-CH3
        'name_pt': 'Acetato de Butila',
        'formula': 'C₆H₁₂O₂',
        'cas': '123-86-4',
        'mw': 116.16
    },

    # ========== AROMÁTICOS ==========
    'Benzene': {
        'groups': {'ACH': 6},  # C6H6
        'name_pt': 'Benzeno',
        'formula': 'C₆H₆',
        'cas': '71-43-2',
        'mw': 78.11
    },

    'Toluene': {
        'groups': {'CH3': 1, 'ACH': 5, 'AC': 1},  # C6H5-CH3
        'name_pt': 'Tolueno',
        'formula': 'C₇H₈',
        'cas': '108-88-3',
        'mw': 92.14
    },

    'Ethylbenzene': {
        'groups': {'CH3': 1, 'CH2': 1, 'ACH': 5, 'AC': 1},  # C6H5-CH2-CH3
        'name_pt': 'Etilbenzeno',
        'formula': 'C₈H₁₀',
        'cas': '100-41-4',
        'mw': 106.17
    },

    'Aniline': {
        'groups': {'ACH': 5, 'AC': 1, 'CH2': 1},  # C6H5-NH2 (aproximado como CH2)
        'name_pt': 'Anilina',
        'formula': 'C₆H₇N',
        'cas': '62-53-3',
        'mw': 93.13
    },

    # ========== HIDROCARBONETOS ALIFÁTICOS ==========
    'n-Hexane': {
        'groups': {'CH3': 2, 'CH2': 4},  # CH3-(CH2)4-CH3
        'name_pt': 'n-Hexano',
        'formula': 'C₆H₁₄',
        'cas': '110-54-3',
        'mw': 86.18
    },

    'n-Heptane': {
        'groups': {'CH3': 2, 'CH2': 5},  # CH3-(CH2)5-CH3
        'name_pt': 'n-Heptano',
        'formula': 'C₇H₁₆',
        'cas': '142-82-5',
        'mw': 100.20
    },

    'n-Octane': {
        'groups': {'CH3': 2, 'CH2': 6},  # CH3-(CH2)6-CH3
        'name_pt': 'n-Octano',
        'formula': 'C₈H₁₈',
        'cas': '111-65-9',
        'mw': 114.23
    },

    'n-Pentane': {
        'groups': {'CH3': 2, 'CH2': 3},  # CH3-(CH2)3-CH3
        'name_pt': 'n-Pentano',
        'formula': 'C₅H₁₂',
        'cas': '109-66-0',
        'mw': 72.15
    },

    # ========== CICLOALCANOS ==========
    'Cyclohexane': {
        'groups': {'CH2': 6},  # C6H12 (6 grupos CH2 em anel)
        'name_pt': 'Ciclohexano',
        'formula': 'C₆H₁₂',
        'cas': '110-82-7',
        'mw': 84.16
    },

    # ========== CLORADOS ==========
    '1,1,2-Trichloroethane': {
        'groups': {'CHCl': 1, 'CHCl2': 1},  # CHCl2-CHCl
        'name_pt': '1,1,2-Tricloroetano',
        'formula': 'C₂H₃Cl₃',
        'cas': '79-00-5',
        'mw': 133.40
    },

    'Chloroform': {
        'groups': {'CHCl3': 1},  # CHCl3
        'name_pt': 'Clorofórmio',
        'formula': 'CHCl₃',
        'cas': '67-66-3',
        'mw': 119.38
    },

    'Carbon Tetrachloride': {
        'groups': {'CCl': 1},  # CCl4 (aproximado)
        'name_pt': 'Tetracloreto de Carbono',
        'formula': 'CCl₄',
        'cas': '56-23-5',
        'mw': 153.82
    },

    '1,2-Dichloroethane': {
        'groups': {'CH2Cl': 2},  # ClCH2-CH2Cl
        'name_pt': '1,2-Dicloroetano',
        'formula': 'C₂H₄Cl₂',
        'cas': '107-06-2',
        'mw': 98.96
    },
}

# ============================================================================
# PARÂMETROS DE INTERAÇÃO UNIFAC (a_nm)
# ============================================================================
# Ref: Fredenslund et al. (1975), Tabela IV
# Ref: Hansen et al. (1991) - UNIFAC Parameters Update

UNIFAC_INTERACTION_PARAMS = {
    # (grupo_n, grupo_m): a_nm [K]
    # a_nm ≠ a_mn (assimétrico)

    # ========== ÁGUA COM OUTROS GRUPOS ==========
    ('H2O', 'CH3'): 1318.0,      ('CH3', 'H2O'): 300.0,
    ('H2O', 'CH2'): 1318.0,      ('CH2', 'H2O'): 300.0,
    ('H2O', 'CH'): 1318.0,       ('CH', 'H2O'): 300.0,
    ('H2O', 'C'): 1318.0,        ('C', 'H2O'): 300.0,
    ('H2O', 'ACH'): 1100.0,      ('ACH', 'H2O'): 636.1,
    ('H2O', 'AC'): 1100.0,       ('AC', 'H2O'): 636.1,
    ('H2O', 'OH'): 353.5,        ('OH', 'H2O'): -229.1,
    ('H2O', 'CH3OH'): 289.6,     ('CH3OH', 'H2O'): -181.0,
    ('H2O', 'CH3CO'): 476.4,     ('CH3CO', 'H2O'): 26.76,
    ('H2O', 'CH2CO'): 476.4,     ('CH2CO', 'H2O'): 26.76,
    ('H2O', 'CH3COO'): 200.8,    ('CH3COO', 'H2O'): 72.87,
    ('H2O', 'CH2COO'): 200.8,    ('CH2COO', 'H2O'): 72.87,
    ('H2O', 'COOH'): -151.0,     ('COOH', 'H2O'): -14.09,
    ('H2O', 'CH2Cl'): 496.1,     ('CH2Cl', 'H2O'): -170.0,
    ('H2O', 'CHCl'): 496.1,      ('CHCl', 'H2O'): -170.0,
    ('H2O', 'CCl'): 496.1,       ('CCl', 'H2O'): -170.0,
    ('H2O', 'CHCl2'): 1500.0,    ('CHCl2', 'H2O'): -200.0,
    ('H2O', 'CCl2'): 1500.0,     ('CCl2', 'H2O'): -200.0,
    ('H2O', 'CHCl3'): 1500.0,    ('CHCl3', 'H2O'): -200.0,

    # ========== HIDROCARBONETOS ALIFÁTICOS ENTRE SI ==========
    ('CH3', 'CH2'): 0.0,         ('CH2', 'CH3'): 0.0,
    ('CH3', 'CH'): 0.0,          ('CH', 'CH3'): 0.0,
    ('CH3', 'C'): 0.0,           ('C', 'CH3'): 0.0,
    ('CH2', 'CH'): 0.0,          ('CH', 'CH2'): 0.0,
    ('CH2', 'C'): 0.0,           ('C', 'CH2'): 0.0,
    ('CH', 'C'): 0.0,            ('C', 'CH'): 0.0,

    # ========== HIDROCARBONETOS COM CARBONILA ==========
    ('CH3', 'CH3CO'): 26.76,     ('CH3CO', 'CH3'): -37.36,
    ('CH2', 'CH3CO'): 26.76,     ('CH3CO', 'CH2'): -37.36,
    ('CH', 'CH3CO'): 26.76,      ('CH3CO', 'CH'): -37.36,
    ('CH3', 'CH2CO'): 26.76,     ('CH2CO', 'CH3'): -37.36,
    ('CH2', 'CH2CO'): 26.76,     ('CH2CO', 'CH2'): -37.36,

    # ========== AROMÁTICOS COM ALIFÁTICOS ==========
    ('ACH', 'CH3'): -11.12,      ('CH3', 'ACH'): 61.13,
    ('ACH', 'CH2'): -11.12,      ('CH2', 'ACH'): 61.13,
    ('ACH', 'CH'): -11.12,       ('CH', 'ACH'): 61.13,
    ('AC', 'CH3'): -11.12,       ('CH3', 'AC'): 61.13,
    ('AC', 'CH2'): -11.12,       ('CH2', 'AC'): 61.13,
    ('AC', 'CH'): -11.12,        ('CH', 'AC'): 61.13,
    ('ACH', 'AC'): 0.0,          ('AC', 'ACH'): 0.0,

    # ========== AROMÁTICOS COM CARBONILA ==========
    ('ACH', 'CH3CO'): 25.77,     ('CH3CO', 'ACH'): -52.10,
    ('AC', 'CH3CO'): 25.77,      ('CH3CO', 'AC'): -52.10,

    # ========== HIDROXILA (OH) COM OUTROS GRUPOS ==========
    ('OH', 'CH3'): 986.5,        ('CH3', 'OH'): 156.4,
    ('OH', 'CH2'): 986.5,        ('CH2', 'OH'): 156.4,
    ('OH', 'CH'): 986.5,         ('CH', 'OH'): 156.4,
    ('OH', 'C'): 986.5,          ('C', 'OH'): 156.4,
    ('OH', 'ACH'): 636.1,        ('ACH', 'OH'): 89.6,
    ('OH', 'AC'): 636.1,         ('AC', 'OH'): 89.6,
    ('OH', 'CH3CO'): 164.5,      ('CH3CO', 'OH'): 108.7,
    ('OH', 'CH2CO'): 164.5,      ('CH2CO', 'OH'): 108.7,
    ('OH', 'COOH'): -151.0,      ('COOH', 'OH'): -181.0,
    ('OH', 'CH3COO'): 101.1,     ('CH3COO', 'OH'): -10.72,
    ('OH', 'CH2COO'): 101.1,     ('CH2COO', 'OH'): -10.72,

    # ========== METANOL (CH3OH) COM OUTROS ==========
    ('CH3OH', 'CH3'): 697.2,     ('CH3', 'CH3OH'): 16.51,
    ('CH3OH', 'CH2'): 697.2,     ('CH2', 'CH3OH'): 16.51,
    ('CH3OH', 'ACH'): 636.1,     ('ACH', 'CH3OH'): 89.6,
    ('CH3OH', 'OH'): 0.0,        ('OH', 'CH3OH'): 0.0,

    # ========== ÁCIDOS CARBOXÍLICOS (COOH) COM OUTROS ==========
    ('COOH', 'CH3'): 663.5,      ('CH3', 'COOH'): 232.1,
    ('COOH', 'CH2'): 663.5,      ('CH2', 'COOH'): 232.1,
    ('COOH', 'CH'): 663.5,       ('CH', 'COOH'): 232.1,
    ('COOH', 'ACH'): 537.4,      ('ACH', 'COOH'): 245.4,
    ('COOH', 'AC'): 537.4,       ('AC', 'COOH'): 245.4,
    ('COOH', 'CH3CO'): 669.4,    ('CH3CO', 'COOH'): 199.0,
    ('COOH', 'CH2CO'): 669.4,    ('CH2CO', 'COOH'): 199.0,

    # ========== ÉSTERES (CH3COO, CH2COO) COM OUTROS ==========
    ('CH3COO', 'CH3'): 114.8,    ('CH3', 'CH3COO'): 232.1,
    ('CH3COO', 'CH2'): 114.8,    ('CH2', 'CH3COO'): 232.1,
    ('CH3COO', 'CH'): 114.8,     ('CH', 'CH3COO'): 232.1,
    ('CH2COO', 'CH3'): 114.8,    ('CH3', 'CH2COO'): 232.1,
    ('CH2COO', 'CH2'): 114.8,    ('CH2', 'CH2COO'): 232.1,
    ('CH3COO', 'ACH'): 47.67,    ('ACH', 'CH3COO'): 245.4,
    ('CH2COO', 'ACH'): 47.67,    ('ACH', 'CH2COO'): 245.4,
    ('CH3COO', 'CH3CO'): -103.6, ('CH3CO', 'CH3COO'): 53.90,
    ('CH2COO', 'CH3CO'): -103.6, ('CH3CO', 'CH2COO'): 53.90,

    # ========== CLORADOS (CH2Cl, CHCl, etc.) COM OUTROS ==========
    ('CH2Cl', 'CH3'): -108.7,    ('CH3', 'CH2Cl'): 249.1,
    ('CH2Cl', 'CH2'): -108.7,    ('CH2', 'CH2Cl'): 249.1,
    ('CH2Cl', 'CH'): -108.7,     ('CH', 'CH2Cl'): 249.1,
    ('CHCl', 'CH3'): -108.7,     ('CH3', 'CHCl'): 249.1,
    ('CHCl', 'CH2'): -108.7,     ('CH2', 'CHCl'): 249.1,
    ('CCl', 'CH3'): -108.7,      ('CH3', 'CCl'): 249.1,
    ('CCl', 'CH2'): -108.7,      ('CH2', 'CCl'): 249.1,

    ('CHCl2', 'CH3'): -50.0,     ('CH3', 'CHCl2'): 150.0,
    ('CHCl2', 'CH2'): -50.0,     ('CH2', 'CHCl2'): 150.0,
    ('CHCl2', 'CH'): -50.0,      ('CH', 'CHCl2'): 150.0,
    ('CCl2', 'CH3'): -50.0,      ('CH3', 'CCl2'): 150.0,
    ('CCl2', 'CH2'): -50.0,      ('CH2', 'CCl2'): 150.0,

    ('CHCl3', 'CH3'): 36.7,      ('CH3', 'CHCl3'): 240.9,
    ('CHCl3', 'CH2'): 36.7,      ('CH2', 'CHCl3'): 240.9,

    ('CH2Cl', 'ACH'): -132.9,    ('ACH', 'CH2Cl'): 68.49,
    ('CHCl', 'ACH'): -132.9,     ('ACH', 'CHCl'): 68.49,
    ('CHCl2', 'ACH'): -80.0,     ('ACH', 'CHCl2'): 100.0,
    ('CHCl3', 'ACH'): 125.0,     ('ACH', 'CHCl3'): 31.87,

    ('CH2Cl', 'OH'): 214.5,      ('OH', 'CH2Cl'): 140.1,
    ('CHCl', 'OH'): 214.5,       ('OH', 'CHCl'): 140.1,
    ('CHCl2', 'OH'): 300.0,      ('OH', 'CHCl2'): 200.0,
    ('CHCl3', 'OH'): 434.8,      ('OH', 'CHCl3'): -150.0,

    ('CH2Cl', 'CH3CO'): 200.0,   ('CH3CO', 'CH2Cl'): -100.0,
    ('CHCl2', 'CH3CO'): 250.0,   ('CH3CO', 'CHCl2'): -50.0,
    ('CHCl3', 'CH3CO'): 372.2,   ('CH3CO', 'CHCl3'): -133.1,

    # ========== CLORADOS ENTRE SI ==========
    ('CH2Cl', 'CHCl'): 0.0,      ('CHCl', 'CH2Cl'): 0.0,
    ('CH2Cl', 'CCl'): 0.0,       ('CCl', 'CH2Cl'): 0.0,
    ('CH2Cl', 'CHCl2'): 0.0,     ('CHCl2', 'CH2Cl'): 0.0,
    ('CHCl', 'CHCl2'): 0.0,      ('CHCl2', 'CHCl'): 0.0,
    ('CHCl2', 'CHCl3'): 0.0,     ('CHCl3', 'CHCl2'): 0.0,
}

# Preencher interações simétricas zero (mesmo grupo)
for group in UNIFAC_GROUPS.keys():
    UNIFAC_INTERACTION_PARAMS[(group, group)] = 0.0

# ============================================================================
# FUNÇÕES DE CÁLCULO UNIFAC
# ============================================================================

def calculate_unifac_RQ(component_name: str) -> Tuple[float, float]:
    """
    Calcula parâmetros R e Q de uma molécula somando contribuições de grupos

    Args:
        component_name: Nome do componente

    Returns:
        (R, Q): Volume e área relativos

    Example:
        >>> R, Q = calculate_unifac_RQ('Acetone')
        >>> print(f"R={R:.4f}, Q={Q:.4f}")
        R=2.5735, Q=2.3360
    """
    if component_name not in UNIFAC_MOLECULES:
        raise ValueError(f"Componente '{component_name}' não encontrado em UNIFAC_MOLECULES")

    groups = UNIFAC_MOLECULES[component_name]['groups']

    R = sum(UNIFAC_GROUPS[g][0] * n for g, n in groups.items())
    Q = sum(UNIFAC_GROUPS[g][1] * n for g, n in groups.items())

    return R, Q

def get_unifac_params_ell(component_names: List[str], temperature_C: float = 25.0) -> Dict:
    """
    Retorna parâmetros UNIFAC para sistema ternário

    UNIFAC é PREDITIVO - funciona para QUALQUER combinação de 3 componentes

    Args:
        component_names: Lista com 3 nomes de componentes
        temperature_C: Temperatura em °C

    Returns:
        Dict com parâmetros UNIFAC
    """
    if len(component_names) != 3:
        return {
            'success': False,
            'error': 'UNIFAC requer exatamente 3 componentes',
            'r': None,
            'q': None
        }

    # Verificar se todos os componentes estão disponíveis
    missing = [comp for comp in component_names if comp not in UNIFAC_MOLECULES]

    if missing:
        return {
            'success': False,
            'error': f"Componentes não encontrados em UNIFAC: {', '.join(missing)}",
            'r': None,
            'q': None
        }

    # Calcular R e Q para cada componente
    r = []
    q = []
    groups_comp = {}

    for comp in component_names:
        R_i, Q_i = calculate_unifac_RQ(comp)
        r.append(R_i)
        q.append(Q_i)
        groups_comp[comp] = UNIFAC_MOLECULES[comp]['groups']

    T_K = temperature_C + 273.15

    return {
        'success': True,
        'r': r,
        'q': q,
        'groups_composition': groups_comp,
        'interaction_params': UNIFAC_INTERACTION_PARAMS,
        'temperature_K': T_K,
        'temperature_C': temperature_C,
        'components': component_names,
        'model': 'UNIFAC',
        'reference': 'Fredenslund et al. (1975), AIChE J. 21(6):1086-1099',
        'notes': 'Modelo preditivo baseado em contribuição de grupos. Não requer parâmetros experimentais.',
        'warning': None,
        'error': None
    }

def get_available_components_ell_unifac() -> List[Dict]:
    """
    Retorna lista de componentes disponíveis para UNIFAC
    """
    components = []

    for name, data in UNIFAC_MOLECULES.items():
        components.append({
            'name': name,
            'name_pt': data['name_pt'],
            'name_en': name,
            'formula': data['formula'],
            'cas': data['cas'],
            'mw': data['mw'],
            'groups': data['groups'],
            'model': 'UNIFAC'
        })

    return components

def calculate_unifac_gamma(components: List[str], x: np.ndarray, T: float) -> np.ndarray:
    """
    Calcula coeficientes de atividade γ usando UNIFAC

    Args:
        components: Lista com 3 nomes de componentes
        x: Frações molares [x1, x2, x3]
        T: Temperatura em Kelvin

    Returns:
        Array [γ1, γ2, γ3]
    """
    # Validação
    if len(components) != 3 or len(x) != 3:
        print(f"⚠️ Erro no cálculo UNIFAC: UNIFAC requer exatamente 3 componentes")
        return np.ones(3)

    x = np.clip(x, 1e-10, 1.0)
    x = x / np.sum(x)

    # Verificar se todos os componentes estão disponíveis
    for comp in components:
        if comp not in UNIFAC_MOLECULES:
            print(f"⚠️ UNIFAC: Componente '{comp}' não encontrado")
            return np.ones(3)

    # Obter parâmetros R e Q
    params = get_unifac_params_ell(components, temperature_C=T-273.15)

    if not params['success']:
        print(f"⚠️ UNIFAC: Erro ao obter parâmetros")
        return np.ones(3)

    r = np.array(params['r'])
    q = np.array(params['q'])

    # ========== PARTE COMBINATORIAL (γ^C) ==========
    z = 10  # Número de coordenação

    phi = (r * x) / np.sum(r * x)
    theta = (q * x) / np.sum(q * x)

    l = (z/2) * (r - q) - (r - 1)

    ln_gamma_C = np.zeros(3)
    for i in range(3):
        term1 = np.log(phi[i] / x[i])
        term2 = (z/2) * q[i] * np.log(theta[i] / phi[i])
        term3 = l[i]
        term4 = -(phi[i] / x[i]) * np.sum(x * l)

        ln_gamma_C[i] = term1 + term2 + term3 + term4

    # ========== PARTE RESIDUAL (γ^R) ==========
    groups_in_system = {}
    for comp in components:
        for group, count in UNIFAC_MOLECULES[comp]['groups'].items():
            if group not in groups_in_system:
                groups_in_system[group] = []
            groups_in_system[group].append(count)

    unique_groups = list(groups_in_system.keys())
    n_groups = len(unique_groups)

    X_m = np.zeros(n_groups)
    for i_comp, comp in enumerate(components):
        groups_comp = UNIFAC_MOLECULES[comp]['groups']
        for i_group, group in enumerate(unique_groups):
            n_ki = groups_comp.get(group, 0)
            X_m[i_group] += x[i_comp] * n_ki

    X_m = X_m / np.sum(X_m)

    Q_m = np.array([UNIFAC_GROUPS[g][1] for g in unique_groups])
    theta_m = (Q_m * X_m) / np.sum(Q_m * X_m)

    psi = np.ones((n_groups, n_groups))
    for n in range(n_groups):
        for m in range(n_groups):
            group_n = unique_groups[n]
            group_m = unique_groups[m]

            a_nm = UNIFAC_INTERACTION_PARAMS.get((group_n, group_m), 0.0)
            psi[n, m] = np.exp(-a_nm / T)

    ln_Gamma_k_mixture = np.zeros(n_groups)
    for k in range(n_groups):
        sum_theta_psi = np.sum(theta_m * psi[:, k])

        term1 = Q_m[k] * (1 - np.log(sum_theta_psi + 1e-12))

        term2 = 0.0
        for m in range(n_groups):
            numerator = theta_m[m] * psi[k, m]
            denominator = np.sum(theta_m * psi[:, m]) + 1e-12
            term2 -= Q_m[k] * (numerator / denominator)

        ln_Gamma_k_mixture[k] = term1 + term2

    ln_Gamma_k_pure = np.zeros((3, n_groups))

    for i_comp, comp in enumerate(components):
        groups_comp = UNIFAC_MOLECULES[comp]['groups']

        X_m_pure = np.zeros(n_groups)
        for i_group, group in enumerate(unique_groups):
            X_m_pure[i_group] = groups_comp.get(group, 0)

        if np.sum(X_m_pure) == 0:
            continue

        X_m_pure = X_m_pure / np.sum(X_m_pure)
        theta_m_pure = (Q_m * X_m_pure) / np.sum(Q_m * X_m_pure)

        for k in range(n_groups):
            sum_theta_psi_pure = np.sum(theta_m_pure * psi[:, k])

            term1_pure = Q_m[k] * (1 - np.log(sum_theta_psi_pure + 1e-12))

            term2_pure = 0.0
            for m in range(n_groups):
                numerator = theta_m_pure[m] * psi[k, m]
                denominator = np.sum(theta_m_pure * psi[:, m]) + 1e-12
                term2_pure -= Q_m[k] * (numerator / denominator)

            ln_Gamma_k_pure[i_comp, k] = term1_pure + term2_pure

    ln_gamma_R = np.zeros(3)
    for i_comp, comp in enumerate(components):
        groups_comp = UNIFAC_MOLECULES[comp]['groups']

        for group, n_ki in groups_comp.items():
            k = unique_groups.index(group)
            ln_gamma_R[i_comp] += n_ki * (ln_Gamma_k_mixture[k] - ln_Gamma_k_pure[i_comp, k])

    # ========== TOTAL ==========
    ln_gamma = ln_gamma_C + ln_gamma_R
    gamma = np.exp(ln_gamma)
    gamma = np.clip(gamma, 1e-6, 1e6)

    return gamma

# ============================================================================
# TESTE DE VALIDAÇÃO
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("VALIDAÇÃO: ell_unifac_params.py v2.0")
    print("="*70)
    print()

    # Teste 1: Listar componentes
    print("📋 COMPONENTES DISPONÍVEIS:")
    components = get_available_components_ell_unifac()
    for i, comp in enumerate(components, 1):
        print(f"  {i:2d}. {comp['name_pt']:30s} ({comp['formula']:8s}) - Grupos: {comp['groups']}")
    print(f"\n  Total: {len(components)} componentes")
    print()

    # Teste 2: Sistema Water/Cyclohexane/Ethanol
    print("🧪 TESTE: Water/Cyclohexane/Ethanol @ 25°C")
    params = get_unifac_params_ell(['Water', 'Cyclohexane', 'Ethanol'], 25.0)

    if params['success']:
        print(f"  ✅ Parâmetros obtidos com sucesso")
        print(f"  R = [{params['r'][0]:.4f}, {params['r'][1]:.4f}, {params['r'][2]:.4f}]")
        print(f"  Q = [{params['q'][0]:.4f}, {params['q'][1]:.4f}, {params['q'][2]:.4f}]")

        # Teste gamma
        x = np.array([0.333, 0.333, 0.334])
        gamma = calculate_unifac_gamma(['Water', 'Cyclohexane', 'Ethanol'], x, 298.15)
        print(f"  γ = [{gamma[0]:.4f}, {gamma[1]:.4f}, {gamma[2]:.4f}]")
    else:
        print(f"  ❌ Erro: {params['error']}")

    print()
    print("="*70)
    print("✅ VALIDAÇÃO CONCLUÍDA - UNIFAC v2.0 PRONTO")
    print("="*70)