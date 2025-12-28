from app.utils.component_database import ComponentDatabase
from app.data.uniquac_params import UNIQUAC_R_Q

db = ComponentDatabase()
all_comps = db.list_all_components()

# Mapear aliases
NAME_ALIASES = {
    '2-propanol': 'isopropanol',
    'n-heptane': 'heptane',
    'n-hexane': 'hexane',
    'n-octane': 'octane',
}

# Componentes com r e q definidos
uniquac_components = set()
for comp in UNIQUAC_R_Q.keys():
    if comp != 'ethanol/carbon tetrachloride':
        comp_lower = comp.lower()
        mapped_name = NAME_ALIASES.get(comp_lower, comp_lower)
        uniquac_components.add(mapped_name)

print(f'\n📋 UNIQUAC componentes mapeados ({len(uniquac_components)}):')
print('='*70)
for comp in sorted(uniquac_components):
    print(f'  {comp}')

# Filtrar do banco
filtered = []
found_names = []

for comp in all_comps:
    name_en = comp.get('name_en', comp['name']).lower()
    if name_en in uniquac_components:
        filtered.append(comp)
        found_names.append(name_en)

print(f'\n✅ ENCONTRADOS NO BANCO ({len(filtered)}):')
print('='*70)
for name in sorted(found_names):
    print(f'  {name}')

# Ver quais faltam
missing = uniquac_components - set(found_names)
print(f'\n❌ FALTANDO NO BANCO ({len(missing)}):')
print('='*70)
for name in sorted(missing):
    print(f'  {name}')
