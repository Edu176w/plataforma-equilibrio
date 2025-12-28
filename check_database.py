from app.utils.component_database import ComponentDatabase

db = ComponentDatabase()
comps = db.list_all_components()

print(f'\nTotal de componentes no banco: {len(comps)}\n')
print('='*70)
print(f'{"Nome em Português":30s} -> Nome em Inglês')
print('='*70)

for c in comps[:35]:
    name = c['name']
    name_en = c.get('name_en', 'N/A')
    print(f'{name:30s} -> {name_en}')
