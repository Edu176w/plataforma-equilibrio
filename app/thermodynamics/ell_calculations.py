import numpy as np
from scipy.optimize import fsolve, minimize
from app.thermodynamics.ideal import IdealModel
from app.thermodynamics.nrtl import NRTLModel
from app.thermodynamics.uniquac import UNIQUACModel

class ELLCalculations:
    '''Classe para cálculos de Equilíbrio Líquido-Líquido'''
    
    def __init__(self, model_type='nrtl'):
        '''
        Inicializar calculadora ELL
        
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
        else:
            raise ValueError(f'Modelo {model_type} não implementado para ELL')
    
    def stability_test(self, x, T, **kwargs):
        '''
        Teste de estabilidade para verificar se haverá separação de fases
        
        Args:
            x: Composição (array)
            T: Temperatura (K)
            **kwargs: Parâmetros do modelo
        
        Returns:
            stable: True se estável (uma fase), False se instável (duas fases)
        '''
        n_comp = len(x)
        
        # Calcular coeficientes de atividade
        if self.model_type == 'nrtl':
            gamma = self.model.activity_coefficient(x, T, kwargs['tau_params'], kwargs['alpha_params'])
        elif self.model_type == 'uniquac':
            gamma = self.model.activity_coefficient(x, T, kwargs['r_params'], 
                                                    kwargs['q_params'], kwargs['tau_params'])
        
        # Critério de estabilidade baseado em energia de Gibbs
        # Se ln(gamma_i * x_i) tem concavidade positiva, sistema é estável
        ln_activity = np.log(gamma * x)
        
        # Verificação simplificada: se gamma > 1 para todos, pode haver separação
        if np.all(gamma > 1.5):
            return False
        
        return True
    
    def calculate_lle(self, z, T, **kwargs):
        '''
        Calcular equilíbrio líquido-líquido
        
        Args:
            z: Composição global (array)
            T: Temperatura (K)
            **kwargs: Parâmetros do modelo (tau_params, alpha_params, etc.)
        
        Returns:
            dict com resultados ou None se não houver separação
        '''
        n_comp = len(z)
        
        # Teste de estabilidade
        if self.stability_test(z, T, **kwargs):
            return {
                'type': 'lle',
                'stable': True,
                'phases': 1,
                'message': 'Sistema monofásico - não há separação de fases',
                'model': self.model_type
            }
        
        # Sistema bifásico - resolver equilíbrio
        # Condição: gamma_i^I * x_i^I = gamma_i^II * x_i^II para todos os componentes
        
        def objective(vars):
            # vars = [x1^I, x2^I, ..., x1^II, x2^II, ...]
            n = n_comp
            x_phase1 = vars[:n]
            x_phase2 = vars[n:2*n]
            
            # Normalizar composições
            x_phase1 = x_phase1 / np.sum(x_phase1)
            x_phase2 = x_phase2 / np.sum(x_phase2)
            
            # Calcular coeficientes de atividade
            if self.model_type == 'nrtl':
                gamma1 = self.model.activity_coefficient(x_phase1, T, 
                                                        kwargs['tau_params'], kwargs['alpha_params'])
                gamma2 = self.model.activity_coefficient(x_phase2, T,
                                                        kwargs['tau_params'], kwargs['alpha_params'])
            elif self.model_type == 'uniquac':
                gamma1 = self.model.activity_coefficient(x_phase1, T,
                                                        kwargs['r_params'], kwargs['q_params'],
                                                        kwargs['tau_params'])
                gamma2 = self.model.activity_coefficient(x_phase2, T,
                                                        kwargs['r_params'], kwargs['q_params'],
                                                        kwargs['tau_params'])
            
            # Equações de equilíbrio: gamma_i^I * x_i^I = gamma_i^II * x_i^II
            equations = gamma1 * x_phase1 - gamma2 * x_phase2
            
            return equations
        
        # Estimativa inicial
        x0 = np.concatenate([
            np.array([0.9, 0.1] if n_comp == 2 else [0.8] + [0.2/(n_comp-1)]*(n_comp-1)),
            np.array([0.1, 0.9] if n_comp == 2 else [0.2] + [0.8/(n_comp-1)]*(n_comp-1))
        ])
        
        try:
            solution = fsolve(objective, x0, full_output=True)
            x_sol = solution[0]
            info = solution[1]
            
            if info['fvec'].max() < 1e-4:  # Convergiu
                x_phase1 = x_sol[:n_comp]
                x_phase2 = x_sol[n_comp:2*n_comp]
                
                # Normalizar
                x_phase1 = x_phase1 / np.sum(x_phase1)
                x_phase2 = x_phase2 / np.sum(x_phase2)
                
                return {
                    'type': 'lle',
                    'stable': False,
                    'phases': 2,
                    'temperature': T,
                    'phase1': x_phase1.tolist(),
                    'phase2': x_phase2.tolist(),
                    'model': self.model_type
                }
        except:
            pass
        
        return {
            'type': 'lle',
            'stable': True,
            'phases': 1,
            'message': 'Não foi possível encontrar equilíbrio bifásico',
            'model': self.model_type
        }
    
    def calculate_binodal_curve(self, T, **kwargs):
        '''
        Calcular curva binodal para sistema binário
        
        Args:
            T: Temperatura (K)
            **kwargs: Parâmetros do modelo
        
        Returns:
            dict com pontos da curva binodal
        '''
        x1_phase1_data = []
        x1_phase2_data = []
        
        # Varrer diferentes composições iniciais
        for x1_init in np.linspace(0.1, 0.9, 20):
            z = np.array([x1_init, 1-x1_init])
            result = self.calculate_lle(z, T, **kwargs)
            
            if result['phases'] == 2:
                x1_phase1_data.append(result['phase1'][0])
                x1_phase2_data.append(result['phase2'][0])
        
        if len(x1_phase1_data) > 0:
            return {
                'type': 'binodal_curve',
                'temperature': T,
                'phase1_x1': x1_phase1_data,
                'phase2_x1': x1_phase2_data,
                'model': self.model_type
            }
        else:
            return {
                'type': 'binodal_curve',
                'message': 'Nenhuma separação de fases encontrada',
                'model': self.model_type
            }
    
    def calculate_tie_lines(self, T, n_lines=5, **kwargs):
        '''
        Calcular tie-lines para sistema binário
        
        Args:
            T: Temperatura (K)
            n_lines: Número de tie-lines
            **kwargs: Parâmetros do modelo
        
        Returns:
            lista de tie-lines
        '''
        tie_lines = []
        
        for x1_init in np.linspace(0.2, 0.8, n_lines):
            z = np.array([x1_init, 1-x1_init])
            result = self.calculate_lle(z, T, **kwargs)
            
            if result['phases'] == 2:
                tie_lines.append({
                    'phase1': result['phase1'],
                    'phase2': result['phase2']
                })
        
        return {
            'type': 'tie_lines',
            'temperature': T,
            'tie_lines': tie_lines,
            'model': self.model_type
        }
    
    def calculate_ternary_diagram(self, T, n_points=20, **kwargs):
        '''
        Calcular diagrama ternário (simplificado)
        
        Args:
            T: Temperatura (K)
            n_points: Número de pontos por eixo
            **kwargs: Parâmetros do modelo
        
        Returns:
            dict com dados do diagrama ternário
        '''
        stable_points = []
        unstable_points = []
        
        # Varrer composições ternárias
        for i in range(n_points):
            for j in range(n_points - i):
                x1 = i / n_points
                x2 = j / n_points
                x3 = 1.0 - x1 - x2
                
                if x3 >= 0:
                    z = np.array([x1, x2, x3])
                    result = self.calculate_lle(z, T, **kwargs)
                    
                    if result['phases'] == 1:
                        stable_points.append(z.tolist())
                    else:
                        unstable_points.append(z.tolist())
        
        return {
            'type': 'ternary_diagram',
            'temperature': T,
            'stable_points': stable_points,
            'unstable_points': unstable_points,
            'model': self.model_type
        }
