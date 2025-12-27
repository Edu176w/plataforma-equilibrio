"""
Component Database - Banco de dados de componentes químicos
Usa biblioteca thermo para propriedades termodinâmicas
"""

from thermo import ChemicalConstantsPackage, PRMIX, CEOSLiquid, CEOSGas, FlashPureVLS
from thermo.chemical import Chemical
from chemicals.identifiers import search_chemical
import json
import os


class ComponentDatabase:
    def __init__(self):
        self.cache = {}
        self._all_components = None
        self._translations = self._load_translations()
        self._name_index = {}  # ✅ Índice para busca rápida por nome
    
    def _load_translations(self):
        """Carregar traduções PT-BR"""
        try:
            trans_file = os.path.join('app', 'data', 'translations_pt.json')
            if os.path.exists(trans_file):
                with open(trans_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Tentar caminho alternativo
            trans_file = os.path.join('data', 'translations_pt.json')
            if os.path.exists(trans_file):
                with open(trans_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar traduções - {e}")
        
        return {}
    
    def _translate(self, name):
        """Traduzir nome para português (case-insensitive)"""
        if not name:
            return name
        
        # Primeiro tentar exato
        if name in self._translations:
            return self._translations[name]
        
        # Tentar case-insensitive
        for key, value in self._translations.items():
            if key.lower() == name.lower():
                return value
        
        # Tentar capitalizar primeira letra
        capitalized = name.capitalize()
        if capitalized in self._translations:
            return self._translations[capitalized]
        
        # Se não encontrou tradução, retornar original capitalizado
        return name.title()
    
    def search_component(self, identifier):
        """Buscar componente por nome, CAS, fórmula"""
        try:
            # Verificar cache primeiro
            if identifier in self.cache:
                return self.cache[identifier]
            
            # Buscar no thermo
            result = search_chemical(identifier)
            if result and result.CASs:
                chem = Chemical(result.CASs)
                self.cache[identifier] = chem
                return chem
            
            return None
        except Exception as e:
            print(f"Erro ao buscar componente '{identifier}': {e}")
            return None
    
    def get_component_properties(self, identifier):
        """Obter todas as propriedades de um componente"""
        chem = self.search_component(identifier)
        
        if not chem:
            raise ValueError(f"Componente '{identifier}' não encontrado")
        
        return {
            'name': self._translate(chem.name),
            'name_en': chem.name,
            'formula': chem.formula,
            'cas': chem.CAS,
            'MW': chem.MW,
            'Tb': chem.Tb,
            'Tm': chem.Tm,
            'Tc': chem.Tc,
            'Pc': chem.Pc,
            'Vc': chem.Vc,
            'omega': chem.omega,
            'dipole': chem.dipole,
            'Hfus': chem.Hfus,
            'UNIFAC_R': getattr(chem, 'UNIFAC_R', None),
            'UNIFAC_Q': getattr(chem, 'UNIFAC_Q', None)
        }
    
    # ✅ MÉTODO NOVO - NECESSÁRIO PARA ell_calculator.py e ai_ell.py
    def get_component_by_name(self, name: str) -> dict:
        """
        Buscar componente por nome (inglês ou português)
        Retorna dict com propriedades completas
        
        Args:
            name: Nome do componente (case-insensitive)
        
        Returns:
            dict com propriedades do componente
        
        Raises:
            ValueError: Se componente não encontrado
        """
        # Normalizar nome
        name_normalized = name.lower().strip()
        
        # Tentar buscar diretamente
        try:
            return self.get_component_properties(name)
        except:
            pass
        
        # Buscar na lista de todos os componentes
        all_comps = self.list_all_components()
        
        for comp in all_comps:
            # Comparar nome em inglês
            if comp.get('name_en', '').lower() == name_normalized:
                return comp
            
            # Comparar nome em português
            if comp.get('name', '').lower() == name_normalized:
                return comp
        
        # Se não encontrou, tentar busca fuzzy
        for comp in all_comps:
            name_en = comp.get('name_en', '').lower()
            name_pt = comp.get('name', '').lower()
            
            if name_normalized in name_en or name_normalized in name_pt:
                return comp
        
        # Último recurso: tentar buscar novamente no thermo
        try:
            result = search_chemical(name)
            if result and result.CASs:
                chem = Chemical(result.CASs)
                return {
                    'name': self._translate(chem.name),
                    'name_en': chem.name,
                    'formula': chem.formula,
                    'cas': chem.CAS,
                    'MW': chem.MW,
                    'Tb': chem.Tb,
                    'Tm': chem.Tm,
                    'Tc': chem.Tc,
                    'Pc': chem.Pc,
                    'Vc': chem.Vc,
                    'omega': chem.omega,
                    'dipole': chem.dipole,
                    'UNIFAC_R': getattr(chem, 'UNIFAC_R', None),
                    'UNIFAC_Q': getattr(chem, 'UNIFAC_Q', None)
                }
        except:
            pass
        
        # Se chegou aqui, não encontrou
        raise ValueError(f"Componente '{name}' não encontrado no banco de dados")
    
    def list_all_components(self):
        """Listar TODOS os componentes disponíveis"""
        if self._all_components:
            return self._all_components
        
        all_components = []
        
        # Lista MASSIVA de componentes importantes
        component_list = [
            # Água e isotópos
            'Water', 'Heavy water', 'Deuterium oxide',
            
            # Álcoois C1-C20
            'Methanol', 'Ethanol', 
            '1-Propanol', '2-Propanol', 'Isopropanol',
            '1-Butanol', '2-Butanol', 'Isobutanol', 'tert-Butanol',
            '1-Pentanol', '2-Pentanol', '3-Pentanol', 'Isopentanol', 'Neopentanol',
            '1-Hexanol', '2-Hexanol', '3-Hexanol',
            '1-Heptanol', '2-Heptanol', 
            '1-Octanol', '2-Octanol',
            '1-Nonanol', '1-Decanol',
            '1-Undecanol', '1-Dodecanol', 'Lauryl alcohol',
            '1-Tetradecanol', 'Myristyl alcohol',
            '1-Hexadecanol', 'Cetyl alcohol',
            '1-Octadecanol', 'Stearyl alcohol',
            '1-Eicosanol',
            
            # Glicóis e polióis
            'Ethylene glycol', 'Propylene glycol', '1,2-Propanediol',
            '1,3-Propanediol', '1,2-Butanediol', '1,3-Butanediol', '1,4-Butanediol',
            'Glycerol', 'Erythritol', 'Xylitol', 'Sorbitol',
            'Diethylene glycol', 'Triethylene glycol', 'Tetraethylene glycol',
            
            # Cetonas
            'Acetone', 'Methyl ethyl ketone', 'MEK',
            'Methyl propyl ketone', 'Methyl isobutyl ketone', 'MIBK',
            '2-Pentanone', '3-Pentanone',
            '2-Hexanone', '3-Hexanone',
            '2-Heptanone', '3-Heptanone', '4-Heptanone',
            '2-Octanone', '2-Nonanone', '2-Decanone',
            'Cyclohexanone', 'Cyclopentanone',
            'Acetophenone', 'Propiophenone', 'Benzophenone',
            
            # Aromáticos - Benzenos
            'Benzene', 'Toluene', 'Ethylbenzene', 
            'o-Xylene', 'm-Xylene', 'p-Xylene',
            'Propylbenzene', 'Isopropylbenzene', 'Cumene',
            'Butylbenzene', 'sec-Butylbenzene', 'tert-Butylbenzene',
            'Styrene', 'alpha-Methylstyrene',
            'Mesitylene', '1,2,3-Trimethylbenzene', '1,2,4-Trimethylbenzene', '1,3,5-Trimethylbenzene',
            
            # Aromáticos policíclicos
            'Naphthalene', '1-Methylnaphthalene', '2-Methylnaphthalene',
            'Anthracene', 'Phenanthrene', 'Pyrene',
            'Biphenyl', 'Diphenylmethane',
            'Fluorene', 'Acenaphthene',
            
            # Fenóis
            'Phenol', 'o-Cresol', 'm-Cresol', 'p-Cresol',
            '2,3-Xylenol', '2,4-Xylenol', '2,5-Xylenol', '2,6-Xylenol', '3,4-Xylenol', '3,5-Xylenol',
            'Catechol', 'Resorcinol', 'Hydroquinone',
            'Pyrogallol', 'Phloroglucinol',
            
            # Alcanos C1-C40
            'Methane', 'Ethane', 'Propane', 
            'Butane', 'Isobutane', '2-Methylpropane',
            'Pentane', 'Isopentane', 'Neopentane', '2-Methylbutane', '2,2-Dimethylpropane',
            'Hexane', '2-Methylpentane', '3-Methylpentane', '2,2-Dimethylbutane', '2,3-Dimethylbutane',
            'Heptane', '2-Methylhexane', '3-Methylhexane', '2,2-Dimethylpentane', '2,3-Dimethylpentane', '2,4-Dimethylpentane', '3,3-Dimethylpentane', '3-Ethylpentane',
            'Octane', '2-Methylheptane', '3-Methylheptane', '4-Methylheptane',
            'Nonane', '2-Methyloctane', '3-Methyloctane', '4-Methyloctane',
            'Decane', 'Undecane', 'Dodecane', 'Tridecane', 'Tetradecane', 'Pentadecane',
            'Hexadecane', 'Heptadecane', 'Octadecane', 'Nonadecane', 'Eicosane',
            'Heneicosane', 'Docosane', 'Tricosane', 'Tetracosane', 'Pentacosane',
            'Hexacosane', 'Heptacosane', 'Octacosane', 'Nonacosane', 'Triacontane',
            'Hentriacontane', 'Dotriacontane', 'Tritriacontane', 'Tetratriacontane', 'Pentatriacontane',
            'Hexatriacontane', 'Heptatriacontane', 'Octatriacontane', 'Nonatriacontane', 'Tetracontane',
            
            # Alcenos
            'Ethylene', 'Propylene', '1-Butene', '2-Butene', 'Isobutylene',
            '1-Pentene', '2-Pentene', '2-Methyl-1-butene', '2-Methyl-2-butene', '3-Methyl-1-butene',
            '1-Hexene', '2-Hexene', '3-Hexene',
            '1-Heptene', '1-Octene', '1-Nonene', '1-Decene',
            '1-Dodecene', '1-Tetradecene', '1-Hexadecene', '1-Octadecene',
            
            # Dienos
            '1,3-Butadiene', 'Isoprene', '1,4-Pentadiene', '1,5-Hexadiene',
            
            # Alcinos
            'Acetylene', 'Propyne', '1-Butyne', '2-Butyne',
            
            # Cicloalcanos
            'Cyclopropane', 'Cyclobutane', 'Cyclopentane', 'Cyclohexane', 'Cycloheptane', 'Cyclooctane',
            'Methylcyclopentane', 'Ethylcyclopentane',
            'Methylcyclohexane', 'Ethylcyclohexane',
            
            # Ácidos carboxílicos
            'Formic acid', 'Acetic acid', 'Propionic acid', 'Butyric acid', 'Isobutyric acid',
            'Valeric acid', 'Isovaleric acid', 'Caproic acid', 'Enanthic acid', 'Caprylic acid',
            'Pelargonic acid', 'Capric acid', 'Lauric acid', 'Myristic acid', 'Palmitic acid', 'Stearic acid',
            'Oleic acid', 'Linoleic acid', 'Linolenic acid',
            'Benzoic acid', 'Phenylacetic acid', 'Cinnamic acid',
            'Oxalic acid', 'Malonic acid', 'Succinic acid', 'Glutaric acid', 'Adipic acid',
            'Phthalic acid', 'Isophthalic acid', 'Terephthalic acid',
            
            # Ésteres
            'Methyl formate', 'Ethyl formate', 'Propyl formate', 'Butyl formate',
            'Methyl acetate', 'Ethyl acetate', 'Propyl acetate', 'Isopropyl acetate', 'Butyl acetate', 'Isobutyl acetate',
            'Methyl propionate', 'Ethyl propionate', 'Propyl propionate',
            'Methyl butyrate', 'Ethyl butyrate',
            'Dimethyl carbonate', 'Diethyl carbonate',
            'Dimethyl oxalate', 'Diethyl oxalate',
            'Dimethyl malonate', 'Diethyl malonate',
            'Dimethyl succinate', 'Diethyl succinate',
            'Dimethyl phthalate', 'Diethyl phthalate', 'Dibutyl phthalate',
            
            # Éteres
            'Dimethyl ether', 'Diethyl ether', 'Dipropyl ether', 'Diisopropyl ether', 'Dibutyl ether',
            'Methyl ethyl ether', 'Methyl propyl ether', 'Methyl isopropyl ether',
            'Methyl tert-butyl ether', 'MTBE', 'Ethyl tert-butyl ether', 'ETBE',
            'Tetrahydrofuran', 'THF', '2-Methyltetrahydrofuran',
            '1,4-Dioxane', '1,3-Dioxane', '1,3-Dioxolane',
            'Anisole', 'Phenetole',
            'Ethylene glycol dimethyl ether', 'Diethylene glycol dimethyl ether',
            
            # Aminas
            'Methylamine', 'Ethylamine', 'Propylamine', 'Isopropylamine', 'Butylamine', 'Isobutylamine',
            'Dimethylamine', 'Diethylamine', 'Dipropylamine', 'Diisopropylamine', 'Dibutylamine',
            'Trimethylamine', 'Triethylamine', 'Tripropylamine', 'Tributylamine',
            'Aniline', 'N-Methylaniline', 'N,N-Dimethylaniline',
            'o-Toluidine', 'm-Toluidine', 'p-Toluidine',
            'Benzylamine', 'Phenethylamine',
            'Pyridine', '2-Methylpyridine', '3-Methylpyridine', '4-Methylpyridine',
            '2,6-Lutidine', 'Piperidine', 'Pyrrolidine',
            'Morpholine', 'N-Methylmorpholine',
            
            # Halogenados
            'Chloromethane', 'Dichloromethane', 'Chloroform', 'Carbon tetrachloride',
            'Bromomethane', 'Dibromomethane', 'Bromoform',
            'Iodomethane', 'Diiodomethane',
            'Chloroethane', '1,1-Dichloroethane', '1,2-Dichloroethane', '1,1,1-Trichloroethane', '1,1,2-Trichloroethane',
            '1,1,1,2-Tetrachloroethane', '1,1,2,2-Tetrachloroethane', 'Pentachloroethane', 'Hexachloroethane',
            'Vinyl chloride', '1,1-Dichloroethylene', 'cis-1,2-Dichloroethylene', 'trans-1,2-Dichloroethylene',
            'Trichloroethylene', 'Tetrachloroethylene', 'Perchloroethylene',
            '1-Chloropropane', '2-Chloropropane', '1,2-Dichloropropane', '1,3-Dichloropropane',
            '1-Chlorobutane', '2-Chlorobutane', '1-Chloropentane', '1-Chlorohexane',
            'Chlorobenzene', 'o-Dichlorobenzene', 'm-Dichlorobenzene', 'p-Dichlorobenzene',
            '1,2,3-Trichlorobenzene', '1,2,4-Trichlorobenzene', '1,3,5-Trichlorobenzene',
            'Bromobenzene', 'Iodobenzene',
            'Benzyl chloride', 'Benzyl bromide',
            'Chlorotoluene', 'Bromotoluene',
            
            # Nitro compostos
            'Nitromethane', 'Nitroethane', '1-Nitropropane', '2-Nitropropane',
            'Nitrobenzene', 'o-Nitrotoluene', 'm-Nitrotoluene', 'p-Nitrotoluene',
            '2,4-Dinitrotoluene', '2,6-Dinitrotoluene',
            
            # Gases inorgânicos
            'Nitrogen', 'Oxygen', 'Hydrogen', 'Helium', 'Neon', 'Argon', 'Krypton', 'Xenon',
            'Carbon dioxide', 'Carbon monoxide',
            'Ammonia', 'Hydrogen chloride', 'Hydrogen bromide', 'Hydrogen iodide', 'Hydrogen fluoride',
            'Hydrogen sulfide', 'Sulfur dioxide', 'Sulfur trioxide',
            'Nitric oxide', 'Nitrogen dioxide', 'Nitrous oxide', 'Dinitrogen tetroxide',
            'Chlorine', 'Bromine', 'Fluorine', 'Iodine',
            
            # Outros solventes
            'Acetonitrile', 'Propionitrile', 'Butyronitrile',
            'Benzonitrile', 'Phenylacetonitrile',
            'Dimethylformamide', 'DMF', 'Diethylformamide',
            'Dimethylacetamide', 'DMAc',
            'N-Methyl-2-pyrrolidone', 'NMP',
            'Dimethyl sulfoxide', 'DMSO',
            'Sulfolane', 'Tetramethylene sulfone',
            'Formamide', 'N-Methylformamide',
            
            # Ácidos inorgânicos
            'Sulfuric acid', 'Nitric acid', 'Hydrochloric acid', 'Hydrobromic acid',
            'Phosphoric acid', 'Phosphorous acid',
            'Perchloric acid', 'Chloric acid',
            'Boric acid', 'Carbonic acid',
            
            # Bases inorgânicas
            'Sodium hydroxide', 'Potassium hydroxide', 'Calcium hydroxide',
            'Ammonium hydroxide',
            
            # Outros inorgânicos
            'Hydrogen peroxide', 'Sodium chloride', 'Potassium chloride',
            'Calcium chloride', 'Magnesium chloride',
            
            # Refrigerantes e fluidos
            'R-11', 'R-12', 'R-22', 'R-32', 'R-113', 'R-114', 'R-115', 'R-123', 'R-124', 'R-125',
            'R-134a', 'R-141b', 'R-142b', 'R-143a', 'R-152a',
            'R-218', 'R-227ea', 'R-236fa', 'R-245fa',
            'R-404A', 'R-407C', 'R-410A', 'R-507A',
        ]
        
        # Processar todos os componentes
        for name in component_list:
            try:
                result = search_chemical(name)
                if result and result.CASs:
                    chem = Chemical(result.CASs)
                    if chem.MW and chem.MW > 0:
                        comp_data = {
                            'name': self._translate(chem.name),
                            'name_en': chem.name,
                            'formula': chem.formula,
                            'cas': chem.CAS,
                            'MW': chem.MW,
                            'Tb': chem.Tb,
                            'Tm': chem.Tm,
                            'Tc': chem.Tc,
                            'Pc': chem.Pc,
                            'Vc': chem.Vc,
                            'omega': chem.omega,
                            'dipole': chem.dipole,
                            'UNIFAC_R': getattr(chem, 'UNIFAC_R', None),
                            'UNIFAC_Q': getattr(chem, 'UNIFAC_Q', None)
                        }
                        all_components.append(comp_data)
                        
                        # ✅ Construir índice para busca rápida
                        self._name_index[chem.name.lower()] = comp_data
                        self._name_index[self._translate(chem.name).lower()] = comp_data
            except Exception as e:
                # Silenciar erros de componentes individuais
                continue
        
        self._all_components = all_components
        print(f"✅ Carregados {len(all_components)} componentes no banco de dados")
        return all_components
    
    def list_common_components(self):
        """Listar apenas componentes mais comuns"""
        common_names = [
            'Water', 'Ethanol', 'Methanol', 'Acetone', 'Benzene', 'Toluene',
            'Hexane', 'Heptane', 'Octane', 'Acetic acid', 'Propanol',
            'Butanol', 'Chloroform', 'Ethyl acetate', 'Diethyl ether',
            'Tetrahydrofuran', 'Cyclohexane'
        ]
        
        components = []
        for name in common_names:
            try:
                props = self.get_component_properties(name)
                components.append(props)
            except:
                continue
        
        return components
    
    # ✅ MÉTODOS UTILITÁRIOS ADICIONAIS
    
    def clear_cache(self):
        """Limpar cache de componentes"""
        self.cache.clear()
        print("✅ Cache de componentes limpo")
    
    def get_cache_size(self):
        """Obter tamanho do cache"""
        return len(self.cache)
    
    def reload_database(self):
        """Recarregar banco de dados"""
        self._all_components = None
        self._name_index.clear()
        self.clear_cache()
        self.list_all_components()
        print("✅ Banco de dados recarregado")
