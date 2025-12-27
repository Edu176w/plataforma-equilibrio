import numpy as np
from scipy.optimize import fsolve, brentq
from app.thermodynamics.ideal import IdealModel

class UNIQUACModel(IdealModel):
    '''Modelo UNIQUAC (Universal Quasi-Chemical) para equilíbrio de fases'''
    
    def __init__(self):
        super().__init__()
        self.name = 'UNIQUAC'
        self.z = 10.0  # Número de coordenação
    
    def activity_coefficient(self, x, T, r_params, q_params, tau_params):
        '''
        Coeficiente de atividade segundo modelo UNIQUAC
        
        Args:
            x: Composição da fase líquida (array)
            T: Temperatura (K)
            r_params: Array de parâmetros r_i (volume molecular relativo)
            q_params: Array de parâmetros q_i (área molecular relativa)
            tau_params: Matriz de parâmetros tau_ij = exp(-u_ij/RT)
        
        Returns:
            gamma: Array de coeficientes de atividade
        '''
        n_comp = len(x)
        
        # Calcular frações de volume (phi) e área (theta)
        r_sum = np.sum(x * r_params)
        q_sum = np.sum(x * q_params)
        
        phi = (x * r_params) / r_sum
        theta = (x * q_params) / q_sum
        
        # Parâmetro l_i
        l = (self.z / 2.0) * (r_params - q_params) - (r_params - 1.0)
        
        # Termo combinatorial
        ln_gamma_c = np.log(phi / x) + (self.z / 2.0) * q_params * np.log(theta / phi) + l - (phi / x) * np.sum(x * l)
        
        # Termo residual
        ln_gamma_r = np.zeros(n_comp)
        
        for i in range(n_comp):
            sum_theta_tau = np.sum(theta * tau_params[:, i])
            term1 = q_params[i] * (1.0 - np.log(sum_theta_tau))
            
            term2 = 0.0
            for j in range(n_comp):
                sum_theta_tau_j = np.sum(theta * tau_params[:, j])
                term2 += (theta[j] * tau_params[i, j]) / sum_theta_tau_j
            
            ln_gamma_r[i] = term1 - q_params[i] * term2
        
        # Coeficiente de atividade total
        gamma = np.exp(ln_gamma_c + ln_gamma_r)
        
        return gamma
    
    def bubble_point_pressure(self, x, T, antoine_params, r_params, q_params, tau_params):
        '''Cálculo de ponto de bolha com modelo UNIQUAC'''
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        gamma = self.activity_coefficient(x, T, r_params, q_params, tau_params)
        
        P = np.sum(x * gamma * P_sat)
        y = (x * gamma * P_sat) / P
        
        return P, y
    
    def dew_point_pressure(self, y, T, antoine_params, r_params, q_params, tau_params, x_guess=None):
        '''Cálculo de ponto de orvalho com modelo UNIQUAC'''
        n_comp = len(y)
        
        if x_guess is None:
            x_guess = y.copy()
        
        def objective(vars):
            x = vars[:n_comp]
            x = x / np.sum(x)
            
            P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
            gamma = self.activity_coefficient(x, T, r_params, q_params, tau_params)
            
            P_calc = y / (x * gamma / P_sat)
            return P_calc[:-1] - P_calc[-1]
        
        x_sol = fsolve(objective, x_guess)
        x = x_sol / np.sum(x_sol)
        
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        gamma = self.activity_coefficient(x, T, r_params, q_params, tau_params)
        P = np.mean(y / (x * gamma / P_sat))
        
        return P, x
    
    def bubble_point_temperature(self, x, P, antoine_params, r_params, q_params, tau_params, T_guess=300.0):
        '''Cálculo de ponto de bolha (dada P, calcular T) com modelo UNIQUAC'''
        def objective(T):
            P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
            gamma = self.activity_coefficient(x, T, r_params, q_params, tau_params)
            return np.sum(x * gamma * P_sat) - P
        
        T = fsolve(objective, T_guess)[0]
        
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        gamma = self.activity_coefficient(x, T, r_params, q_params, tau_params)
        y = (x * gamma * P_sat) / P
        
        return T, y
    
    def flash_isothermal(self, z, T, P, antoine_params, r_params, q_params, tau_params, beta_guess=0.5):
        '''Cálculo de flash isotérmico com modelo UNIQUAC'''
        n_comp = len(z)
        max_iter = 100
        tol = 1e-6
        
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        K = P_sat / P
        beta = beta_guess
        
        for iteration in range(max_iter):
            x = z / (1 + beta * (K - 1))
            y = K * x
            
            x = x / np.sum(x)
            y = y / np.sum(y)
            
            gamma = self.activity_coefficient(x, T, r_params, q_params, tau_params)
            K_new = gamma * P_sat / P
            
            if np.max(np.abs(K_new - K)) < tol:
                break
            
            K = K_new
            
            def rachford_rice(b):
                return np.sum(z * (K - 1) / (1 + b * (K - 1)))
            
            beta_min = max(0.0, 1.0 / (1.0 - np.max(K)))
            beta_max = min(1.0, 1.0 / (1.0 - np.min(K)))
            
            if rachford_rice(0.0) * rachford_rice(1.0) > 0:
                if rachford_rice(0.0) > 0:
                    return 1.0, z.copy(), z.copy()
                else:
                    return 0.0, z.copy(), z.copy()
            
            beta = brentq(rachford_rice, beta_min, beta_max)
        
        x = z / (1 + beta * (K - 1))
        y = K * x
        x = x / np.sum(x)
        y = y / np.sum(y)
        
        return beta, x, y
