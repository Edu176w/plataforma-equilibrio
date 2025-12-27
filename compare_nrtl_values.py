import json

# valores de literatura (seu nrtl_params.py)
LIT = {
    ('methanol','water'): {'a12': -39.56, 'a21': 196.24, 'alpha': 0.30},
    ('ethanol','water'): {'a12': -0.80, 'a21': 0.50, 'alpha': 0.30},
    ('1-butanol','water'): {'a12': 342.72, 'a21': 756.61, 'alpha': 0.30},
    ('acetone','water'): {'a12': 330.99, 'a21': -100.71, 'alpha': 0.30},
    ('methyl ethyl ketone','water'): {'a12': 444.04, 'a21': 13.52, 'alpha': 0.30},
    ('ethanol','hexane'): {'a12': 626.42, 'a21': 282.67, 'alpha': 0.30},
    ('ethanol','heptane'): {'a12': 651.30, 'a21': 291.89, 'alpha': 0.30},
    ('ethanol','octane'): {'a12': -123.57, 'a21': 1354.92, 'alpha': 0.30},
    ('methanol','hexane'): {'a12': 1075.20, 'a21': 196.38, 'alpha': 0.30},
    ('methanol','octane'): {'a12': 379.31, 'a21': -108.42, 'alpha': 0.30},
    ('acetone','methanol'): {'a12': -39.76, 'a21': 237.69, 'alpha': 0.30},
    ('acetone','ethanol'): {'a12': 47.92, 'a21': 176.05, 'alpha': 0.30},
    ('chloroform','acetone'): {'a12': -171.71, 'a21': 93.93, 'alpha': 0.30},
    ('chloroform','ethanol'): {'a12': -120.45, 'a21': 350.71, 'alpha': 0.30},
    ('chloroform','methanol'): {'a12': -58.87, 'a21': 301.24, 'alpha': 0.30},
    ('benzene','ethanol'): {'a12': 471.08, 'a21': 38.28, 'alpha': 0.30},
}

name_to_cas = {
    'water': '7732-18-5',
    'methanol': '67-56-1',
    'ethanol': '64-17-5',
    '1-butanol': '71-36-3',
    'acetone': '67-64-1',
    'methyl ethyl ketone': '78-93-3',
    'hexane': '110-54-3',
    'heptane': '142-82-5',
    'octane': '111-65-9',
    'benzene': '71-43-2',
    'toluene': '108-88-3',
    'chloroform': '67-66-3',
}

print("="*80)
print("COMPARAÇÃO NRTL: nrtl_params.py  vs  elv_nrtl_params.json")
print("="*80)

with open("elv_nrtl_params.json", "r", encoding="utf-8") as f:
    elv = json.load(f)

for (n1, n2), lit in LIT.items():
    cas1 = name_to_cas[n1]
    cas2 = name_to_cas[n2]
    k12 = f"{cas1}__{cas2}"
    k21 = f"{cas2}__{cas1}"
    rec = elv.get(k12) or elv.get(k21)

    if not rec:
        print(f"\n{n1} / {n2}: ❌ não existe em elv_nrtl_params.json")
        continue

    bij = rec["bij"]
    alphaij = rec["alphaij"]

    print("\n" + "-"*80)
    print(f"{n1} / {n2}")
    print("-"*80)
    print("Literatura (nrtl_params.py):")
    print(f"  a12  = {lit['a12']:10.2f} K")
    print(f"  a21  = {lit['a21']:10.2f} K")
    print(f"  alfa = {lit['alpha']:10.4f}")
    print("\nBase extraída (elv_nrtl_params.json):")
    print(f"  bij  = {bij:10.2f} K")
    print(f"  alfa = {alphaij:10.4f}")
    print("\nDiferenças:")
    print(f"  |a12 - bij| = {abs(lit['a12'] - bij):10.2f} K")
    print(f"  |alfa_lit - alfa_ext| = {abs(lit['alpha'] - alphaij):10.4f}")

print("\n" + "="*80)
