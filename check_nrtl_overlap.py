import json

# pares de interesse (nomes)
name_pairs = [
    ('methanol', 'water'),
    ('ethanol', 'water'),
    ('1-propanol', 'water'),
    ('2-propanol', 'water'),
    ('1-butanol', 'water'),
    ('acetone', 'water'),
    ('methyl ethyl ketone', 'water'),
    ('acetic acid', 'water'),
    ('formic acid', 'water'),
    ('hexane', 'benzene'),
    ('heptane', 'benzene'),
    ('octane', 'benzene'),
    ('hexane', 'toluene'),
    ('ethanol', 'hexane'),
    ('ethanol', 'heptane'),
    ('ethanol', 'octane'),
    ('methanol', 'hexane'),
    ('methanol', 'octane'),
    ('acetone', 'hexane'),
    ('acetone', 'heptane'),
    ('acetone', 'methanol'),
    ('acetone', 'ethanol'),
    ('chloroform', 'acetone'),
    ('chloroform', 'ethanol'),
    ('chloroform', 'methanol'),
    ('acetonitrile', 'water'),
    ('acetonitrile', 'benzene'),
    ('benzene', 'ethanol'),
    ('benzene', 'water'),
    ('toluene', 'water'),
]

# mapa simples nome -> CAS
name_to_cas = {
    'water': '7732-18-5',
    'methanol': '67-56-1',
    'ethanol': '64-17-5',
    '1-propanol': '71-23-8',
    '2-propanol': '67-63-0',
    '1-butanol': '71-36-3',
    'acetone': '67-64-1',
    'methyl ethyl ketone': '78-93-3',
    'acetic acid': '64-19-7',
    'formic acid': '64-18-6',
    'hexane': '110-54-3',
    'heptane': '142-82-5',
    'octane': '111-65-9',
    'benzene': '71-43-2',
    'toluene': '108-88-3',
    'chloroform': '67-66-3',
    'acetonitrile': '75-05-8',
}

print("="*80)
print("VERIFICANDO SE PARES DO nrtl_params.py EXISTEM EM elv_nrtl_params.json")
print("="*80)

try:
    with open("elv_nrtl_params.json", "r", encoding="utf-8") as f:
        elv = json.load(f)
except FileNotFoundError:
    print("❌ Arquivo elv_nrtl_params.json não encontrado na pasta atual.")
    raise SystemExit

found = []
missing = []

for n1, n2 in name_pairs:
    cas1 = name_to_cas.get(n1)
    cas2 = name_to_cas.get(n2)
    if not cas1 or not cas2:
        missing.append((n1, n2, "sem CAS mapeado"))
        continue

    k12 = f"{cas1}__{cas2}"
    k21 = f"{cas2}__{cas1}"

    if k12 in elv:
        found.append((n1, n2, k12))
    elif k21 in elv:
        found.append((n1, n2, k21))
    else:
        missing.append((n1, n2, "não encontrado"))

print()
print(f"✅ ENCONTRADOS NO elv_nrtl_params.json: {len(found)}")
for n1, n2, key in found:
    print(f"  • {n1} / {n2}  → chave: {key}")

print()
print(f"❌ NÃO ENCONTRADOS: {len(missing)}")
for n1, n2, motivo in missing:
    print(f"  • {n1} / {n2}  → {motivo}")
print("="*80)
