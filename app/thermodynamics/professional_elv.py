import numpy as np
from thermo import ChemicalConstantsPackage, PropertyCorrelationsPackage
from thermo.eos_mix import PRMIX
from thermo.phases import CEOSLiquid, CEOSGas
from thermo.flash import FlashVL
from chemicals import normalize

class ProfessionalELVCalculator:
    '''Calculadora profissional de ELV usando biblioteca thermo'''
    
    def __init__(self, components_names, model='PR'):
        '''
        Inicializar calculadora
        
        Args:
            components_names: Lista de nomes dos componentes
            model: 'PR' (Peng-Robinson), 'ideal'
        '''
        self.components_names = components_names
        self.model_type = model
        self.n_components = len(components_names)
        
        # Importar componentes usando thermo
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
    
    def setup_flash(self, T, P, zs):
        '''
        Configurar flash para cálculo de equilíbrio
        
        Args:
            T: Temperatura (K)
            P: Pressão (Pa)
            zs: Composições globais
        
        Returns:
            FlashVL object
        '''
        # Equação de estado Peng-Robinson
        eos_kwargs = dict(Tcs=self.constants.Tcs, Pcs=self.constants.Pcs, 
                        omegas=self.constants.omegas)
        
        gas = CEOSGas(PRMIX, eos_kwargs, HeatCapacityGases=self.correlations.HeatCapacityGases)
        liquid = CEOSLiquid(PRMIX, eos_kwargs, HeatCapacityGases=self.correlations.HeatCapacityGases)
        
        flasher = FlashVL(self.constants, self.correlations, liquid=liquid, gas=gas)
        
        return flasher
    
    def calculate_bubble_point_T(self, P, xs):
        '''
        Calcular ponto de bolha (dada P, calcular T)
        
        Args:
            P: Pressão (Pa)
            xs: Composição do líquido
        
        Returns:
            dict com T, ys, e propriedades
        '''
        xs = normalize(xs)
        
        flasher = self.setup_flash(T=300, P=P, zs=xs)
        
        # Buscar temperatura de bolha
        res = flasher.flash(P=P, VF=0, zs=xs)
        
        return {
            'T': res.T,
            'P': P,
            'xs': list(xs),
            'ys': list(res.gas.zs) if res.gas else list(xs),
            'phase': res.phase,
            'quality': res.gas_beta if hasattr(res, 'gas_beta') else 0.0,
            'model': self.model_type
        }
    
    def calculate_bubble_point_P(self, T, xs):
        '''
        Calcular ponto de bolha (dada T, calcular P)
        
        Args:
            T: Temperatura (K)
            xs: Composição do líquido
        
        Returns:
            dict com P, ys, e propriedades
        '''
        xs = normalize(xs)
        
        flasher = self.setup_flash(T=T, P=101325, zs=xs)
        
        # Buscar pressão de bolha
        res = flasher.flash(T=T, VF=0, zs=xs)
        
        return {
            'T': T,
            'P': res.P,
            'xs': list(xs),
            'ys': list(res.gas.zs) if res.gas else list(xs),
            'phase': res.phase,
            'quality': res.gas_beta if hasattr(res, 'gas_beta') else 0.0,
            'model': self.model_type
        }
    
    def calculate_dew_point_T(self, P, ys):
        '''
        Calcular ponto de orvalho (dada P, calcular T)
        
        Args:
            P: Pressão (Pa)
            ys: Composição do vapor
        
        Returns:
            dict com T, xs, e propriedades
        '''
        ys = normalize(ys)
        
        flasher = self.setup_flash(T=300, P=P, zs=ys)
        
        # Buscar temperatura de orvalho
        res = flasher.flash(P=P, VF=1, zs=ys)
        
        return {
            'T': res.T,
            'P': P,
            'xs': list(res.liquid0.zs) if res.liquid0 else list(ys),
            'ys': list(ys),
            'phase': res.phase,
            'quality': res.gas_beta if hasattr(res, 'gas_beta') else 1.0,
            'model': self.model_type
        }
    
    def calculate_flash(self, T, P, zs):
        '''
        Calcular flash isotérmico
        
        Args:
            T: Temperatura (K)
            P: Pressão (Pa)
            zs: Composição global
        
        Returns:
            dict com resultados completos
        '''
        zs = normalize(zs)
        
        flasher = self.setup_flash(T=T, P=P, zs=zs)
        
        # Flash
        res = flasher.flash(T=T, P=P, zs=zs)
        
        return {
            'T': res.T,
            'P': res.P,
            'zs': list(zs),
            'xs': list(res.liquid0.zs) if res.liquid0 else list(zs),
            'ys': list(res.gas.zs) if res.gas else list(zs),
            'beta': res.gas_beta if hasattr(res, 'gas_beta') else 0.0,
            'phase': res.phase,
            'model': self.model_type
        }
    
    def generate_Txy_diagram(self, P, n_points=50):
        '''
        Gerar diagrama T-xy para sistema binário
        
        Args:
            P: Pressão (Pa)
            n_points: Número de pontos
        
        Returns:
            dict com arrays de T, x, y
        '''
        if self.n_components != 2:
            raise ValueError('Diagrama T-xy apenas para sistemas binários')
        
        x1_values = np.linspace(0.01, 0.99, n_points)
        T_bubble = []
        T_dew = []
        y1_values = []
        
        for x1 in x1_values:
            xs = [x1, 1-x1]
            
            try:
                # Ponto de bolha
                result_bubble = self.calculate_bubble_point_T(P, xs)
                T_bubble.append(result_bubble['T'])
                y1_values.append(result_bubble['ys'][0])
                
                # Ponto de orvalho
                ys = [x1, 1-x1]
                result_dew = self.calculate_dew_point_T(P, ys)
                T_dew.append(result_dew['T'])
            
            except:
                T_bubble.append(None)
                T_dew.append(None)
                y1_values.append(None)
        
        return {
            'type': 'Txy',
            'P': P,
            'x': list(x1_values),
            'y': y1_values,
            'T_bubble': T_bubble,
            'T_dew': T_dew,
            'components': self.components_names,
            'model': self.model_type
        }
    
    def generate_Pxy_diagram(self, T, n_points=50):
        '''
        Gerar diagrama P-xy para sistema binário
        
        Args:
            T: Temperatura (K)
            n_points: Número de pontos
        
        Returns:
            dict com arrays de P, x, y
        '''
        if self.n_components != 2:
            raise ValueError('Diagrama P-xy apenas para sistemas binários')
        
        x1_values = np.linspace(0.01, 0.99, n_points)
        P_bubble = []
        y1_values = []
        
        for x1 in x1_values:
            xs = [x1, 1-x1]
            
            try:
                result = self.calculate_bubble_point_P(T, xs)
                P_bubble.append(result['P'])
                y1_values.append(result['ys'][0])
            except:
                P_bubble.append(None)
                y1_values.append(None)
        
        return {
            'type': 'Pxy',
            'T': T,
            'x': list(x1_values),
            'y': y1_values,
            'P_bubble': P_bubble,
            'components': self.components_names,
            'model': self.model_type
        }
