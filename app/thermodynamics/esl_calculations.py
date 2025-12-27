import numpy as np
from scipy.optimize import fsolve
from app.thermodynamics.ideal import IdealModel
from app.thermodynamics.nrtl import NRTLModel
from app.thermodynamics.uniquac import UNIQUACModel

class ESLCalculations:
    '''Classe para cálculos de Equilíbrio Sólido-Líquido'''
    
    def __init__(self, model_type='ideal'):
        '''
        Inicializar calculadora ESL
        
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
            raise ValueError(f'Modelo {model_type} não implementado para ESL')
    
    def calculate_solubility(self, T, solute_idx, solvent_composition, 
                            fusion_temp, fusion_enthalpy, **kwargs):
        '''
        Calcular solubilidade de um sólido em um solvente
        
        Args:
            T: Temperatura (K)
            solute_idx: Índice do componente sólido
            solvent_composition: Composição do solvente (array, sem soluto)
            fusion_temp: Temperatura de fusão do soluto (K)
            fusion_enthalpy: Entalpia de fusão do soluto (J/mol)
            **kwargs: Parâmetros do modelo
        
        Returns:
            dict com resultados
        '''
        R = 8.314  # J/(mol·K)
        
        # Equação de solubilidade ideal (simplificada)
        # ln(x_soluto * gamma_soluto) = -(ΔH_fus/R) * (1/T - 1/T_fus)
        
        ln_x_ideal = -(fusion_enthalpy / R) * (1/T - 1/fusion_temp)
        x_ideal = np.exp(ln_x_ideal)
        
        if self.model_type == 'ideal':
            x_solute = x_ideal
            gamma_solute = 1.0
        else:
            # Para modelos não-ideais, resolver iterativamente
            def objective(x_sol):
                # Criar composição completa
                n_comp = len(solvent_composition) + 1
                x_total = np.zeros(n_comp)
                x_total[solute_idx] = x_sol
                
                # Distribuir solvente
                remaining = 1.0 - x_sol
                for i, xi in enumerate(solvent_composition):
                    idx = i if i < solute_idx else i + 1
                    x_total[idx] = xi * remaining
                
                # Normalizar
                x_total = x_total / np.sum(x_total)
                
                # Calcular coeficiente de atividade
                if self.model_type == 'nrtl':
                    gamma = self.model.activity_coefficient(x_total, T,
                                                           kwargs['tau_params'], 
                                                           kwargs['alpha_params'])
                elif self.model_type == 'uniquac':
                    gamma = self.model.activity_coefficient(x_total, T,
                                                           kwargs['r_params'],
                                                           kwargs['q_params'],
                                                           kwargs['tau_params'])
                
                gamma_solute = gamma[solute_idx]
                
                # Equação de solubilidade
                ln_activity = np.log(x_sol * gamma_solute)
                ln_activity_expected = -(fusion_enthalpy / R) * (1/T - 1/fusion_temp)
                
                return ln_activity - ln_activity_expected
            
            # Resolver
            try:
                x_solute = fsolve(objective, x_ideal)[0]
                
                # Calcular gamma final
                n_comp = len(solvent_composition) + 1
                x_total = np.zeros(n_comp)
                x_total[solute_idx] = x_solute
                remaining = 1.0 - x_solute
                for i, xi in enumerate(solvent_composition):
                    idx = i if i < solute_idx else i + 1
                    x_total[idx] = xi * remaining
                x_total = x_total / np.sum(x_total)
                
                if self.model_type == 'nrtl':
                    gamma = self.model.activity_coefficient(x_total, T,
                                                           kwargs['tau_params'],
                                                           kwargs['alpha_params'])
                elif self.model_type == 'uniquac':
                    gamma = self.model.activity_coefficient(x_total, T,
                                                           kwargs['r_params'],
                                                           kwargs['q_params'],
                                                           kwargs['tau_params'])
                
                gamma_solute = gamma[solute_idx]
            except:
                x_solute = x_ideal
                gamma_solute = 1.0
        
        return {
            'type': 'solubility',
            'temperature': T,
            'solubility': x_solute,
            'activity_coefficient': gamma_solute,
            'model': self.model_type
        }
    
    def calculate_eutectic_point(self, fusion_temps, fusion_enthalpies, **kwargs):
        '''
        Calcular ponto eutético para sistema binário (simplificado)
        
        Args:
            fusion_temps: Lista de temperaturas de fusão [T1, T2] (K)
            fusion_enthalpies: Lista de entalpias de fusão [ΔH1, ΔH2] (J/mol)
            **kwargs: Parâmetros do modelo
        
        Returns:
            dict com ponto eutético
        '''
        R = 8.314
        
        # Estimativa inicial do ponto eutético
        T_eutectic_guess = min(fusion_temps) * 0.8
        
        def objective(T):
            # Calcular solubilidades de ambos componentes
            x1 = np.exp(-(fusion_enthalpies[0] / R) * (1/T - 1/fusion_temps[0]))
            x2 = np.exp(-(fusion_enthalpies[1] / R) * (1/T - 1/fusion_temps[1]))
            
            # No eutético: x1 + x2 = 1
            return x1 + x2 - 1.0
        
        try:
            T_eutectic = fsolve(objective, T_eutectic_guess)[0]
            x1_eutectic = np.exp(-(fusion_enthalpies[0] / R) * (1/T_eutectic - 1/fusion_temps[0]))
            x2_eutectic = 1.0 - x1_eutectic
            
            return {
                'type': 'eutectic_point',
                'temperature': T_eutectic,
                'composition': [x1_eutectic, x2_eutectic],
                'model': self.model_type
            }
        except:
            return {
                'type': 'eutectic_point',
                'error': 'Não foi possível calcular ponto eutético',
                'model': self.model_type
            }
    
    def generate_solubility_curve(self, T_range, solute_idx, solvent_composition,
                                  fusion_temp, fusion_enthalpy, n_points=50, **kwargs):
        '''
        Gerar curva de solubilidade vs temperatura
        
        Args:
            T_range: Tupla (T_min, T_max) em K
            solute_idx: Índice do componente sólido
            solvent_composition: Composição do solvente
            fusion_temp: Temperatura de fusão (K)
            fusion_enthalpy: Entalpia de fusão (J/mol)
            n_points: Número de pontos
            **kwargs: Parâmetros do modelo
        
        Returns:
            dict com curva de solubilidade
        '''
        T_data = np.linspace(T_range[0], min(T_range[1], fusion_temp), n_points)
        x_data = []
        
        for T in T_data:
            result = self.calculate_solubility(T, solute_idx, solvent_composition,
                                              fusion_temp, fusion_enthalpy, **kwargs)
            x_data.append(result['solubility'])
        
        return {
            'type': 'solubility_curve',
            'temperature': T_data.tolist(),
            'solubility': x_data,
            'model': self.model_type
        }
    
    def generate_phase_diagram_binary(self, fusion_temps, fusion_enthalpies,
                                     T_range=(200, 400), n_points=50, **kwargs):
        '''
        Gerar diagrama de fases binário sólido-líquido
        
        Args:
            fusion_temps: [T_fus1, T_fus2] (K)
            fusion_enthalpies: [ΔH_fus1, ΔH_fus2] (J/mol)
            T_range: (T_min, T_max) em K
            n_points: Número de pontos
            **kwargs: Parâmetros do modelo
        
        Returns:
            dict com diagrama de fases
        '''
        R = 8.314
        
        # Curva de liquidus do componente 1
        T_data_1 = np.linspace(T_range[0], fusion_temps[0], n_points//2)
        x1_liquidus_1 = []
        
        for T in T_data_1:
            x1 = np.exp(-(fusion_enthalpies[0] / R) * (1/T - 1/fusion_temps[0]))
            x1_liquidus_1.append(min(x1, 1.0))
        
        # Curva de liquidus do componente 2
        T_data_2 = np.linspace(T_range[0], fusion_temps[1], n_points//2)
        x2_liquidus_2 = []
        
        for T in T_data_2:
            x2 = np.exp(-(fusion_enthalpies[1] / R) * (1/T - 1/fusion_temps[1]))
            x2_liquidus_2.append(min(x2, 1.0))
        
        return {
            'type': 'binary_phase_diagram',
            'component1_curve': {
                'temperature': T_data_1.tolist(),
                'composition': x1_liquidus_1
            },
            'component2_curve': {
                'temperature': T_data_2.tolist(),
                'composition': [1-x2 for x2 in x2_liquidus_2]
            },
            'model': self.model_type
        }
