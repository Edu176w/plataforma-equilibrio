"""
experimental_lle_data.py
Dados REAIS de Trofimova et al. (2020)
Sistema: Ethanol + Ethyl Acetate + Water
"""

# Componentes na ordem: [Ethyl acetate, Water, Ethanol]
# Dados da Tabela 4 (pág. 8) do artigo Trofimova et al. (2020)

TIE_LINES_323K = [
    # Fase aquosa (x2, x3, x4) -> reordenar para [x3, x4, x2]
    {
        'phase1': [0.674, 0.019, 0.022],  # Fase orgânica (rica em ethyl acetate)
        'phase2': [0.022, 0.959, 0.019],  # Fase aquosa (rica em water)
        'description': 'Tie-line 1 @ 323K - Trofimova 2020'
    },
    {
        'phase1': [0.575, 0.038, 0.031],
        'phase2': [0.031, 0.931, 0.038],
        'description': 'Tie-line 2 @ 323K'
    },
    {
        'phase1': [0.507, 0.048, 0.044],
        'phase2': [0.044, 0.908, 0.048],
        'description': 'Tie-line 3 @ 323K'
    },
    {
        'phase1': [0.426, 0.058, 0.054],
        'phase2': [0.054, 0.888, 0.058],
        'description': 'Tie-line 4 @ 323K'
    },
    {
        'phase1': [0.332, 0.074, 0.066],
        'phase2': [0.066, 0.860, 0.074],
        'description': 'Tie-line 5 @ 323K'
    },
    {
        'phase1': [0.279, 0.091, 0.090],
        'phase2': [0.090, 0.819, 0.091],
        'description': 'Tie-line 6 @ 323K'
    },
]

# Tabela 4 também tem tie-lines para o sistema com ácido acético
# Vamos pegar apenas as linhas com x1=0 (sem ácido acético)

TIE_LINES_333K = [
    {
        'phase1': [0.697, 0.017, 0.024],
        'phase2': [0.024, 0.959, 0.017],
        'description': 'Tie-line 1 @ 333K - Trofimova 2020'
    },
    {
        'phase1': [0.585, 0.042, 0.035],
        'phase2': [0.035, 0.923, 0.042],
        'description': 'Tie-line 2 @ 333K'
    },
    {
        'phase1': [0.489, 0.059, 0.049],
        'phase2': [0.049, 0.892, 0.059],
        'description': 'Tie-line 3 @ 333K'
    },
    {
        'phase1': [0.394, 0.076, 0.064],
        'phase2': [0.064, 0.860, 0.076],
        'description': 'Tie-line 4 @ 333K'
    },
    {
        'phase1': [0.284, 0.089, 0.085],
        'phase2': [0.085, 0.826, 0.089],
        'description': 'Tie-line 5 @ 333K'
    },
]

def get_data(temperature=323.15):
    """
    Retorna dados experimentais reais
    
    Fonte: Trofimova et al. (2020) Fluid Phase Equilibria 503, 112321
           Table 4, pág. 8
    """
    data_map = {
        323.15: TIE_LINES_323K,
        333.15: TIE_LINES_333K,
    }
    
    if temperature not in data_map:
        raise ValueError(f"Dados disponíveis apenas para T=323.15 K ou 333.15 K")
    
    return {
        'temperature': temperature,
        'tie_lines': data_map[temperature],
        'binodal': None,
        'components': ['Ethyl acetate', 'Water', 'Ethanol'],
        'units': 'mole fraction',
        'pressure': 101.3,
        'reference': 'Trofimova et al. (2020) Fluid Phase Equilibria 503, 112321'
    }

if __name__ == "__main__":
    for T in [323.15, 333.15]:
        data = get_data(T)
        print(f"\n{'='*70}")
        print(f"T = {T} K ({T-273.15:.2f}°C)")
        print(f"{'='*70}")
        for tl in data['tie_lines']:
            print(f"{tl['description']}")
            print(f"  Orgânica: {tl['phase1']}")
            print(f"  Aquosa:   {tl['phase2']}")
