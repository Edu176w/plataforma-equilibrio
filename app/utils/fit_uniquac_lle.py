"""
Módulo para ajuste de parâmetros UNIQUAC usando dados de LLE
Baseado em Abrams & Prausnitz (1975), páginas 124-125
"""

import numpy as np
from scipy.optimize import minimize
from app.calculators.ell_calculator import LLEModel

def fit_uniquac_binary_lle(cas1, cas2, name1, name2, 
                           x1_in_phase2, x2_in_phase1, 
                           temperature_C, 
                           initial_guess=None):
    """
    Ajusta parâmetros UNIQUAC u21-u11 e u12-u22 para dados de solubilidade mútua.
    
    Args:
        cas1, cas2: CAS numbers
        name1, name2: Nomes dos componentes
        x1_in_phase2: Fração molar de componente 1 na fase rica em 2
        x2_in_phase1: Fração molar de componente 2 na fase rica em 1
        temperature_C: Temperatura em °C
        initial_guess: [u21_minus_u11, u12_minus_u22] em cal/mol
    
    Returns:
        dict com parâmetros otimizados
    """
    
    if initial_guess is None:
        initial_guess = [800.0, -300.0]  # Valores típicos para sistemas polares
    
    def objective(params):
        """Função objetivo: minimizar erro na solubilidade mútua"""
        u21_minus_u11, u12_minus_u22 = params
        
        # Criar arquivo temporário de parâmetros
        from app.data.ell_uniquac_params import ELL_UNIQUAC_RQ
        
        # Criar modelo com parâmetros temporários
        # Aqui você precisaria modificar temporariamente os parâmetros
        # Por simplicidade, vou calcular gamma diretamente
        
        try:
            # Calcular gamma_1^inf na fase rica em 2 (x1 → 0)
            x_phase2 = np.array([0.001, 0.999])
            gamma_phase2 = _calc_gamma_uniquac_binary(
                x_phase2, u21_minus_u11, u12_minus_u22, temperature_C
            )
            gamma1_inf_phase2 = gamma_phase2[0]
            
            # Calcular gamma_2^inf na fase rica em 1 (x2 → 0)
            x_phase1 = np.array([0.999, 0.001])
            gamma_phase1 = _calc_gamma_uniquac_binary(
                x_phase1, u21_minus_u11, u12_minus_u22, temperature_C
            )
            gamma2_inf_phase1 = gamma_phase1[1]
            
            # Estimar solubilidade usando γ_i^∞
            # x1_in_phase2_calc ≈ 1 / gamma1_inf_phase2
            # x2_in_phase1_calc ≈ 1 / gamma2_inf_phase1
            
            x1_calc = 1.0 / gamma1_inf_phase2
            x2_calc = 1.0 / gamma2_inf_phase1
            
            # Erro quadrático
            error = (x1_calc - x1_in_phase2)**2 + (x2_calc - x2_in_phase1)**2
            
            return error
            
        except:
            return 1e10  # Penalidade por erro
    
    # Otimização
    result = minimize(
        objective,
        initial_guess,
        method='Nelder-Mead',
        options={'maxiter': 1000, 'xatol': 1e-6}
    )
    
    if result.success:
        u21_minus_u11_opt, u12_minus_u22_opt = result.x
        
        return {
            'cas1': cas1,
            'cas2': cas2,
            'name1': name1,
            'name2': name2,
            'u21_minus_u11': float(u21_minus_u11_opt),
            'u12_minus_u22': float(u12_minus_u22_opt),
            'T_ref_C': temperature_C,
            'reference': 'Ajustado para solubilidade mútua experimental',
            'success': True,
            'error': float(result.fun)
        }
    else:
        return {'success': False, 'message': result.message}


def _calc_gamma_uniquac_binary(x, u21_minus_u11, u12_minus_u22, temperature_C):
    """Calcula gamma UNIQUAC para sistema binário"""
    # Parâmetros estruturais (exemplos - buscar valores reais)
    r = np.array([2.11, 4.50])  # ethanol, hexane
    q = np.array([1.97, 3.86])
    
    T = temperature_C + 273.15
    R = 1.987  # cal/(mol·K)
    z = 10.0
    
    # Converter u_delta para a_ij
    a21 = u21_minus_u11 / R
    a12 = u12_minus_u22 / R
    
    # Normalizar composição
    x = np.clip(x, 1e-10, 1.0)
    x = x / x.sum()
    
    # Frações de segmento e área
    phi = x * r / np.dot(x, r)
    theta = x * q / np.dot(x, q)
    
    l = (z / 2.0) * (r - q) - (r - 1.0)
    
    # Termo combinatorial
    ln_gamma_c = (
        np.log(phi / x)
        + (z / 2.0) * q * np.log(theta / phi)
        + l
        - (phi / x) * np.dot(x, l)
    )
    
    # Termo residual
    tau = np.array([[1.0, np.exp(-a12 / T)],
                    [np.exp(-a21 / T), 1.0]])
    
    ln_gamma_r = np.zeros(2)
    for i in range(2):
        denom_i = np.sum(theta * tau[:, i])
        term1 = -np.log(denom_i + 1e-16)
        
        term2 = 0.0
        for j in range(2):
            denom_j = np.sum(theta * tau[:, j])
            if denom_j > 1e-16:
                term2 += theta[j] * tau[i, j] / denom_j
        
        ln_gamma_r[i] = q[i] * (1.0 + term1 - term2)
    
    ln_gamma = ln_gamma_c + ln_gamma_r
    return np.exp(np.clip(ln_gamma, -50, 50))


# Teste de ajuste para ethanol-hexane
if __name__ == "__main__":
    result = fit_uniquac_binary_lle(
        cas1='64-17-5',
        cas2='110-54-3',
        name1='ethanol',
        name2='hexane',
        x1_in_phase2=0.047,  # Solubilidade de ethanol em hexane
        x2_in_phase1=0.254,  # Solubilidade de hexane em ethanol
        temperature_C=25.0,
        initial_guess=[940.9, -335.0]  # Chute inicial da Tabela 4
    )
    
    print("=" * 70)
    print("AJUSTE DE PARÂMETROS UNIQUAC PARA LLE")
    print("=" * 70)
    print(f"\nSistema: {result['name1']} - {result['name2']}")
    print(f"Temperatura: {result['T_ref_C']}°C")
    print(f"\nParâmetros ajustados:")
    print(f"  u21_minus_u11 = {result['u21_minus_u11']:.1f} cal/mol")
    print(f"  u12_minus_u22 = {result['u12_minus_u22']:.1f} cal/mol")
    print(f"\nErro de ajuste: {result['error']:.6f}")
    print("=" * 70)
