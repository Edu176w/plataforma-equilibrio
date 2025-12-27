"""
Script COMPLETO para extrair parâmetros NRTL, UNIQUAC e UNIFAC
organizados por tipo de equilíbrio: ELV, ELL e ESL
"""

import json
import os
import csv

print("=" * 80)
print("EXTRAÇÃO COMPLETA DE PARÂMETROS PARA ELV, ELL E ESL")
print("=" * 80)

# ==============================================================================
# 1. EXTRAIR PARÂMETROS NRTL (serve para ELV, ELL e ESL)
# ==============================================================================
print("\n[1/5] Extraindo parâmetros NRTL (ChemSep)...")

try:
    from thermo.interaction_parameters import IPDB

    if 'ChemSep NRTL' in IPDB.tables:
        chemsep_nrtl = IPDB.tables['ChemSep NRTL']

        nrtl_params = {}

        for key, value in chemsep_nrtl.items():
            # Chave no formato "CAS1 CAS2"
            if ' ' in key:
                cas1, cas2 = key.split(' ')
                dict_key = f"{cas1}__{cas2}"

                # value é um dict com 'name', 'bij', 'alphaij'
                nrtl_params[dict_key] = {
                    "cas1": cas1,
                    "cas2": cas2,
                    "name": value.get('name', ''),
                    "bij": value.get('bij', 0.0),
                    "alphaij": value.get('alphaij', 0.3)
                }

        print(f"  ✓ Extraídos {len(nrtl_params)} pares NRTL")

        # Salvar arquivo único (serve para ELV, ELL, ESL)
        with open("nrtl_params_complete.json", "w", encoding="utf-8") as f:
            json.dump(nrtl_params, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Salvo em: nrtl_params_complete.json")

        # Criar links simbólicos (conceituais) para cada módulo
        for module in ['elv', 'ell', 'esl']:
            filename = f"{module}_nrtl_params.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(nrtl_params, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Cópia para {module.upper()}: {filename}")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 2. EXTRAIR PARÂMETROS UNIQUAC (r, q)
# ==============================================================================
print("\n[2/5] Extraindo parâmetros UNIQUAC (r, q)...")

try:
    from thermo.chemical import Chemical

    # Lista expandida de componentes
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

    # Estrutura UNIQUAC completa
    uniquac_complete = {
        "pure_component_params": pure_params,
        "binary_params": {},
        "note": "Parameters r and q are used for combinatorial part. Use NRTL binary parameters for residual part in runtime calculations."
    }

    # Salvar para cada módulo
    for module in ['elv', 'ell', 'esl']:
        filename = f"{module}_uniquac_params.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(uniquac_complete, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Salvo para {module.upper()}: {filename}")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 3. EXTRAIR PARÂMETROS UNIFAC - GRUPOS E GRUPOS PRINCIPAIS
# ==============================================================================
print("\n[3/5] Extraindo grupos UNIFAC...")

try:
    from thermo.unifac import UFSG, UFMG

    # 3.1 - Parâmetros dos subgrupos
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

    # 3.2 - Grupos principais
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
    import traceback
    traceback.print_exc()

# ==============================================================================
# 4. EXTRAIR INTERAÇÕES UNIFAC DOS ARQUIVOS TSV
# ==============================================================================
print("\n[4/5] Extraindo interações UNIFAC de arquivos TSV...")

try:
    from thermo import unifac
    thermo_path = os.path.dirname(unifac.__file__)

    # 4.1 - UNIFAC Original (para ELV)
    print("\n  [4.1] UNIFAC Original (ELV)...")
    unifac_original_path = os.path.join(thermo_path, "Group Contribution", 
                                        "UNIFAC original interaction parameters.tsv")

    elv_interactions = {}

    if os.path.exists(unifac_original_path):
        with open(unifac_original_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                # TSV tem colunas: Group1, Group2, a_mn, a_nm, etc.
                try:
                    group1 = int(row.get('Group1', row.get('group1', 0)))
                    group2 = int(row.get('Group2', row.get('group2', 0)))
                    amn = float(row.get('a_mn', row.get('amn', 0)))
                    anm = float(row.get('a_nm', row.get('anm', 0)))

                    if group1 and group2:
                        key = f"{group1}__{group2}"
                        elv_interactions[key] = {
                            "group1": group1,
                            "group2": group2,
                            "amn": amn,
                            "anm": anm
                        }
                except:
                    continue

        print(f"    ✓ {len(elv_interactions)} interações ELV extraídas")
    else:
        print(f"    ⚠ Arquivo não encontrado: {unifac_original_path}")

    # 4.2 - UNIFAC LLE (para ELL)
    print("\n  [4.2] UNIFAC LLE (ELL)...")
    unifac_lle_path = os.path.join(thermo_path, "Group Contribution",
                                   "UNIFAC LLE interaction parameters.tsv")

    ell_interactions = {}

    if os.path.exists(unifac_lle_path):
        with open(unifac_lle_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                try:
                    group1 = int(row.get('Group1', row.get('group1', 0)))
                    group2 = int(row.get('Group2', row.get('group2', 0)))
                    amn = float(row.get('a_mn', row.get('amn', 0)))
                    anm = float(row.get('a_nm', row.get('anm', 0)))

                    if group1 and group2:
                        key = f"{group1}__{group2}"
                        ell_interactions[key] = {
                            "group1": group1,
                            "group2": group2,
                            "amn": amn,
                            "anm": anm
                        }
                except:
                    continue

        print(f"    ✓ {len(ell_interactions)} interações ELL extraídas")
    else:
        print(f"    ⚠ Arquivo não encontrado: {unifac_lle_path}")

    # Para ESL, usar UNIFAC Original também
    esl_interactions = elv_interactions.copy()
    print(f"\n  [4.3] UNIFAC para ESL: usando Original ({len(esl_interactions)} interações)")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 5. EXTRAIR DECOMPOSIÇÃO DE COMPONENTES (DDBST)
# ==============================================================================
print("\n[5/5] Extraindo decomposição de componentes (DDBST)...")

try:
    ddbst_path = os.path.join(thermo_path, "Group Contribution",
                              "DDBST UNIFAC assignments.tsv")

    component_groups = {}

    if os.path.exists(ddbst_path):
        with open(ddbst_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')

            count = 0
            for row in reader:
                try:
                    cas = row.get('CAS', row.get('cas', ''))
                    # Grupos estão em colunas separadas
                    groups = {}
                    for col, val in row.items():
                        if col not in ['CAS', 'cas', 'Name', 'name', 'Formula']:
                            if val and val.strip():
                                try:
                                    group_id = int(col)
                                    group_count = int(val)
                                    groups[group_id] = group_count
                                except:
                                    pass

                    if cas and groups:
                        component_groups[cas] = {
                            "cas": cas,
                            "name": row.get('Name', row.get('name', '')),
                            "groups": groups
                        }
                        count += 1

                        # Limitar a 5000 componentes para teste
                        if count >= 5000:
                            break
                except:
                    continue

        print(f"  ✓ {len(component_groups)} componentes decompostos")
    else:
        print(f"  ⚠ Arquivo não encontrado: {ddbst_path}")
        # Fallback: usar Chemical
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
        print(f"  ✓ Fallback: {len(component_groups)} componentes de Chemical")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 6. MONTAR E SALVAR ESTRUTURAS FINAIS
# ==============================================================================
print("\n" + "=" * 80)
print("MONTANDO ARQUIVOS FINAIS POR MÓDULO")
print("=" * 80)

# Estrutura base UNIFAC
unifac_base = {
    "group_params": group_params if 'group_params' in locals() else {},
    "main_groups": main_groups if 'main_groups' in locals() else {},
    "component_groups": component_groups if 'component_groups' in locals() else {}
}

# ELV
print("\n[ELV] Montando elv_unifac_params.json...")
elv_unifac = unifac_base.copy()
elv_unifac["group_interactions"] = elv_interactions if 'elv_interactions' in locals() else {}
with open("elv_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(elv_unifac, f, indent=2, ensure_ascii=False)
print(f"  ✓ {len(elv_unifac['group_interactions'])} interações para ELV")

# ELL
print("\n[ELL] Montando ell_unifac_params.json...")
ell_unifac = unifac_base.copy()
ell_unifac["group_interactions"] = ell_interactions if 'ell_interactions' in locals() else {}
with open("ell_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(ell_unifac, f, indent=2, ensure_ascii=False)
print(f"  ✓ {len(ell_unifac['group_interactions'])} interações para ELL")

# ESL
print("\n[ESL] Montando esl_unifac_params.json...")
esl_unifac = unifac_base.copy()
esl_unifac["group_interactions"] = esl_interactions if 'esl_interactions' in locals() else {}
with open("esl_unifac_params.json", "w", encoding="utf-8") as f:
    json.dump(esl_unifac, f, indent=2, ensure_ascii=False)
print(f"  ✓ {len(esl_unifac['group_interactions'])} interações para ESL")

# ==============================================================================
# RESUMO FINAL
# ==============================================================================
print("\n" + "=" * 80)
print("RESUMO FINAL - ARQUIVOS GERADOS")
print("=" * 80)

print("\n📁 NRTL (para ELV, ELL, ESL):")
print(f"  • elv_nrtl_params.json - {len(nrtl_params) if 'nrtl_params' in locals() else 0} pares")
print(f"  • ell_nrtl_params.json - {len(nrtl_params) if 'nrtl_params' in locals() else 0} pares")
print(f"  • esl_nrtl_params.json - {len(nrtl_params) if 'nrtl_params' in locals() else 0} pares")

print("\n📁 UNIQUAC (para ELV, ELL, ESL):")
print(f"  • elv_uniquac_params.json - {len(pure_params) if 'pure_params' in locals() else 0} componentes")
print(f"  • ell_uniquac_params.json - {len(pure_params) if 'pure_params' in locals() else 0} componentes")
print(f"  • esl_uniquac_params.json - {len(pure_params) if 'pure_params' in locals() else 0} componentes")

print("\n📁 UNIFAC (específico por módulo):")
print(f"  • elv_unifac_params.json:")
print(f"      - {len(group_params) if 'group_params' in locals() else 0} subgrupos")
print(f"      - {len(elv_interactions) if 'elv_interactions' in locals() else 0} interações (Original)")
print(f"      - {len(component_groups) if 'component_groups' in locals() else 0} componentes")
print(f"  • ell_unifac_params.json:")
print(f"      - {len(group_params) if 'group_params' in locals() else 0} subgrupos")
print(f"      - {len(ell_interactions) if 'ell_interactions' in locals() else 0} interações (LLE)")
print(f"      - {len(component_groups) if 'component_groups' in locals() else 0} componentes")
print(f"  • esl_unifac_params.json:")
print(f"      - {len(group_params) if 'group_params' in locals() else 0} subgrupos")
print(f"      - {len(esl_interactions) if 'esl_interactions' in locals() else 0} interações (Original)")
print(f"      - {len(component_groups) if 'component_groups' in locals() else 0} componentes")

print("\n" + "=" * 80)
print("✅ EXTRAÇÃO COMPLETA!")
print("=" * 80)
print("\nPRÓXIMOS PASSOS:")
print("  1. Integre os arquivos *_nrtl_params.json nos calculadores")
print("  2. Integre os arquivos *_uniquac_params.json nos calculadores")
print("  3. Integre os arquivos *_unifac_params.json nos calculadores")
print("  4. Para ELL, use UNIFAC-LLE (ell_unifac_params.json)")
print("  5. Valide com dados experimentais do TCC")
print("=" * 80)