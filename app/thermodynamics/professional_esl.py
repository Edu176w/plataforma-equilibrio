import numpy as np
from thermo import Chemical, ChemicalConstantsPackage
from scipy.optimize import fsolve, brentq
from chemicals import normalize

class ProfessionalESLCalculator:
    '''Calculadora profissional de ESL usando biblioteca thermo'''
    
    def __init__(self, components_names, model='ideal'):
        '''
        Inicializar calculadora ESL
        
        Args:
            components_names: Lista de nomes dos componentes
            model: 'ideal', 'NRTL', 'UNIQUAC'
        '''
        self.components_names = components_names
        self.model_type = model
        self.n_components = len(components_names)
        
        # Importar componentes
        self.chemicals = [Chemical(name) for name in components_names]
        
        # Constante dos gases
        self.R = 8.314  # J/(mol·K)
    
    def calculate_solubility(self, T, solute_idx=0, P=101325):
        '''
        Calcular solubilidade de sólido em líquido
        
        Args:
            T: Temperatura (K)
            solute_idx: Índice do componente sólido
            P: Pressão (Pa)
        
        Returns:
            dict com solubilidade
        '''
        solute = self.chemicals[solute_idx]
        
        # Obter propriedades de fusão
        Tm = solute.Tm  # Temperatura de fusão
        Hm = solute.Hfus if hasattr(solute, 'Hfus') else None
        
        if not Tm or not Hm:
            return {
                'error': 'Propriedades de fusão não disponíveis',
                'solute': solute.name
            }
        
        # Equação de solubilidade ideal
        # ln(x_soluto) = -(ΔHfus/R) * (1/T - 1/Tm)
        
        if T >= Tm:
            # Acima da temperatura de fusão, totalmente solúvel
            x_solute = 1.0
        else:
            ln_x = -(Hm / self.R) * (1/T - 1/Tm)
            x_solute = np.exp(ln_x)
            
            # Limitar entre 0 e 1
            x_solute = min(max(x_solute, 0.0), 1.0)
        
        return {
            'type': 'solubility',
            'T': T,
            'P': P,
            'solute': solute.name,
            'solubility': x_solute,
            'Tm': Tm,
            'Hfus': Hm,
            'model': self.model_type
        }
    
    def calculate_eutectic_point(self):
        '''
        Calcular ponto eutético para sistema binário
        
        Returns:
            dict com ponto eutético
        '''
        if self.n_components != 2:
            raise ValueError('Ponto eutético apenas para sistemas binários')
        
        comp1 = self.chemicals[0]
        comp2 = self.chemicals[1]
        
        Tm1 = comp1.Tm
        Tm2 = comp2.Tm
        Hm1 = comp1.Hfus if hasattr(comp1, 'Hfus') else None
        Hm2 = comp2.Hfus if hasattr(comp2, 'Hfus') else None
        
        if not all([Tm1, Tm2, Hm1, Hm2]):
            return {
                'error': 'Propriedades de fusão incompletas'
            }
        
        # Estimativa inicial
        T_eut_guess = min(Tm1, Tm2) * 0.85
        
        def equations(T):
            # No eutético: x1 + x2 = 1
            ln_x1 = -(Hm1 / self.R) * (1/T - 1/Tm1)
            ln_x2 = -(Hm2 / self.R) * (1/T - 1/Tm2)
            
            x1 = np.exp(ln_x1)
            x2 = np.exp(ln_x2)
            
            return x1 + x2 - 1.0
        
        try:
            T_eut = fsolve(equations, T_eut_guess)[0]
            
            # Calcular composições
            ln_x1 = -(Hm1 / self.R) * (1/T_eut - 1/Tm1)
            x1 = np.exp(ln_x1)
            x2 = 1.0 - x1
            
            return {
                'type': 'eutectic_point',
                'T': T_eut,
                'composition': [x1, x2],
                'components': self.components_names,
                'model': self.model_type
            }
        
        except:
            return {
                'error': 'Não foi possível calcular ponto eutético'
            }
    
    def generate_solubility_curve(self, T_range, solute_idx=0, n_points=50):
        '''
        Gerar curva de solubilidade vs temperatura
        
        Args:
            T_range: (T_min, T_max) em K
            solute_idx: Índice do soluto
            n_points: Número de pontos
        
        Returns:
            dict com curva
        '''
        solute = self.chemicals[solute_idx]
        Tm = solute.Tm
        
        T_max = min(T_range[1], Tm)
        T_values = np.linspace(T_range[0], T_max, n_points)
        
        x_values = []
        
        for T in T_values:
            result = self.calculate_solubility(T, solute_idx)
            x_values.append(result['solubility'])
        
        return {
            'type': 'solubility_curve',
            'T': list(T_values),
            'solubility': x_values,
            'solute': solute.name,
            'model': self.model_type
        }
    
    def generate_phase_diagram(self, T_range=(200, 400), n_points=50):
        '''
        Gerar diagrama de fases binário SLE
        
        Args:
            T_range: (T_min, T_max) em K
            n_points: Número de pontos
        
        Returns:
            dict com diagrama
        '''
        if self.n_components != 2:
            raise ValueError('Diagrama de fases apenas para sistemas binários')
        
        comp1 = self.chemicals[0]
        comp2 = self.chemicals[1]
        
        Tm1 = comp1.Tm
        Tm2 = comp2.Tm
        Hm1 = comp1.Hfus if hasattr(comp1, 'Hfus') else 10000
        Hm2 = comp2.Hfus if hasattr(comp2, 'Hfus') else 10000
        
        # Curva de liquidus do componente 1
        T1_values = np.linspace(T_range[0], Tm1, n_points//2)
        x1_liquidus = []
        
        for T in T1_values:
            if T < Tm1:
                ln_x = -(Hm1 / self.R) * (1/T - 1/Tm1)
                x1 = min(np.exp(ln_x), 1.0)
            else:
                x1 = 1.0
            x1_liquidus.append(x1)
        
        # Curva de liquidus do componente 2
        T2_values = np.linspace(T_range[0], Tm2, n_points//2)
        x2_liquidus = []
        
        for T in T2_values:
            if T < Tm2:
                ln_x = -(Hm2 / self.R) * (1/T - 1/Tm2)
                x2 = min(np.exp(ln_x), 1.0)
            else:
                x2 = 1.0
            x2_liquidus.append(1.0 - x2)  # Converter para x1
        
        return {
            'type': 'phase_diagram',
            'component1_curve': {
                'T': list(T1_values),
                'x': x1_liquidus
            },
            'component2_curve': {
                'T': list(T2_values),
                'x': x2_liquidus
            },
            'components': self.components_names,
            'model': self.model_type
        }
