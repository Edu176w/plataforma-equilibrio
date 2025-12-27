import json
from pathlib import Path

"""
Gera o módulo elv_nrtl_params.py combinando:
- literatura (seu nrtl_params.py)
- biblioteca (elv_nrtl_params_filtered.json ou elv_nrtl_params.json)
"""

# tenta usar o filtrado; se não existir, usa o completo
base_path = Path(".")
filtered_path = base_path / "elv_nrtl_params_filtered.json"
full_path = base_path / "elv_nrtl_params.json"

if filtered_path.exists():
    json_path = filtered_path
else:
    json_path = full_path

with open(json_path, "r", encoding="utf-8") as f:
    elv_filtered = json.load(f)

header = '''"""
Parâmetros NRTL para ELV

- NRTL_LITERATURE_PARAMS: pares binários de literatura (didáticos)
- NRTL_LIBRARY_PARAMS   : pares adicionais da base ChemSep/thermo

Convenção:
  tau_ij = a_ij / T  (a_ij em Kelvin)
"""
# =======================
# PARTE 1 - LITERATURA
# =======================

NRTL_LITERATURE_PARAMS = {
    # Álcool-Água
    ('methanol', 'water'): {'a12': -39.56, 'a21': 196.24, 'alpha': 0.30},
    ('ethanol', 'water'): {'a12': -0.80, 'a21': 0.50, 'alpha': 0.30},
    ('1-propanol', 'water'): {'a12': 179.53, 'a21': 518.36, 'alpha': 0.30},
    ('2-propanol', 'water'): {'a12': 101.30, 'a21': 388.20, 'alpha': 0.30},
    ('1-butanol', 'water'): {'a12': 342.72, 'a21': 756.61, 'alpha': 0.30},
    ('water', 'tce'): {'a12': 5.98775, 'a21': 3.60977, 'alpha': 0.2485},
    ('tce', 'acetone'): {'a12': -0.19920, 'a21': -0.20102, 'alpha': 0.30},

    # Cetona-Água
    ('acetone', 'water'): {'a12': 330.99, 'a21': -100.71, 'alpha': 0.30},
    ('methyl ethyl ketone', 'water'): {'a12': 444.04, 'a21': 13.52, 'alpha': 0.30},

    # Ácido-Água
    ('acetic acid', 'water'): {'a12': -54.87, 'a21': 190.36, 'alpha': 0.30},
    ('formic acid', 'water'): {'a12': -120.35, 'a21': 98.24, 'alpha': 0.30},

    # Alcanos-Aromáticos
    ('hexane', 'benzene'): {'a12': 0.0, 'a21': 0.0, 'alpha': 0.30},
    ('heptane', 'benzene'): {'a12': 0.0, 'a21': 0.0, 'alpha': 0.30},
    ('octane', 'benzene'): {'a12': -19.27, 'a21': 6.81, 'alpha': 0.30},
    ('hexane', 'toluene'): {'a12': 0.0, 'a21': 0.0, 'alpha': 0.30},

    # Álcool-Alcano
    ('ethanol', 'hexane'): {'a12': 626.42, 'a21': 282.67, 'alpha': 0.30},
    ('ethanol', 'heptane'): {'a12': 651.30, 'a21': 291.89, 'alpha': 0.30},
    ('ethanol', 'octane'): {'a12': -123.57, 'a21': 1354.92, 'alpha': 0.30},
    ('methanol', 'hexane'): {'a12': 1075.20, 'a21': 196.38, 'alpha': 0.30},
    ('methanol', 'octane'): {'a12': 379.31, 'a21': -108.42, 'alpha': 0.30},

    # Cetona-Alcano
    ('acetone', 'hexane'): {'a12': 122.34, 'a21': 136.53, 'alpha': 0.30},
    ('acetone', 'heptane'): {'a12': 134.56, 'a21': 145.23, 'alpha': 0.30},

    # Cetona-Álcool
    ('acetone', 'methanol'): {'a12': -39.76, 'a21': 237.69, 'alpha': 0.30},
    ('acetone', 'ethanol'): {'a12': 47.92, 'a21': 176.05, 'alpha': 0.30},

    # Clorados
    ('chloroform', 'acetone'): {'a12': -171.71, 'a21': 93.93, 'alpha': 0.30},
    ('chloroform', 'ethanol'): {'a12': -120.45, 'a21': 350.71, 'alpha': 0.30},
    ('chloroform', 'methanol'): {'a12': -58.87, 'a21': 301.24, 'alpha': 0.30},

    # Nitrilas
    ('acetonitrile', 'water'): {'a12': 116.21, 'a21': 398.79, 'alpha': 0.30},
    ('acetonitrile', 'benzene'): {'a12': -40.70, 'a21': 299.79, 'alpha': 0.30},

    # Benzeno
    ('benzene', 'ethanol'): {'a12': 471.08, 'a21': 38.28, 'alpha': 0.30},
    ('benzene', 'water'): {'a12': 1271.32, 'a21': 595.42, 'alpha': 0.20},
    ('toluene', 'water'): {'a12': 1346.59, 'a21': 623.27, 'alpha': 0.20},

    # Adicionais
    ('acetone', 'benzene'): {'a12': -25.45, 'a21': 89.32, 'alpha': 0.30},
    ('methanol', 'benzene'): {'a12': 523.71, 'a21': 151.83, 'alpha': 0.30},
    ('ethanol', 'benzene'): {'a12': 471.08, 'a21': 38.28, 'alpha': 0.30},

    # Ternários
    ('methanol', 'ethanol'): {'a12': -48.92, 'a21': 75.36, 'alpha': 0.30},
    ('benzene', 'toluene'): {'a12': 0.0, 'a21': 0.0, 'alpha': 0.30},
    ('chloroform', 'benzene'): {'a12': -12.34, 'a21': 45.67, 'alpha': 0.30},
    ('compa', 'compb'): {'a12': 1000.0, 'a21': -1000.0, 'alpha': 0.30},
}

# =======================
# PARTE 2 - BIBLIOTECA
# =======================

# Parâmetros em termos de CAS; a12 = bij, a21 = bij por falta de informação de assimetria
NRTL_LIBRARY_PARAMS = {
'''

lines = []
for key, val in sorted(elv_filtered.items()):
    cas1 = val.get("cas1")
    cas2 = val.get("cas2")
    bij = float(val.get("bij", 0.0))
    alpha = float(val.get("alphaij", 0.3))
    name = val.get("name", "")
    lines.append(
        f"    ('{cas1}', '{cas2}'): {{'a12': {bij:.6g}, 'a21': {bij:.6g}, 'alpha': {alpha:.4g}}},  # {name}\n"
    )

body = "".join(lines) + "}\n\n"

footer = '''
def _norm(x: str) -> str:
    return x.strip().lower()

def get_nrtl_elv_params(comp1: str, comp2: str):
    """
    Obter parâmetros NRTL para ELV.

    Prioridade:
      1) NRTL_LITERATURE_PARAMS (nomes comuns)
      2) NRTL_LIBRARY_PARAMS (CAS-CAS)
    """
    c1 = _norm(comp1)
    c2 = _norm(comp2)

    # 1) literatura (nomes)
    if (c1, c2) in NRTL_LITERATURE_PARAMS:
        return NRTL_LITERATURE_PARAMS[(c1, c2)]
    if (c2, c1) in NRTL_LITERATURE_PARAMS:
        p = NRTL_LITERATURE_PARAMS[(c2, c1)]
        return {'a12': p['a21'], 'a21': p['a12'], 'alpha': p['alpha']}

    # 2) biblioteca (CAS)
    if (comp1, comp2) in NRTL_LIBRARY_PARAMS:
        return NRTL_LIBRARY_PARAMS[(comp1, comp2)]
    if (comp2, comp1) in NRTL_LIBRARY_PARAMS:
        p = NRTL_LIBRARY_PARAMS[(comp2, comp1)]
        return {'a12': p['a21'], 'a21': p['a12'], 'alpha': p['alpha']}

    return None

def get_available_nrtl_literature_components():
    comps = set()
    for c1, c2 in NRTL_LITERATURE_PARAMS.keys():
        comps.add(c1)
        comps.add(c2)
    return sorted(comps)

def get_available_nrtl_library_pairs():
    return sorted(NRTL_LIBRARY_PARAMS.keys())
'''

module_code = header + body + footer

with open("elv_nrtl_params.py", "w", encoding="utf-8") as f:
    f.write(module_code)

print("✅ Módulo gerado: elv_nrtl_params.py usando", json_path.name)
