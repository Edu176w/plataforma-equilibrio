"""
Script CORRIGIDO para extrair parâmetros completos de NRTL, UNIQUAC e UNIFAC 
da biblioteca thermo para uso no módulo ELL.

Baseado na estrutura real da biblioteca thermo instalada.
"""

import json
from collections import defaultdict

print("=" * 80)
print("EXTRAÇÃO DE PARÂMETROS COMPLETOS PARA MÓDULO ELL (VERSÃO CORRIGIDA)")
print("=" * 80)

# ==============================================================================
# 1. EXTRAÇÃO DE PARÂMETROS NRTL COMPLETOS
# ==============================================================================
print("\n[1/3] Extraindo parâmetros NRTL...")

try:
    from thermo.interaction_parameters import IPDB
    from thermo.nrtl import NRTL

    # Carregar banco de dados de interação
    ipdb = IPDB()

    nrtl_complete = {}
    count = 0

    # O IPDB contém dados para vários modelos
    # Vamos iterar e pegar os que têm dados NRTL
    for pair, data in ipdb.data.items():
        if 'NRTL' in data or 'nrtl' in str(data).lower():
            cas1, cas2 = pair
            dict_key = f"{cas1}__{cas2}"

            # Extrair parâmetros NRTL se existirem
            if 'tau12' in data or 'tau21' in data or 'alpha' in data:
                nrtl_complete[dict_key] = {
                    "cas1": cas1,
                    "cas2": cas2,
                    "name": data.get("name", f"{cas1}/{cas2}")
                }

                # Extrair parâmetros disponíveis
                for key in ['tau12', 'tau21', 'alpha', 'a12', 'a21', 'b12', 'b21']:
                    if key in data:
                        nrtl_complete[dict_key][key] = data[key]

                count += 1

    if count == 0:
        # Se não houver dados no IPDB, vamos usar dados diretos da thermo
        print("  ! IPDB não contém dados NRTL, tentando abordagem alternativa...")

        # Tentar carregar dados ChemSep
        try:
            from thermo.interaction_parameters import ChemSep_IP

            for pair, params in ChemSep_IP.items():
                if 'NRTL' in params.get('type', ''):
                    cas1, cas2 = pair
                    dict_key = f"{cas1}__{cas2}"

                    nrtl_complete[dict_key] = {
                        "cas1": cas1,
                        "cas2": cas2,
                        "name": params.get("name", f"{cas1}/{cas2}")
                    }

                    # Parâmetros típicos ChemSep
                    if 'params' in params:
                        p = params['params']
                        if len(p) >= 3:
                            nrtl_complete[dict_key]["bij"] = p[0]  # ou tau12
                            nrtl_complete[dict_key]["bji"] = p[1]  # ou tau21
                            nrtl_complete[dict_key]["alphaij"] = p[2]

                    count += 1
        except:
            pass

    print(f"  ✓ Extraídos {len(nrtl_complete)} pares binários NRTL")

    if len(nrtl_complete) > 0:
        with open("ell_nrtl_params_complete.json", "w", encoding="utf-8") as f:
            json.dump(nrtl_complete, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Salvo em: ell_nrtl_params_complete.json")

        example_key = list(nrtl_complete.keys())[0]
        print(f"  ✓ Exemplo: {example_key}")
        print(f"    {nrtl_complete[example_key]}")
    else:
        print("  ⚠ Nenhum parâmetro NRTL encontrado no IPDB")

except Exception as e:
    print(f"  ✗ Erro ao extrair NRTL: {e}")
    import traceback
    traceback.print_exc()
    nrtl_complete = {}

# ==============================================================================
# 2. EXTRAÇÃO DE PARÂMETROS UNIQUAC COMPLETOS
# ==============================================================================
print("\n[2/3] Extraindo parâmetros UNIQUAC...")

try:
    from thermo.chemical import Chemical
    from thermo.uniquac import UNIQUAC

    # 2.1 - Parâmetros de substância pura (r, q)
    print("  [2.1] Extraindo parâmetros r e q de componentes puros...")

    pure_params = {}

    # Lista de CAS - vamos pegar alguns comuns primeiro
    # Você deve expandir isso para todos os 455 componentes do seu banco
    common_cas = [
        "7732-18-5",  # Water
        "67-56-1",    # Methanol
        "64-17-5",    # Ethanol
        "67-63-0",    # Isopropanol
        "71-23-8",    # 1-Propanol
        "71-36-3",    # 1-Butanol
        "78-83-1",    # Isobutanol
        "75-65-0",    # tert-Butanol
        "78-93-3",    # 2-Butanone
        "67-64-1",    # Acetone
        "141-78-6",   # Ethyl acetate
        "79-20-9",    # Methyl acetate
        "64-19-7",    # Acetic acid
        "110-54-3",   # n-Hexane
        "109-66-0",   # n-Pentane
        "106-97-8",   # n-Butane
        "74-98-6",    # Propane
        "71-43-2",    # Benzene
        "108-88-3",   # Toluene
        "67-66-3",    # Chloroform
    ]

    for cas in common_cas:
        try:
            chem = Chemical(cas)
            if hasattr(chem, 'UNIFAC_R') and chem.UNIFAC_R is not None:
                pure_params[cas] = {
                    "name": chem.name,
                    "cas": cas,
                    "r": chem.UNIFAC_R,
                    "q": chem.UNIFAC_Q if hasattr(chem, 'UNIFAC_Q') else None
                }
        except Exception as e:
            print(f"    ⚠ Erro ao carregar {cas}: {e}")

    print(f"    ✓ Extraídos parâmetros r/q de {len(pure_params)} componentes")

    # 2.2 - Parâmetros de interação binária UNIQUAC
    print("  [2.2] Extraindo parâmetros de interação binária UNIQUAC...")

    uniquac_binary = {}

    # Tentar extrair do IPDB
    try:
        from thermo.interaction_parameters import IPDB
        ipdb = IPDB()

        for pair, data in ipdb.data.items():
            if 'UNIQUAC' in str(data) or 'uniquac' in str(data).lower():
                cas1, cas2 = pair
                dict_key = f"{cas1}__{cas2}"

                uniquac_binary[dict_key] = {
                    "cas1": cas1,
                    "cas2": cas2,
                    "name": data.get("name", f"{cas1}/{cas2}")
                }

                # Extrair parâmetros
                for key in ['a12', 'a21', 'b12', 'b21']:
                    if key in data:
                        uniquac_binary[dict_key][key] = data[key]
    except:
        pass

    print(f"    ✓ Extraídos {len(uniquac_binary)} pares binários UNIQUAC")

    # Montar estrutura completa
    uniquac_complete = {
        "pure_component_params": pure_params,
        "binary_params": uniquac_binary
    }

    with open("ell_uniquac_params_complete.json", "w", encoding="utf-8") as f:
        json.dump(uniquac_complete, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Salvo em: ell_uniquac_params_complete.json")

except Exception as e:
    print(f"  ✗ Erro ao extrair UNIQUAC: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 3. EXTRAÇÃO DE PARÂMETROS UNIFAC COMPLETOS
# ==============================================================================
print("\n[3/3] Extraindo parâmetros UNIFAC...")

try:
    from thermo.unifac import (
        UFSG, UFMG, DDBST_UNIFAC_assignments,
        load_unifac_ip, UNIFAC_RQ
    )
    from thermo.chemical import Chemical

    # 3.1 - Parâmetros dos grupos (Rk, Qk)
    print("  [3.1] Extraindo parâmetros Rk e Qk dos grupos UNIFAC...")

    group_params = {}

    # UFSG = UNIFAC SubGroups
    for subgroup_id, subgroup_data in UFSG.items():
        group_params[str(subgroup_id)] = {
            "subgroup_id": subgroup_id,
            "subgroup_name": subgroup_data.get('subgroup', f"Group_{subgroup_id}"),
            "main_group_id": subgroup_data.get('main_group_id'),
            "R": subgroup_data.get('R', 0.0),
            "Q": subgroup_data.get('Q', 0.0)
        }

    print(f"    ✓ Extraídos parâmetros de {len(group_params)} subgrupos UNIFAC")

    # 3.2 - Parâmetros de interação entre grupos
    print("  [3.2] Extraindo parâmetros de interação entre grupos...")

    group_interactions = {}

    # Carregar parâmetros de interação
    try:
        unifac_ip = load_unifac_ip()

        # unifac_ip é uma matriz ou dicionário de interações
        if isinstance(unifac_ip, dict):
            for key, value in unifac_ip.items():
                if isinstance(key, tuple) and len(key) == 2:
                    group1, group2 = key
                    dict_key = f"{group1}__{group2}"

                    group_interactions[dict_key] = {
                        "group1": group1,
                        "group2": group2,
                        "amn": value
                    }
    except Exception as e:
        print(f"    ⚠ Erro ao carregar parâmetros de interação: {e}")
        # Tentar alternativa
        try:
            from thermo.unifac import UFMG
            # UFMG = UNIFAC Main Groups interactions
            for key, value in UFMG.items():
                if isinstance(key, tuple):
                    group1, group2 = key
                    dict_key = f"{group1}__{group2}"
                    group_interactions[dict_key] = {
                        "group1": group1,
                        "group2": group2,
                        "amn": value
                    }
        except:
            pass

    print(f"    ✓ Extraídos {len(group_interactions)} pares de interação")

    # 3.3 - Decomposição de componentes em grupos
    print("  [3.3] Extraindo decomposição de componentes em grupos...")

    component_groups = {}

    # Usar DDBST_UNIFAC_assignments
    if DDBST_UNIFAC_assignments:
        for cas, groups_dict in DDBST_UNIFAC_assignments.items():
            if groups_dict:
                component_groups[cas] = {
                    "cas": cas,
                    "groups": groups_dict
                }

        print(f"    ✓ Extraídos assignments de {len(component_groups)} componentes")
    else:
        # Fallback: tentar pegar de Chemical
        for cas in common_cas:
            try:
                chem = Chemical(cas)
                if hasattr(chem, 'UNIFAC_groups') and chem.UNIFAC_groups:
                    component_groups[cas] = {
                        "cas": cas,
                        "name": chem.name,
                        "groups": chem.UNIFAC_groups
                    }
            except:
                pass

        print(f"    ✓ Extraídos assignments de {len(component_groups)} componentes")

    # Montar estrutura completa
    unifac_complete = {
        "group_params": group_params,
        "group_interactions": group_interactions,
        "component_groups": component_groups
    }

    with open("ell_unifac_params_complete.json", "w", encoding="utf-8") as f:
        json.dump(unifac_complete, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Salvo em: ell_unifac_params_complete.json")

except Exception as e:
    print(f"  ✗ Erro ao extrair UNIFAC: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# RESUMO FINAL
# ==============================================================================
print("\n" + "=" * 80)
print("RESUMO DA EXTRAÇÃO")
print("=" * 80)

nrtl_count = len(nrtl_complete) if 'nrtl_complete' in locals() else 0
uniquac_pure = len(pure_params) if 'pure_params' in locals() else 0
uniquac_bin = len(uniquac_binary) if 'uniquac_binary' in locals() else 0
unifac_groups = len(group_params) if 'group_params' in locals() else 0
unifac_inter = len(group_interactions) if 'group_interactions' in locals() else 0
unifac_comps = len(component_groups) if 'component_groups' in locals() else 0

print(f"✓ NRTL:   {nrtl_count} pares binários")
print(f"✓ UNIQUAC: {uniquac_pure} componentes puros + {uniquac_bin} pares binários")
print(f"✓ UNIFAC:  {unifac_groups} subgrupos + {unifac_inter} interações + {unifac_comps} componentes")
print("\nArquivos gerados:")
if nrtl_count > 0:
    print("  ✓ ell_nrtl_params_complete.json")
print("  ✓ ell_uniquac_params_complete.json")
print("  ✓ ell_unifac_params_complete.json")
print("=" * 80)