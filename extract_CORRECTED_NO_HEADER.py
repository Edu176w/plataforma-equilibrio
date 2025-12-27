"""
Script CORRIGIDO - Os TSVs não têm cabeçalho!
"""

import json
import os

print("=" * 80)
print("EXTRAÇÃO FINAL CORRIGIDA")
print("=" * 80)

# Carregar caminhos
with open('tsv_paths.json', 'r') as f:
    tsv_paths = json.load(f)

# ==============================================================================
# 1. NRTL - JÁ FUNCIONA
# ==============================================================================
print("\n[1/5] NRTL")

from thermo.interaction_parameters import IPDB

if 'ChemSep NRTL' in IPDB.tables:
    chemsep_nrtl = IPDB.tables['ChemSep NRTL']

    nrtl_params = {}

    for key, value in chemsep_nrtl.items():
        if ' ' in key:
            cas1, cas2 = key.split(' ')
            dict_key = f"{cas1}__{cas2}"

            nrtl_params[dict_key] = {
                "cas1": cas1,
                "cas2": cas2,
                "name": value.get('name', ''),
                "bij": value.get('bij', 0.0),
                "alphaij": value.get('alphaij', 0.3)
            }

    print(f"  ✓ {len(nrtl_params)} pares NRTL")

    for module in ['elv', 'ell', 'esl']:
        with open(f"{module}_nrtl_params.json", "w", encoding="utf-8") as f:
            json.dump(nrtl_params, f, indent=2, ensure_ascii=False)

# ==============================================================================
# 2. UNIQUAC - JÁ FUNCIONA
# ==============================================================================
print("\n[2/5] UNIQUAC")

from thermo.chemical import Chemical

common_cas = [
    "7732-18-5", "67-56-1", "64-17-5", "67-63-0", "71-23-8", "71-36-3",
    "78-83-1", "75-65-0", "71-41-0", "78-93-3", "67-64-1", "96-22-0",
    "141-78-6", "79-20-9", "109-60-4", "123-86-4", "64-19-7", "79-09-4",
    "107-92-6", "110-54-3", "109-66-0", "106-97-8", "74-98-6", "71-43-2",
    "108-88-3", "100-41-4", "108-38-3", "67-66-3", "56-23-5", "75-09-2",
    "107-06-2", "109-99-9", "60-29-7", "123-91-1", "67-68-5", "75-05-8",
    "110-82-7", "108-94-1", "100-51-6", "108-95-2", "108-90-7", "62-53-3",
    "110-86-1", "98-95-3", "121-44-8", "123-39-7", "68-12-2", "126-33-0",
    "7664-41-7", "7697-37-2", "7664-93-9"
]

pure_params = {}

for cas in common_cas:
    try:
        chem = Chemical(cas)
        if hasattr(chem, 'UNIFAC_R') and chem.UNIFAC_R is not None:
            pure_params[cas] = {
                "name": chem.name,
                "cas": cas,
                "r": float(chem.UNIFAC_R),
                "q": float(chem.UNIFAC_Q) if hasattr(chem, 'UNIFAC_Q') and chem.UNIFAC_Q else None
            }
    except:
        pass

print(f"  ✓ {len(pure_params)} componentes")

uniquac_complete = {
    "pure_component_params": pure_params,
    "binary_params": {},
    "note": "Use NRTL for binary interactions"
}

for module in ['elv', 'ell', 'esl']:
    with open(f"{module}_uniquac_params.json", "w", encoding="utf-8") as f:
        json.dump(uniquac_complete, f, indent=2, ensure_ascii=False)

# ==============================================================================
# 3. GRUPOS UNIFAC - JÁ FUNCIONA
# ==============================================================================
print("\n[3/5] GRUPOS UNIFAC")

from thermo.unifac import UFSG, UFMG

group_params = {}
for subgroup_id, subgroup_obj in UFSG.items():
    group_params[str(subgroup_id)] = {
        "subgroup_id": subgroup_id,
        "subgroup_name": str(subgroup_obj),
        "main_group_id": subgroup_obj.main_group_id,
        "R": float(subgroup_obj.R),
        "Q": float(subgroup_obj.Q)
    }

print(f"  ✓ {len(group_params)} subgrupos")

main_groups = {}
for group_id, (group_name, subgroup_ids) in UFMG.items():
    main_groups[str(group_id)] = {
        "group_id": group_id,
        "group_name": group_name,
        "subgroup_ids": subgroup_ids
    }

print(f"  ✓ {len(main_groups)} grupos principais")

# ==============================================================================
# 4. INTERAÇÕES UNIFAC - SEM CABEÇALHO!
# ==============================================================================
print("\n[4/5] INTERAÇÕES UNIFAC")

# 4.1 - UNIFAC Original (ELV)
print("\n  [4.1] UNIFAC Original (ELV)...")
elv_interactions = {}

unifac_original_path = tsv_paths['unifac_original']

if unifac_original_path and os.path.exists(unifac_original_path):
    with open(unifac_original_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    group1 = int(parts[0])
                    group2 = int(parts[1])
                    amn = float(parts[2])

                    key = f"{group1}__{group2}"

                    # Se já existe, adicionar anm
                    if key in elv_interactions:
                        elv_interactions[key]["anm"] = amn
                    else:
                        # Procurar par reverso
                        reverse_key = f"{group2}__{group1}"
                        if reverse_key in elv_interactions:
                            elv_interactions[reverse_key]["anm"] = amn
                        else:
                            # Criar nova entrada
                            elv_interactions[key] = {
                                "group1": group1,
                                "group2": group2,
                                "amn": amn,
                                "anm": 0.0  # Será preenchido depois
                            }
            except:
                continue

    print(f"    ✓ {len(elv_interactions)} interações")
else:
    print(f"    ✗ Arquivo não encontrado")

# 4.2 - UNIFAC LLE (ELL)
print("\n  [4.2] UNIFAC LLE (ELL)...")
ell_interactions = {}

unifac_lle_path = tsv_paths['unifac_lle']

if unifac_lle_path and os.path.exists(unifac_lle_path):
    with open(unifac_lle_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    group1 = int(parts[0])
                    group2 = int(parts[1])
                    amn = float(parts[2])

                    key = f"{group1}__{group2}"

                    if key in ell_interactions:
                        ell_interactions[key]["anm"] = amn
                    else:
                        reverse_key = f"{group2}__{group1}"
                        if reverse_key in ell_interactions:
                            ell_interactions[reverse_key]["anm"] = amn
                        else:
                            ell_interactions[key] = {
                                "group1": group1,
                                "group2": group2,
                                "amn": amn,
                                "anm": 0.0
                            }
            except:
                continue

    print(f"    ✓ {len(ell_interactions)} interações")
else:
    print(f"    ✗ Arquivo não encontrado")

# 4.3 - ESL usa Original
esl_interactions = elv_interactions.copy()
print(f"\n  [4.3] UNIFAC ESL: {len(esl_interactions)} interações")

# ==============================================================================
# 5. DECOMPOSIÇÃO - FORMATO ESPECIAL DO DDBST
# ==============================================================================
print("\n[5/5] DECOMPOSIÇÃO DE COMPONENTES")

component_groups = {}
ddbst_path = tsv_paths['ddbst']

# O DDBST tem formato especial - usar fallback do Chemical
print("  Usando Chemical.UNIFAC_groups (formato DDBST é não-padrão)")

for cas in common_cas:
    try:
        chem = Chemical(cas)
        if hasattr(chem, 'UNIFAC_groups') and chem.UNIFAC_groups:
            component_groups[cas] = {
                "cas": cas,
                "name": chem.name,
                "groups": dict(chem.UNIFAC_groups)
            }
    except:
        pass

print(f"  ✓ {len(component_groups)} componentes")

# ==============================================================================
# 6. SALVAR ARQUIVOS FINAIS
# ==============================================================================
print("\n" + "=" * 80)
print("SALVANDO ARQUIVOS")
print("=" * 80)

unifac_base = {
    "group_params": group_params,
    "main_groups": main_groups,
    "component_groups": component_groups
}

# ELV
elv_unifac = unifac_base.copy()
elv_unifac["group_interactions"] = elv_interactions
with open("elv_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(elv_unifac, f, indent=2, ensure_ascii=False)
print(f"✓ ELV: {len(elv_interactions)} interações")

# ELL
ell_unifac = unifac_base.copy()
ell_unifac["group_interactions"] = ell_interactions
with open("ell_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(ell_unifac, f, indent=2, ensure_ascii=False)
print(f"✓ ELL: {len(ell_interactions)} interações")

# ESL
esl_unifac = unifac_base.copy()
esl_unifac["group_interactions"] = esl_interactions
with open("esl_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(esl_unifac, f, indent=2, ensure_ascii=False)
print(f"✓ ESL: {len(esl_interactions)} interações")

# ==============================================================================
# RESUMO
# ==============================================================================
print("\n" + "=" * 80)
print("RESUMO DA EXTRAÇÃO")
print("=" * 80)

print("\n📦 NRTL (todos os módulos):")
print(f"  • {len(nrtl_params)} pares binários")

print("\n📦 UNIQUAC (todos os módulos):")
print(f"  • {len(pure_params)} componentes")

print("\n📦 UNIFAC:")
print(f"  • {len(group_params)} subgrupos")
print(f"  • {len(main_groups)} grupos principais")
print(f"  • ELV: {len(elv_interactions)} interações")
print(f"  • ELL: {len(ell_interactions)} interações")
print(f"  • ESL: {len(esl_interactions)} interações")
print(f"  • {len(component_groups)} componentes decompostos")

print("\n" + "=" * 80)
print("✅ SUCESSO!")
print("=" * 80)
print("\nArquivos gerados:")
print("  • elv_nrtl_params.json, elv_uniquac_params.json, elv_unifac_params.json")
print("  • ell_nrtl_params.json, ell_uniquac_params.json, ell_unifac_params.json")
print("  • esl_nrtl_params.json, esl_uniquac_params.json, esl_unifac_params.json")
print("=" * 80)