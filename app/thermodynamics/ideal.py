import numpy as np
from scipy.optimize import fsolve, brentq

class IdealModel:
    '''Modelo ideal para equilíbrio de fases (Lei de Raoult)'''
    
    def __init__(self):
        self.name = 'Ideal'
        self.R = 8.314  # J/(mol·K) - Constante dos gases
    
    def antoine_equation(self, T, A, B, C):
        '''
        Equação de Antoine para pressão de saturação
        log10(P_sat) = A - B/(T + C)
        
        Args:
            T: Temperatura (K)
            A, B, C: Parâmetros de Antoine
        
        Returns:
            P_sat: Pressão de saturação (Pa)
        '''
        log_p = A - B / (T + C)
        return 10**log_p * 133.322  # Converter mmHg para Pa
    
    def activity_coefficient(self, x, T, component_idx=0):
        '''
        Coeficiente de atividade (gamma = 1 para modelo ideal)
        
        Args:
            x: Composição da fase líquida (array)
            T: Temperatura (K)
            component_idx: Índice do componente
        
        Returns:
            gamma: Coeficiente de atividade (sempre 1)
        '''
        return 1.0
    
    def fugacity_coefficient(self, y, P, T, component_idx=0):
        '''
        Coeficiente de fugacidade (phi = 1 para modelo ideal)
        
        Args:
            y: Composição da fase vapor (array)
            P: Pressão total (Pa)
            T: Temperatura (K)
            component_idx: Índice do componente
        
        Returns:
            phi: Coeficiente de fugacidade (sempre 1)
        '''
        return 1.0
    
    def bubble_point_pressure(self, x, T, antoine_params):
        '''
        Cálculo de ponto de bolha (dada T, calcular P)
        
        Args:
            x: Composição da fase líquida (array)
            T: Temperatura (K)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
        
        Returns:
            P: Pressão de bolha (Pa)
            y: Composição da fase vapor (array)
        '''
        n_comp = len(x)
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        
        # Lei de Raoult: P = sum(x_i * P_sat_i)
        P = np.sum(x * P_sat)
        
        # Lei de Raoult: y_i = x_i * P_sat_i / P
        y = (x * P_sat) / P
        
        return P, y
    
    def dew_point_pressure(self, y, T, antoine_params):
        '''
        Cálculo de ponto de orvalho (dada T, calcular P)
        
        Args:
            y: Composição da fase vapor (array)
            T: Temperatura (K)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
        
        Returns:
            P: Pressão de orvalho (Pa)
            x: Composição da fase líquida (array)
        '''
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        
        # Lei de Raoult: P = 1 / sum(y_i / P_sat_i)
        P = 1.0 / np.sum(y / P_sat)
        
        # Lei de Raoult: x_i = y_i * P / P_sat_i
        x = (y * P) / P_sat
        
        return P, x
    
    def bubble_point_temperature(self, x, P, antoine_params, T_guess=300.0):
        '''
        Cálculo de ponto de bolha (dada P, calcular T)
        
        Args:
            x: Composição da fase líquida (array)
            P: Pressão total (Pa)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
            T_guess: Estimativa inicial de temperatura (K)
        
        Returns:
            T: Temperatura de bolha (K)
            y: Composição da fase vapor (array)
        '''
        def objective(T):
            P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
            return np.sum(x * P_sat) - P
        
        # Resolver equação não-linear
        T = fsolve(objective, T_guess)[0]
        
        # Calcular composição do vapor
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        y = (x * P_sat) / P
        
        return T, y
    
    def dew_point_temperature(self, y, P, antoine_params, T_guess=300.0):
        '''
        Cálculo de ponto de orvalho (dada P, calcular T)
        
        Args:
            y: Composição da fase vapor (array)
            P: Pressão total (Pa)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
            T_guess: Estimativa inicial de temperatura (K)
        
        Returns:
            T: Temperatura de orvalho (K)
            x: Composição da fase líquida (array)
        '''
        def objective(T):
            P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
            return np.sum(y / P_sat) - 1.0/P
        
        # Resolver equação não-linear
        T = fsolve(objective, T_guess)[0]
        
        # Calcular composição do líquido
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        x = (y * P) / P_sat
        
        return T, x
    
    def flash_isothermal(self, z, T, P, antoine_params, beta_guess=0.5):
        '''
        Cálculo de flash isotérmico (Rachford-Rice)
        
        Args:
            z: Composição global (array)
            T: Temperatura (K)
            P: Pressão (Pa)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2), ...]
            beta_guess: Fração de vapor inicial
        
        Returns:
            beta: Fração de vapor
            x: Composição da fase líquida (array)
            y: Composição da fase vapor (array)
        '''
        # Calcular constantes de equilíbrio K_i = y_i/x_i = P_sat_i/P
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        K = P_sat / P
        
        # Equação de Rachford-Rice
        def rachford_rice(beta):
            return np.sum(z * (K - 1) / (1 + beta * (K - 1)))
        
        # Limites de beta
        beta_min = 1.0 / (1.0 - np.max(K))
        beta_max = 1.0 / (1.0 - np.min(K))
        beta_min = max(0.0, beta_min)
        beta_max = min(1.0, beta_max)
        
        # Verificar se é bifásico
        if rachford_rice(0.0) * rachford_rice(1.0) > 0:
            # Sistema monofásico
            if rachford_rice(0.0) > 0:
                # Todo vapor
                return 1.0, z.copy(), z.copy()
            else:
                # Todo líquido
                return 0.0, z.copy(), z.copy()
        
        # Resolver Rachford-Rice
        beta = brentq(rachford_rice, beta_min, beta_max)
        
        # Calcular composições
        x = z / (1 + beta * (K - 1))
        y = K * x
        
        return beta, x, y
    
    def xy_diagram(self, T_or_P, antoine_params, n_points=50, fixed='T'):
        '''
        Gerar diagrama x-y para sistema binário
        
        Args:
            T_or_P: Temperatura (K) ou Pressão (Pa)
            antoine_params: Lista de tuplas [(A1, B1, C1), (A2, B2, C2)]
            n_points: Número de pontos
            fixed: 'T' para isotérmico ou 'P' para isobárico
        
        Returns:
            x_data: Composições do líquido
            y_data: Composições do vapor
        '''
        x_data = np.linspace(0, 1, n_points)
        y_data = np.zeros(n_points)
        
        for i, x1 in enumerate(x_data):
            x = np.array([x1, 1-x1])
            
            if fixed == 'T':
                _, y = self.bubble_point_pressure(x, T_or_P, antoine_params)
            else:  # fixed == 'P'
                _, y = self.bubble_point_temperature(x, T_or_P, antoine_params)
            
            y_data[i] = y[0]
        
        return x_data, y_data
