# app/data/esl_data.py
"""
ESL Data - Propriedades Termodinâmicas para Equilíbrio Sólido-Líquido
===============================================================================

Base de dados de propriedades de fusão para cálculos de ESL.

Fontes dos dados:
-----------------
1. NIST Chemistry WebBook (https://webbook.nist.gov)
2. Prausnitz et al., "Molecular Thermodynamics of Fluid-Phase Equilibria", 3rd Ed.
3. CRC Handbook of Chemistry and Physics
4. DIPPR Database
5. Literatura científica revisada por pares
6. Dortmund Data Bank (NRTL parameters)
7. UNIFAC parameter tables (Hansen et al., 1991)

Propriedades incluídas:
-----------------------
- Tm: Temperatura de fusão [K]
- Tt: Temperatura do ponto triplo [K]
- Hfus: Entalpia de fusão [J/mol]
- delta_Cp: Diferença de capacidade calorífica [J/(mol·K)]
- Sfus: Entropia de fusão [J/(mol·K)]
- CAS: Chemical Abstracts Service registry number
- name: Nome em português (PT-BR)
- name_en: Nome em inglês
- source: Referência da fonte dos dados

Autor: Plataforma de Equilíbrio de Fases
Data: 2025-12-20
Versão: 2.1 - Com parâmetros NRTL, UNIQUAC e UNIFAC
"""

import numpy as np

# =============================================================================
# BASE DE DADOS PRINCIPAL - COMPONENTES PUROS
# =============================================================================

ESL_DATA = {
    # =========================================================================
    # HIDROCARBONETOS AROMÁTICOS POLICÍCLICOS (PAH)
    # =========================================================================
    
    'naphthalene': {
        'name': 'Naftaleno',
        'name_en': 'Naphthalene',
        'formula': 'C₁₀H₈',
        'CAS': '91-20-3',
        'MW': 128.1705,
        'Tm': 353.43,
        'Tm_C': 80.28,
        'Tt': 353.39,
        'Hfus': 19046.0,
        'Hfus_kJ_mol': 19.046,
        'Sfus': 53.90,
        'delta_Cp': 0.0,
        'Hvap': 43300.0,
        'source': 'NIST WebBook - Andon & Connett (1980)',
        'uncertainty': {'Tm': 0.7, 'Hfus': 100.0},
        'applications': 'Naftaleno é amplamente usado em estudos de ESL como soluto modelo',
        'notes': 'Composto PAH mais simples, dados de alta qualidade disponíveis'
    },
    
    'anthracene': {
        'name': 'Antraceno',
        'name_en': 'Anthracene',
        'formula': 'C₁₄H₁₀',
        'CAS': '120-12-7',
        'MW': 178.2292,
        'Tm': 489.45,
        'Tm_C': 216.30,
        'Tt': 489.0,
        'Hfus': 28800.0,
        'Hfus_kJ_mol': 28.8,
        'Sfus': 58.8,
        'delta_Cp': 0.0,
        'Hvap': 55200.0,
        'source': 'NIST WebBook + Goldfarb & Kulaots (2010)',
        'uncertainty': {'Tm': 1.0, 'Hfus': 500.0},
        'applications': 'PAH de 3 anéis, usado em estudos de solubilidade em solventes orgânicos',
        'notes': 'Estrutura linear, menor solubilidade que fenantreno'
    },
    
    'phenanthrene': {
        'name': 'Fenantreno',
        'name_en': 'Phenanthrene',
        'formula': 'C₁₄H₁₀',
        'CAS': '85-01-8',
        'MW': 178.2292,
        'Tm': 373.0,
        'Tm_C': 99.85,
        'Tt': 373.0,
        'Hfus': 16460.0,
        'Hfus_kJ_mol': 16.46,
        'Sfus': 44.1,
        'delta_Cp': 0.0,
        'Hvap': 49800.0,
        'source': 'NIST WebBook + Goldfarb & Kulaots (2010)',
        'uncertainty': {'Tm': 1.0, 'Hfus': 400.0},
        'applications': 'PAH de 3 anéis angular, isômero do antraceno',
        'notes': 'Estrutura angular, maior solubilidade que antraceno devido menor Tm e ΔHfus'
    },
    
    'biphenyl': {
        'name': 'Bifenila',
        'name_en': 'Biphenyl',
        'formula': 'C₁₂H₁₀',
        'CAS': '92-52-4',
        'MW': 154.2078,
        'Tm': 342.2,
        'Tm_C': 69.05,
        'Tt': 342.0,
        'Hfus': 18580.0,
        'Hfus_kJ_mol': 18.58,
        'Sfus': 54.3,
        'delta_Cp': 0.0,
        'Hvap': 49900.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.5, 'Hfus': 200.0},
        'applications': 'Bifenilo usado em sistemas binários com naftaleno',
        'notes': 'Dois anéis benzênicos conectados, usado como refrigerante'
    },
    
    # =========================================================================
    # HIDROCARBONETOS AROMÁTICOS SIMPLES
    # =========================================================================
    
    'benzene': {
        'name': 'Benzeno',
        'name_en': 'Benzene',
        'formula': 'C₆H₆',
        'CAS': '71-43-2',
        'MW': 78.1118,
        'Tm': 278.64,
        'Tm_C': 5.49,
        'Tt': 278.5,
        'Hfus': 9870.0,
        'Hfus_kJ_mol': 9.87,
        'Sfus': 35.40,
        'delta_Cp': 0.0,
        'Hvap': 33900.0,
        'source': 'NIST WebBook - Domalski & Hearing (1996)',
        'uncertainty': {'Tm': 0.08, 'Hfus': 50.0},
        'applications': 'Solvente comum em estudos de ESL, referência padrão',
        'notes': 'Composto aromático mais simples, dados de altíssima qualidade'
    },
    
    'toluene': {
        'name': 'Tolueno',
        'name_en': 'Toluene',
        'formula': 'C₇H₈',
        'CAS': '108-88-3',
        'MW': 92.1384,
        'Tm': 178.16,
        'Tm_C': -94.99,
        'Tt': 178.0,
        'Hfus': 6636.0,
        'Hfus_kJ_mol': 6.636,
        'Sfus': 37.2,
        'delta_Cp': 0.0,
        'Hvap': 38000.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.5, 'Hfus': 100.0},
        'applications': 'Solvente industrial comum',
        'notes': 'Metil-benzeno, líquido à temperatura ambiente'
    },
    
    'p_xylene': {
        'name': 'p-Xileno',
        'name_en': 'p-Xylene',
        'formula': 'C₈H₁₀',
        'CAS': '106-42-3',
        'MW': 106.165,
        'Tm': 286.40,
        'Tm_C': 13.25,
        'Tt': 286.4,
        'Hfus': 17120.0,
        'Hfus_kJ_mol': 17.12,
        'Sfus': 59.8,
        'delta_Cp': 0.0,
        'Hvap': 42400.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.3, 'Hfus': 200.0},
        'applications': 'Isômero para do dimetilbenzeno',
        'notes': 'Maior Tm entre os isômeros devido simetria molecular'
    },
    
    # =========================================================================
    # ÁCIDOS ORGÂNICOS
    # =========================================================================
    
    'benzoic_acid': {
        'name': 'Ácido Benzoico',
        'name_en': 'Benzoic Acid',
        'formula': 'C₇H₆O₂',
        'CAS': '65-85-0',
        'MW': 122.1213,
        'Tm': 395.45,
        'Tm_C': 122.30,
        'Tt': 395.5,
        'Hfus': 18020.0,
        'Hfus_kJ_mol': 18.02,
        'Sfus': 45.6,
        'delta_Cp': 0.0,
        'Hvap': 57300.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.5, 'Hfus': 300.0},
        'applications': 'Conservante alimentar, usado em estudos de ESL com ácido salicílico',
        'notes': 'Forma dímeros via ligações H, solúvel em álcoois'
    },
    
    'salicylic_acid': {
        'name': 'Ácido Salicílico',
        'name_en': 'Salicylic Acid',
        'formula': 'C₇H₆O₃',
        'CAS': '69-72-7',
        'MW': 138.1207,
        'Tm': 432.15,
        'Tm_C': 159.0,
        'Tt': 432.0,
        'Hfus': 24300.0,
        'Hfus_kJ_mol': 24.3,
        'Sfus': 56.2,
        'delta_Cp': 0.0,
        'Hvap': 65400.0,
        'source': 'RSC CrystEngComm (2023) - Mohajerani et al.',
        'uncertainty': {'Tm': 1.0, 'Hfus': 500.0},
        'applications': 'Precursor da aspirina, sistema eutético com ácido benzoico',
        'notes': 'Ponto eutético com benzoic acid: 60% BA, T=385.84K (112.69°C)'
    },
    
    'stearic_acid': {
        'name': 'Ácido Esteárico',
        'name_en': 'Stearic Acid',
        'formula': 'C₁₈H₃₆O₂',
        'CAS': '57-11-4',
        'MW': 284.4772,
        'Tm': 342.75,
        'Tm_C': 69.60,
        'Tt': 342.5,
        'Hfus': 61200.0,
        'Hfus_kJ_mol': 61.2,
        'Sfus': 178.6,
        'delta_Cp': 0.0,
        'Hvap': 122000.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.5, 'Hfus': 1000.0},
        'applications': 'Ácido graxo saturado, usado em PCM (phase change materials)',
        'notes': 'Alto ΔHfus, usado para armazenamento térmico'
    },
    
    # =========================================================================
    # FENÓIS E DERIVADOS
    # =========================================================================
    
    'phenol': {
        'name': 'Fenol',
        'name_en': 'Phenol',
        'formula': 'C₆H₆O',
        'CAS': '108-95-2',
        'MW': 94.1112,
        'Tm': 314.06,
        'Tm_C': 40.91,
        'Tt': 314.0,
        'Hfus': 11510.0,
        'Hfus_kJ_mol': 11.51,
        'Sfus': 36.6,
        'delta_Cp': 0.0,
        'Hvap': 57800.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.3, 'Hfus': 200.0},
        'applications': 'Precursor de plásticos e resinas fenólicas',
        'notes': 'Ligações de hidrogênio fortes, alta solubilidade em água'
    },
    
    # ============================================================================
    # ADICIONAR após 'phenol' no dicionário ESLDATA
    # ============================================================================

    'beta-naphthol': {
        'name': 'β-Naftol',
        'name_en': 'beta-Naphthol',
        'formula': 'C10H8O',
        'CAS': '135-19-3',
        'MW': 144.170,
        'Tm': 395.15,  # 122°C
        'Tm_C': 122.0,
        'Tt': 395.0,
        'Hfus': 18700.0,  # 18.7 kJ/mol
        'Hfus_kJ_mol': 18.7,
        'Sfus': 47.3,
        'deltaCp': 0.0,
        'Hvap': 58200.0,
        'source': 'Prausnitz Figure 11-17 (p. 658) + CRC Handbook',
        'uncertainty': {'Tm': 0.5, 'Hfus': 400.0},
        'applications': 'Sistema eutético com naftaleno (Prausnitz Fig. 11-17)',
        'notes': '2-Naftol (β-naftol), possui grupo -OH que forma ligações H. Isômero do α-naftol (1-naftol).'
    },

    
    'resorcinol': {
        'name': 'Resorcinol',
        'name_en': 'Resorcinol',
        'formula': 'C₆H₆O₂',
        'CAS': '108-46-3',
        'MW': 110.1106,
        'Tm': 383.65,
        'Tm_C': 110.50,
        'Tt': 383.5,
        'Hfus': 20800.0,
        'Hfus_kJ_mol': 20.8,
        'Sfus': 54.2,
        'delta_Cp': 0.0,
        'Hvap': 68100.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.5, 'Hfus': 400.0},
        'applications': '1,3-dihidroxibenzeno, usado em adesivos e borrachas',
        'notes': 'Duas hidroxilas em meta, forte ligação H'
    },
    
    'hydroquinone': {
        'name': 'Hidroquinona',
        'name_en': 'Hydroquinone',
        'formula': 'C₆H₆O₂',
        'CAS': '123-31-9',
        'MW': 110.1106,
        'Tm': 445.15,
        'Tm_C': 172.0,
        'Tt': 445.0,
        'Hfus': 26900.0,
        'Hfus_kJ_mol': 26.9,
        'Sfus': 60.4,
        'delta_Cp': 0.0,
        'Hvap': 71200.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 1.0, 'Hfus': 500.0},
        'applications': '1,4-dihidroxibenzeno, revelador fotográfico',
        'notes': 'Hidroxilas em para, maior Tm que resorcinol'
    },
    
    # =========================================================================
    # COMPOSTOS FARMACÊUTICOS / ORGÂNICOS NITROGENADOS
    # =========================================================================
    
    'caffeine': {
        'name': 'Cafeína',
        'name_en': 'Caffeine',
        'formula': 'C₈H₁₀N₄O₂',
        'CAS': '58-08-2',
        'MW': 194.1906,
        'Tm': 511.15,
        'Tm_C': 238.0,
        'Tt': 511.0,
        'Hfus': 22000.0,
        'Hfus_kJ_mol': 22.0,
        'Sfus': 43.0,
        'delta_Cp': 0.0,
        'Hvap': 68000.0,
        'source': 'Literatura farmacêutica',
        'uncertainty': {'Tm': 2.0, 'Hfus': 1000.0},
        'applications': 'Alcaloide, estudos de solubilidade em formulações',
        'notes': 'Sublima abaixo do ponto de fusão, dados com maior incerteza'
    },
    
    'urea': {
        'name': 'Ureia',
        'name_en': 'Urea',
        'formula': 'CH₄N₂O',
        'CAS': '57-13-6',
        'MW': 60.0553,
        'Tm': 406.15,
        'Tm_C': 133.0,
        'Tt': 406.0,
        'Hfus': 14100.0,
        'Hfus_kJ_mol': 14.1,
        'Sfus': 34.7,
        'delta_Cp': 0.0,
        'Hvap': 58500.0,
        'source': 'Voskov et al. (2012) - Phase Equilibria Urea-Biuret-Water',
        'uncertainty': {'Tm': 0.5, 'Hfus': 300.0},
        'applications': 'Fertilizante, sistema eutético com biureto',
        'notes': 'Decompõe-se próximo ao ponto de fusão, forma biureto'
    },
    
    'biuret': {
        'name': 'Biureto',
        'name_en': 'Biuret',
        'formula': 'C₂H₅N₃O₂',
        'CAS': '108-19-0',
        'MW': 103.0806,
        'Tm': 466.15,
        'Tm_C': 193.0,
        'Tt': 466.0,
        'Hfus': 24800.0,
        'Hfus_kJ_mol': 24.8,
        'Sfus': 53.2,
        'delta_Cp': 0.0,
        'Hvap': 72000.0,
        'source': 'Voskov et al. (2012)',
        'uncertainty': {'Tm': 1.5, 'Hfus': 500.0},
        'applications': 'Produto de decomposição de ureia, sistemas eutéticos',
        'notes': 'Sistema eutético com ureia: eutectic a ~379-384K'
    },
    
    # =========================================================================
    # ÁLCOOIS E POLIÓIS
    # =========================================================================
    
    'menthol': {
        'name': 'Mentol',
        'name_en': 'Menthol',
        'formula': 'C₁₀H₂₀O',
        'CAS': '2216-51-5',
        'MW': 156.2652,
        'Tm': 315.15,
        'Tm_C': 42.0,
        'Tt': 315.0,
        'Hfus': 11100.0,
        'Hfus_kJ_mol': 11.1,
        'Sfus': 35.2,
        'delta_Cp': 0.0,
        'Hvap': 49300.0,
        'source': 'CRC Handbook of Chemistry and Physics',
        'uncertainty': {'Tm': 0.5, 'Hfus': 300.0},
        'applications': 'Formulações farmacêuticas, sistemas eutéticos profundos (DES)',
        'notes': 'Usado como componente em DES com ácidos orgânicos'
    },
    
    'camphor': {
        'name': 'Cânfora',
        'name_en': 'Camphor',
        'formula': 'C₁₀H₁₆O',
        'CAS': '76-22-2',
        'MW': 152.2334,
        'Tm': 452.15,
        'Tm_C': 179.0,
        'Tt': 452.0,
        'Hfus': 6100.0,
        'Hfus_kJ_mol': 6.1,
        'Sfus': 13.5,
        'delta_Cp': 0.0,
        'Hvap': 50000.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 1.0, 'Hfus': 200.0},
        'applications': 'Cânfora, sistemas eutéticos',
        'notes': 'Sublima facilmente, baixo ΔHfus'
    },
    
    # =============================================================================
    # ADICIONAR APÓS A SEÇÃO DE ÁLCOOIS E POLIÓIS (linha ~350)
    # =============================================================================

    # =========================================================================
    # ÁLCOOIS DE CADEIA CURTA (para sistemas aquosos)
    # =========================================================================

    'methanol': {
        'name': 'Metanol',
        'name_en': 'Methanol',
        'formula': 'CH₃OH',
        'CAS': '67-56-1',
        'MW': 32.042,
        'Tm': 175.65,  # -97.5°C
        'Tm_C': -97.50,
        'Tt': 175.6,
        'Hfus': 3177.0,
        'Hfus_kJ_mol': 3.177,
        'Sfus': 18.08,
        'delta_Cp': 0.0,
        'Hvap': 35210.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.1, 'Hfus': 50.0},
        'applications': 'Solvente para colesterol, sistemas aquosos',
        'notes': 'Álcool mais simples, miscível com água'
    },

    'ethanol': {
        'name': 'Etanol',
        'name_en': 'Ethanol',
        'formula': 'C₂H₅OH',
        'CAS': '64-17-5',
        'MW': 46.068,
        'Tm': 159.05,  # -114.1°C
        'Tm_C': -114.10,
        'Tt': 159.0,
        'Hfus': 5021.0,
        'Hfus_kJ_mol': 5.021,
        'Sfus': 31.57,
        'delta_Cp': 0.0,
        'Hvap': 38560.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.2, 'Hfus': 80.0},
        'applications': 'Co-solvente em sistemas aquosos, solubilização de PAHs',
        'notes': 'Sistema ternário Naftaleno/Etanol/Água (Prausnitz Fig. 11-14)'
    },

    'propanol_1': {
        'name': '1-Propanol',
        'name_en': '1-Propanol',
        'formula': 'C₃H₇OH',
        'CAS': '71-23-8',
        'MW': 60.095,
        'Tm': 146.95,  # -126.2°C
        'Tm_C': -126.20,
        'Tt': 146.9,
        'Hfus': 5195.0,
        'Hfus_kJ_mol': 5.195,
        'Sfus': 35.35,
        'delta_Cp': 0.0,
        'Hvap': 41400.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.3, 'Hfus': 100.0},
        'applications': 'Co-solvente, sistema ternário com água',
        'notes': 'Sistema Naftaleno/1-Propanol/Água estudado por Prausnitz'
    },

    # =========================================================================
    # HIDROCARBONETOS CÍCLICOS
    # =========================================================================

    'cyclohexane': {
        'name': 'Ciclohexano',
        'name_en': 'Cyclohexane',
        'formula': 'C₆H₁₂',
        'CAS': '110-82-7',
        'MW': 84.159,
        'Tm': 279.69,  # 6.54°C
        'Tm_C': 6.54,
        'Tt': 279.5,
        'Hfus': 2630.0,
        'Hfus_kJ_mol': 2.630,
        'Sfus': 9.40,
        'delta_Cp': 0.0,
        'Hvap': 29970.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.1, 'Hfus': 50.0},
        'applications': 'Solvente apolar para antibióticos (Carbomycin A)',
        'notes': 'Hidrocarboneto saturado cíclico, não aromático'
    },

    'cis_decahydronaphthalene': {
        'name': 'cis-Decalina',
        'name_en': 'cis-Decahydronaphthalene',
        'formula': 'C₁₀H₁₈',
        'CAS': '493-01-6',
        'MW': 138.250,
        'Tm': 230.20,  # -42.95°C
        'Tm_C': -42.95,
        'Tt': 230.0,
        'Hfus': 9490.0,
        'Hfus_kJ_mol': 9.49,
        'Sfus': 41.2,
        'delta_Cp': 0.0,
        'Hvap': 41000.0,
        'source': 'NIST WebBook + Chickos & Acree (2002)',
        'uncertainty': {'Tm': 0.5, 'Hfus': 200.0},
        'applications': 'Solvente para PAHs (Acenafteno)',
        'notes': 'Naftaleno hidrogenado, sistema estudado por Prausnitz'
    },

    # =========================================================================
    # PAHs ADICIONAIS
    # =========================================================================

    'acenaphthene': {
        'name': 'Acenafteno',
        'name_en': 'Acenaphthene',
        'formula': 'C₁₂H₁₀',
        'CAS': '83-32-9',
        'MW': 154.207,
        'Tm': 366.56,  # 93.41°C
        'Tm_C': 93.41,
        'Tt': 366.5,
        'Hfus': 21490.0,
        'Hfus_kJ_mol': 21.49,
        'Sfus': 58.6,
        'delta_Cp': 0.0,
        'Hvap': 52300.0,
        'source': 'NIST WebBook + Goldfarb & Kulaots (2010)',
        'uncertainty': {'Tm': 0.3, 'Hfus': 300.0},
        'applications': 'Sistema ternário Benzeno/Acenafteno/Fenol (Prausnitz Fig. 11-11)',
        'notes': 'PAH tricíclico com ponte etênica'
    },

    # =========================================================================
    # AROMÁTICOS CLORADOS/NITRADOS
    # =========================================================================

    'o_chloronitrobenzene': {
        'name': 'o-Cloronitrobenzeno',
        'name_en': 'o-Chloronitrobenzene',
        'formula': 'C₆H₄ClNO₂',
        'CAS': '88-73-3',
        'MW': 157.555,
        'Tm': 305.85,  # 32.7°C
        'Tm_C': 32.70,
        'Tt': 305.8,
        'Hfus': 17900.0,
        'Hfus_kJ_mol': 17.9,
        'Sfus': 58.5,
        'delta_Cp': 0.0,
        'Hvap': 52400.0,
        'source': 'CRC Handbook + Prausnitz',
        'uncertainty': {'Tm': 0.5, 'Hfus': 400.0},
        'applications': 'Sistema eutético clássico com p-cloronitrobenzeno (Prausnitz Fig. 11-5)',
        'notes': 'Isômero orto, forma eutético simples'
    },

    'p_chloronitrobenzene': {
        'name': 'p-Cloronitrobenzeno',
        'name_en': 'p-Chloronitrobenzene',
        'formula': 'C₆H₄ClNO₂',
        'CAS': '100-00-5',
        'MW': 157.555,
        'Tm': 356.65,  # 83.5°C
        'Tm_C': 83.50,
        'Tt': 356.6,
        'Hfus': 19200.0,
        'Hfus_kJ_mol': 19.2,
        'Sfus': 53.8,
        'delta_Cp': 0.0,
        'Hvap': 54100.0,
        'source': 'CRC Handbook + Prausnitz',
        'uncertainty': {'Tm': 0.5, 'Hfus': 400.0},
        'applications': 'Sistema eutético clássico, exemplo didático em Prausnitz',
        'notes': 'Isômero para, Tm maior que orto devido simetria'
    },

    # =========================================================================
    # ESTERÓIS E COMPOSTOS FARMACÊUTICOS
    # =========================================================================

    'cholesterol': {
        'name': 'Colesterol',
        'name_en': 'Cholesterol',
        'formula': 'C₂₇H₄₆O',
        'CAS': '57-88-5',
        'MW': 386.654,
        'Tm': 421.65,  # 148.5°C
        'Tm_C': 148.50,
        'Tt': 421.5,
        'Hfus': 28450.0,
        'Hfus_kJ_mol': 28.45,
        'Sfus': 67.5,
        'delta_Cp': 0.0,
        'Hvap': 98000.0,
        'source': 'CRC Handbook + Literatura farmacêutica',
        'uncertainty': {'Tm': 1.0, 'Hfus': 1000.0},
        'applications': 'Solubilidade em metanol, estudos farmacêuticos',
        'notes': 'Esterol biológico importante, cristalização em vesículas'
    },

    'carbomycin_a': {
        'name': 'Carbomicina A',
        'name_en': 'Carbomycin A',
        'formula': 'C₄₂H₆₇NO₁₆',
        'CAS': '4564-87-8',
        'MW': 841.968,
        'Tm': 477.15,  # 204°C (estimado, decompõe)
        'Tm_C': 204.0,
        'Tt': 477.0,
        'Hfus': 52000.0,  # Estimado
        'Hfus_kJ_mol': 52.0,
        'Sfus': 109.0,
        'delta_Cp': 0.0,
        'Hvap': 150000.0,
        'source': 'Literatura antibióticos + estimativas',
        'uncertainty': {'Tm': 3.0, 'Hfus': 5000.0},
        'applications': 'Antibiótico macrolídeo, solubilidade em solventes orgânicos',
        'notes': 'Decompõe antes de fundir, dados experimentais escassos'
    },

    
    # =========================================================================
    # N-ALCANOS (para sistemas parafínicos)
    # =========================================================================
    
    'hexadecane': {
        'name': 'Hexadecano',
        'name_en': 'Hexadecane',
        'formula': 'C₁₆H₃₄',
        'CAS': '544-76-3',
        'MW': 226.4412,
        'Tm': 291.31,
        'Tm_C': 18.16,
        'Tt': 291.0,
        'Hfus': 53360.0,
        'Hfus_kJ_mol': 53.36,
        'Sfus': 183.2,
        'delta_Cp': 0.0,
        'Hvap': 81350.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.2, 'Hfus': 500.0},
        'applications': 'n-alcano, PCM, misturas com aromáticos',
        'notes': 'Usado como solvente e em estudos de cristalização parafínica'
    },
    
    'octadecane': {
        'name': 'Octadecano',
        'name_en': 'Octadecane',
        'formula': 'C₁₈H₃₈',
        'CAS': '593-45-3',
        'MW': 254.4946,
        'Tm': 301.31,
        'Tm_C': 28.16,
        'Tt': 301.0,
        'Hfus': 61110.0,
        'Hfus_kJ_mol': 61.11,
        'Sfus': 202.8,
        'delta_Cp': 0.0,
        'Hvap': 91440.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.2, 'Hfus': 600.0},
        'applications': 'PCM para armazenamento térmico',
        'notes': 'Alto ΔHfus, boa estabilidade térmica'
    },
    
    'eicosane': {
        'name': 'Eicosano',
        'name_en': 'Eicosane',
        'formula': 'C₂₀H₄₂',
        'CAS': '112-95-8',
        'MW': 282.5480,
        'Tm': 309.58,
        'Tm_C': 36.43,
        'Tt': 309.5,
        'Hfus': 69900.0,
        'Hfus_kJ_mol': 69.9,
        'Sfus': 225.8,
        'delta_Cp': 0.0,
        'Hvap': 101600.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.3, 'Hfus': 700.0},
        'applications': 'n-alcano C20, PCM',
        'notes': 'Parte de misturas comerciais de parafinas'
    },
    
    # Adicionar água para sistemas aquosos
    'water': {
        'name': 'Água',
        'name_en': 'Water',
        'formula': 'H₂O',
        'CAS': '7732-18-5',
        'MW': 18.0153,
        'Tm': 273.15,
        'Tm_C': 0.0,
        'Tt': 273.16,
        'Hfus': 6010.0,
        'Hfus_kJ_mol': 6.01,
        'Sfus': 22.0,
        'delta_Cp': 0.0,
        'Hvap': 40660.0,
        'source': 'NIST WebBook',
        'uncertainty': {'Tm': 0.01, 'Hfus': 5.0},
        'applications': 'Solvente universal, sistemas aquosos',
        'notes': 'Ponto de fusão padrão de referência'
    },
    
    'sodiumchloride': {
        'name': 'Cloreto de Sódio',
        'name_en': 'Sodium Chloride',
        'formula': 'NaCl',
        'CAS': '7647-14-5',
        'MW': 58.44,
        'Tm': 1074.15,  # 801°C
        'TmC': 801.0,
        'Tt': 1074.0,
        'Hfus': 28160.0,  # J/mol (NIST)
        'HfuskJmol': 28.16,
        'Sfus': 26.2,
        'deltaCp': 0.0,
        'Hvap': 170000.0,
        'source': 'NIST WebBook - CRC Handbook',
        'uncertainty': {'Tm': 1.0, 'Hfus': 500.0},
        'applications': 'Sal de cozinha, solubilidade em água, cristalização',
        'notes': '⚠️ Eletrólito - modelos de γ não são adequados. Use modelo de van\'t Hoff ou Pitzer.'
    }
}

# =============================================================================
# PARÂMETROS NRTL (τ₁₂, τ₂₁, α₁₂)
# Fonte: Dortmund Data Bank / Aspen Plus (Beneke et al., 2013)
# =============================================================================

NRTL_PARAMETERS = {
    # Naftaleno + Benzeno (sistema aromático clássico para ESL)
    ('Naftaleno', 'Benzeno'): {
        'tau12': 0.0,  # Sistema quase ideal
        'tau21': 0.0,
        'alpha': 0.3,
        'a12': -11.120,
        'a21': 3.4460,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Dortmund Data Bank (Beneke et al., 2013)',
        'notes': 'Sistema aromático, quase ideal devido similaridade molecular'
    },
    
    # Benzeno + Fenol (sistema aromático + OH)
    ('Benzeno', 'Fenol'): {
        'tau12': 1.5313,  # τ = b/T
        'tau21': 0.3694,
        'alpha': 0.2,
        'a12': 45.191,
        'a21': 140.087,
        'b12': 591.4,
        'b21': 5954.3,
        'source': 'Dortmund Data Bank (Beneke et al., 2013)',
        'notes': 'Interação aromático-fenol, ligações H moderadas'
    },
    
    # Tolueno + Naftaleno (aromáticos de tamanhos diferentes)
    ('Tolueno', 'Naftaleno'): {
        'tau12': 0.4561,
        'tau21': 0.2891,
        'alpha': 0.3,
        'a12': 2.191,
        'a21': 2.885,
        'b12': 863.7,
        'b21': 1124.0,
        'source': 'Dortmund Data Bank (Beneke et al., 2013)',
        'notes': 'Sistema não-ideal moderado'
    },
    
    # Benzeno + p-Xileno (isômeros aromáticos)
    ('Benzeno', 'p-Xileno'): {
        'tau12': 0.0412,
        'tau21': 0.0458,
        'alpha': 0.3,
        'a12': 0.0,
        'a21': 0.0,
        'b12': 122.7,
        'b21': 136.5,
        'source': 'Dortmund Data Bank (Beneke et al., 2013)',
        'notes': 'Sistema quase ideal, estruturas similares'
    },
    
    # Fenol + Água (sistema aquoso com ligação H forte)
    ('Fenol', 'Água'): {
        'tau12': 1.0851,
        'tau21': 2.0581,
        'alpha': 0.3,
        'a12': 324.50,
        'a21': 362.30,
        'b12': 0.0,  # Parâmetros típicos, podem precisar fitting
        'b21': 0.0,
        'source': 'Estimado a partir de sistemas fenólicos',
        'notes': 'Forte interação por ligação de hidrogênio'
    },
    
    # =============================================================================
    # ADICIONAR AO NRTL_PARAMETERS (após linha ~700)
    # =============================================================================

    # Naftaleno + Etanol (sistema aquoso-orgânico)
    ('Naftaleno', 'Etanol'): {
        'tau12': 2.1847,
        'tau21': 0.8934,
        'alpha': 0.3,
        'a12': 652.4,
        'a21': 266.5,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Estimado de sistemas PAH-álcool',
        'notes': 'PAH apolar + álcool polar, não-idealidade moderada'
    },

    # Naftaleno + 1-Propanol
    ('Naftaleno', '1-Propanol'): {
        'tau12': 1.9234,
        'tau21': 0.7821,
        'alpha': 0.3,
        'a12': 574.2,
        'a21': 233.4,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Estimado similaridade com etanol',
        'notes': 'Álcool de cadeia mais longa, menor polaridade'
    },

    # Acenafteno + Benzeno (aromáticos)
    ('Acenafteno', 'Benzeno'): {
        'tau12': 0.3421,
        'tau21': 0.2156,
        'alpha': 0.3,
        'a12': 102.1,
        'a21': 64.4,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Estimado de sistemas PAH-aromáticos',
        'notes': 'Sistema aromático, quase ideal'
    },

    # Acenafteno + Fenol
    ('Acenafteno', 'Fenol'): {
        'tau12': 1.8932,
        'tau21': 0.6745,
        'alpha': 0.25,
        'a12': 565.2,
        'a21': 201.3,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Sistema ternário Benzeno/Acenafteno/Fenol (Prausnitz)',
        'notes': 'Ligações H PAH-fenol'
    },

    # Acenafteno + cis-Decalina (hidrocarbonetos)
    ('Acenafteno', 'cis-Decalina'): {
        'tau12': 0.1234,
        'tau21': 0.0987,
        'alpha': 0.3,
        'a12': 36.8,
        'a21': 29.4,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Estimado sistema aromático-saturado',
        'notes': 'Ambos hidrocarbonetos, não-idealidade fraca'
    },

    # Colesterol + Metanol (sistema farmacêutico)
    ('Colesterol', 'Metanol'): {
        'tau12': 1.2456,
        'tau21': 2.3421,
        'alpha': 0.3,
        'a12': 372.0,
        'a21': 699.2,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Literatura farmacêutica',
        'notes': 'Esterol apolar + álcool polar, alta não-idealidade'
    },

    # o-Cloronitrobenzeno + p-Cloronitrobenzeno (isômeros)
    ('o-Cloronitrobenzeno', 'p-Cloronitrobenzeno'): {
        'tau12': 0.0523,
        'tau21': 0.0487,
        'alpha': 0.3,
        'a12': 15.6,
        'a21': 14.5,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Prausnitz Fig. 11-5',
        'notes': 'Sistema eutético clássico, quase ideal'
    },

    # Ácido Benzoico + Ácido Salicílico (ADICIONAR SE NÃO EXISTE)
    ('Ácido Benzoico', 'Ácido Salicílico'): {
        'tau12': 0.3214,
        'tau21': -0.2891,
        'alpha': 0.3,
        'a12': 95.9,
        'a21': -86.3,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Fitted from RSC CrystEngComm (2023)',
        'notes': 'Sistema ácido-ácido com ligações H, eutético a 60% BA'
    },
    
    # ============================================================================
    # ADICIONAR ao dicionário NRTL_PARAMETERS (sistema aromático OH)
    # ============================================================================

    ('Naftaleno', 'β-Naftol'): {
        'tau12': 0.8234,
        'tau21': 0.4567,
        'alpha': 0.25,
        'a12': 245.7,
        'a21': 136.3,
        'b12': 0.0,
        'b21': 0.0,
        'source': 'Estimado de sistemas PAH-fenol (Prausnitz Fig. 11-17)',
        'notes': 'PAH aromático + grupo -OH, ligações H moderadas'
    },


}

# =============================================================================
# PARÂMETROS UNIQUAC (u₁₂, u₂₁) + propriedades r, q
# Fonte: DECHEMA Chemistry Data Series / Literatura
# =============================================================================

UNIQUAC_PARAMETERS = {
    ('Naftaleno', 'Benzeno'): {
        'u12': -10.5,  # (u₁₂ - u₂₂) [K]
        'u21': 25.3,   # (u₂₁ - u₁₁) [K]
        'source': 'DECHEMA + Literatura ESL',
        'notes': 'Sistema aromático, não-idealidade fraca'
    },
    
    ('Benzeno', 'Fenol'): {
        'u12': 215.8,
        'u21': -158.3,
        'source': 'Literatura de equilíbrio líquido-líquido',
        'notes': 'Interação aromático-OH significativa'
    },
    
    ('Ácido Benzoico', 'Ácido Salicílico'): {
        'u12': 42.1,
        'u21': -35.6,
        'source': 'Fitted from SLE data (Mohajerani et al., 2023)',
        'notes': 'Sistema eutético bem caracterizado'
    },
    
    ('Tolueno', 'Naftaleno'): {
        'u12': 18.7,
        'u21': -12.4,
        'source': 'DECHEMA',
        'notes': 'Aromáticos de tamanhos diferentes'
    },
    
    # ============================================================================
    # ADICIONAR ao UNIQUACPARAMETERS
    # ============================================================================

    ('Naftaleno', 'β-Naftol'): {
        'u12': 189.4,  # u12 - u22 (K)
        'u21': -97.2,  # u21 - u11 (K)
        'source': 'Estimado de sistemas aromáticos com -OH',
        'notes': 'Interação aromático-hidroxila'
    },

}

# Propriedades estruturais UNIQUAC (r = volume, q = área superficial)
# Fonte: Prausnitz et al. "Molecular Thermodynamics" + UNIFAC tables
UNIQUAC_PURE_PROPERTIES = {
    'Naftaleno': {'r': 5.1734, 'q': 3.904},
    'Benzeno': {'r': 3.1878, 'q': 2.400},
    'Ácido Benzoico': {'r': 4.6502, 'q': 3.488},
    'Ácido Salicílico': {'r': 5.0214, 'q': 3.760},
    'Antraceno': {'r': 6.9230, 'q': 5.408},
    'Fenantreno': {'r': 6.9230, 'q': 5.408},
    'Bifenila': {'r': 5.9246, 'q': 4.240},
    'Tolueno': {'r': 3.9228, 'q': 2.968},
    'p-Xileno': {'r': 4.6578, 'q': 3.536},
    'Fenol': {'r': 3.5517, 'q': 2.680},
    'Resorcinol': {'r': 4.0093, 'q': 3.128},
    'Hidroquinona': {'r': 4.0093, 'q': 3.128},
    'Cafeína': {'r': 7.0840, 'q': 5.376},
    'Ureia': {'r': 1.5928, 'q': 1.472},
    'Biureto': {'r': 2.7536, 'q': 2.408},
    'Mentol': {'r': 6.0181, 'q': 4.720},
    'Cânfora': {'r': 5.7442, 'q': 4.528},
    'Hexadecano': {'r': 11.2380, 'q': 8.872},
    'Octadecano': {'r': 12.5930, 'q': 9.944},
    'Eicosano': {'r': 13.9480, 'q': 11.016},
    'Ácido Esteárico': {'r': 12.8822, 'q': 10.192},
    'Água': {'r': 0.92, 'q': 1.40},
    # =============================================================================
    # ADICIONAR AO UNIQUAC_PURE_PROPERTIES (após linha ~850)
    # =============================================================================

    'Metanol': {'r': 1.4311, 'q': 1.432},
    'Etanol': {'r': 2.1055, 'q': 1.972},
    '1-Propanol': {'r': 2.7799, 'q': 2.512},
    'Ciclohexano': {'r': 4.0464, 'q': 3.240},
    'cis-Decalina': {'r': 6.1514, 'q': 4.880},
    'Acenafteno': {'r': 6.0872, 'q': 4.652},
    'o-Cloronitrobenzeno': {'r': 4.2013, 'q': 3.168},
    'p-Cloronitrobenzeno': {'r': 4.2013, 'q': 3.168},
    'Colesterol': {'r': 15.8742, 'q': 12.360},
    'Carbomicina A': {'r': 32.4567, 'q': 25.840},  # Estimado, molécula grande
    # ============================================================================
    # ADICIONAR ao UNIQUACPUREPROPERTIES
    # ============================================================================

    'β-Naftol': {'r': 5.2089, 'q': 3.904},


}

# =============================================================================
# GRUPOS FUNCIONAIS UNIFAC
# Fonte: Hansen et al. (1991), Fredenslund et al.
# =============================================================================

UNIFAC_GROUPS = {
    'Naftaleno': {
        'ACH': 8,   # Aromático CH
        'AC': 2     # Aromático C (ponte)
    },
    'Benzeno': {
        'ACH': 6    # 6 CH aromáticos
    },
    'Ácido Benzoico': {
        'ACH': 5,   # 5 CH aromáticos
        'AC': 1,    # 1 C aromático
        'COOH': 1   # Grupo carboxila
    },
    'Ácido Salicílico': {
        'ACH': 4,
        'AC': 2,
        'COOH': 1,
        'ACOH': 1   # Hidroxila fenólica
    },
    'Tolueno': {
        'ACH': 5,
        'ACCH3': 1  # Metil aromático
    },
    'p-Xileno': {
        'ACH': 4,
        'ACCH3': 2
    },
    'Fenol': {
        'ACH': 5,
        'ACOH': 1
    },
    'Bifenila': {
        'ACH': 10
    },
    'Antraceno': {
        'ACH': 10,
        'AC': 4
    },
    'Fenantreno': {
        'ACH': 10,
        'AC': 4
    },
    'Ureia': {
        'CONH2': 1,  # Grupo especial ureia
        'CH4N2O': 1  # Tratamento especial
    },
    'Hexadecano': {
        'CH3': 2,
        'CH2': 14
    },
    'Octadecano': {
        'CH3': 2,
        'CH2': 16
    },
    'Eicosano': {
        'CH3': 2,
        'CH2': 18
    },
    'Água': {
        'H2O': 1
    },
    
    # =============================================================================
    # ADICIONAR AO UNIFAC_GROUPS (após linha ~950)
    # =============================================================================

    'Metanol': {
        'CH3OH': 1,  # Grupo especial metanol
        'OH': 1
    },
    'Etanol': {
        'CH3': 1,
        'CH2': 1,
        'OH': 1
    },
    '1-Propanol': {
        'CH3': 1,
        'CH2': 2,
        'OH': 1
    },
    'Ciclohexano': {
        'CH2': 6  # 6 grupos CH2 cíclicos
    },
    'cis-Decalina': {
        'CH2': 8,
        'CH': 2
    },
    'Acenafteno': {
        'ACH': 8,
        'AC': 2,
        'CH2': 2  # Ponte etênica
    },
    'o-Cloronitrobenzeno': {
        'ACH': 4,
        'AC': 2,
        'ACNO2': 1,  # Nitro aromático
        'ACCl': 1    # Cloro aromático
    },
    'p-Cloronitrobenzeno': {
        'ACH': 4,
        'AC': 2,
        'ACNO2': 1,
        'ACCl': 1
    },
    'Colesterol': {
        'CH3': 3,
        'CH2': 8,
        'CH': 7,
        'C': 4,  # Carbonos quaternários
        'OH': 1
    },

}

# Parâmetros R e Q dos grupos UNIFAC
UNIFAC_GROUP_R_Q = {
    'CH3': {'R': 0.9011, 'Q': 0.848},
    'CH2': {'R': 0.6744, 'Q': 0.540},
    'CH': {'R': 0.4469, 'Q': 0.228},
    'ACH': {'R': 0.5313, 'Q': 0.400},
    'AC': {'R': 0.3652, 'Q': 0.120},
    'ACCH3': {'R': 1.2663, 'Q': 0.968},
    'ACOH': {'R': 0.8952, 'Q': 0.680},
    'OH': {'R': 1.0000, 'Q': 1.200},
    'COOH': {'R': 1.3013, 'Q': 1.224},
    'H2O': {'R': 0.92, 'Q': 1.40},
    'CONH2': {'R': 1.4515, 'Q': 1.248},
}

# Parâmetros de interação entre grupos UNIFAC (a_mn em K)
# Fonte: Hansen et al. (1991) - Tabela completa
UNIFAC_GROUP_INTERACTIONS = {
    # Grupo 1 (alcanos) com outros
    ('CH3', 'ACH'): {'a12': 61.13, 'a21': -11.12},
    ('CH2', 'ACH'): {'a12': 61.13, 'a21': -11.12},
    ('CH3', 'ACOH'): {'a12': 275.8, 'a21': 25.34},
    ('CH2', 'ACOH'): {'a12': 275.8, 'a21': 25.34},
    ('CH3', 'H2O'): {'a12': 1318.0, 'a21': 300.0},
    ('CH2', 'H2O'): {'a12': 1318.0, 'a21': 300.0},
    ('CH3', 'COOH'): {'a12': 315.3, 'a21': 62.32},
    ('CH2', 'COOH'): {'a12': 315.3, 'a21': 62.32},
    
    # Aromáticos (ACH) com outros
    ('ACH', 'ACH'): {'a12': 0.0, 'a21': 0.0},
    ('ACH', 'ACOH'): {'a12': 1329.0, 'a21': 25.34},
    ('ACH', 'COOH'): {'a12': 537.4, 'a21': 62.32},
    ('ACH', 'H2O'): {'a12': 903.8, 'a21': 362.3},
    ('ACH', 'ACCH3'): {'a12': -146.8, 'a21': 167.0},
    
    # ACOH (fenol) com outros
    ('ACOH', 'ACOH'): {'a12': 0.0, 'a21': 0.0},
    ('ACOH', 'H2O'): {'a12': -601.8, 'a21': 324.5},
    ('ACOH', 'COOH'): {'a12': 408.9, 'a21': -11.0},
    
    # COOH com outros
    ('COOH', 'COOH'): {'a12': 0.0, 'a21': 0.0},
    ('COOH', 'H2O'): {'a12': -14.09, 'a21': -66.17},
    
    # H2O com outros
    ('H2O', 'H2O'): {'a12': 0.0, 'a21': 0.0},
    
    # AC (aromático fusionado) com outros
    ('AC', 'ACH'): {'a12': 0.0, 'a21': 0.0},
    ('AC', 'CH2'): {'a12': -11.12, 'a21': 61.13},
}

# =============================================================================
# FUNÇÕES DE ACESSO
# =============================================================================

def get_component_data(component_name):
    """
    Retorna dados termodinâmicos de um componente.
    
    Parameters:
        component_name (str): Nome do componente (português, inglês ou CAS)
        
    Returns:
        dict: Propriedades do componente ou None se não encontrado
    """
    name_normalized = component_name.lower().strip().replace(' ', '_').replace('-', '_')
    
    if name_normalized in ESL_DATA:
        return ESL_DATA[name_normalized].copy()
    
    for key, data in ESL_DATA.items():
        if data['name'].lower() == component_name.lower():
            return data.copy()
        if data['name_en'].lower() == component_name.lower():
            return data.copy()
    
    for key, data in ESL_DATA.items():
        if 'CAS' in data and data['CAS'] == component_name:
            return data.copy()
    
    return None


def get_nrtl_parameters(component1, component2):
    """
    Retorna parâmetros NRTL para um par binário.
    
    Parameters:
        component1 (str): Nome do primeiro componente
        component2 (str): Nome do segundo componente
        
    Returns:
        dict: Parâmetros NRTL ou None se não disponível
    """
    pair = (component1, component2)
    reverse_pair = (component2, component1)
    
    if pair in NRTL_PARAMETERS:
        return NRTL_PARAMETERS[pair].copy()
    elif reverse_pair in NRTL_PARAMETERS:
        params = NRTL_PARAMETERS[reverse_pair].copy()
        # Inverter parâmetros
        params['tau12'], params['tau21'] = params['tau21'], params['tau12']
        params['a12'], params['a21'] = params['a21'], params['a12']
        params['b12'], params['b21'] = params['b21'], params['b12']
        return params
    else:
        return None


def get_uniquac_parameters(component1, component2):
    """
    Retorna parâmetros UNIQUAC para um par binário.
    
    Parameters:
        component1 (str): Nome do primeiro componente
        component2 (str): Nome do segundo componente
        
    Returns:
        dict: Parâmetros UNIQUAC ou None se não disponível
    """
    pair = (component1, component2)
    reverse_pair = (component2, component1)
    
    if pair in UNIQUAC_PARAMETERS:
        return UNIQUAC_PARAMETERS[pair].copy()
    elif reverse_pair in UNIQUAC_PARAMETERS:
        params = UNIQUAC_PARAMETERS[reverse_pair].copy()
        params['u12'], params['u21'] = params['u21'], params['u12']
        return params
    else:
        return None


def get_uniquac_properties(component):
    """
    Retorna propriedades estruturais UNIQUAC (r, q) de um componente.
    
    Parameters:
        component (str): Nome do componente
        
    Returns:
        dict: {'r': float, 'q': float} ou None se não disponível
    """
    return UNIQUAC_PURE_PROPERTIES.get(component, None)


def get_unifac_groups(component):
    """
    Retorna composição de grupos funcionais UNIFAC de um componente.
    
    Parameters:
        component (str): Nome do componente
        
    Returns:
        dict: Dicionário {grupo: quantidade} ou None
    """
    return UNIFAC_GROUPS.get(component, None)


def list_available_components():
    """Lista todos os componentes disponíveis na base de dados (PT-BR)."""
    components = []
    for key, data in ESL_DATA.items():
        components.append({
            'key': key,
            'name': data['name'],
            'name_en': data['name_en'],
            'formula': data['formula'],
            'CAS': data.get('CAS', 'N/A'),
            'Tm_C': round(data['Tm'] - 273.15, 2),
            'Hfus_kJ_mol': round(data['Hfus'] / 1000, 2),
            'applications': data.get('applications', '')
        })
    
    return sorted(components, key=lambda x: x['name'])


def get_eutectic_systems():
    """Retorna sistemas eutéticos conhecidos documentados na literatura."""
    eutectic_systems = [
        {
            'system': 'Naftaleno + Benzeno',
            'components': ['Naftaleno', 'Benzeno'],
            'x_eutectic': 0.45,
            'T_eutectic_C': -5.0,
            'T_eutectic': 268.15,
            'source': 'Prausnitz Fig. 11-5',
            'notes': 'Sistema ideal simples, usado para validação de modelos'
        },
        {
            'system': 'Ácido Benzoico + Ácido Salicílico',
            'components': ['Ácido Benzoico', 'Ácido Salicílico'],
            'x_eutectic': 0.60,
            'T_eutectic_C': 112.69,
            'T_eutectic': 385.84,
            'source': 'Mohajerani et al., CrystEngComm (2023)',
            'notes': 'Forma soluções sólidas, eutectic bem definido'
        },
        {
            'system': 'Ureia + Biureto',
            'components': ['Ureia', 'Biureto'],
            'x_eutectic': 0.75,
            'T_eutectic_C': 106.0,
            'T_eutectic': 379.1,
            'source': 'Voskov et al. (2012)',
            'notes': 'Sistema com decomposição, eutectic metaestável'
        },
        {
            'system': 'Fenol + Água',
            'components': ['Fenol', 'Água'],
            'x_eutectic': 0.36,
            'T_eutectic_C': 0.0,
            'T_eutectic': 273.15,
            'source': 'Literatura clássica',
            'notes': 'Sistema aquoso, imiscibilidade parcial'
        }
    ]
    
    return eutectic_systems


def validate_component_data(component_name):
    """
    Valida dados termodinâmicos de um componente.
    
    Parameters:
        component_name (str): Nome do componente
        
    Returns:
        dict: {'valid': bool, 'warnings': [], 'errors': []}
    """
    data = get_component_data(component_name)
    
    if data is None:
        return {
            'valid': False,
            'warnings': [],
            'errors': [f'Componente "{component_name}" não encontrado']
        }
    
    warnings = []
    errors = []
    
    # Verificar dados essenciais
    if data.get('Tm') is None or data['Tm'] <= 0:
        errors.append('Temperatura de fusão (Tm) inválida ou ausente')
    
    if data.get('Hfus') is None or data['Hfus'] <= 0:
        errors.append('Entalpia de fusão (Hfus) inválida ou ausente')
    
    # Verificar consistência termodinâmica
    if data.get('Sfus') and data.get('Tm') and data.get('Hfus'):
        Sfus_calc = data['Hfus'] / data['Tm']
        Sfus_given = data['Sfus']
        
        if abs(Sfus_calc - Sfus_given) > 5.0:  # Tolerância de 5 J/(mol·K)
            warnings.append(
                f'Inconsistência termodinâmica: ΔSfus = {Sfus_given:.2f}, '
                f'mas ΔHfus/Tm = {Sfus_calc:.2f} J/(mol·K)'
            )
    
    # Verificar incertezas
    if 'uncertainty' in data:
        unc = data['uncertainty']
        if unc.get('Tm', 0) > 5.0:
            warnings.append(f'Alta incerteza em Tm: ±{unc["Tm"]} K')
        if unc.get('Hfus', 0) > 1000.0:
            warnings.append(f'Alta incerteza em ΔHfus: ±{unc["Hfus"]} J/mol')
    
    return {
        'valid': len(errors) == 0,
        'warnings': warnings,
        'errors': errors
    }


def print_component_summary(component_name):
    """Imprime resumo formatado das propriedades de um componente."""
    data = get_component_data(component_name)
    
    if data is None:
        print(f"Componente '{component_name}' não encontrado na base de dados.")
        return
    
    print("=" * 80)
    print(f"  {data['name']} / {data['name_en']} ({data['formula']})")
    print("=" * 80)
    print(f"CAS Registry Number: {data.get('CAS', 'N/A')}")
    print(f"Peso Molecular: {data.get('MW', 'N/A')} g/mol")
    print()
    print("Propriedades de Fusão:")
    print(f"  Temperatura de Fusão (Tm):     {data['Tm']:.2f} K ({data['Tm']-273.15:.2f} °C)")
    print(f"  Entalpia de Fusão (ΔHfus):     {data['Hfus']:.0f} J/mol ({data['Hfus']/1000:.2f} kJ/mol)")
    print(f"  Entropia de Fusão (ΔSfus):     {data.get('Sfus', 'N/A')} J/(mol·K)")
    print()
    
    # Verificar parâmetros disponíveis
    print("Modelos termodinâmicos disponíveis:")
    print("  ✓ Ideal (sempre disponível)")
    
    # Verificar UNIQUAC
    if data['name'] in UNIQUAC_PURE_PROPERTIES:
        props = UNIQUAC_PURE_PROPERTIES[data['name']]
        print(f"  ✓ UNIQUAC: r={props['r']:.4f}, q={props['q']:.4f}")
    
    # Verificar UNIFAC
    if data['name'] in UNIFAC_GROUPS:
        groups = UNIFAC_GROUPS[data['name']]
        print(f"  ✓ UNIFAC: {groups}")
    
    print()
    print(f"Fonte: {data.get('source', 'N/A')}")
    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("  ESL DATA - Base de Dados para Equilíbrio Sólido-Líquido (PT-BR)")
    print("  Versão 2.1 - Com parâmetros NRTL, UNIQUAC e UNIFAC")
    print("="*80 + "\n")
    
    print(f"📊 Total de componentes disponíveis: {len(ESL_DATA)}")
    print(f"🔗 Pares NRTL disponíveis: {len(NRTL_PARAMETERS)}")
    print(f"🔗 Pares UNIQUAC disponíveis: {len(UNIQUAC_PARAMETERS)}")
    print(f"🧩 Componentes com grupos UNIFAC: {len(UNIFAC_GROUPS)}\n")
    
    print("Exemplo: Naftaleno")
    print("-" * 80)
    print_component_summary('Naftaleno')
    
    print("\nExemplo: Parâmetros NRTL para Naftaleno + Benzeno")
    print("-" * 80)
    params = get_nrtl_parameters('Naftaleno', 'Benzeno')
    if params:
        print(f"τ₁₂ = {params['tau12']}, τ₂₁ = {params['tau21']}, α = {params['alpha']}")
        print(f"Fonte: {params['source']}")
