from app.utils.component_database import ComponentDatabase
from app.data.uniquac_params import UNIQUAC_R_Q, COMPONENT_TRANSLATIONS

db = ComponentDatabase()
all_comps = db.list_all_components()

# Criar dicionário de nomes do banco
db_names = {}
for c in all_comps:
    name_en = c.get('name_en', c['name']).lower()
    db_names[name_en] = c['name']

print('\n' + '='*80)
print('VERIFICAÇÃO DE MAPEAMENTO UNIQUAC -> BANCO DE DADOS')
print('='*80)

found = []
missing = []

for comp_uniquac in sorted(UNIQUAC_R_Q.keys()):
    if comp_uniquac == 'ethanol/carbon tetrachloride':
        continue
    
    comp_lower = comp_uniquac.lower()
    traduzido = COMPONENT_TRANSLATIONS.get(comp_uniquac, comp_uniquac.title())
    
    if comp_lower in db_names:
        print(f'✅ {comp_uniquac:30s} -> {db_names[comp_lower]:30s} (encontrado)')
        found.append(comp_uniquac)
    else:
        print(f'❌ {comp_uniquac:30s} -> {traduzido:30s} (NÃO ENCONTRADO)')
        missing.append((comp_uniquac, traduzido))

print('='*80)
print(f'\n📊 RESUMO:')
print(f'   Encontrados no banco: {len(found)}')
print(f'   Faltando no banco: {len(missing)}')

if missing:
    print(f'\n❌ Componentes UNIQUAC sem correspondência no banco (esses precisam ser adicionados):')
    print('-'*80)
    for comp_en, comp_pt in missing:
        print(f'   {comp_en:30s} -> Tradução: {comp_pt}')
