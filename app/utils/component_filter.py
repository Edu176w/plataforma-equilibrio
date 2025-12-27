from thermo.chemical import Chemical
from thermo.interaction_parameters import IPDB
import itertools

class ComponentFilter:
    def __init__(self):
        self.component_db = None
        self._nrtl_available = set()
        self._uniquac_available = set()
        self._unifac_available = set()
        self._load_available_components()
    
    def _load_available_components(self):
        """Identificar quais componentes têm parâmetros para cada modelo"""
        from app.utils.component_database import ComponentDatabase
        
        self.component_db = ComponentDatabase()
        all_comps = self.component_db.list_all_components()
        
        for comp in all_comps:
            cas = comp.get('cas')
            name_en = comp.get('name_en', comp.get('name'))
            
            # UNIFAC: verificar se tem grupos definidos
            if comp.get('UNIFAC_R') is not None and comp.get('UNIFAC_Q') is not None:
                self._unifac_available.add(name_en)
            
            # Alternativa: tentar carregar da thermo
            try:
                chem = Chemical(name_en)
                if hasattr(chem, 'UNIFAC_groups') and chem.UNIFAC_groups:
                    self._unifac_available.add(name_en)
                
                # NRTL/UNIQUAC: verificar se Chemical tem parâmetros
                if hasattr(chem, 'UNIFAC_R') and chem.UNIFAC_R:
                    self._nrtl_available.add(name_en)
                    self._uniquac_available.add(name_en)
            except:
                pass
        
        # Adicionar componentes conhecidos que funcionam
        known_unifac = {
            'water', 'ethanol', 'methanol', 'acetone', 'benzene', 'toluene',
            'hexane', 'heptane', 'octane', 'propanol', '1-propanol', '2-propanol',
            'butanol', '1-butanol', 'acetonitrile', 'chloroform', 'ethyl acetate',
            'cyclohexane', 'dichloromethane', 'acetic acid', 'formic acid'
        }
        self._unifac_available.update(known_unifac)
        
        # NRTL/UNIQUAC: usar mesmos componentes do UNIFAC (fallback)
        if len(self._nrtl_available) < 10:
            self._nrtl_available = known_unifac.copy()
        if len(self._uniquac_available) < 10:
            self._uniquac_available = known_unifac.copy()
        
        print(f'[ComponentFilter] UNIFAC: {len(self._unifac_available)} componentes')
        print(f'[ComponentFilter] NRTL: {len(self._nrtl_available)} componentes')
        print(f'[ComponentFilter] UNIQUAC: {len(self._uniquac_available)} componentes')
    
    def filter_components_by_model(self, model):
        """
        Retornar lista de componentes disponíveis para o modelo
        
        Parameters:
        -----------
        model : str
            'IDEAL', 'NRTL', 'UNIQUAC', ou 'UNIFAC'
        
        Returns:
        --------
        list : Lista de componentes filtrados
        """
        if not self.component_db:
            from app.utils.component_database import ComponentDatabase
            self.component_db = ComponentDatabase()
        
        all_comps = self.component_db.list_all_components()
        
        if model.upper() == 'IDEAL':
            # Modelo ideal funciona para todos
            return all_comps
        
        elif model.upper() == 'UNIFAC':
            # Filtrar por componentes com grupos UNIFAC
            return [c for c in all_comps 
                    if c.get('name_en', c.get('name')) in self._unifac_available]
        
        elif model.upper() == 'NRTL':
            # Filtrar por componentes disponíveis no NRTL
            return [c for c in all_comps 
                    if c.get('name_en', c.get('name')) in self._nrtl_available]
        
        elif model.upper() == 'UNIQUAC':
            # Filtrar por componentes disponíveis no UNIQUAC
            return [c for c in all_comps 
                    if c.get('name_en', c.get('name')) in self._uniquac_available]
        
        return all_comps
    
    def get_component_count(self, model):
        """Retornar número de componentes disponíveis para o modelo"""
        return len(self.filter_components_by_model(model))

