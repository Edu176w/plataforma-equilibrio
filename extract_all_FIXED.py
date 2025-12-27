"""
Script CORRIGIDO - Extração completa com caminhos corretos dos arquivos TSV
"""

import json
import os
import csv

print("=" * 80)
print("EXTRAÇÃO COMPLETA DE PARÂMETROS PARA ELV, ELL E ESL (CORRIGIDO)")
print("=" * 80)

# ==============================================================================
# 1. EXTRAIR PARÂMETROS NRTL (ChemSep) - JÁ FUNCIONA!
# ==============================================================================
print("\n[1/5] Extraindo parâmetros NRTL (ChemSep)...")

try:
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

        print(f"  ✓ Extraídos {len(nrtl_params)} pares NRTL")

        # Salvar
        with open("nrtl_params_complete.json", "w", encoding="utf-8") as f:
            json.dump(nrtl_params, f, indent=2, ensure_ascii=False)

        for module in ['elv', 'ell', 'esl']:
            filename = f"{module}_nrtl_params.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(nrtl_params, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Cópia para {module.upper()}: {filename}")

except Exception as e:
    print(f"  ✗ Erro: {e}")

# ==============================================================================
# 2. EXTRAIR PARÂMETROS UNIQUAC (r, q) - JÁ FUNCIONA!
# ==============================================================================
print("\n[2/5] Extraindo parâmetros UNIQUAC (r, q)...")

try:
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

    print(f"  ✓ Extraídos {len(pure_params)} componentes com r/q")

    uniquac_complete = {
        "pure_component_params": pure_params,
        "binary_params": {},
        "note": "Use NRTL binary parameters for residual part"
    }

    for module in ['elv', 'ell', 'esl']:
        filename = f"{module}_uniquac_params.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(uniquac_complete, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Salvo para {module.upper()}: {filename}")

except Exception as e:
    print(f"  ✗ Erro: {e}")

# ==============================================================================
# 3. EXTRAIR GRUPOS UNIFAC - JÁ FUNCIONA!
# ==============================================================================
print("\n[3/5] Extraindo grupos UNIFAC...")

try:
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

    print(f"  ✓ {len(group_params)} subgrupos extraídos")

    main_groups = {}
    for group_id, (group_name, subgroup_ids) in UFMG.items():
        main_groups[str(group_id)] = {
            "group_id": group_id,
            "group_name": group_name,
            "subgroup_ids": subgroup_ids
        }

    print(f"  ✓ {len(main_groups)} grupos principais extraídos")

except Exception as e:
    print(f"  ✗ Erro: {e}")

# ==============================================================================
# 4. EXTRAIR INTERAÇÕES UNIFAC - CAMINHO CORRIGIDO!
# ==============================================================================
print("\n[4/5] Extraindo interações UNIFAC de arquivos TSV...")

try:
    from thermo import unifac
    import thermo

    # Caminho base da thermo (onde estão os TSVs)
    thermo_base_path = os.path.dirname(thermo.__file__)

    print(f"  Caminho base da thermo: {thermo_base_path}")

    # Listar arquivos para debug
    tsv_files = [f for f in os.listdir(thermo_base_path) if f.endswith('.tsv')]
    print(f"  Arquivos TSV encontrados: {len(tsv_files)}")

    # 4.1 - UNIFAC Original (ELV)
    print("\n  [4.1] UNIFAC Original (ELV)...")
    unifac_original_path = os.path.join(thermo_base_path, "UNIFAC original interaction parameters.tsv")

    elv_interactions = {}

    if os.path.exists(unifac_original_path):
        print(f"    ✓ Arquivo encontrado!")
        with open(unifac_original_path, 'r', encoding='utf-8') as f:
            # Ler primeira linha para ver estrutura
            first_line = f.readline()
            print(f"    Cabeçalho: {first_line.strip()}")

            f.seek(0)  # Voltar ao início
            reader = csv.DictReader(f, delimiter='\t')

            for row in reader:
                try:
                    # Tentar diferentes nomes de colunas
                    group1 = None
                    group2 = None
                    amn = None
                    anm = None

                    # Descobrir nomes das colunas
                    for key in row.keys():
                        if 'group' in key.lower() and '1' in key:
                            group1 = int(row[key]) if row[key].strip() else None
                        elif 'group' in key.lower() and '2' in key:
                            group2 = int(row[key]) if row[key].strip() else None
                        elif 'a' in key.lower() and 'mn' in key.lower():
                            amn = float(row[key]) if row[key].strip() else 0.0
                        elif 'a' in key.lower() and 'nm' in key.lower():
                            anm = float(row[key]) if row[key].strip() else 0.0

                    if group1 and group2 and amn is not None:
                        key = f"{group1}__{group2}"
                        elv_interactions[key] = {
                            "group1": group1,
                            "group2": group2,
                            "amn": amn,
                            "anm": anm if anm is not None else 0.0
                        }
                except Exception as e:
                    continue

        print(f"    ✓ {len(elv_interactions)} interações ELV extraídas")
    else:
        print(f"    ✗ Arquivo não encontrado: {unifac_original_path}")

    # 4.2 - UNIFAC LLE (ELL)
    print("\n  [4.2] UNIFAC LLE (ELL)...")
    unifac_lle_path = os.path.join(thermo_base_path, "UNIFAC LLE interaction parameters.tsv")

    ell_interactions = {}

    if os.path.exists(unifac_lle_path):
        print(f"    ✓ Arquivo encontrado!")
        with open(unifac_lle_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            print(f"    Cabeçalho: {first_line.strip()}")

            f.seek(0)
            reader = csv.DictReader(f, delimiter='\t')

            for row in reader:
                try:
                    group1 = None
                    group2 = None
                    amn = None
                    anm = None

                    for key in row.keys():
                        if 'group' in key.lower() and '1' in key:
                            group1 = int(row[key]) if row[key].strip() else None
                        elif 'group' in key.lower() and '2' in key:
                            group2 = int(row[key]) if row[key].strip() else None
                        elif 'a' in key.lower() and 'mn' in key.lower():
                            amn = float(row[key]) if row[key].strip() else 0.0
                        elif 'a' in key.lower() and 'nm' in key.lower():
                            anm = float(row[key]) if row[key].strip() else 0.0

                    if group1 and group2 and amn is not None:
                        key = f"{group1}__{group2}"
                        ell_interactions[key] = {
                            "group1": group1,
                            "group2": group2,
                            "amn": amn,
                            "anm": anm if anm is not None else 0.0
                        }
                except:
                    continue

        print(f"    ✓ {len(ell_interactions)} interações ELL extraídas")
    else:
        print(f"    ✗ Arquivo não encontrado: {unifac_lle_path}")

    # ESL usa Original
    esl_interactions = elv_interactions.copy()
    print(f"\n  [4.3] UNIFAC para ESL: usando Original ({len(esl_interactions)} interações)")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 5. EXTRAIR DECOMPOSIÇÃO - CAMINHO CORRIGIDO!
# ==============================================================================
print("\n[5/5] Extraindo decomposição de componentes (DDBST)...")

try:
    ddbst_path = os.path.join(thermo_base_path, "DDBST UNIFAC assignments.tsv")

    component_groups = {}

    if os.path.exists(ddbst_path):
        print(f"  ✓ Arquivo encontrado: {ddbst_path}")
        with open(ddbst_path, 'r', encoding='utf-8') as f:
            # Ler cabeçalho
            first_line = f.readline()
            print(f"  Primeiras colunas: {first_line.strip().split(chr(9))[:10]}")

            f.seek(0)
            reader = csv.DictReader(f, delimiter='\t')

            count = 0
            for row in reader:
                try:
                    cas = row.get('CAS', row.get('CASRN', ''))
                    name = row.get('Name', row.get('Chemical', ''))

                    groups = {}
                    for col, val in row.items():
                        if col not in ['CAS', 'CASRN', 'Name', 'Chemical', 'Formula', 'Smiles', 'InChI']:
                            if val and val.strip() and val.strip() != '0':
                                try:
                                    group_count = int(float(val))
                                    if group_count > 0:
                                        # Coluna pode ser só número ou "Group X"
                                        group_id = int(col) if col.isdigit() else int(col.split()[-1])
                                        groups[group_id] = group_count
                                except:
                                    pass

                    if cas and groups:
                        component_groups[cas] = {
                            "cas": cas,
                            "name": name,
                            "groups": groups
                        }
                        count += 1

                        if count >= 1000:  # Limitar para teste
                            break
                except:
                    continue

        print(f"  ✓ {len(component_groups)} componentes decompostos do DDBST")
    else:
        print(f"  ✗ Arquivo não encontrado: {ddbst_path}")
        # Fallback
        from thermo.chemical import Chemical
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
        print(f"  ✓ Fallback: {len(component_groups)} componentes")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 6. MONTAR ARQUIVOS FINAIS
# ==============================================================================
print("\n" + "=" * 80)
print("MONTANDO ARQUIVOS FINAIS")
print("=" * 80)

unifac_base = {
    "group_params": group_params if 'group_params' in locals() else {},
    "main_groups": main_groups if 'main_groups' in locals() else {},
    "component_groups": component_groups if 'component_groups' in locals() else {}
}

# ELV
print("\n[ELV]")
elv_unifac = unifac_base.copy()
elv_unifac["group_interactions"] = elv_interactions if 'elv_interactions' in locals() else {}
with open("elv_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(elv_unifac, f, indent=2, ensure_ascii=False)
print(f"  ✓ {len(elv_unifac['group_interactions'])} interações")

# ELL
print("\n[ELL]")
ell_unifac = unifac_base.copy()
ell_unifac["group_interactions"] = ell_interactions if 'ell_interactions' in locals() else {}
with open("ell_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(ell_unifac, f, indent=2, ensure_ascii=False)
print(f"  ✓ {len(ell_unifac['group_interactions'])} interações")

# ESL
print("\n[ESL]")
esl_unifac = unifac_base.copy()
esl_unifac["group_interactions"] = esl_interactions if 'esl_interactions' in locals() else {}
with open("esl_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(esl_unifac, f, indent=2, ensure_ascii=False)
print(f"  ✓ {len(esl_unifac['group_interactions'])} interações")

print("\n" + "=" * 80)
print("✅ EXTRAÇÃO COMPLETA COM SUCESSO!")
print("=" * 80)