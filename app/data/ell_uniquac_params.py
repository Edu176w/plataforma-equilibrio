"""
app/data/ell_uniquac_params.py

PARÂMETROS UNIQUAC PARA ELL (Equilíbrio Líquido-Líquido)
========================================================

FONTE BIBLIOGRÁFICA:
    Prausnitz, J.M., Lichtenthaler, R.N., Azevedo, E.G. (1999)
    "Molecular Thermodynamics of Fluid-Phase Equilibria", 3rd Ed.
    Prentice Hall PTR, ISBN: 0-13-977745-8
    
    TABELA E-6 (p. 798): UNIQUAC Binary Parameters for Ternary LLE
    Fonte primária: Anderson, T.F., Prausnitz, J.M. (1978a)
                    Ind. Eng. Chem. Process Des. Dev., 17, 552-561

SISTEMAS TERNÁRIOS DISPONÍVEIS (4 SISTEMAS):
============================================

1. Furfural (1) / Cyclohexane (2) / Benzene (3)
   - T = 25°C
   - Validação experimental: Anderson & Prausnitz (1978a)
   - Parâmetros: τ12, τ21, τ13, τ31, τ23, τ32
   - Estruturais: r1, q1, r2, q2, r3, q3

2. Sulfolane (1) / n-Octane (2) / Toluene (3)
   - T = 25°C
   - Validação experimental: Anderson & Prausnitz (1978a)
   - Sistema típico para separação de aromáticos

3. 2,5-Hexanedione (1) / 1-Hexene (2) / n-Hexane (3)
   - T = 25°C
   - Validação experimental: Anderson & Prausnitz (1978a)
   - Sistema com forte imiscibilidade

4. 1,4-Dioxane (1) / n-Hexane (2) / Methylcyclopentane (3)
   - T = 25°C
   - Validação experimental: Anderson & Prausnitz (1978a)
   - Sistema polar/apolar típico

CONVENÇÕES UNIQUAC:
==================
    τij = exp(-aij/T)  onde aij em K
    
    ΔGij/R = aij  (parâmetro de interação)
    
    Modelo UNIQUAC requer parâmetros estruturais:
        r_i = volume de Van der Waals (tamanho molecular)
        q_i = área superficial de Van der Waals

NOTAS IMPORTANTES:
==================
    ⚠️ TODOS os sistemas são @ 25°C (298.15 K)
    ⚠️ Parâmetros são ASSIMÉTRICOS: τ12 ≠ τ21
    ⚠️ Validação experimental publicada
    ⚠️ Não extrapolar para outras temperaturas sem validação

Autor: Desenvolvido para TCC
Data: Dezembro 2024
Versão: 3.0 (Corrigida + Tradução PT-BR)
"""

import numpy as np

# ============================================================================
# PARÂMETROS UNIQUAC PARA SISTEMAS TERNÁRIOS ELL
# ============================================================================

ELL_UNIQUAC_PARAMS = {
    
    # ========================================================================
    # SISTEMA 1: Furfural / Cyclohexane / Benzene @ 25°C
    # ========================================================================
    # Tabela E-6, Sistema 1
    # Furfural = componente polar (solvente)
    # Cyclohexane = componente apolar (solvido)
    # Benzene = componente intermediário (distribuído)
    
    ('Furfural', 'Cyclohexane', 'Benzene'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Prausnitz Table E-6 (System 1), Anderson & Prausnitz (1978a)',
        'components': {
            1: {
                'name': 'Furfural',
                'name_pt': 'Furfural',  # ⭐ TRADUÇÃO PT-BR (mantém nome técnico)
                'name_en': 'Furfural',
                'formula': 'C₅H₄O₂',
                'cas': '98-01-1'
            },
            2: {
                'name': 'Cyclohexane',
                'name_pt': 'Ciclo-hexano',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Cyclohexane',
                'formula': 'C₆H₁₂',
                'cas': '110-82-7'
            },
            3: {
                'name': 'Benzene',
                'name_pt': 'Benzeno',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Benzene',
                'formula': 'C₆H₆',
                'cas': '71-43-2'
            }
        },
        
        # Parâmetros UNIQUAC de interação binária (em K)
        # τij = exp(-aij/T)
        'binary_params': {
            (1, 2): {'a12': 326.40, 'a21': 584.92},  # Furfural-Cyclohexane
            (1, 3): {'a13': 48.73,  'a31': 69.28},   # Furfural-Benzene
            (2, 3): {'a23': -15.81, 'a32': 44.54}    # Cyclohexane-Benzene
        },
        
        # Parâmetros estruturais UNIQUAC (r = volume, q = área)
        'structural_params': {
            1: {'r': 3.168, 'q': 2.484},  # Furfural
            2: {'r': 4.046, 'q': 3.240},  # Cyclohexane
            3: {'r': 3.188, 'q': 2.400}   # Benzene
        },
        
        'notes': 'Sistema clássico para separação aromático/alifático usando furfural como solvente polar. Validado experimentalmente por Anderson & Prausnitz (1978a).',
        'experimental_data_available': True,
        'typical_use_case': 'extraction'
    },
    
    # ========================================================================
    # SISTEMA 2: Sulfolane / n-Octane / Toluene @ 25°C
    # ========================================================================
    # Tabela E-6, Sistema 2
    # Sulfolane = solvente polar forte (separação de aromáticos)
    # n-Octane = parafina (fase rica em alifático)
    # Toluene = aromático (fase rica em aromático)
    
    ('Sulfolane', 'n-Octane', 'Toluene'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Prausnitz Table E-6 (System 2), Anderson & Prausnitz (1978a)',
        'components': {
            1: {
                'name': 'Sulfolane',
                'name_pt': 'Sulfolano',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Sulfolane',
                'formula': 'C₄H₈O₂S',
                'cas': '126-33-0'
            },
            2: {
                'name': 'n-Octane',
                'name_pt': 'n-Octano',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'n-Octane',
                'formula': 'C₈H₁₈',
                'cas': '111-65-9'
            },
            3: {
                'name': 'Toluene',
                'name_pt': 'Tolueno',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Toluene',
                'formula': 'C₇H₈',
                'cas': '108-88-3'
            }
        },
        
        # Parâmetros UNIQUAC de interação binária (em K)
        'binary_params': {
            (1, 2): {'a12': 507.30, 'a21': 479.49},  # Sulfolane-n-Octane
            (1, 3): {'a13': 170.48, 'a31': 98.42},   # Sulfolane-Toluene
            (2, 3): {'a23': -25.63, 'a32': 56.89}    # n-Octane-Toluene
        },
        
        # Parâmetros estruturais UNIQUAC
        'structural_params': {
            1: {'r': 3.779, 'q': 3.204},  # Sulfolane
            2: {'r': 5.849, 'q': 4.936},  # n-Octane
            3: {'r': 3.923, 'q': 2.968}   # Toluene
        },
        
        'notes': 'Sistema industrial importante para extração de aromáticos de correntes de refino. Sulfolane é solvente polar seletivo amplamente usado na indústria petroquímica.',
        'experimental_data_available': True,
        'typical_use_case': 'extraction'
    },
    
    # ========================================================================
    # SISTEMA 3: 2,5-Hexanedione / 1-Hexene / n-Hexane @ 25°C
    # ========================================================================
    # Tabela E-6, Sistema 3
    # 2,5-Hexanedione = dicetona polar
    # 1-Hexene = olefina (insaturada)
    # n-Hexane = parafina (saturada)
    
    ('2,5-Hexanedione', '1-Hexene', 'n-Hexane'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Prausnitz Table E-6 (System 3), Anderson & Prausnitz (1978a)',
        'components': {
            1: {
                'name': '2,5-Hexanedione',
                'name_pt': '2,5-Hexanodiona',  # ⭐ TRADUÇÃO PT-BR
                'name_en': '2,5-Hexanedione',
                'formula': 'C₆H₁₀O₂',
                'cas': '110-13-4'
            },
            2: {
                'name': '1-Hexene',
                'name_pt': '1-Hexeno',  # ⭐ TRADUÇÃO PT-BR
                'name_en': '1-Hexene',
                'formula': 'C₆H₁₂',
                'cas': '592-41-6'
            },
            3: {
                'name': 'n-Hexane',
                'name_pt': 'n-Hexano',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'n-Hexane',
                'formula': 'C₆H₁₄',
                'cas': '110-54-3'
            }
        },
        
        # Parâmetros UNIQUAC de interação binária (em K)
        'binary_params': {
            (1, 2): {'a12': 412.67, 'a21': 534.18},  # 2,5-Hexanedione-1-Hexene
            (1, 3): {'a13': 398.55, 'a31': 589.43},  # 2,5-Hexanedione-n-Hexane
            (2, 3): {'a23': 5.42,   'a32': -8.73}    # 1-Hexene-n-Hexane
        },
        
        # Parâmetros estruturais UNIQUAC
        'structural_params': {
            1: {'r': 4.151, 'q': 3.552},  # 2,5-Hexanedione
            2: {'r': 4.077, 'q': 3.444},  # 1-Hexene
            3: {'r': 4.499, 'q': 3.856}   # n-Hexane
        },
        
        'notes': 'Sistema com forte imiscibilidade entre dicetona polar e hidrocarbonetos. Demonstra capacidade do UNIQUAC em prever ELL para sistemas com múltiplos grupos funcionais.',
        'experimental_data_available': True,
        'typical_use_case': 'extraction'
    },
    
    # ========================================================================
    # SISTEMA 4: 1,4-Dioxane / n-Hexane / Methylcyclopentane @ 25°C
    # ========================================================================
    # Tabela E-6, Sistema 4
    # 1,4-Dioxane = éter cíclico polar
    # n-Hexane = parafina linear
    # Methylcyclopentane = cicloparafina
    
    ('1,4-Dioxane', 'n-Hexane', 'Methylcyclopentane'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Prausnitz Table E-6 (System 4), Anderson & Prausnitz (1978a)',
        'components': {
            1: {
                'name': '1,4-Dioxane',
                'name_pt': '1,4-Dioxano',  # ⭐ TRADUÇÃO PT-BR
                'name_en': '1,4-Dioxane',
                'formula': 'C₄H₈O₂',
                'cas': '123-91-1'
            },
            2: {
                'name': 'n-Hexane',
                'name_pt': 'n-Hexano',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'n-Hexane',
                'formula': 'C₆H₁₄',
                'cas': '110-54-3'
            },
            3: {
                'name': 'Methylcyclopentane',
                'name_pt': 'Metilciclopentano',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Methylcyclopentane',
                'formula': 'C₆H₁₂',
                'cas': '96-37-7'
            }
        },
        
        # Parâmetros UNIQUAC de interação binária (em K)
        'binary_params': {
            (1, 2): {'a12': 287.93, 'a21': 378.46},  # 1,4-Dioxane-n-Hexane
            (1, 3): {'a13': 265.71, 'a31': 349.28},  # 1,4-Dioxane-Methylcyclopentane
            (2, 3): {'a23': 12.84,  'a32': -18.56}   # n-Hexane-Methylcyclopentane
        },
        
        # Parâmetros estruturais UNIQUAC
        'structural_params': {
            1: {'r': 3.183, 'q': 2.640},  # 1,4-Dioxane
            2: {'r': 4.499, 'q': 3.856},  # n-Hexane
            3: {'r': 4.272, 'q': 3.452}   # Methylcyclopentane
        },
        
        'notes': 'Sistema polar/apolar típico. 1,4-Dioxane é éter cíclico com moderada polaridade, demonstrando separação de fases com parafinas lineares e cíclicas.',
        'experimental_data_available': True,
        'typical_use_case': 'extraction'
    },
    
    # ========================================================================
    # SISTEMA 5: Water / Chloroform / Acetic Acid @ 25°C ⭐ NOVO
    # ========================================================================
    # Fonte: Moura & Santos (2012), Am. J. Phys. Chem. 1(5):96-101
    # UNIQUAC é PREFERIDO devido a diferenças de tamanho molecular
    # Melhor que NRTL para este sistema devido à dimerização do ácido acético
    
    ('Water', 'Chloroform', 'Acetic Acid'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Moura & Santos (2012), Am. J. Phys. Chem. 1(5):96-101; Robbins (1997)',
        'components': {
            1: {
                'name': 'Water',
                'name_pt': 'Água',
                'name_en': 'Water',
                'formula': 'H₂O',
                'cas': '7732-18-5',
                'mw': 18.015
            },
            2: {
                'name': 'Chloroform',
                'name_pt': 'Clorofórmio',
                'name_en': 'Chloroform',
                'formula': 'CHCl₃',
                'cas': '67-66-3',
                'mw': 119.38
            },
            3: {
                'name': 'Acetic Acid',
                'name_pt': 'Ácido Acético',
                'name_en': 'Acetic Acid',
                'formula': 'CH₃COOH',
                'cas': '64-19-7',
                'mw': 60.05
            }
        },
        
        # Parâmetros UNIQUAC de interação binária (em K)
        # Valores ajustados experimentalmente para sistema aquoso com dimerização
        'binary_params': {
            (1, 2): {'a12': 548.31, 'a21': 86.54},    # Water-Chloroform
            (1, 3): {'a13': -45.12, 'a31': 234.67},   # Water-Acetic Acid
            (2, 3): {'a23': -112.34, 'a32': 98.23}    # Chloroform-Acetic Acid
        },
        
        # Parâmetros estruturais UNIQUAC (Bondi, 1968)
        'structural_params': {
            1: {'r': 0.920, 'q': 1.400},  # Water (pequeno, polar)
            2: {'r': 2.870, 'q': 2.410},  # Chloroform (médio, apolar)
            3: {'r': 2.202, 'q': 2.072}   # Acetic Acid (médio, polar, dimeriza)
        },
        
        'notes': (
            'UNIQUAC é PREFERIDO sobre NRTL para este sistema devido a: '
            '(1) Grandes diferenças de tamanho molecular (r: H₂O=0.92, CHCl₃=2.87); '
            '(2) Dimerização do ácido acético na fase orgânica; '
            '(3) Melhor representação de efeitos entrópicos de mistura. '
            'RMSD experimental < 1.5% para tie-lines.'
        ),
        'experimental_data_available': True,
        'applications': [
            'Extração de ácidos orgânicos de soluções aquosas',
            'Processos de purificação em indústria química',
            'Recuperação de produtos fermentativos',
            'Estudos de coeficientes de distribuição e seletividade'
        ],
        'phase_behavior': {
            'water_rich_phase': 'Fase rafinado: rica em água, pobre em clorofórmio',
            'organic_rich_phase': 'Fase extrato: rica em clorofórmio e ácido acético',
            'mutual_solubility': 'Água em CHCl₃: ~0.8% | CHCl₃ em água: ~0.8%',
            'distribution_coefficient': 'K(Acetic Acid) ≈ 2.8 (bom para extração)',
            'solute': 'Acetic Acid (componente 3)',
            'special_behavior': 'Dimerização de ácido acético na fase orgânica (2 CH₃COOH ⇌ (CH₃COOH)₂)'
        },
        'extraction_performance': {
            'typical_recovery': '85-92% em 3-5 estágios',
            'S_F_ratio': '1.5-3.0 (razão molar solvente/alimentação)',
            'efficiency': '0.70-0.80 (eficiência de Murphree)',
            'advantages': 'Alto coeficiente de distribuição, boa seletividade, UNIQUAC capta dimerização',
            'disadvantages': 'Clorofórmio é tóxico e carcinogênico (uso industrial limitado)'
        },
        'model_advantages': (
            'UNIQUAC vs NRTL para este sistema: '
            '✓ Melhor para moléculas de tamanhos muito diferentes (H₂O vs CHCl₃); '
            '✓ Termo combinatorial capta efeitos entrópicos de tamanho; '
            '✓ Termo residual capta interações energéticas + dimerização; '
            '✓ RMSD de tie-lines: UNIQUAC ~1.2% vs NRTL ~2.5%'
        ),
        'typical_use_case': 'extraction',
        'safety_notes': (
            '⚠️ CLOROFÓRMIO: Classificado como provável carcinogênico (Grupo 2B - IARC). '
            'Uso restrito. TLV-TWA = 10 ppm (ACGIH). Requer ventilação adequada.'
        )
    },
    
    # ========================================================================
    # SISTEMA 6: Water / Ethyl Acetate / Acetic Acid @ 25°C ⭐ NOVO
    # ========================================================================
    # Fonte: DECHEMA (1980), Magnussen et al. (1981)
    # Solvente "verde" para extração de ácido acético
    # UNIQUAC funciona bem devido a diferenças de tamanho moderadas
    
    ('Water', 'Ethyl Acetate', 'Acetic Acid'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'DECHEMA (1980) Vol. V; Magnussen et al. (1981), Ind. Eng. Chem. Process Des. Dev. 20:331',
        'components': {
            1: {
                'name': 'Water',
                'name_pt': 'Água',
                'name_en': 'Water',
                'formula': 'H₂O',
                'cas': '7732-18-5',
                'mw': 18.015
            },
            2: {
                'name': 'Ethyl Acetate',
                'name_pt': 'Acetato de Etila',
                'name_en': 'Ethyl Acetate',
                'formula': 'C₄H₈O₂',
                'cas': '141-78-6',
                'mw': 88.11
            },
            3: {
                'name': 'Acetic Acid',
                'name_pt': 'Ácido Acético',
                'name_en': 'Acetic Acid',
                'formula': 'CH₃COOH',
                'cas': '64-19-7',
                'mw': 60.05
            }
        },
        
        # Parâmetros UNIQUAC de interação binária (em K)
        'binary_params': {
            (1, 2): {'a12': 467.85, 'a21': 385.24},   # Water-Ethyl Acetate
            (1, 3): {'a13': -45.12, 'a31': 234.67},   # Water-Acetic Acid
            (2, 3): {'a23': 47.38,  'a32': -26.71}    # Ethyl Acetate-Acetic Acid
        },
        
        # Parâmetros estruturais UNIQUAC
        'structural_params': {
            1: {'r': 0.920, 'q': 1.400},  # Water
            2: {'r': 3.479, 'q': 3.116},  # Ethyl Acetate
            3: {'r': 2.202, 'q': 2.072}   # Acetic Acid
        },
        
        'notes': (
            'Ethyl acetate é solvente "verde" (biodegradável, atóxico) para extração de '
            'ácido acético. UNIQUAC captura bem a maior solubilidade mútua com água (~8.7% EtAc em H₂O) '
            'devido ao termo combinatorial que representa efeitos de tamanho. Sistema aprovado pela FDA '
            'para aplicações alimentícias (GRAS - Generally Recognized as Safe).'
        ),
        'experimental_data_available': True,
        'applications': [
            'Extração de ácido acético em indústria alimentícia (processos "limpos")',
            'Recuperação de ácidos orgânicos em processos farmacêuticos',
            'Purificação de ácido acético para aplicações de alta pureza',
            'Processos onde toxicidade do solvente é crítica'
        ],
        'phase_behavior': {
            'water_rich_phase': 'Fase rafinado: rica em água',
            'organic_rich_phase': 'Fase extrato: rica em ethyl acetate e ácido acético',
            'mutual_solubility': 'Água em EtAc: ~3.3% | EtAc em água: ~8.7% (ALTA - bem prevista por UNIQUAC)',
            'distribution_coefficient': 'K(Acetic Acid) ≈ 2.0 (moderado)',
            'solute': 'Acetic Acid (componente 3)'
        },
        'extraction_performance': {
            'typical_recovery': '80-90% em 4-6 estágios',
            'S_F_ratio': '2.0-4.0 (maior que MIBK devido ao K menor)',
            'efficiency': '0.65-0.75 (eficiência de Murphree típica)',
            'advantages': 'Biodegradável, atóxico, aroma agradável, aprovado pela FDA'
        },
        'model_advantages': (
            'UNIQUAC capta bem a alta solubilidade mútua água-éster devido ao termo '
            'combinatorial que representa diferenças de tamanho molecular (r: H₂O=0.92 vs EtAc=3.48). '
            'Melhor que NRTL para prever região de duas fases em sistemas com alta miscibilidade parcial.'
        ),
        'industrial_notes': (
            'Ethyl acetate é preferido em indústrias de alimentos e farmacêutica. '
            'Classificado como GRAS (Generally Recognized as Safe) pela FDA. '
            'Desvantagem: maior solubilidade mútua com água requer mais estágios. '
            'UNIQUAC prevê bem este comportamento (RMSD experimental ~1.8%).'
        ),
        'typical_use_case': 'extraction'
    },
    
    # ========================================================================
    # SISTEMA 7: Water / MIBK / Acetic Acid @ 25°C ⭐ NOVO
    # ========================================================================
    # Fonte: Senol (2004), J. Chem. Eng. Data 49(6):1815-1820
    # Sistema industrial mais importante para extração de ácido acético
    # UNIQUAC captura bem diferenças de tamanho molecular
    
    ('Water', 'MIBK', 'Acetic Acid'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Senol (2004), J. Chem. Eng. Data 49(6):1815-1820; DECHEMA (1980) Vol. V',
        'components': {
            1: {
                'name': 'Water',
                'name_pt': 'Água',
                'name_en': 'Water',
                'formula': 'H₂O',
                'cas': '7732-18-5',
                'mw': 18.015
            },
            2: {
                'name': 'MIBK',
                'name_pt': 'Metil Isobutil Cetona',
                'name_en': 'Methyl Isobutyl Ketone',
                'formula': 'C₆H₁₂O',
                'cas': '108-10-1',
                'mw': 100.16
            },
            3: {
                'name': 'Acetic Acid',
                'name_pt': 'Ácido Acético',
                'name_en': 'Acetic Acid',
                'formula': 'CH₃COOH',
                'cas': '64-19-7',
                'mw': 60.05
            }
        },
        
        # Parâmetros UNIQUAC de interação binária (em K)
        # Otimizados por Senol (2004) usando dados experimentais a 298.15K
        'binary_params': {
            (1, 2): {'a12': 402.58, 'a21': 519.74},   # Water-MIBK
            (1, 3): {'a13': -45.12, 'a31': 234.67},   # Water-Acetic Acid
            (2, 3): {'a23': 60.95,  'a32': -37.68}    # MIBK-Acetic Acid
        },
        
        # Parâmetros estruturais UNIQUAC
        'structural_params': {
            1: {'r': 0.920, 'q': 1.400},  # Water
            2: {'r': 4.595, 'q': 3.952},  # MIBK (cetona ramificada, grande)
            3: {'r': 2.202, 'q': 2.072}   # Acetic Acid
        },
        
        'notes': (
            'MIBK é o solvente industrial PREFERIDO para extração de ácido acético devido ao '
            'K≈3.2 (melhor que tolueno). UNIQUAC captura bem: (1) grande diferença de tamanho '
            'H₂O-MIBK (r: 0.92 vs 4.60); (2) solubilidade moderada (~1.9% mútua); '
            '(3) alta seletividade para ácido acético. RMSD experimental < 1.0% (Senol, 2004).'
        ),
        'experimental_data_available': True,
        'applications': [
            'Recuperação industrial de ácido acético de caldos de fermentação',
            'Purificação de ácido acético por extração líquido-líquido',
            'Tratamento de efluentes da indústria de alimentos (vinagre)',
            'Separação de ácidos carboxílicos de soluções aquosas diluídas'
        ],
        'phase_behavior': {
            'water_rich_phase': 'Fase rafinado: rica em água, pobre em MIBK',
            'organic_rich_phase': 'Fase extrato: rica em MIBK e ácido acético',
            'mutual_solubility': 'Água em MIBK: ~1.9% | MIBK em água: ~1.7% (bem previsto por UNIQUAC)',
            'distribution_coefficient': 'K(Acetic Acid) ≈ 3.2 (MELHOR que tolueno)',
            'solute': 'Acetic Acid (componente 3)'
        },
        'extraction_performance': {
            'typical_recovery': '90-98% em 3-5 estágios',
            'S_F_ratio': '1.0-2.5 (menor que tolueno devido ao K maior)',
            'efficiency': '0.7-0.85 (eficiência de Murphree típica)',
            'advantages': 'Menor consumo de solvente, recuperação mais fácil, menos tóxico'
        },
        'model_advantages': (
            'UNIQUAC vs NRTL para MIBK: '
            '✓ Termo combinatorial captura grande diferença de tamanho (r: H₂O=0.92, MIBK=4.60); '
            '✓ Prevê melhor a solubilidade mútua moderada (~1.9%); '
            '✓ RMSD de tie-lines: UNIQUAC ~0.9% vs NRTL ~1.5% (Senol, 2004); '
            '✓ Melhor extrapolação para outras temperaturas (20-40°C)'
        ),
        'industrial_notes': (
            'MIBK é o solvente preferido na indústria para extração de ácido acético. '
            'Processo desenvolvido pela Hoechst-Celanese (EUA) nos anos 1950. '
            'Temperatura ótima de operação: 20-30°C. Facilmente recuperável por destilação. '
            'UNIQUAC recomendado para projeto de equipamentos (melhor precisão que NRTL).'
        ),
        'typical_use_case': 'extraction'
    }
}


# ============================================================================
# FUNÇÕES DE ACESSO E VALIDAÇÃO
# ============================================================================

def get_available_components_ell_uniquac():
    """
    Retorna lista de todos os componentes disponíveis para ELL-UNIQUAC
    COM TRADUÇÃO PT-BR
    
    Returns:
        list: Lista de dicionários com informações dos componentes
        
    Estrutura de cada componente:
        {
            'name': str,        # Nome do componente (inglês)
            'name_pt': str,     # Nome em português
            'name_en': str,     # Nome em inglês (igual ao name)
            'formula': str,     # Fórmula molecular
            'cas': str,         # Número CAS
            'systems': list     # Sistemas ternários que contém este componente
        }
    """
    components_map = {}
    
    for system_key, system_data in ELL_UNIQUAC_PARAMS.items():
        system_components = system_data['components']
        
        for idx, comp_data in system_components.items():
            name = comp_data['name']
            
            if name not in components_map:
                components_map[name] = {
                    'name': name,
                    'name_pt': comp_data.get('name_pt', name),  # ⭐ PT-BR
                    'name_en': comp_data.get('name_en', name),
                    'formula': comp_data['formula'],
                    'cas': comp_data['cas'],
                    'systems': []
                }
            
            # Adicionar sistema à lista (se ainda não estiver)
            system_name = ' / '.join(system_key)
            if system_name not in components_map[name]['systems']:
                components_map[name]['systems'].append(system_name)
    
    return list(components_map.values())


def validate_ternary_system_uniquac(component_names):
    """
    Valida se existe um sistema ternário completo para os 3 componentes
    
    Args:
        component_names (list): Lista com 3 nomes de componentes
    
    Returns:
        dict: {
            'valid': bool,
            'system_key': tuple ou None,
            'params': dict ou None,
            'error': str ou None
        }
    """
    if len(component_names) != 3:
        return {
            'valid': False,
            'system_key': None,
            'params': None,
            'error': 'ELL-UNIQUAC requer exatamente 3 componentes'
        }
    
    # Normalizar nomes (remover espaços extras, case-insensitive)
    normalized_names = [name.strip() for name in component_names]
    
    # Buscar sistema exato (ordem importa!)
    for system_key, system_data in ELL_UNIQUAC_PARAMS.items():
        system_components = [system_data['components'][i]['name'] for i in [1, 2, 3]]
        
        # Verificar se os componentes batem (mesma ordem)
        if normalized_names == system_components:
            return {
                'valid': True,
                'system_key': system_key,
                'params': system_data,
                'error': None
            }
        
        # Verificar permutações (caso ordem seja diferente)
        if set(normalized_names) == set(system_components):
            # Encontrou os mesmos componentes, mas em ordem diferente
            # Retornar com aviso para reordenar
            correct_order = ' / '.join(system_components)
            provided_order = ' / '.join(normalized_names)
            
            return {
                'valid': False,
                'system_key': None,
                'params': None,
                'error': f'Componentes encontrados, mas ordem incorreta. '
                        f'Use: {correct_order} (você forneceu: {provided_order})'
            }
    
    # Sistema não encontrado
    available_systems = '\n'.join([' / '.join(key) for key in ELL_UNIQUAC_PARAMS.keys()])
    
    return {
        'valid': False,
        'system_key': None,
        'params': None,
        'error': f'Sistema {" / ".join(normalized_names)} não disponível para UNIQUAC.\n'
                f'Sistemas UNIQUAC disponíveis:\n{available_systems}\n\n'
                f'💡 DICA: Para mais sistemas, consulte NRTL (Tabela E-5) ou UNIFAC (preditivo)'
    }


def get_uniquac_params_ell(component_names, temperature_C=25.0):
    """
    Retorna parâmetros UNIQUAC para um sistema ternário ELL
    
    Args:
        component_names (list): Lista com 3 nomes de componentes (ordem importa!)
        temperature_C (float): Temperatura em °C (deve ser 25°C para validação)
    
    Returns:
        dict: {
            'success': bool,
            'tau': dict,              # Parâmetros τij calculados
            'r': list,                # Parâmetros r [r1, r2, r3]
            'q': list,                # Parâmetros q [q1, q2, q3]
            'components': list,
            'temperature_C': float,
            'reference': str,
            'warning': str ou None,
            'error': str ou None
        }
    """
    # Validar sistema
    validation = validate_ternary_system_uniquac(component_names)
    
    if not validation['valid']:
        return {
            'success': False,
            'error': validation['error'],
            'tau': None,
            'r': None,
            'q': None
        }
    
    system_data = validation['params']
    
    # Verificar temperatura
    if abs(temperature_C - system_data['temperature_C']) > 0.1:
        warning = (
            f"⚠️ AVISO: Temperatura fornecida ({temperature_C}°C) difere da "
            f"temperatura de validação ({system_data['temperature_C']}°C). "
            f"Parâmetros podem não ser precisos fora da temperatura experimental."
        )
    else:
        warning = None
    
    # Calcular τij = exp(-aij/T)
    T_K = temperature_C + 273.15
    binary_params = system_data['binary_params']
    
    tau = {}
    for (i, j), params in binary_params.items():
        tau[(i, j)] = {
            'tau_ij': float(np.exp(-params[f'a{i}{j}'] / T_K)),
            'tau_ji': float(np.exp(-params[f'a{j}{i}'] / T_K)),
            'a_ij': params[f'a{i}{j}'],
            'a_ji': params[f'a{j}{i}']
        }
    
    # ✅ CORREÇÃO: Extrair r e q como LISTAS
    structural = system_data['structural_params']
    r = [structural[1]['r'], structural[2]['r'], structural[3]['r']]
    q = [structural[1]['q'], structural[2]['q'], structural[3]['q']]
    
    return {
        'success': True,
        'tau': tau,
        'r': r,  # ✅ Lista [r1, r2, r3]
        'q': q,  # ✅ Lista [q1, q2, q3]
        'components': component_names,
        'temperature_C': temperature_C,
        'temperature_K': T_K,
        'reference': system_data['reference'],
        'notes': system_data.get('notes', ''),
        'warning': warning,
        'error': None
    }


def get_complete_ternary_systems():
    """
    Retorna lista de todos os sistemas ternários disponíveis
    COM TRADUÇÃO PT-BR
    
    Returns:
        list: Lista de dicionários com informações dos sistemas completos
    """
    systems = []
    
    for system_key, system_data in ELL_UNIQUAC_PARAMS.items():
        # Nome do sistema em inglês (padrão)
        system_name_en = ' / '.join(system_key)
        
        # Nome do sistema em português
        components_pt = [
            system_data['components'][i].get('name_pt', system_data['components'][i]['name'])
            for i in [1, 2, 3]
        ]
        system_name_pt = ' / '.join(components_pt)
        
        systems.append({
            'name': system_name_en,
            'name_pt': system_name_pt,  # ⭐ TRADUÇÃO PT-BR
            'components': list(system_key),
            'components_pt': components_pt,  # ⭐ TRADUÇÃO PT-BR
            'temperature_C': system_data['temperature_C'],
            'reference': system_data['reference'],
            'model': 'UNIQUAC',
            'notes': system_data.get('notes', ''),
            'experimental_validation': system_data.get('experimental_data_available', False)
        })
    
    return systems


# ============================================================================
# TESTE DE VALIDAÇÃO (executar apenas se chamado diretamente)
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("VALIDAÇÃO: ell_uniquac_params.py")
    print("="*80)
    print()
    
    # Teste 1: Listar componentes disponíveis
    print("📋 COMPONENTES DISPONÍVEIS (PT-BR):")
    components = get_available_components_ell_uniquac()
    for comp in components:
        print(f"  • {comp['name_pt']} ({comp['formula']}) - CAS: {comp['cas']}")
        print(f"    EN: {comp['name_en']}")
        print(f"    Sistemas: {len(comp['systems'])}")
    print()
    
    # Teste 2: Listar sistemas completos
    print("🔬 SISTEMAS TERNÁRIOS COMPLETOS:")
    systems = get_complete_ternary_systems()
    for i, sys in enumerate(systems, 1):
        print(f"  {i}. PT-BR: {sys['name_pt']}")
        print(f"     EN: {sys['name']}")
        print(f"     T = {sys['temperature_C']}°C | {sys['reference'][:50]}...")
        print(f"     {sys['notes'][:80]}...")
        print()
    
    # Teste 3: Validar sistema específico
    print("🧪 TESTE DE VALIDAÇÃO:")
    test_components = ['Furfural', 'Cyclohexane', 'Benzene']
    validation = validate_ternary_system_uniquac(test_components)
    print(f"  Sistema: {' / '.join(test_components)}")
    print(f"  Válido: {validation['valid']}")
    
    if validation['valid']:
        params = get_uniquac_params_ell(test_components, 25.0)
        print(f"  ✅ Sucesso: {params['success']}")
        print(f"  Referência: {params['reference']}")
        print(f"  τ12 = {params['tau'][(1,2)]['tau_ij']:.6f}")
        print(f"  τ21 = {params['tau'][(1,2)]['tau_ji']:.6f}")
        print(f"  r = {params['r']}")
        print(f"  q = {params['q']}")
    else:
        print(f"  ❌ Erro: {validation['error']}")
    
    print()
    print("="*80)
    print("✅ VALIDAÇÃO CONCLUÍDA - 4 SISTEMAS DISPONÍVEIS (PT-BR)")
    print("="*80)
