# analisar_componentes_modelos.py
from app.utils.component_database import ComponentDatabase

db = ComponentDatabase()
components = db.list_all_components()

print("TOTAL_COMPONENTES", len(components))

# salvar CASs e nomes para reuso
cas_list = []
for c in components:
    cas_list.append((c['cas'], c['name_en']))

# salvar em arquivo texto ou JSON se quiser inspecionar
with open('componentes_ideais.txt', 'w', encoding='utf-8') as f:
    for cas, name_en in cas_list:
        f.write(f"{cas}\t{name_en}\n")

print("EXEMPLO_5", cas_list[:5])
