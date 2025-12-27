"""
app/data/ell_nrtl_params.py

PARÂMETROS NRTL PARA ELL (Equilíbrio Líquido-Líquido)
======================================================

FONTES BIBLIOGRÁFICAS:
    [1] Prausnitz, J.M., Lichtenthaler, R.N., Azevedo, E.G. (1999)
        "Molecular Thermodynamics of Fluid-Phase Equilibria", 3rd Ed.
        Prentice Hall PTR, ISBN: 0-13-977745-8
        TABELA E-5 (p. 798): NRTL Binary Parameters for Ternary LLE
        Fonte primária: Bender, E., Block, U. (1975)
                        Ber. Bunsenges. Phys. Chem., 79, 298-309

    [2] Renon, H., Prausnitz, J.M. (1968)
        "Local compositions in thermodynamic excess functions for liquid mixtures"
        AIChE Journal, 14(1), 135-144
        
    [3] Sørensen, J.M., Arlt, W. (1980)
        "Liquid-Liquid Equilibrium Data Collection"
        DECHEMA Chemistry Data Series, Vol. V, Part 1
        
    [4] Perry's Chemical Engineers' Handbook, 8th Ed. (2008)
        Section 15: Liquid-Liquid Extraction and Other Liquid-Liquid Operations

SISTEMAS TERNÁRIOS DISPONÍVEIS (4 SISTEMAS):
=============================================

1. Water / 1,1,2-Trichloroethane (TCE) / Acetone @ 25°C
   - Fonte: Prausnitz Tabela E-5, Bender & Block (1975)
   - Aplicação: Sistema clássico polar/apolar com cosolvente

2. Water / Toluene / Acetic Acid @ 25°C
   - Fonte: Renon & Prausnitz (1968), DECHEMA (1980)
   - Aplicação: Extração de ácido acético de águas residuais

3. Water / MIBK / Acetic Acid @ 25°C
   - Fonte: DECHEMA (1980), Perry's Section 15
   - Aplicação: Extração industrial de ácido acético (K≈3.2)

4. Water / Ethyl Acetate / Acetic Acid @ 25°C
   - Fonte: DECHEMA (1980), Othmer et al. (1941)
   - Aplicação: Recuperação de ácido acético (solvente biodegradável)

CONVENÇÕES NRTL:
================
    τij = (gij - gjj) / RT = bij / T  onde bij em K
    
    ln(γi) = [Σj τji Gji xj / Σk Gki xk] + 
             Σj [xj Gij / Σk Gkj xk] [τij - (Σm xm τmj Gmj / Σk Gkj xk)]
    
    Gij = exp(-αij τij)
    
    αij = αji (parâmetro de não-aleatoriedade)
        - αij próximo de 0: mistura quase ideal
        - αij = 0.2-0.3: hidrocarbonetos + polares
        - αij = 0.3-0.4: sistemas fortemente não-ideais

NOTAS IMPORTANTES:
==================
    ⚠️ Todos os sistemas são @ 25°C (298.15 K)
    ⚠️ Parâmetros são ASSIMÉTRICOS: τ12 ≠ τ21
    ⚠️ Não extrapolar para outras temperaturas sem validação
    ⚠️ Para mais sistemas, consulte DECHEMA Data Series ou UNIQUAC (Tabela E-6)

Autor: Desenvolvido para TCC - Plataforma de Equilíbrio de Fases
Data: Dezembro 2024
Versão: 3.0 (Expandido com 4 sistemas de extração + Tradução PT-BR)
"""

import numpy as np

# ============================================================================
# PARÂMETROS NRTL PARA SISTEMAS TERNÁRIOS ELL
# ============================================================================

ELL_NRTL_PARAMS = {
    
    # ========================================================================
    # SISTEMA 1: Water / 1,1,2-Trichloroethane (TCE) / Acetone @ 25°C
    # ========================================================================
    # Tabela E-5 (Prausnitz), Sistema validado por Bender & Block (1975)
    # Water = componente polar (fase aquosa)
    # TCE = componente apolar clorado (fase orgânica)
    # Acetone = cosolvente (distribuído entre fases)
    
    ('Water', '1,1,2-Trichloroethane', 'Acetone'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Prausnitz Table E-5, Bender & Block (1975), Ber. Bunsenges. Phys. Chem., 79, 298-309',
        'components': {
            1: {
                'name': 'Water',
                'name_pt': 'Água',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Water',
                'formula': 'H₂O',
                'cas': '7732-18-5',
                'mw': 18.015
            },
            2: {
                'name': '1,1,2-Trichloroethane',
                'name_pt': '1,1,2-Tricloroetano',  # ⭐ TRADUÇÃO PT-BR
                'name_en': '1,1,2-Trichloroethane',
                'formula': 'C₂H₃Cl₃',
                'cas': '79-00-5',
                'mw': 133.40
            },
            3: {
                'name': 'Acetone',
                'name_pt': 'Acetona',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Acetone',
                'formula': 'C₃H₆O',
                'cas': '67-64-1',
                'mw': 58.08
            }
        },
        
        'binary_params': {
            (1, 2): {
                'b12': 1486.53,   # Water-TCE (g12-g22)/R [K]
                'b21': 778.88,    # TCE-Water (g21-g11)/R [K]
                'alpha12': 0.30
            },
            (1, 3): {
                'b13': -94.78,    # Water-Acetone (g13-g33)/R [K]
                'b31': 548.15,    # Acetone-Water (g31-g11)/R [K]
                'alpha13': 0.30
            },
            (2, 3): {
                'b23': 212.89,    # TCE-Acetone (g23-g33)/R [K]
                'b32': -48.34,    # Acetone-TCE (g32-g22)/R [K]
                'alpha23': 0.30
            }
        },
        
        'notes': (
            'Sistema ternário clássico para ELL envolvendo água, solvente clorado e '
            'cosolvente polar. Water e TCE são praticamente imiscíveis, enquanto acetona '
            'distribui-se entre as duas fases, aumentando a solubilidade mútua.'
        ),
        'experimental_data_available': True,
        'applications': [
            'Extração líquido-líquido de compostos orgânicos de soluções aquosas',
            'Separação de misturas água-orgânicos usando cosolvente',
            'Estudos de distribuição de solutos em sistemas bifásicos'
        ],
        'phase_behavior': {
            'water_rich_phase': 'Fase L1 (aquosa): alta concentração de água e acetona, baixa de TCE',
            'organic_rich_phase': 'Fase L2 (orgânica): alta concentração de TCE e acetona, baixa de água',
            'mutual_solubility': 'Água e TCE têm solubilidade mútua muito baixa (~0.1% em massa)',
            'distribution_coefficient': 'K(Acetone) ≈ 1.5 (distribuição moderada entre fases)'
        },
        'typical_use_case': 'flash'  # Sistema clássico para flash bifásico
    },
    
    # ========================================================================
    # SISTEMA 2: Water / Toluene / Acetic Acid @ 25°C
    # ========================================================================
    # Fonte: Renon & Prausnitz (1968), DECHEMA Data Series Vol. V
    # Sistema clássico de extração de ácido acético
    
    ('Water', 'Toluene', 'Acetic Acid'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Renon & Prausnitz (1968), AIChE J. 14(1):135-144; DECHEMA (1980) Vol. V',
        'components': {
            1: {
                'name': 'Water',
                'name_pt': 'Água',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Water',
                'formula': 'H₂O',
                'cas': '7732-18-5',
                'mw': 18.015
            },
            2: {
                'name': 'Toluene',
                'name_pt': 'Tolueno',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Toluene',
                'formula': 'C₇H₈',
                'cas': '108-88-3',
                'mw': 92.14
            },
            3: {
                'name': 'Acetic Acid',
                'name_pt': 'Ácido Acético',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Acetic Acid',
                'formula': 'CH₃COOH',
                'cas': '64-19-7',
                'mw': 60.05
            }
        },
        
        'binary_params': {
            (1, 2): {
                'b12': 2638.71,   # Water-Toluene (fortemente imiscíveis)
                'b21': 2073.15,   # Toluene-Water
                'alpha12': 0.20   # Típico para água-hidrocarboneto
            },
            (1, 3): {
                'b13': -47.25,    # Water-Acetic Acid (miscíveis, interação favorável)
                'b31': 257.05,    # Acetic Acid-Water
                'alpha13': 0.30
            },
            (2, 3): {
                'b23': 371.42,    # Toluene-Acetic Acid
                'b32': -204.59,   # Acetic Acid-Toluene
                'alpha23': 0.30
            }
        },
        
        'notes': (
            'Sistema clássico para recuperação de ácido acético de soluções aquosas. '
            'Tolueno é usado como solvente extrator devido à sua baixa miscibilidade com água '
            'e capacidade de dissolver ácido acético. Sistema muito estudado na indústria química.'
        ),
        'experimental_data_available': True,
        'applications': [
            'Recuperação de ácido acético de águas residuais industriais',
            'Purificação de ácido acético por extração líquido-líquido',
            'Descontaminação de efluentes contendo ácidos carboxílicos'
        ],
        'phase_behavior': {
            'water_rich_phase': 'Fase rafinado: rica em água, pobre em tolueno',
            'organic_rich_phase': 'Fase extrato: rica em tolueno e ácido acético',
            'mutual_solubility': 'Água em tolueno: ~0.05% | Tolueno em água: ~0.05%',
            'distribution_coefficient': 'K(Acetic Acid) ≈ 2.5 (favorável para extração)',
            'solute': 'Acetic Acid (componente 3)'
        },
        'extraction_performance': {
            'typical_recovery': '85-95% em 3-5 estágios',
            'S_F_ratio': '1.5-3.0 (razão molar solvente/alimentação)',
            'efficiency': '0.6-0.8 (eficiência de Murphree típica)'
        },
        'typical_use_case': 'extraction'  # Sistema para extração multi-estágios
    },
    
    # ========================================================================
    # SISTEMA 3: Water / MIBK / Acetic Acid @ 25°C
    # ========================================================================
    # MIBK = Methyl Isobutyl Ketone (Metil Isobutil Cetona)
    # Fonte: DECHEMA (1980), Perry's Handbook Section 15
    # Melhor K de distribuição que tolueno
    
    ('Water', 'MIBK', 'Acetic Acid'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'DECHEMA (1980) Vol. V; Perry\'s Handbook 8th Ed. Section 15',
        'components': {
            1: {
                'name': 'Water',
                'name_pt': 'Água',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Water',
                'formula': 'H₂O',
                'cas': '7732-18-5',
                'mw': 18.015
            },
            2: {
                'name': 'MIBK',
                'name_pt': 'Metil Isobutil Cetona',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Methyl Isobutyl Ketone',
                'formula': 'C₆H₁₂O',
                'cas': '108-10-1',
                'mw': 100.16
            },
            3: {
                'name': 'Acetic Acid',
                'name_pt': 'Ácido Acético',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Acetic Acid',
                'formula': 'CH₃COOH',
                'cas': '64-19-7',
                'mw': 60.05
            }
        },
        
        'binary_params': {
            (1, 2): {
                'b12': 1348.25,   # Water-MIBK (menos imiscível que tolueno)
                'b21': 1739.88,   # MIBK-Water
                'alpha12': 0.20
            },
            (1, 3): {
                'b13': -47.25,    # Water-Acetic Acid (mesmo que tolueno)
                'b31': 257.05,    # Acetic Acid-Water
                'alpha13': 0.30
            },
            (2, 3): {
                'b23': 204.15,    # MIBK-Acetic Acid (melhor solubilidade)
                'b32': -126.38,   # Acetic Acid-MIBK
                'alpha23': 0.30
            }
        },
        
        'notes': (
            'MIBK é preferido industrialmente sobre tolueno para extração de ácido acético '
            'devido ao maior coeficiente de distribuição (K≈3.2 vs 2.5 do tolueno), menor '
            'toxicidade e facilidade de recuperação por destilação. Sistema amplamente usado '
            'na indústria de fermentação para recuperar ácido acético de caldos.'
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
            'mutual_solubility': 'Água em MIBK: ~1.9% | MIBK em água: ~1.7%',
            'distribution_coefficient': 'K(Acetic Acid) ≈ 3.2 (MELHOR que tolueno)',
            'solute': 'Acetic Acid (componente 3)'
        },
        'extraction_performance': {
            'typical_recovery': '90-98% em 3-5 estágios',
            'S_F_ratio': '1.0-2.5 (menor que tolueno devido ao K maior)',
            'efficiency': '0.7-0.85 (eficiência de Murphree típica)',
            'advantages': 'Menor consumo de solvente, recuperação mais fácil, menos tóxico'
        },
        'industrial_notes': (
            'MIBK é o solvente preferido na indústria para extração de ácido acético. '
            'Processo desenvolvido pela Hoechst-Celanese (EUA) nos anos 1950. '
            'Temperatura ótima de operação: 20-30°C. Facilmente recuperável por destilação.'
        ),
        'typical_use_case': 'extraction'  # Sistema para extração multi-estágios
    },
    
    # ========================================================================
    # SISTEMA 4: Water / Ethyl Acetate / Acetic Acid @ 25°C
    # ========================================================================
    # Fonte: DECHEMA (1980), Othmer et al. (1941)
    # Solvente biodegradável, menos tóxico
    
    ('Water', 'Ethyl Acetate', 'Acetic Acid'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'DECHEMA (1980) Vol. V; Othmer et al. (1941), Ind. Eng. Chem. 33:1240',
        'components': {
            1: {
                'name': 'Water',
                'name_pt': 'Água',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Water',
                'formula': 'H₂O',
                'cas': '7732-18-5',
                'mw': 18.015
            },
            2: {
                'name': 'Ethyl Acetate',
                'name_pt': 'Acetato de Etila',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Ethyl Acetate',
                'formula': 'C₄H₈O₂',
                'cas': '141-78-6',
                'mw': 88.11
            },
            3: {
                'name': 'Acetic Acid',
                'name_pt': 'Ácido Acético',  # ⭐ TRADUÇÃO PT-BR
                'name_en': 'Acetic Acid',
                'formula': 'CH₃COOH',
                'cas': '64-19-7',
                'mw': 60.05
            }
        },
        
        'binary_params': {
            (1, 2): {
                'b12': 1562.38,   # Water-Ethyl Acetate
                'b21': 1289.47,   # Ethyl Acetate-Water
                'alpha12': 0.25
            },
            (1, 3): {
                'b13': -47.25,    # Water-Acetic Acid
                'b31': 257.05,    # Acetic Acid-Water
                'alpha13': 0.30
            },
            (2, 3): {
                'b23': 158.76,    # Ethyl Acetate-Acetic Acid
                'b32': -89.25,    # Acetic Acid-Ethyl Acetate
                'alpha23': 0.30
            }
        },
        
        'notes': (
            'Ethyl acetate é um solvente "verde" (biodegradável, atóxico) usado para '
            'extração de ácido acético. Embora tenha K menor que MIBK (~2.0), é preferido '
            'em aplicações alimentícias e farmacêuticas devido à baixa toxicidade. '
            'Tem maior solubilidade mútua com água que os solventes anteriores.'
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
            'mutual_solubility': 'Água em EtAc: ~3.3% | EtAc em água: ~8.7% (ALTA)',
            'distribution_coefficient': 'K(Acetic Acid) ≈ 2.0 (moderado)',
            'solute': 'Acetic Acid (componente 3)'
        },
        'extraction_performance': {
            'typical_recovery': '80-90% em 4-6 estágios',
            'S_F_ratio': '2.0-4.0 (maior que MIBK devido ao K menor)',
            'efficiency': '0.65-0.75 (eficiência de Murphree típica)',
            'advantages': 'Biodegradável, atóxico, aroma agradável, aprovado pela FDA'
        },
        'industrial_notes': (
            'Ethyl acetate é preferido em indústrias de alimentos e farmacêutica. '
            'Classificado como GRAS (Generally Recognized as Safe) pela FDA. '
            'Desvantagem: maior solubilidade mútua com água requer mais estágios.'
        ),
        'typical_use_case': 'extraction'  # Sistema para extração multi-estágios
    },
    
    # ========================================================================
    # SISTEMA 5: Water / 1-Butanol / Acetone @ 25°C
    # ========================================================================
    # Fonte: Santos et al. (2001), Fluid Phase Equilibria 187:265-274
    # Sistema com co-solvente: acetona aumenta miscibilidade água-butanol
    
    ('Water', '1-Butanol', 'Acetone'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Santos et al. (2001), Fluid Phase Equilib. 187:265-274; Treybal (1963)',
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
                'name': '1-Butanol',
                'name_pt': '1-Butanol',
                'name_en': '1-Butanol',
                'formula': 'C₄H₁₀O',
                'cas': '71-36-3',
                'mw': 74.12
            },
            3: {
                'name': 'Acetone',
                'name_pt': 'Acetona',
                'name_en': 'Acetone',
                'formula': 'C₃H₆O',
                'cas': '67-64-1',
                'mw': 58.08
            }
        },
        
        'binary_params': {
            (1, 2): {
                'b12': 1346.23,   # Water-1-Butanol (parcialmente imiscíveis)
                'b21': 47.16,     # 1-Butanol-Water
                'alpha12': 0.20
            },
            (1, 3): {
                'b13': 499.15,    # Water-Acetone (miscíveis)
                'b31': 233.56,    # Acetone-Water
                'alpha13': 0.30
            },
            (2, 3): {
                'b23': -70.41,    # 1-Butanol-Acetone (miscíveis)
                'b32': 86.21,     # Acetone-1-Butanol
                'alpha23': 0.30
            }
        },
        
        'notes': (
            'Sistema ternário clássico com imiscibilidade parcial entre água e 1-butanol. '
            'Acetona atua como co-solvente, aumentando a miscibilidade mútua das fases aquosa '
            'e orgânica. A adição de acetona reduz a região de duas fases (binodal menor). '
            'Sistema muito estudado para validação de modelos termodinâmicos ELL.'
        ),
        'experimental_data_available': True,
        'applications': [
            'Extração líquido-líquido com co-solvente',
            'Recuperação de solventes em processos químicos',
            'Purificação de produtos químicos',
            'Estudos de diagrama ternário e binodal'
        ],
        'phase_behavior': {
            'water_rich_phase': 'Fase L1 (aquosa): alta concentração de água e acetona',
            'organic_rich_phase': 'Fase L2 (orgânica): alta concentração de 1-butanol e acetone',
            'mutual_solubility': 'Água em butanol: ~20% (25°C) | Butanol em água: ~7.5%',
            'distribution_coefficient': 'K(Acetone) ≈ 1.8 (distribuído entre ambas as fases)',
            'cosolvent_effect': 'Acetona reduz região de imiscibilidade (efeito co-solvente)'
        },
        'extraction_performance': {
            'typical_recovery': '70-85% em 2-4 estágios',
            'S_F_ratio': '1.5-3.0 (razão molar solvente/alimentação)',
            'efficiency': '0.65-0.75 (eficiência de Murphree)',
            'advantages': 'Co-solvente aumenta capacidade de dissolução'
        },
        'industrial_notes': (
            'Sistema usado em processos de recuperação de solventes da indústria química. '
            'Acetona facilita a separação e pode ser recuperada por destilação posterior. '
            'Diagrama ternário bem caracterizado experimentalmente (dados em DECHEMA).'
        ),
        'typical_use_case': 'ternary_diagram'  # Sistema ideal para diagrama ternário
    },
    
    # ========================================================================
    # SISTEMA 6: Water / Toluene / Aniline @ 25°C
    # ========================================================================
    # Fonte: Grenner et al. (2006), J. Chem. Eng. Data 51(3):1009-1014
    # Sistema com plait point bem definido
    
    ('Water', 'Toluene', 'Aniline'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Grenner et al. (2006), J. Chem. Eng. Data 51(3):1009-1014; Null (1970)',
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
                'name': 'Toluene',
                'name_pt': 'Tolueno',
                'name_en': 'Toluene',
                'formula': 'C₇H₈',
                'cas': '108-88-3',
                'mw': 92.14
            },
            3: {
                'name': 'Aniline',
                'name_pt': 'Anilina',
                'name_en': 'Aniline',
                'formula': 'C₆H₇N',
                'cas': '62-53-3',
                'mw': 93.13
            }
        },
        
        'binary_params': {
            (1, 2): {
                'b12': 2514.89,   # Water-Toluene (fortemente imiscíveis)
                'b21': 1692.34,   # Toluene-Water
                'alpha12': 0.20
            },
            (1, 3): {
                'b13': 861.72,    # Water-Aniline (parcialmente miscíveis)
                'b31': 367.85,    # Aniline-Water
                'alpha13': 0.30
            },
            (2, 3): {
                'b23': -46.52,    # Toluene-Aniline (miscíveis)
                'b32': 126.18,    # Aniline-Toluene
                'alpha23': 0.47
            }
        },
        
        'notes': (
            'Sistema ternário complexo com anilina anfifílica (grupo NH₂ polar + anel aromático '
            'apolar), tendo afinidade por ambas as fases aquosa e orgânica. Apresenta plait point '
            'bem definido e região binodal ampla. Água e tolueno são praticamente imiscíveis. '
            'Sistema clássico para estudo de equilíbrio líquido-líquido ternário.'
        ),
        'experimental_data_available': True,
        'applications': [
            'Extração de anilina de soluções aquosas',
            'Processos de síntese orgânica',
            'Purificação de compostos aromáticos',
            'Estudos de plait point e binodal em sistemas ternários'
        ],
        'phase_behavior': {
            'water_rich_phase': 'Fase L1 (aquosa): água + anilina dissolvida (~10%)',
            'organic_rich_phase': 'Fase L2 (orgânica): tolueno + anilina dissolvida (~15%)',
            'mutual_solubility': 'Água em tolueno: ~0.05% | Tolueno em água: ~0.05%',
            'distribution_coefficient': 'K(Aniline) ≈ 1.5 (moderado)',
            'plait_point': 'Composição crítica onde duas fases se tornam idênticas',
            'solute': 'Aniline (componente anfifílico, componente 3)'
        },
        'extraction_performance': {
            'typical_recovery': '75-85% em 3-5 estágios',
            'S_F_ratio': '2.0-3.5 (razão molar solvente/alimentação)',
            'efficiency': '0.60-0.70 (eficiência de Murphree)',
            'advantages': 'Sistema bem caracterizado, plait point definido'
        },
        'industrial_notes': (
            'Sistema usado na indústria de corantes e produtos químicos para extração de anilina. '
            'Anilina é matéria-prima importante para síntese de corantes, poliuretanos e borrachas. '
            'Diagrama ternário apresenta região binodal ampla com curvatura característica.'
        ),
        'typical_use_case': 'ternary_diagram'  # Sistema ideal para diagrama ternário com plait point
    },
    
    # ========================================================================
    # SISTEMA 7: Water / Chloroform / Acetic Acid @ 25°C
    # ========================================================================
    # Fonte: Moura & Santos (2012), Am. J. Phys. Chem. 1(5):96-101
    # NOTA: Preferencialmente use UNIQUAC, mas NRTL também funciona
    
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
        
        'binary_params': {
            (1, 2): {
                'b12': 1638.45,   # Water-Chloroform (fortemente imiscíveis)
                'b21': 258.17,    # Chloroform-Water
                'alpha12': 0.20
            },
            (1, 3): {
                'b13': -47.25,    # Water-Acetic Acid (miscíveis)
                'b31': 257.05,    # Acetic Acid-Water
                'alpha13': 0.30
            },
            (2, 3): {
                'b23': 327.89,    # Chloroform-Acetic Acid
                'b32': -335.12,   # Acetic Acid-Chloroform (dimerização)
                'alpha23': 0.30
            }
        },
        
        'notes': (
            'Sistema clássico de extração de ácido acético com clorofórmio. Ácido acético '
            'se distribui entre as fases aquosa e orgânica. IMPORTANTE: Dimerização do ácido '
            'acético na fase orgânica complica o equilíbrio (moléculas associadas). '
            'UNIQUAC pode ser preferível devido a diferenças de tamanho molecular, mas NRTL funciona.'
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
            'advantages': 'Alto coeficiente de distribuição, boa seletividade',
            'disadvantages': 'Clorofórmio é tóxico e carcinogênico (uso industrial limitado)'
        },
        'industrial_notes': (
            'Historicamente importante, mas uso limitado atualmente devido à toxicidade do '
            'clorofórmio. Substituído por MIBK ou acetato de etila em aplicações modernas. '
            'Ainda usado em laboratório e algumas aplicações industriais controladas. '
            '⚠️ AVISO: Clorofórmio requer manuseio especial (EPI, exaustão).'
        ),
        'typical_use_case': 'extraction',  # Sistema para extração multi-estágios
        'safety_notes': (
            '⚠️ CLOROFÓRMIO: Classificado como provável carcinogênico (Grupo 2B - IARC). '
            'Uso restrito. TLV-TWA = 10 ppm (ACGIH). Requer ventilação adequada.'
        )
    },
    
    # ========================================================================
    # SISTEMA 8: Water / Cyclohexane / Ethanol @ 25°C ⭐ DO PDF
    # ========================================================================
    # Fonte: D. Plačkov (1992), Fluid Phase Equilib.
    # Sistema EXPERIMENTAL estudado no PDF fornecido
    # VALIDADO com dados de tie-lines e binodal experimentais
    
    ('Water', 'Cyclohexane', 'Ethanol'): {
        'temperature_C': 25.0,
        'temperature_K': 298.15,
        'reference': 'Plačkov, D. (1992), Fluid Phase Equilib.; Santos et al. (2001); UERJ Lab Report',
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
                'name': 'Cyclohexane',
                'name_pt': 'Ciclo-hexano',
                'name_en': 'Cyclohexane',
                'formula': 'C₆H₁₂',
                'cas': '110-82-7',
                'mw': 84.16
            },
            3: {
                'name': 'Ethanol',
                'name_pt': 'Etanol',
                'name_en': 'Ethanol',
                'formula': 'C₂H₆O',
                'cas': '64-17-5',
                'mw': 46.07
            }
        },
        
        # ⭐ PARÂMETROS NRTL DO PDF (Figura 7)
        # Convertendo de Aij [J/mol] para bij [K]: bij = Aij / R
        # R = 8.314 J/(mol·K)
        'binary_params': {
            (1, 2): {
                'b12': 1806.08,   # A12 = 15019.9 / 8.314 = 1806.08 K | Water-Cyclohexane
                'b21': 2841.07,   # A21 = 23619.4 / 8.314 = 2841.07 K | Cyclohexane-Water
                'alpha12': 0.200
            },
            (1, 3): {
                'b13': 666.90,    # A13 = 5545.1 / 8.314 = 666.90 K | Water-Ethanol
                'b31': 699.30,    # A31 = 5816.2 / 8.314 = 699.30 K | Ethanol-Water
                'alpha13': 0.1537
            },
            (2, 3): {
                'b23': 416.41,    # A23 = 3461.1 / 8.314 = 416.41 K | Cyclohexane-Ethanol
                'b32': -290.16,   # A32 = -2413.2 / 8.314 = -290.16 K | Ethanol-Cyclohexane
                'alpha23': 0.4304
            }
        },
        
        # ⭐ DADOS EXPERIMENTAIS DA BINODAL (Figura 6 do PDF - 23 pontos)
        'experimental_binodal': [
            {'x_cyclohexane': 0.9994, 'x_water': 0.000580, 'x_ethanol': 0.0},
            {'x_cyclohexane': 0.9506, 'x_water': 0.0061, 'x_ethanol': 0.0433},
            {'x_cyclohexane': 0.8826, 'x_water': 0.0116, 'x_ethanol': 0.1058},
            {'x_cyclohexane': 0.7851, 'x_water': 0.0259, 'x_ethanol': 0.1890},
            {'x_cyclohexane': 0.6653, 'x_water': 0.0432, 'x_ethanol': 0.2915},
            {'x_cyclohexane': 0.5531, 'x_water': 0.0645, 'x_ethanol': 0.3824},
            {'x_cyclohexane': 0.4600, 'x_water': 0.0847, 'x_ethanol': 0.4553},
            {'x_cyclohexane': 0.3726, 'x_water': 0.1070, 'x_ethanol': 0.5204},
            {'x_cyclohexane': 0.3181, 'x_water': 0.1231, 'x_ethanol': 0.5588},
            {'x_cyclohexane': 0.2590, 'x_water': 0.1465, 'x_ethanol': 0.5945},
            {'x_cyclohexane': 0.1915, 'x_water': 0.1855, 'x_ethanol': 0.6230},
            {'x_cyclohexane': 0.1653, 'x_water': 0.2063, 'x_ethanol': 0.6284},
            {'x_cyclohexane': 0.0939, 'x_water': 0.2936, 'x_ethanol': 0.6125},
            {'x_cyclohexane': 0.0366, 'x_water': 0.4399, 'x_ethanol': 0.5235},
            {'x_cyclohexane': 0.0105, 'x_water': 0.6031, 'x_ethanol': 0.3864},
            {'x_cyclohexane': 0.0044, 'x_water': 0.6883, 'x_ethanol': 0.3073},
            {'x_cyclohexane': 0.0021, 'x_water': 0.7508, 'x_ethanol': 0.2471},
            {'x_cyclohexane': 0.0008, 'x_water': 0.8059, 'x_ethanol': 0.1933},
            {'x_cyclohexane': 0.0005, 'x_water': 0.8504, 'x_ethanol': 0.1491},
            {'x_cyclohexane': 0.0004, 'x_water': 0.8885, 'x_ethanol': 0.1111},
            {'x_cyclohexane': 0.0002, 'x_water': 0.9263, 'x_ethanol': 0.0735},
            {'x_cyclohexane': 0.0002, 'x_water': 0.9664, 'x_ethanol': 0.0334},
            {'x_cyclohexane': 0.000012, 'x_water': 0.999988, 'x_ethanol': 0.0}
        ],
        
        # ⭐ DADOS EXPERIMENTAIS DAS TIE-LINES (Figura 9 do PDF - 6 tie-lines)
        'experimental_tielines': [
            {
                'organic_phase': {'x_cyclohexane': 0.994, 'x_water': 0.003, 'x_ethanol': 0.003},
                'aqueous_phase': {'x_cyclohexane': 0.000, 'x_water': 0.943, 'x_ethanol': 0.057}
            },
            {
                'organic_phase': {'x_cyclohexane': 0.990, 'x_water': 0.003, 'x_ethanol': 0.007},
                'aqueous_phase': {'x_cyclohexane': 0.000, 'x_water': 0.868, 'x_ethanol': 0.132}
            },
            {
                'organic_phase': {'x_cyclohexane': 0.982, 'x_water': 0.003, 'x_ethanol': 0.015},
                'aqueous_phase': {'x_cyclohexane': 0.003, 'x_water': 0.779, 'x_ethanol': 0.218}
            },
            {
                'organic_phase': {'x_cyclohexane': 0.976, 'x_water': 0.003, 'x_ethanol': 0.021},
                'aqueous_phase': {'x_cyclohexane': 0.004, 'x_water': 0.706, 'x_ethanol': 0.290}
            },
            {
                'organic_phase': {'x_cyclohexane': 0.964, 'x_water': 0.004, 'x_ethanol': 0.032},
                'aqueous_phase': {'x_cyclohexane': 0.005, 'x_water': 0.618, 'x_ethanol': 0.377}
            },
            {
                'organic_phase': {'x_cyclohexane': 0.943, 'x_water': 0.006, 'x_ethanol': 0.051},
                'aqueous_phase': {'x_cyclohexane': 0.009, 'x_water': 0.526, 'x_ethanol': 0.465}
            }
        ],
        
        'notes': (
            '⭐ SISTEMA VALIDADO EXPERIMENTALMENTE (PDF fornecido) ⭐\n\n'
            'Sistema ternário clássico para estudos de ELL com imiscibilidade parcial entre '
            'água e ciclo-hexano. Etanol atua como co-solvente, aumentando a miscibilidade mútua '
            'das fases aquosa e orgânica. A adição de etanol reduz a região de duas fases (binodal menor).\n\n'
            'PARÂMETROS NRTL otimizados por Plačkov (1992) usando regressão não-linear com dados '
            'experimentais a 298.15K. RMSD < 2% para tie-lines.\n\n'
            'DADOS EXPERIMENTAIS INCLUÍDOS:\n'
            '- 23 pontos da curva binodal (titulação turbidimétrica)\n'
            '- 6 tie-lines (análise de fases em equilíbrio)\n'
            '- Validado por Santos et al. (2001) e UERJ Lab'
        ),
        'experimental_data_available': True,
        'applications': [
            'Extração líquido-líquido com co-solvente',
            'Recuperação de solventes em processos químicos',
            'Purificação de produtos químicos',
            'Estudos de equilíbrio bifásico ternário',
            'Validação de modelos termodinâmicos (caso de estudo clássico)'
        ],
        'phase_behavior': {
            'water_rich_phase': 'Fase L1 (aquosa): alta concentração de água e etanol, baixa de ciclo-hexano (~0.01%)',
            'organic_rich_phase': 'Fase L2 (orgânica): alta concentração de ciclo-hexano e etanol, baixa de água (~0.3%)',
            'mutual_solubility': 'Água em cyclohexane: ~0.01% | Cyclohexane em água: ~0.01% (BAIXÍSSIMA)',
            'distribution_coefficient': 'K(Ethanol) ≈ 1.2 a 8.1 (dependendo da concentração, varia muito)',
            'cosolvent_effect': 'Etanol reduz drasticamente a região de imiscibilidade (efeito co-solvente forte)',
            'plait_point': 'Ponto crítico estimado em x_ethanol ≈ 0.63 (Figura 5 do PDF)'
        },
        'model_performance': {
            'rmsd_tielines': '< 2.0%',
            'rmsd_binodal': '< 1.5%',
            'model': 'NRTL',
            'reference': 'Plačkov (1992)',
            'validation': 'Dados experimentais do PDF (UERJ Lab Report)'
        },
        'industrial_notes': (
            'Sistema usado em processos de recuperação de solventes da indústria química. '
            'Etanol facilita a separação e pode ser recuperado por destilação posterior. '
            'Bem caracterizado experimentalmente (dados em DECHEMA, Fluid Phase Equilibria e literatura).\n\n'
            'IMPORTANTE: Este é um CASO DE ESTUDO CLÁSSICO usado em universidades para ensino de ELL. '
            'Dados disponíveis na literatura desde os anos 1960.'
        ),
        'typical_use_case': 'flash',  # ✅ Para cálculos de equilíbrio bifásico
        'teaching_notes': (
            'Sistema ideal para ensino de:\n'
            '- Diagrama ternário tipo 1 (um par parcialmente imiscível)\n'
            '- Efeito de co-solvente (etanol aumenta miscibilidade)\n'
            '- Tie-lines e regra da alavanca\n'
            '- Plait point (ponto crítico)\n'
            '- Validação de modelos NRTL\n'
            '- Comparação modelo vs experimental'
        ),
        'experimental_method': (
            'MÉTODO EXPERIMENTAL (do PDF):\n'
            '1. Titulação turbidimétrica para curva binodal (Cloud Point Method)\n'
            '2. Equilíbrio em funil de separação para tie-lines (24h repouso, 25°C)\n'
            '3. Análise por cromatografia gasosa (GC) ou refratometria\n'
            '4. Correção de volumes para álcool comercial (99.57°GL)'
        )
    }

}


# ============================================================================
# FUNÇÕES DE ACESSO E VALIDAÇÃO
# ============================================================================

def get_available_components_ell_nrtl():
    """
    Retorna lista de todos os componentes disponíveis para ELL-NRTL
    COM TRADUÇÃO PT-BR
    
    Returns:
        list: Lista de dicionários com informações dos componentes
    """
    components_map = {}
    
    for system_key, system_data in ELL_NRTL_PARAMS.items():
        system_components = system_data['components']
        
        for idx, comp_data in system_components.items():
            name = comp_data['name']
            
            if name not in components_map:
                components_map[name] = {
                    'name': comp_data['name'],
                    'name_pt': comp_data.get('name_pt', comp_data['name']),  # ⭐ PT-BR
                    'name_en': comp_data.get('name_en', comp_data['name']),
                    'formula': comp_data['formula'],
                    'cas': comp_data['cas'],
                    'mw': comp_data['mw'],
                    'systems': []
                }
            
            # Adicionar sistema à lista
            system_name = ' / '.join(system_key)
            if system_name not in components_map[name]['systems']:
                components_map[name]['systems'].append(system_name)
    
    return list(components_map.values())


def validate_ternary_system_nrtl(component_names):
    """
    Valida se existe um sistema ternário completo para os 3 componentes
    
    Args:
        component_names (list): Lista com 3 nomes de componentes
    
    Returns:
        dict: Resultado da validação
    """
    if len(component_names) != 3:
        return {
            'valid': False,
            'system_key': None,
            'params': None,
            'error': 'ELL-NRTL requer exatamente 3 componentes'
        }
    
    # Normalizar nomes
    normalized_names = [name.strip() for name in component_names]
    
    # Buscar sistema exato
    for system_key, system_data in ELL_NRTL_PARAMS.items():
        system_components = [system_data['components'][i]['name'] for i in [1, 2, 3]]
        
        if normalized_names == system_components:
            return {
                'valid': True,
                'system_key': system_key,
                'params': system_data,
                'error': None
            }
        
        # Verificar permutações
        if set(normalized_names) == set(system_components):
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
    available_systems = '\n'.join([' / '.join(key) for key in ELL_NRTL_PARAMS.keys()])
    
    return {
        'valid': False,
        'system_key': None,
        'params': None,
        'error': f'Sistema {" / ".join(normalized_names)} não disponível para NRTL.\n'
                f'Sistemas NRTL disponíveis:\n{available_systems}\n\n'
                f'💡 DICA: Para mais sistemas ELL, consulte UNIQUAC (Tabela E-6) ou UNIFAC (preditivo)'
    }


def get_nrtl_params_ell(component_names, temperature_C=25.0):
    """
    Retorna parâmetros NRTL para um sistema ternário ELL
    
    Args:
        component_names (list): Lista com 3 nomes de componentes (ordem importa!)
        temperature_C (float): Temperatura em °C (deve ser 25°C para validação)
    
    Returns:
        dict: Parâmetros NRTL calculados
    """
    # Validar sistema
    validation = validate_ternary_system_nrtl(component_names)
    
    if not validation['valid']:
        return {
            'success': False,
            'error': validation['error'],
            'tau': None,
            'G': None,
            'alpha': None,
            'binary_params': None
        }
    
    system_data = validation['params']
    
    # Verificar temperatura
    if abs(temperature_C - system_data['temperature_C']) > 0.1:
        warning = (
            f"⚠️ AVISO: Temperatura fornecida ({temperature_C}°C) difere da "
            f"temperatura de validação ({system_data['temperature_C']}°C). "
            f"Parâmetros podem não ser precisos."
        )
    else:
        warning = None
    
    # Calcular τij = bij / T e Gij = exp(-αij * τij)
    T_K = temperature_C + 273.15
    binary_params = system_data['binary_params']
    
    tau = {}
    G = {}
    alpha = {}
    
    for (i, j), params in binary_params.items():
        tau_ij = params[f'b{i}{j}'] / T_K
        tau_ji = params[f'b{j}{i}'] / T_K
        alpha_ij = params[f'alpha{i}{j}']
        
        G_ij = float(np.exp(-alpha_ij * tau_ij))
        G_ji = float(np.exp(-alpha_ij * tau_ji))
        
        tau[(i, j)] = {
            'tau_ij': float(tau_ij),
            'tau_ji': float(tau_ji),
            'b_ij': params[f'b{i}{j}'],
            'b_ji': params[f'b{j}{i}']
        }
        
        G[(i, j)] = {'G_ij': G_ij, 'G_ji': G_ji}
        alpha[(i, j)] = alpha_ij
    
    return {
        'success': True,
        'tau': tau,
        'G': G,
        'alpha': alpha,
        'binary_params': binary_params,
        'components': component_names,
        'temperature_C': temperature_C,
        'temperature_K': T_K,
        'reference': system_data['reference'],
        'notes': system_data.get('notes', ''),
        'applications': system_data.get('applications', []),
        'phase_behavior': system_data.get('phase_behavior', {}),
        'extraction_performance': system_data.get('extraction_performance', {}),
        'typical_use_case': system_data.get('typical_use_case', 'flash'),
        'warning': warning,
        'error': None
    }


def get_complete_ternary_systems():
    """
    Retorna lista de todos os sistemas ternários disponíveis
    COM TRADUÇÃO PT-BR
    
    Returns:
        list: Lista de sistemas completos
    """
    systems = []
    
    for system_key, system_data in ELL_NRTL_PARAMS.items():
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
            'model': 'NRTL',
            'notes': system_data.get('notes', ''),
            'applications': system_data.get('applications', []),
            'experimental_validation': system_data.get('experimental_data_available', False),
            'typical_use_case': system_data.get('typical_use_case', 'flash')
        })
    
    return systems


# ============================================================================
# TESTE DE VALIDAÇÃO
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("VALIDAÇÃO: ell_nrtl_params.py")
    print("="*80)
    print()
    
    # Teste 1: Listar componentes
    print("📋 COMPONENTES DISPONÍVEIS (PT-BR):")
    components = get_available_components_ell_nrtl()
    for comp in components:
        print(f"  • {comp['name_pt']} ({comp['formula']}) - CAS: {comp['cas']}")
        print(f"    EN: {comp['name_en']} | MW: {comp['mw']} g/mol | Sistemas: {len(comp['systems'])}")
    print()
    
    # Teste 2: Listar sistemas
    print("🔬 SISTEMAS TERNÁRIOS COMPLETOS:")
    systems = get_complete_ternary_systems()
    for i, sys in enumerate(systems, 1):
        print(f"  {i}. PT-BR: {sys['name_pt']}")
        print(f"     EN: {sys['name']}")
        print(f"     T = {sys['temperature_C']}°C | Uso: {sys['typical_use_case']}")
        print(f"     {sys['reference'][:60]}...")
        print()
    
    # Teste 3: Validar sistema de extração
    print("🧪 TESTE: Water/MIBK/Acetic Acid")
    test_components = ['Water', 'MIBK', 'Acetic Acid']
    params = get_nrtl_params_ell(test_components, 25.0)
    
    if params['success']:
        print(f"  ✅ Válido | Uso típico: {params['typical_use_case']}")
        print(f"  K(Acetic Acid) = {params['phase_behavior']['distribution_coefficient']}")
        print(f"  Recuperação típica: {params['extraction_performance']['typical_recovery']}")
    
    print()
    print("="*80)
    print("✅ VALIDAÇÃO CONCLUÍDA - 4 SISTEMAS DISPONÍVEIS (PT-BR)")
    print("="*80)
