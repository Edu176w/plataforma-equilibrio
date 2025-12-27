import numpy as np
from scipy.optimize import fsolve, brentq
from app.thermodynamics.uniquac import UNIQUACModel

class UNIFACModel(UNIQUACModel):
    '''Modelo UNIFAC (UNIQUAC Functional-group Activity Coefficients)'''
    
    def __init__(self):
        super().__init__()
        self.name = 'UNIFAC'
    
    def calculate_rq_from_groups(self, molecule_groups, group_params):
        '''
        Calcular parâmetros r e q a partir de contribuição de grupos
        
        Args:
            molecule_groups: Dict {group_id: count} para cada molécula
            group_params: Dict {group_id: {'R': R_k, 'Q': Q_k}}
        
        Returns:
            r: Volume molecular relativo
            q: Área molecular relativa
        '''
        r = sum(count * group_params[gid]['R'] for gid, count in molecule_groups.items())
        q = sum(count * group_params[gid]['Q'] for gid, count in molecule_groups.items())
        
        return r, q
    
    def group_activity_coefficient(self, x, T, molecules_groups, group_params, group_interaction_params):
        '''
        Calcular coeficientes de atividade de grupos
        
        Args:
            x: Composição molar (array)
            T: Temperatura (K)
            molecules_groups: Lista de dicts com grupos de cada molécula
            group_params: Parâmetros R_k, Q_k dos grupos
            group_interaction_params: Matriz a_mn de interação entre grupos
        
        Returns:
            ln_gamma_groups: Coeficientes de atividade dos grupos na mistura
        '''
        n_groups = len(group_params)
        
        # Calcular frações de área dos grupos
        X_m = np.zeros(n_groups)
        for i, mol_groups in enumerate(molecules_groups):
            for gid, count in mol_groups.items():
                X_m[gid] += x[i] * count
        
        X_m = X_m / np.sum(X_m)
        
        # Calcular theta_m
        Q_m = np.array([group_params[k]['Q'] for k in range(n_groups)])
        theta_m = (X_m * Q_m) / np.sum(X_m * Q_m)
        
        # Calcular psi_mn = exp(-a_mn/T)
        psi = np.exp(-group_interaction_params / T)
        
        # Calcular ln(Gamma_m)
        ln_gamma_groups = np.zeros(n_groups)
        
        for m in range(n_groups):
            sum_theta_psi = np.sum(theta_m * psi[:, m])
            term1 = Q_m[m] * (1.0 - np.log(sum_theta_psi))
            
            term2 = 0.0
            for n in range(n_groups):
                sum_theta_psi_n = np.sum(theta_m * psi[:, n])
                term2 += (theta_m[n] * psi[m, n]) / sum_theta_psi_n
            
            ln_gamma_groups[m] = term1 - Q_m[m] * term2
        
        return ln_gamma_groups
    
    def activity_coefficient_unifac(self, x, T, molecules_groups, group_params, group_interaction_params):
        '''
        Calcular coeficientes de atividade usando UNIFAC
        
        Args:
            x: Composição da fase líquida (array)
            T: Temperatura (K)
            molecules_groups: Lista de dicts com grupos de cada molécula
            group_params: Parâmetros R_k, Q_k dos grupos
            group_interaction_params: Matriz a_mn de interação entre grupos
        
        Returns:
            gamma: Array de coeficientes de atividade
        '''
        n_comp = len(x)
        
        # Calcular r_i e q_i para cada molécula
        r_params = np.array([self.calculate_rq_from_groups(mol, group_params)[0] 
                             for mol in molecules_groups])
        q_params = np.array([self.calculate_rq_from_groups(mol, group_params)[1] 
                             for mol in molecules_groups])
        
        # Termo combinatorial (mesmo do UNIQUAC)
        r_sum = np.sum(x * r_params)
        q_sum = np.sum(x * q_params)
        
        phi = (x * r_params) / r_sum
        theta = (x * q_params) / q_sum
        
        l = (self.z / 2.0) * (r_params - q_params) - (r_params - 1.0)
        
        ln_gamma_c = np.log(phi / x) + (self.z / 2.0) * q_params * np.log(theta / phi) + l - (phi / x) * np.sum(x * l)
        
        # Termo residual (contribuição de grupos)
        ln_gamma_groups_mixture = self.group_activity_coefficient(x, T, molecules_groups, 
                                                                   group_params, group_interaction_params)
        
        ln_gamma_r = np.zeros(n_comp)
        
        for i in range(n_comp):
            # Calcular ln(Gamma) para componente puro
            x_pure = np.zeros(n_comp)
            x_pure[i] = 1.0
            
            ln_gamma_groups_pure = self.group_activity_coefficient(x_pure, T, molecules_groups,
                                                                    group_params, group_interaction_params)
            
            # Contribuição residual
            for gid, count in molecules_groups[i].items():
                ln_gamma_r[i] += count * (ln_gamma_groups_mixture[gid] - ln_gamma_groups_pure[gid])
        
        # Coeficiente de atividade total
        gamma = np.exp(ln_gamma_c + ln_gamma_r)
        
        return gamma
    
    def bubble_point_pressure(self, x, T, antoine_params, molecules_groups, group_params, group_interaction_params):
        '''Cálculo de ponto de bolha com modelo UNIFAC'''
        P_sat = np.array([self.antoine_equation(T, *params) for params in antoine_params])
        gamma = self.activity_coefficient_unifac(x, T, molecules_groups, group_params, group_interaction_params)
        
        P = np.sum(x * gamma * P_sat)
        y = (x * gamma * P_sat) / P
        
        return P, y
