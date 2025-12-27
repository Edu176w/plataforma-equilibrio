"""
Script para extrair parâmetros completos de NRTL, UNIQUAC e UNIFAC da biblioteca thermo
para uso no módulo ELL da plataforma de equilíbrio de fases.

Execute este script no terminal do VSCode com o ambiente virtual ativado:
(venv) python extract_complete_parameters.py
"""

import json
from collections import defaultdict

print("=" * 80)
print("EXTRAÇÃO DE PARÂMETROS COMPLETOS PARA MÓDULO ELL")
print("=" * 80)

# ==============================================================================
# 1. EXTRAÇÃO DE PARÂMETROS NRTL COMPLETOS
# ==============================================================================
print("\n[1/3] Extraindo parâmetros NRTL...")

try:
    from thermo.nrtl import NRTL_IPDB

    nrtl_db = NRTL_IPDB()
    nrtl_complete = {}

    for key, params in nrtl_db.data.items():
        cas1, cas2 = key

        # A biblioteca thermo armazena os parâmetros como:
        # - 'bij': parâmetro de energia em Kelvin
        # - 'alphaij': parâmetro de não-aleatoriedade
        # - Alguns podem ter 'aij' também (independente de T)

        # Criar chave no formato cas1__cas2
        dict_key = f"{cas1}__{cas2}"

        # Extrair todos os parâmetros disponíveis
        nrtl_complete[dict_key] = {
            "cas1": cas1,
            "cas2": cas2,
            "name": params.get("name", f"{cas1}/{cas2}")
        }

        # Parâmetros de energia
        if "aij" in params:
            nrtl_complete[dict_key]["aij"] = params["aij"]
        if "bij" in params:
            nrtl_complete[dict_key]["bij"] = params["bij"]

        # Parâmetro de não-aleatoriedade
        if "alphaij" in params:
            nrtl_complete[dict_key]["alphaij"] = params["alphaij"]
        elif "alpha" in params:
            nrtl_complete[dict_key]["alphaij"] = params["alpha"]

        # Adicionar outros campos que possam existir
        for field in ["cij", "dij", "eij", "fij"]:
            if field in params:
                nrtl_complete[dict_key][field] = params[field]

    print(f"  ✓ Extraídos {len(nrtl_complete)} pares binários NRTL")

    # Salvar JSON completo
    with open("ell_nrtl_params_complete.json", "w", encoding="utf-8") as f:
        json.dump(nrtl_complete, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Salvo em: ell_nrtl_params_complete.json")

    # Mostrar exemplo
    example_key = list(nrtl_complete.keys())[0]
    print(f"  ✓ Exemplo de entrada:")
    print(f"    {example_key}: {nrtl_complete[example_key]}")

except Exception as e:
    print(f"  ✗ Erro ao extrair NRTL: {e}")
    nrtl_complete = {}

# ==============================================================================
# 2. EXTRAÇÃO DE PARÂMETROS UNIQUAC COMPLETOS
# ==============================================================================
print("\n[2/3] Extraindo parâmetros UNIQUAC...")

try:
    from thermo.uniquac import UNIQUAC, UNIQUAC_IPSQ
    from thermo.chemical import Chemical

    # 2.1 - Parâmetros de substância pura (r, q)
    print("  [2.1] Extraindo parâmetros r e q de componentes puros...")

    pure_params = {}

    # Lista de CAS dos componentes do seu banco
    # Vou extrair apenas alguns exemplos - você deve adicionar todos os 455
    example_cas = [
        "67-56-1",    # Methanol
        "7732-18-5",  # Water
        "64-17-5",    # Ethanol
        "67-63-0",    # Isopropanol
        "71-23-8",    # 1-Propanol
        "78-93-3",    # 2-Butanone
        "141-78-6",   # Ethyl acetate
    ]

    for cas in example_cas:
        try:
            chem = Chemical(cas)
            if hasattr(chem, 'UNIFAC_R') and hasattr(chem, 'UNIFAC_Q'):
                pure_params[cas] = {
                    "name": chem.name,
                    "r": chem.UNIFAC_R,
                    "q": chem.UNIFAC_Q
                }
        except:
            pass

    print(f"    ✓ Extraídos parâmetros r/q de {len(pure_params)} componentes")

    # 2.2 - Parâmetros de interação binária
    print("  [2.2] Extraindo parâmetros de interação binária UNIQUAC...")

    try:
        uniquac_db = UNIQUAC_IPSQ()
        uniquac_binary = {}

        for key, params in uniquac_db.data.items():
            cas1, cas2 = key
            dict_key = f"{cas1}__{cas2}"

            uniquac_binary[dict_key] = {
                "cas1": cas1,
                "cas2": cas2,
                "name": params.get("name", f"{cas1}/{cas2}")
            }

            # Extrair todos os parâmetros de interação
            for field in ["aij", "aji", "bij", "bji", "cij", "cji", "dij", "dji"]:
                if field in params:
                    uniquac_binary[dict_key][field] = params[field]

        print(f"    ✓ Extraídos {len(uniquac_binary)} pares binários UNIQUAC")
    except:
        uniquac_binary = {}
        print(f"    ✗ Banco UNIQUAC_IPSQ não disponível")

    # Montar estrutura completa UNIQUAC
    uniquac_complete = {
        "pure_component_params": pure_params,
        "binary_params": uniquac_binary
    }

    # Salvar JSON completo
    with open("ell_uniquac_params_complete.json", "w", encoding="utf-8") as f:
        json.dump(uniquac_complete, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Salvo em: ell_uniquac_params_complete.json")

except Exception as e:
    print(f"  ✗ Erro ao extrair UNIQUAC: {e}")

# ==============================================================================
# 3. EXTRAÇÃO DE PARÂMETROS UNIFAC COMPLETOS
# ==============================================================================
print("\n[3/3] Extraindo parâmetros UNIFAC...")

try:
    from thermo.unifac import UNIFAC, UFIP, UFSG, DOUFIP2016, load_unifac_ip
    from thermo.group_contribution import UNIFACDecomposer

    # 3.1 - Parâmetros dos grupos (Rk, Qk)
    print("  [3.1] Extraindo parâmetros Rk e Qk dos grupos UNIFAC...")

    group_params = {}

    try:
        # UFSG contém os parâmetros R e Q dos grupos
        for group_id, data in UFSG.items():
            group_params[str(group_id)] = {
                "group_name": data.get("group", f"Group_{group_id}"),
                "R": data.get("R", 0.0),
                "Q": data.get("Q", 0.0)
            }

        print(f"    ✓ Extraídos parâmetros de {len(group_params)} grupos UNIFAC")
    except Exception as e:
        print(f"    ✗ Erro ao extrair grupos: {e}")

    # 3.2 - Parâmetros de interação entre grupos
    print("  [3.2] Extraindo parâmetros de interação entre grupos...")

    group_interactions = {}

    try:
        # UFIP contém os parâmetros de interação amn
        for key, params in UFIP.items():
            group1, group2 = key
            dict_key = f"{group1}__{group2}"

            group_interactions[dict_key] = {
                "group1": group1,
                "group2": group2,
                "amn": params.get("a", 0.0),
                "anm": params.get("b", 0.0)  # Parâmetro simétrico
            }

        print(f"    ✓ Extraídos {len(group_interactions)} pares de interação entre grupos")
    except Exception as e:
        print(f"    ✗ Erro ao extrair interações: {e}")

    # 3.3 - Decomposição de componentes em grupos (assignments)
    print("  [3.3] Extraindo decomposição de componentes em grupos...")

    component_groups = {}

    for cas in example_cas:
        try:
            chem = Chemical(cas)
            if hasattr(chem, 'UNIFAC_groups') and chem.UNIFAC_groups:
                component_groups[cas] = {
                    "name": chem.name,
                    "groups": chem.UNIFAC_groups
                }
        except:
            pass

    print(f"    ✓ Extraídos assignments de {len(component_groups)} componentes")

    # Montar estrutura completa UNIFAC
    unifac_complete = {
        "group_params": group_params,
        "group_interactions": group_interactions,
        "component_groups": component_groups
    }

    # Salvar JSON completo
    with open("ell_unifac_params_complete.json", "w", encoding="utf-8") as f:
        json.dump(unifac_complete, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Salvo em: ell_unifac_params_complete.json")

except Exception as e:
    print(f"  ✗ Erro ao extrair UNIFAC: {e}")

# ==============================================================================
# RESUMO FINAL
# ==============================================================================
print("\n" + "=" * 80)
print("RESUMO DA EXTRAÇÃO")
print("=" * 80)
print(f"✓ NRTL:   {len(nrtl_complete)} pares binários")
print(f"✓ UNIQUAC: {len(pure_params)} componentes puros + {len(uniquac_binary) if 'uniquac_binary' in locals() else 0} pares binários")
print(f"✓ UNIFAC: {len(group_params) if 'group_params' in locals() else 0} grupos + {len(group_interactions) if 'group_interactions' in locals() else 0} interações")
print("\nArquivos gerados:")
print("  - ell_nrtl_params_complete.json")
print("  - ell_uniquac_params_complete.json")
print("  - ell_unifac_params_complete.json")
print("=" * 80)