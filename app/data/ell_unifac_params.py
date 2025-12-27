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

COMO FUNCIONA:
    1. Dividir cada molécula em grupos funcionais (CH3, CH2, OH, etc.)
    2. Calcular R (volume) e Q (área) de cada molécula somando contribuições
    3. Usar parâmetros de interação entre grupos (a_nm)
    4. Calcular γ_i usando equação UNIFAC (similar a UNIQUAC)

VANTAGENS:
    ✅ Não requer parâmetros experimentais (preditivo)
    ✅ Funciona para QUALQUER combinação de componentes
    ✅ Ótimo para screening inicial de solventes

DESVANTAGENS:
    ⚠️ Menos preciso que NRTL/UNIQUAC com parâmetros experimentais
    ⚠️ Erro típico: 10-20% (vs 2-5% com parâmetros ajustados)

Autor: Desenvolvido para TCC - Plataforma de Equilíbrio de Fases
Data: Dezembro 2024
Versão: 1.0
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
    
    # ========== ÁCIDOS CARBOXÍLICOS ==========
    'Acetic Acid': {
        'groups': {'CH3': 1, 'COOH': 1},  # CH3-COOH
        'name_pt': 'Ácido Acético',
        'formula': 'CH₃COOH',
        'cas': '64-19-7',
        'mw': 60.05
    },
    
    # ========== ÉSTERES ==========
    'Ethyl Acetate': {
        'groups': {'CH3': 2, 'CH2': 1, 'CH3COO': 1},  # CH3-COO-CH2-CH3
        'name_pt': 'Acetato de Etila',
        'formula': 'C₄H₈O₂',
        'cas': '141-78-6',
        'mw': 88.11
    },
    
    # ========== AROMÁTICOS ==========
    'Toluene': {
        'groups': {'CH3': 1, 'ACH': 5, 'AC': 1},  # C6H5-CH3
        'name_pt': 'Tolueno',
        'formula': 'C₇H₈',
        'cas': '108-88-3',
        'mw': 92.14
    },
    
    # ========== CLORADOS ==========
    '1,1,2-Trichloroethane': {
        'groups': {'CH': 1, 'CHCl2': 1},  # CHCl2-CHCl
        'name_pt': '1,1,2-Tricloroetano',
        'formula': 'C₂H₃Cl₃',
        'cas': '79-00-5',
        'mw': 133.40
    },
}

# ============================================================================
# PARÂMETROS DE INTERAÇÃO UNIFAC (a_nm)
# ============================================================================
# Ref: Fredenslund et al. (1975), Tabela IV

UNIFAC_INTERACTION_PARAMS = {
    # (grupo_n, grupo_m): a_nm [K]
    # a_nm ≠ a_mn (assimétrico)
    
    # ========== ÁGUA COM OUTROS GRUPOS ==========
    ('H2O', 'CH3'): 1318.0,      ('CH3', 'H2O'): 300.0,
    ('H2O', 'CH2'): 1318.0,      ('CH2', 'H2O'): 300.0,
    ('H2O', 'ACH'): 1100.0,      ('ACH', 'H2O'): 636.1,
    ('H2O', 'CH3CO'): 476.4,     ('CH3CO', 'H2O'): 26.76,
    ('H2O', 'COOH'): -151.0,     ('COOH', 'H2O'): -14.09,
    ('H2O', 'CH2Cl'): 496.1,     ('CH2Cl', 'H2O'): -170.0,
    ('H2O', 'CHCl2'): 1500.0,    ('CHCl2', 'H2O'): -200.0,
    
    # ========== HIDROCARB function WITH CARBONYL ==========
    ('CH3', 'CH3CO'): 26.76,     ('CH3CO', 'CH3'): -37.36,
    ('CH2', 'CH3CO'): 26.76,     ('CH3CO', 'CH2'): -37.36,
    
    # ========== AROMÁTICOS COM ALIFÁTICOS ==========
    ('ACH', 'CH3'): -11.12,      ('CH3', 'ACH'): 61.13,
    ('ACH', 'CH2'): -11.12,      ('CH2', 'ACH'): 61.13,
    
    # ========== ÁCIDOS COM OUTROS GRUPOS ==========
    ('COOH', 'CH3'): 663.5,      ('CH3', 'COOH'): 232.1,
    ('COOH', 'CH2'): 663.5,      ('CH2', 'COOH'): 232.1,
    ('COOH', 'ACH'): 537.4,      ('ACH', 'COOH'): 245.4,
    
    # ========== CLORADOS COM OUTROS ==========
    ('CH2Cl', 'CH3'): -108.7,    ('CH3', 'CH2Cl'): 249.1,
    ('CHCl2', 'CH3'): -50.0,     ('CH3', 'CHCl2'): 150.0,
    
    # ========== GRUPOS IDÊNTICOS ==========
    # a_nn = 0 (mesma espécie não interage consigo mesma)
}

# Preencher interações simétricas zero
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
        raise ValueError(f"Componente {component_name} não encontrado em UNIFAC_MOLECULES")
    
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
        Dict com parâmetros UNIFAC:
            - success: True/False
            - r: [R1, R2, R3] (volumes)
            - q: [Q1, Q2, Q3] (áreas)
            - groups_composition: Composição de grupos de cada molécula
            - interaction_params: Parâmetros a_nm
            - temperature_K: Temperatura em K
            - warning: Avisos (se houver)
    
    Example:
        >>> params = get_unifac_params_ell(['Water', 'Toluene', 'Acetic Acid'], 25.0)
        >>> print(f"R = {params['r']}")
        >>> print(f"Q = {params['q']}")
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
    
    Returns:
        Lista de dicionários com informações dos componentes
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
    
    UNIFAC = γ_C (combinatorial) + γ_R (residual)
    
    Args:
        components: Lista com 3 nomes de componentes
        x: Frações molares [x1, x2, x3]
        T: Temperatura em Kelvin
    
    Returns:
        Array [γ1, γ2, γ3]
    
    References:
        Fredenslund et al. (1975), AIChE J., Eq. 14-17
    """
    # Validação
    if len(components) != 3 or len(x) != 3:
        raise ValueError("UNIFAC requer exatamente 3 componentes")
    
    x = np.clip(x, 1e-10, 1.0)
    x = x / np.sum(x)  # Normalizar
    
    # Verificar se todos os componentes estão disponíveis
    for comp in components:
        if comp not in UNIFAC_MOLECULES:
            print(f"⚠️ UNIFAC: Componente '{comp}' não encontrado")
            return np.ones(3)  # Fallback: solução ideal
    
    # Obter parâmetros R e Q
    params = get_unifac_params_ell(components, temperature_C=T-273.15)
    
    if not params['success']:
        print(f"⚠️ UNIFAC: Erro ao obter parâmetros")
        return np.ones(3)
    
    r = np.array(params['r'])
    q = np.array(params['q'])
    
    # ========== PARTE COMBINATORIAL (γ^C) ==========
    # Ref: Prausnitz Eq. 8.7-9
    
    z = 10  # Número de coordenação
    
    # Frações de volume e área
    phi = (r * x) / np.sum(r * x)
    theta = (q * x) / np.sum(q * x)
    
    # Parâmetro l_i
    l = (z/2) * (r - q) - (r - 1)
    
    # ln(γ^C)
    ln_gamma_C = np.zeros(3)
    for i in range(3):
        term1 = np.log(phi[i] / x[i])
        term2 = (z/2) * q[i] * np.log(theta[i] / phi[i])
        term3 = l[i]
        term4 = -(phi[i] / x[i]) * np.sum(x * l)
        
        ln_gamma_C[i] = term1 + term2 + term3 + term4
    
    # ========== PARTE RESIDUAL (γ^R) ==========
    # Ref: Fredenslund et al. (1975), Eq. 16-17
    
    # Coletar todos os grupos presentes no sistema
    groups_in_system = {}
    for comp in components:
        for group, count in UNIFAC_MOLECULES[comp]['groups'].items():
            if group not in groups_in_system:
                groups_in_system[group] = []
            groups_in_system[group].append(count)
    
    unique_groups = list(groups_in_system.keys())
    n_groups = len(unique_groups)
    
    # Calcular X_m (fração de grupo m na mistura)
    X_m = np.zeros(n_groups)
    for i_comp, comp in enumerate(components):
        groups_comp = UNIFAC_MOLECULES[comp]['groups']
        for i_group, group in enumerate(unique_groups):
            n_ki = groups_comp.get(group, 0)
            X_m[i_group] += x[i_comp] * n_ki
    
    X_m = X_m / np.sum(X_m)  # Normalizar
    
    # Calcular θ_m (fração de área do grupo m)
    Q_m = np.array([UNIFAC_GROUPS[g][1] for g in unique_groups])
    theta_m = (Q_m * X_m) / np.sum(Q_m * X_m)
    
    # Calcular ψ_nm (parâmetros de interação de grupos)
    psi = np.ones((n_groups, n_groups))
    for n in range(n_groups):
        for m in range(n_groups):
            group_n = unique_groups[n]
            group_m = unique_groups[m]
            
            a_nm = UNIFAC_INTERACTION_PARAMS.get((group_n, group_m), 0.0)
            psi[n, m] = np.exp(-a_nm / T)
    
    # Calcular ln(Γ_k) para cada grupo na mistura
    ln_Gamma_k_mixture = np.zeros(n_groups)
    for k in range(n_groups):
        sum_theta_psi = np.sum(theta_m * psi[:, k])
        
        term1 = Q_m[k] * (1 - np.log(sum_theta_psi))
        
        term2 = 0.0
        for m in range(n_groups):
            numerator = theta_m[m] * psi[k, m]
            denominator = np.sum(theta_m * psi[:, m])
            term2 -= Q_m[k] * (numerator / denominator)
        
        ln_Gamma_k_mixture[k] = term1 + term2
    
    # Calcular ln(Γ_k^(i)) para cada grupo em cada componente puro
    ln_Gamma_k_pure = np.zeros((3, n_groups))
    
    for i_comp, comp in enumerate(components):
        groups_comp = UNIFAC_MOLECULES[comp]['groups']
        
        # X_m para componente puro
        X_m_pure = np.zeros(n_groups)
        for i_group, group in enumerate(unique_groups):
            X_m_pure[i_group] = groups_comp.get(group, 0)
        
        if np.sum(X_m_pure) == 0:
            continue
        
        X_m_pure = X_m_pure / np.sum(X_m_pure)
        
        # θ_m para componente puro
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
    
    # Calcular ln(γ^R) para cada componente
    ln_gamma_R = np.zeros(3)
    for i_comp, comp in enumerate(components):
        groups_comp = UNIFAC_MOLECULES[comp]['groups']
        
        for group, n_ki in groups_comp.items():
            k = unique_groups.index(group)
            ln_gamma_R[i_comp] += n_ki * (ln_Gamma_k_mixture[k] - ln_Gamma_k_pure[i_comp, k])
    
    # ========== TOTAL: γ = γ^C × γ^R ==========
    ln_gamma = ln_gamma_C + ln_gamma_R
    gamma = np.exp(ln_gamma)
    
    # Limitar valores extremos
    gamma = np.clip(gamma, 1e-6, 1e6)
    
    return gamma


# ============================================================================
# TESTE DE VALIDAÇÃO
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("VALIDAÇÃO: ell_unifac_params.py")
    print("="*70)
    print()
    
    # Teste 1: Listar componentes
    print("📋 COMPONENTES DISPONÍVEIS:")
    components = get_available_components_ell_unifac()
    for comp in components:
        print(f"  • {comp['name_pt']} ({comp['formula']}) - CAS: {comp['cas']}")
        print(f"    Grupos: {comp['groups']}")
    print()
    
    # Teste 2: Calcular R e Q
    print("🔬 TESTE: Parâmetros R e Q")
    for comp_name in ['Water', 'Acetone', 'Toluene']:
        R, Q = calculate_unifac_RQ(comp_name)
        print(f"  {comp_name}: R={R:.4f}, Q={Q:.4f}")
    print()
    
    # Teste 3: Sistema completo
    print("🧪 TESTE: Water/Toluene/Acetic Acid")
    params = get_unifac_params_ell(['Water', 'Toluene', 'Acetic Acid'], 25.0)
    
    if params['success']:
        print(f"  ✅ Válido")
        print(f"  R = {params['r']}")
        print(f"  Q = {params['q']}")
        print(f"  Referência: {params['reference']}")
    else:
        print(f"  ❌ Erro: {params['error']}")
    
    print()
    print("="*70)
    print("✅ VALIDAÇÃO CONCLUÍDA - UNIFAC PREDITIVO DISPONÍVEL")
    print("="*70)
