import numpy as np
from app.thermodynamics.ideal import IdealModel
from app.thermodynamics.nrtl import NRTLModel
from app.thermodynamics.uniquac import UNIQUACModel
from app.thermodynamics.unifac import UNIFACModel

class ELVCalculations:
    '''Classe para cálculos de Equilíbrio Líquido-Vapor'''
    
    def __init__(self, model_type='ideal'):
        '''
        Inicializar calculadora ELV
        
        Args:
            model_type: 'ideal', 'nrtl', 'uniquac', ou 'unifac'
        '''
        self.model_type = model_type
        
        if model_type == 'ideal':
            self.model = IdealModel()
        elif model_type == 'nrtl':
            self.model = NRTLModel()
        elif model_type == 'uniquac':
            self.model = UNIQUACModel()
        elif model_type == 'unifac':
            self.model = UNIFACModel()
        else:
            raise ValueError(f'Modelo desconhecido: {model_type}')
    
    def calculate_bubble_point(self, x, T=None, P=None, antoine_params=None, **kwargs):
        '''
        Calcular ponto de bolha
        
        Args:
            x: Composição do líquido (array ou lista)
            T: Temperatura (K) - para calcular P
            P: Pressão (Pa) - para calcular T
            antoine_params: Parâmetros de Antoine
            **kwargs: Parâmetros específicos do modelo (tau, alpha, r, q, etc.)
        
        Returns:
            dict com resultados
        '''
        x = np.array(x)
        
        if T is not None and P is None:
            # Calcular pressão
            if self.model_type == 'ideal':
                P_calc, y = self.model.bubble_point_pressure(x, T, antoine_params)
            elif self.model_type == 'nrtl':
                P_calc, y = self.model.bubble_point_pressure(x, T, antoine_params, 
                                                             kwargs['tau_params'], kwargs['alpha_params'])
            elif self.model_type == 'uniquac':
                P_calc, y = self.model.bubble_point_pressure(x, T, antoine_params,
                                                             kwargs['r_params'], kwargs['q_params'], 
                                                             kwargs['tau_params'])
            elif self.model_type == 'unifac':
                P_calc, y = self.model.bubble_point_pressure(x, T, antoine_params,
                                                             kwargs['molecules_groups'], 
                                                             kwargs['group_params'],
                                                             kwargs['group_interaction_params'])
            
            return {
                'type': 'bubble_pressure',
                'temperature': T,
                'pressure': P_calc,
                'x': x.tolist(),
                'y': y.tolist(),
                'model': self.model_type
            }
        
        elif P is not None and T is None:
            # Calcular temperatura
            if self.model_type == 'ideal':
                T_calc, y = self.model.bubble_point_temperature(x, P, antoine_params)
            elif self.model_type == 'nrtl':
                T_calc, y = self.model.bubble_point_temperature(x, P, antoine_params,
                                                               kwargs['tau_params'], kwargs['alpha_params'])
            elif self.model_type == 'uniquac':
                T_calc, y = self.model.bubble_point_temperature(x, P, antoine_params,
                                                               kwargs['r_params'], kwargs['q_params'],
                                                               kwargs['tau_params'])
            
            return {
                'type': 'bubble_temperature',
                'temperature': T_calc,
                'pressure': P,
                'x': x.tolist(),
                'y': y.tolist(),
                'model': self.model_type
            }
        else:
            raise ValueError('Forneça T ou P (não ambos)')
    
    def calculate_dew_point(self, y, T=None, P=None, antoine_params=None, **kwargs):
        '''
        Calcular ponto de orvalho
        
        Args:
            y: Composição do vapor (array ou lista)
            T: Temperatura (K) - para calcular P
            P: Pressão (Pa) - para calcular T
            antoine_params: Parâmetros de Antoine
            **kwargs: Parâmetros específicos do modelo
        
        Returns:
            dict com resultados
        '''
        y = np.array(y)
        
        if T is not None and P is None:
            # Calcular pressão
            if self.model_type == 'ideal':
                P_calc, x = self.model.dew_point_pressure(y, T, antoine_params)
            elif self.model_type == 'nrtl':
                P_calc, x = self.model.dew_point_pressure(y, T, antoine_params,
                                                         kwargs['tau_params'], kwargs['alpha_params'])
            elif self.model_type == 'uniquac':
                P_calc, x = self.model.dew_point_pressure(y, T, antoine_params,
                                                         kwargs['r_params'], kwargs['q_params'],
                                                         kwargs['tau_params'])
            
            return {
                'type': 'dew_pressure',
                'temperature': T,
                'pressure': P_calc,
                'x': x.tolist(),
                'y': y.tolist(),
                'model': self.model_type
            }
        else:
            raise ValueError('Forneça apenas T (cálculo de P)')
    
    def calculate_flash(self, z, T, P, antoine_params=None, **kwargs):
        '''
        Calcular flash isotérmico
        
        Args:
            z: Composição global (array ou lista)
            T: Temperatura (K)
            P: Pressão (Pa)
            antoine_params: Parâmetros de Antoine
            **kwargs: Parâmetros específicos do modelo
        
        Returns:
            dict com resultados
        '''
        z = np.array(z)
        
        if self.model_type == 'ideal':
            beta, x, y = self.model.flash_isothermal(z, T, P, antoine_params)
        elif self.model_type == 'nrtl':
            beta, x, y = self.model.flash_isothermal(z, T, P, antoine_params,
                                                     kwargs['tau_params'], kwargs['alpha_params'])
        elif self.model_type == 'uniquac':
            beta, x, y = self.model.flash_isothermal(z, T, P, antoine_params,
                                                     kwargs['r_params'], kwargs['q_params'],
                                                     kwargs['tau_params'])
        
        return {
            'type': 'flash',
            'temperature': T,
            'pressure': P,
            'beta': beta,
            'z': z.tolist(),
            'x': x.tolist(),
            'y': y.tolist(),
            'phase': 'two-phase' if 0 < beta < 1 else ('vapor' if beta == 1 else 'liquid'),
            'model': self.model_type
        }
    
    def generate_pxy_diagram(self, T, antoine_params, n_points=50, **kwargs):
        '''
        Gerar diagrama P-x-y para sistema binário
        
        Args:
            T: Temperatura (K)
            antoine_params: Parâmetros de Antoine
            n_points: Número de pontos
            **kwargs: Parâmetros específicos do modelo
        
        Returns:
            dict com dados do diagrama
        '''
        x_data = np.linspace(0, 1, n_points)
        p_bubble = []
        p_dew = []
        y_data = []
        
        for x1 in x_data:
            x = np.array([x1, 1-x1])
            
            # Ponto de bolha
            result_bubble = self.calculate_bubble_point(x, T=T, antoine_params=antoine_params, **kwargs)
            p_bubble.append(result_bubble['pressure'])
            y_data.append(result_bubble['y'][0])
        
        return {
            'type': 'pxy_diagram',
            'temperature': T,
            'x': x_data.tolist(),
            'y': y_data,
            'p_bubble': p_bubble,
            'model': self.model_type
        }
    
    def generate_txy_diagram(self, P, antoine_params, n_points=50, **kwargs):
        '''
        Gerar diagrama T-x-y para sistema binário
        
        Args:
            P: Pressão (Pa)
            antoine_params: Parâmetros de Antoine
            n_points: Número de pontos
            **kwargs: Parâmetros específicos do modelo
        
        Returns:
            dict com dados do diagrama
        '''
        x_data = np.linspace(0, 1, n_points)
        t_bubble = []
        y_data = []
        
        for x1 in x_data:
            x = np.array([x1, 1-x1])
            
            # Ponto de bolha
            result_bubble = self.calculate_bubble_point(x, P=P, antoine_params=antoine_params, **kwargs)
            t_bubble.append(result_bubble['temperature'])
            y_data.append(result_bubble['y'][0])
        
        return {
            'type': 'txy_diagram',
            'pressure': P,
            'x': x_data.tolist(),
            'y': y_data,
            't_bubble': t_bubble,
            'model': self.model_type
        }
