from thermo.chemical import Chemical
import json
import os

class ComponentManager:
    def __init__(self):
        self.cache = {}
        self.common_components = [
            'water', 'ethanol', 'methanol', 'acetone', 'benzene', 
            'toluene', 'hexane', 'heptane', 'octane', 'acetonitrile',
            'chloroform', 'propanol', '1-propanol', '2-propanol',
            'butanol', '1-butanol', '2-butanol', 'pentane',
            'cyclohexane', 'methylcyclohexane', 'ethylbenzene',
            'diethylamine', 'triethylamine', 'acetic acid', 'formic acid'
        ]
    
    def get_all_components(self):
        '''Obter lista de todos os componentes disponiveis'''
        components = []
        
        for name in self.common_components:
            try:
                chem = Chemical(name)
                
                component = {
                    'name': chem.name if hasattr(chem, 'name') else name,
                    'name_en': name,
                    'formula': chem.formula if hasattr(chem, 'formula') else '',
                    'cas': chem.CAS if hasattr(chem, 'CAS') else '',
                    'mw': round(chem.MW, 2) if hasattr(chem, 'MW') else 0,
                    'tb': round(chem.Tb - 273.15, 2) if hasattr(chem, 'Tb') and chem.Tb else None,
                    'tc': round(chem.Tc - 273.15, 2) if hasattr(chem, 'Tc') and chem.Tc else None,
                    'pc': round(chem.Pc / 1000, 2) if hasattr(chem, 'Pc') and chem.Pc else None
                }
                
                components.append(component)
                self.cache[chem.CAS] = component
            
            except Exception as e:
                print(f'Erro ao carregar {name}: {e}')
                continue
        
        return components
    
    def get_component_by_cas(self, cas):
        '''Obter componente por CAS'''
        if cas in self.cache:
            return self.cache[cas]
        
        try:
            chem = Chemical(cas)
            
            component = {
                'name': chem.name if hasattr(chem, 'name') else cas,
                'name_en': chem.name if hasattr(chem, 'name') else cas,
                'formula': chem.formula if hasattr(chem, 'formula') else '',
                'cas': chem.CAS if hasattr(chem, 'CAS') else cas,
                'mw': round(chem.MW, 2) if hasattr(chem, 'MW') else 0,
                'tb': round(chem.Tb - 273.15, 2) if hasattr(chem, 'Tb') and chem.Tb else None,
                'tc': round(chem.Tc - 273.15, 2) if hasattr(chem, 'Tc') and chem.Tc else None,
                'pc': round(chem.Pc / 1000, 2) if hasattr(chem, 'Pc') and chem.Pc else None
            }
            
            self.cache[cas] = component
            return component
        
        except Exception as e:
            print(f'Erro ao carregar CAS {cas}: {e}')
            return None
    
    def search_components(self, query):
        '''Buscar componentes por nome, formula ou CAS'''
        all_components = self.get_all_components()
        query_lower = query.lower()
        
        results = [
            comp for comp in all_components
            if query_lower in comp['name'].lower() or
               query_lower in comp['name_en'].lower() or
               query_lower in comp['formula'].lower() or
               query_lower in comp['cas']
        ]
        
        return results
