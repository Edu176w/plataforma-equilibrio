from app.utils.component_database import ComponentDatabase
from thermo.interaction_parameters import IPDB

db = ComponentDatabase()
components = db.list_all_components()
cas_ideais = {c['cas']: c['name_en'] for c in components}

# ---------- NRTL (ChemSep) ----------
name_nrtl = 'ChemSep NRTL'
table_nrtl = IPDB.tables[name_nrtl]

cas_nrtl = set()
for key in table_nrtl.keys():
    parts = key.split()
    cas_nrtl.update(parts)

inter_nrtl = cas_ideais.keys() & cas_nrtl

print("NRTL - componentes IDEAL com parâmetros:", len(inter_nrtl))
for cas in sorted(inter_nrtl):
    print("NRTL_OK", cas, cas_ideais[cas])

# ---------- UNIQUAC ----------
from uniquac_params import UNIQUAC_PARAMS, UNIQUAC_R_Q

cas_ideais = {c['cas']: c['name_en'] for c in components}

cas_uniquac = set()
for (cas1, cas2) in UNIQUAC_PARAMS.keys():
    cas_uniquac.add(cas1)
    cas_uniquac.add(cas2)
cas_uniquac.update(UNIQUAC_R_Q.keys())

inter_uniquac = cas_ideais.keys() & cas_uniquac
print("UNIQUAC - componentes IDEAL com parâmetros:", len(inter_uniquac))
for cas in sorted(inter_uniquac):
    print("UNIQUAC_OK", cas, cas_ideais[cas])

# ---------- UNIFAC ----------
from unifac_params import UNIFAC_GROUPS

cas_unifac = set(UNIFAC_GROUPS.keys())

inter_unifac = cas_ideais.keys() & cas_unifac
print("UNIFAC - componentes IDEAL com parâmetros:", len(inter_unifac))
for cas in sorted(inter_unifac):
    print("UNIFAC_OK", cas, cas_ideais[cas])
