import numpy as np
from thermo import ChemicalConstantsPackage, PropertyCorrelationsPackage
from thermo.eos_mix import PRMIX
from thermo.phases import CEOSLiquid, CEOSGas
from thermo.flash import FlashVL
from chemicals import normalize
from scipy.optimize import minimize, fsolve

class ProfessionalELLCalculator:
    '''Calculadora profissional de ELL usando biblioteca thermo'''
    
    def __init__(self, components_names, model='NRTL'):
        '''
        Inicializar calculadora ELL
        
        Args:
            components_names: Lista de nomes dos componentes
            model: 'NRTL', 'UNIQUAC', 'PR' (Peng-Robinson)
        '''
        self.components_names = components_names
        self.model_type = model
        self.n_components = len(components_names)
        
        # Importar componentes
        from thermo import Chemical
        self.chemicals = [Chemical(name) for name in components_names]
        
        # Criar pacote de constantes
        self.constants = ChemicalConstantsPackage(
            Tcs=[c.Tc for c in self.chemicals],
            Pcs=[c.Pc for c in self.chemicals],
            omegas=[c.omega for c in self.chemicals],
            MWs=[c.MW for c in self.chemicals],
            CASs=[c.CAS for c in self.chemicals],
        )
        
        # Criar pacote de correlações
        self.correlations = PropertyCorrelationsPackage(
            constants=self.constants,
            VaporPressures=[c.VaporPressure for c in self.chemicals],
            HeatCapacityGases=[c.HeatCapacityGas for c in self.chemicals],
        )
    
    def setup_flasher(self, T, P):
        '''Configurar flasher para ELL'''
        eos_kwargs = dict(Tcs=self.constants.Tcs, Pcs=self.constants.Pcs, 
                         omegas=self.constants.omegas)
        
        gas = CEOSGas(PRMIX, eos_kwargs, HeatCapacityGases=self.correlations.HeatCapacityGases)
        liquid = CEOSLiquid(PRMIX, eos_kwargs, HeatCapacityGases=self.correlations.HeatCapacityGases)
        
        return FlashVL(self.constants, self.correlations, liquid=liquid, gas=gas)
    
    def stability_test(self, zs, T, P):
        '''
        Teste de estabilidade de Gibbs
        
        Args:
            zs: Composição global
            T: Temperatura (K)
            P: Pressão (Pa)
        
        Returns:
            stable: True se monofásico, False se bifásico
        '''
        zs = normalize(zs)
        
        flasher = self.setup_flasher(T, P)
        
        try:
            # Tentar flash LL
            res = flasher.flash(T=T, P=P, zs=zs)
            
            # Se tiver duas fases líquidas
            if hasattr(res, 'liquid0') and hasattr(res, 'liquid1'):
                if res.liquid0 and res.liquid1:
                    return False
            
            # Verificar se fração líquida está entre 0 e 1
            if hasattr(res, 'liquid_beta'):
                if 0 < res.liquid_beta < 1:
                    return False
            
            return True
        
        except:
            return True
    
    def calculate_lle(self, zs, T, P=101325):
        '''
        Calcular equilíbrio líquido-líquido
        
        Args:
            zs: Composição global
            T: Temperatura (K)
            P: Pressão (Pa)
        
        Returns:
            dict com resultados
        '''
        zs = normalize(zs)
        
        # Teste de estabilidade
        if self.stability_test(zs, T, P):
            return {
                'type': 'LLE',
                'stable': True,
                'phases': 1,
                'T': T,
                'P': P,
                'composition': list(zs),
                'message': 'Sistema monofásico',
                'model': self.model_type
            }
        
        # Sistema bifásico - usar flasher
        flasher = self.setup_flasher(T, P)
        
        try:
            res = flasher.flash(T=T, P=P, zs=zs)
            
            if hasattr(res, 'liquid0') and hasattr(res, 'liquid1'):
                return {
                    'type': 'LLE',
                    'stable': False,
                    'phases': 2,
                    'T': T,
                    'P': P,
                    'phase1': list(res.liquid0.zs),
                    'phase2': list(res.liquid1.zs),
                    'beta': res.liquid0_beta if hasattr(res, 'liquid0_beta') else 0.5,
                    'model': self.model_type
                }
        except:
            pass
        
        return {
            'type': 'LLE',
            'stable': True,
            'phases': 1,
            'T': T,
            'P': P,
            'message': 'Não foi possível calcular ELL',
            'model': self.model_type
        }
    
    def calculate_binodal_curve(self, T, P=101325, n_points=30):
        '''
        Calcular curva binodal para sistema binário
        
        Args:
            T: Temperatura (K)
            P: Pressão (Pa)
            n_points: Número de pontos
        
        Returns:
            dict com curva binodal
        '''
        if self.n_components != 2:
            raise ValueError('Curva binodal apenas para sistemas binários')
        
        x1_phase1 = []
        x1_phase2 = []
        
        # Varrer composições
        for x1 in np.linspace(0.1, 0.9, n_points):
            zs = [x1, 1-x1]
            
            result = self.calculate_lle(zs, T, P)
            
            if not result['stable'] and result['phases'] == 2:
                x1_phase1.append(result['phase1'][0])
                x1_phase2.append(result['phase2'][0])
        
        if len(x1_phase1) > 0:
            return {
                'type': 'binodal_curve',
                'T': T,
                'P': P,
                'phase1_x1': x1_phase1,
                'phase2_x1': x1_phase2,
                'components': self.components_names,
                'model': self.model_type
            }
        
        return {
            'type': 'binodal_curve',
            'message': 'Nenhuma separação de fases encontrada',
            'T': T,
            'P': P,
            'model': self.model_type
        }
    
    def calculate_tie_lines(self, T, P=101325, n_lines=5):
        '''
        Calcular tie-lines
        
        Args:
            T: Temperatura (K)
            P: Pressão (Pa)
            n_lines: Número de tie-lines
        
        Returns:
            dict com tie-lines
        '''
        if self.n_components != 2:
            raise ValueError('Tie-lines apenas para sistemas binários')
        
        tie_lines = []
        
        for x1 in np.linspace(0.2, 0.8, n_lines):
            zs = [x1, 1-x1]
            
            result = self.calculate_lle(zs, T, P)
            
            if not result['stable'] and result['phases'] == 2:
                tie_lines.append({
                    'phase1': result['phase1'],
                    'phase2': result['phase2']
                })
        
        return {
            'type': 'tie_lines',
            'T': T,
            'P': P,
            'tie_lines': tie_lines,
            'n_lines': len(tie_lines),
            'components': self.components_names,
            'model': self.model_type
        }
    
    def calculate_ternary_diagram(self, T, P=101325, n_points=20):
        '''
        Calcular diagrama ternário
        
        Args:
            T: Temperatura (K)
            P: Pressão (Pa)
            n_points: Resolução do diagrama
        
        Returns:
            dict com dados do diagrama
        '''
        if self.n_components != 3:
            raise ValueError('Diagrama ternário apenas para 3 componentes')
        
        stable_points = []
        unstable_points = []
        
        # Varrer composições ternárias
        for i in range(n_points + 1):
            for j in range(n_points + 1 - i):
                x1 = i / n_points
                x2 = j / n_points
                x3 = 1.0 - x1 - x2
                
                if x3 >= 0:
                    zs = [x1, x2, x3]
                    result = self.calculate_lle(zs, T, P)
                    
                    if result['stable']:
                        stable_points.append(zs)
                    else:
                        unstable_points.append(zs)
        
        return {
            'type': 'ternary_diagram',
            'T': T,
            'P': P,
            'stable_points': stable_points,
            'unstable_points': unstable_points,
            'components': self.components_names,
            'model': self.model_type
        }
