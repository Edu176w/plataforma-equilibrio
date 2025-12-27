import numpy as np
from scipy.optimize import fsolve, brentq
from app.thermodynamics.ideal import IdealModel

class NRTLModel(IdealModel):
    '''Modelo NRTL (Non-Random Two-Liquid) para equilíbrio de fases'''
    
    def __init__(self):
        super().__init__()
        self.name = 'NRTL'
    
    def activity_coefficient(self, x, T, tau_params, alpha_params):
        '''
        Coeficiente de atividade segundo modelo NRTL
        
        Args:
            x: Composição da fase líquida (array)
            T: Temperatura (K)
            tau_params: Matriz de parâmetros tau_ij (g_ij/RT)
            alpha_params: Matriz de parâmetros alpha_ij
        
        Returns:
            gamma: Array de coeficientes de atividade
        '''
        n_comp = len(x)
        gamma = np.zeros(n_comp)
        
        # Calcular G_ij = exp(-alpha_ij * tau_ij)
        G = np.exp(-alpha_params * tau_params)
        
        for i in range(n_comp):
            # Termo 1: sum_j(x_j * tau_ji * G_ji) / sum_j(x_j * G_ji)
            sum_xG = np.sum(x * G[:, i])
            term1 = np.sum(x * tau_params[:, i] * G[:, i]) / sum_xG
            
            # Termo 2: sum_j [ x_j * G_ij / sum_k(x_k * G_kj) * (tau_ij - sum_m(x_m * tau_mj * G_mj) / sum_m(x_m * G_mj)) ]
            term2 = 0.0
            for j in range(n_comp):
                sum_xG_j = np.sum(x * G[:, j])
                sum_xtauG_j = np.sum(x * tau_params[:, j] * G[:, j])
                term2 += (x[j] * G[i, j] / sum_xG_j) * (tau_params[i, j] - sum_xtauG_j / sum_xG_j)
            
            gamma[i] = np.exp(term1 + term2)
        
        return gamma
    
    def bubble_point_pressure(self, x, T, antoine_params, tau_params, alpha_params):
        '''
        Cálculo de ponto de bolha com modelo NRTL
        
        Args:
            x: Composição da fase líquida (array)
            T: Temperatura (K)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
            tau_params: Matriz de parâmetros tau_ij
            alpha_params: Matriz de parâmetros alpha_ij
        
        Returns:
            P: Pressão de bolha (Pa)
            y: Composição da fase vapor (array)
        '''
        n_comp = len(x)
        
        # Calcular pressões de saturação
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        
        # Calcular coeficientes de atividade
        gamma = self.activity_coefficient(x, T, tau_params, alpha_params)
        
        # Pressão de bolha: P = sum(x_i * gamma_i * P_sat_i)
        P = np.sum(x * gamma * P_sat)
        
        # Composição do vapor: y_i = x_i * gamma_i * P_sat_i / P
        y = (x * gamma * P_sat) / P
        
        return P, y
    
    def dew_point_pressure(self, y, T, antoine_params, tau_params, alpha_params, x_guess=None):
        '''
        Cálculo de ponto de orvalho com modelo NRTL
        
        Args:
            y: Composição da fase vapor (array)
            T: Temperatura (K)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
            tau_params: Matriz de parâmetros tau_ij
            alpha_params: Matriz de parâmetros alpha_ij
            x_guess: Estimativa inicial de x
        
        Returns:
            P: Pressão de orvalho (Pa)
            x: Composição da fase líquida (array)
        '''
        n_comp = len(y)
        
        if x_guess is None:
            x_guess = y.copy()
        
        def objective(vars):
            x = vars[:n_comp]
            x = x / np.sum(x)  # Normalizar
            
            P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
            gamma = self.activity_coefficient(x, T, tau_params, alpha_params)
            
            # P = y_i / (x_i * gamma_i / P_sat_i)
            P_calc = y / (x * gamma / P_sat)
            
            # Todas as pressões devem ser iguais
            return P_calc[:-1] - P_calc[-1]
        
        # Resolver sistema
        x_sol = fsolve(objective, x_guess)
        x = x_sol / np.sum(x_sol)  # Normalizar
        
        # Calcular pressão
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        gamma = self.activity_coefficient(x, T, tau_params, alpha_params)
        P = np.mean(y / (x * gamma / P_sat))
        
        return P, x
    
    def bubble_point_temperature(self, x, P, antoine_params, tau_params, alpha_params, T_guess=300.0):
        '''
        Cálculo de ponto de bolha (dada P, calcular T) com modelo NRTL
        
        Args:
            x: Composição da fase líquida (array)
            P: Pressão total (Pa)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
            tau_params: Matriz de parâmetros tau_ij
            alpha_params: Matriz de parâmetros alpha_ij
            T_guess: Estimativa inicial de temperatura (K)
        
        Returns:
            T: Temperatura de bolha (K)
            y: Composição da fase vapor (array)
        '''
        def objective(T):
            P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
            gamma = self.activity_coefficient(x, T, tau_params, alpha_params)
            return np.sum(x * gamma * P_sat) - P
        
        T = fsolve(objective, T_guess)[0]
        
        # Calcular composição do vapor
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        gamma = self.activity_coefficient(x, T, tau_params, alpha_params)
        y = (x * gamma * P_sat) / P
        
        return T, y
    
    def flash_isothermal(self, z, T, P, antoine_params, tau_params, alpha_params, beta_guess=0.5):
        '''
        Cálculo de flash isotérmico com modelo NRTL
        
        Args:
            z: Composição global (array)
            T: Temperatura (K)
            P: Pressão (Pa)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
            tau_params: Matriz de parâmetros tau_ij
            alpha_params: Matriz de parâmetros alpha_ij
            beta_guess: Fração de vapor inicial
        
        Returns:
            beta: Fração de vapor
            x: Composição da fase líquida (array)
            y: Composição da fase vapor (array)
        '''
        n_comp = len(z)
        max_iter = 100
        tol = 1e-6
        
        # Estimativa inicial usando modelo ideal
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        K = P_sat / P
        
        beta = beta_guess
        
        for iteration in range(max_iter):
            # Calcular composições
            x = z / (1 + beta * (K - 1))
            y = K * x
            
            # Normalizar
            x = x / np.sum(x)
            y = y / np.sum(y)
            
            # Atualizar K com coeficientes de atividade
            gamma = self.activity_coefficient(x, T, tau_params, alpha_params)
            K_new = gamma * P_sat / P
            
            # Verificar convergência
            if np.max(np.abs(K_new - K)) < tol:
                break
            
            K = K_new
            
            # Rachford-Rice
            def rachford_rice(b):
                return np.sum(z * (K - 1) / (1 + b * (K - 1)))
            
            # Limites de beta
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
