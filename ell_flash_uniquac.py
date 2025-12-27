# ell_flash_uniquac.py (VERSÃO CORRIGIDA)
"""
Flash LLE (Liquid-Liquid Equilibrium) usando UNIQUAC
Implementação correta baseada em Abrams & Prausnitz (1975), Eq. 25
"""

import numpy as np
from scipy.optimize import fsolve, brentq
from typing import Dict, List, Tuple, Optional


class UNIQUACModel:
    """Modelo UNIQUAC para cálculo de coeficientes de atividade
    Baseado nas Equações 25, 27, 28 de Abrams & Prausnitz (1975)
    """
    
    def __init__(self, r: List[float], q: List[float], u_params: Dict):
        """
        Args:
            r: lista de parâmetros r [r1, r2, r3]
            q: lista de parâmetros q [q1, q2, q3]
            u_params: dict com (i,j): {'u_delta': u_ji - u_ii em cal/mol}
        """
        self.r = np.array(r)
        self.q = np.array(q)
        self.n_comp = len(r)
        self.z = 10.0  # coordenação (artigo usa z=10)
        
        # Montar matriz de parâmetros u_delta
        self.u_matrix = np.zeros((self.n_comp, self.n_comp))
        
        for (i, j), params in u_params.items():
            self.u_matrix[j, i] = params['u_delta']  # u_ji - u_ii
    
    def calc_tau(self, T: float) -> np.ndarray:
        """
        Calcula matriz tau_ji = exp(-(u_ji - u_ii)/RT)
        Equação do artigo: tau = exp(-u_delta/RT)
        """
        R = 1.987  # cal/mol·K
        tau = np.exp(-self.u_matrix / (R * T))
        np.fill_diagonal(tau, 1.0)
        return tau
    
    def activity_coefficients(self, x: np.ndarray, T: float) -> np.ndarray:
        """
        Calcula ln(gamma_i) usando Equação 25 de Abrams & Prausnitz (1975)
        
        ln(gamma_i) = ln(gamma_i^comb) + ln(gamma_i^res)
        
        Args:
            x: frações molares [x1, x2, ...]
            T: temperatura em K
            
        Returns:
            array de gammas [gamma1, gamma2, ...]
        """
        x = np.array(x, dtype=float)
        x = x / x.sum()  # normalizar
        x = np.clip(x, 1e-12, 1.0)  # evitar divisão por zero
        
        # Frações de segmento phi (Eq. 28)
        phi = (self.r * x) / np.sum(self.r * x)
        
        # Frações de área theta (Eq. 27)
        theta = (self.q * x) / np.sum(self.q * x)
        
        # Parâmetro l (Eq. 26)
        l = self.z/2 * (self.r - self.q) - (self.r - 1)
        
        # Matriz tau
        tau = self.calc_tau(T)
        
        # Parte combinatorial (Eq. 25, primeira parte)
        ln_gamma_comb = np.log(phi / x) + self.z/2 * self.q * np.log(theta / phi) + l - (phi / x) * np.sum(x * l)
        
        # Parte residual (Eq. 25, segunda parte)
        ln_gamma_res = np.zeros(self.n_comp)
        
        for i in range(self.n_comp):
            # Soma: sum_j(theta_j * tau_ji)
            sum_theta_tau = np.sum(theta * tau[:, i])
            
            # Termo duplo: sum_j [ theta_j * tau_ij / sum_k(theta_k * tau_kj) ]
            sum_double = 0.0
            for j in range(self.n_comp):
                sum_k_theta_tau = np.sum(theta * tau[:, j])
                sum_double += (theta[j] * tau[i, j]) / sum_k_theta_tau
            
            ln_gamma_res[i] = self.q[i] * (1 - np.log(sum_theta_tau) - sum_double)
        
        ln_gamma = ln_gamma_comb + ln_gamma_res
        gamma = np.exp(ln_gamma)
        
        return gamma


class ELLFlash:
    """Flash LLE para sistemas ternários"""
    
    def __init__(self, model: UNIQUACModel):
        self.model = model
    
    def rachford_rice(self, z: np.ndarray, K: np.ndarray, beta: float) -> float:
        """Equação de Rachford-Rice para flash bifásico"""
        return np.sum(z * (K - 1) / (1 + beta * (K - 1)))
    
    def flash_lle(self, z: np.ndarray, T: float, 
                  initial_guess: Optional[Tuple[np.ndarray, np.ndarray]] = None,
                  max_iter: int = 100, tol: float = 1e-6) -> Dict:
        """
        Resolve flash LLE para composição global z a temperatura T
        Equilíbrio: x_i^I * gamma_i^I = x_i^II * gamma_i^II
        """
        z = np.array(z, dtype=float)
        z = z / z.sum()
        
        # Chute inicial
        if initial_guess is None:
            x1 = z * np.array([1.3, 0.7, 1.0])
            x1 = x1 / x1.sum()
            x2 = z * np.array([0.7, 1.3, 1.0])
            x2 = x2 / x2.sum()
        else:
            x1, x2 = initial_guess
        
        # Iteração sucessiva
        for iteration in range(max_iter):
            # Calcular gammas
            gamma1 = self.model.activity_coefficients(x1, T)
            gamma2 = self.model.activity_coefficients(x2, T)
            
            # Razão de equilíbrio K_i = (x_i * gamma_i)^I / (x_i * gamma_i)^II
            # Simplificando: K_i = gamma_i^I / gamma_i^II
            K = gamma1 / gamma2
            
            # Resolver Rachford-Rice para beta
            try:
                beta = brentq(lambda b: self.rachford_rice(z, K, b), 1e-10, 1.0 - 1e-10)
            except:
                # Não converge = sistema estável (uma fase)
                return {
                    'converged': False,
                    'stable': True,
                    'x_phase1': z,
                    'x_phase2': z,
                    'beta': 0.0
                }
            
            # Calcular novas composições
            x1_new = z / (1 + beta * (K - 1))
            x2_new = K * x1_new
            
            # Normalizar
            x1_new = x1_new / x1_new.sum()
            x2_new = x2_new / x2_new.sum()
            
            # Verificar convergência
            err1 = np.linalg.norm(x1_new - x1)
            err2 = np.linalg.norm(x2_new - x2)
            
            if err1 < tol and err2 < tol:
                # Verificar se são realmente duas fases distintas
                diff = np.linalg.norm(x1_new - x2_new)
                if diff < 0.05:  # threshold
                    return {
                        'converged': True,
                        'stable': True,
                        'x_phase1': z,
                        'x_phase2': z,
                        'beta': 0.0
                    }
                
                return {
                    'converged': True,
                    'stable': False,
                    'x_phase1': x1_new,
                    'x_phase2': x2_new,
                    'beta': beta
                }
            
            x1 = x1_new
            x2 = x2_new
        
        # Não convergiu
        return {
            'converged': False,
            'stable': True,
            'x_phase1': z,
            'x_phase2': z,
            'beta': 0.0
        }
