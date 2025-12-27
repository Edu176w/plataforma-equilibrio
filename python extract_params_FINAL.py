"""
Script FINAL para extrair parâmetros completos de NRTL, UNIQUAC e UNIFAC
Baseado na estrutura real descoberta da biblioteca thermo.
"""

import json
from collections import defaultdict

print("=" * 80)
print("EXTRAÇÃO COMPLETA DE PARÂMETROS - VERSÃO FINAL")
print("=" * 80)

# ==============================================================================
# 1. EXTRAÇÃO DE PARÂMETROS NRTL COMPLETOS
# ==============================================================================
print("\n[1/3] Extraindo parâmetros NRTL...")

try:
    from thermo.interaction_parameters import IPDB

    nrtl_complete = {}

    # IPDB tem atributo 'tables' que contém as tabelas de dados
    if hasattr(IPDB, 'tables'):
        print(f"  Explorando {len(IPDB.tables)} tabelas no IPDB...")

        # Procurar por tabelas NRTL
        nrtl_tables = IPDB.get_tables_with_type('NRTL')

        if nrtl_tables:
            print(f"  ✓ Encontradas {len(nrtl_tables)} tabelas NRTL")

            for table_name in nrtl_tables:
                print(f"    Processando tabela: {table_name}")
                # Aqui você pode iterar sobre os dados da tabela
        else:
            print("  ⚠ Nenhuma tabela NRTL específica encontrada")

            # Tentar extrair manualmente das tabelas disponíveis
            for table_name in IPDB.tables.keys():
                if 'nrtl' in table_name.lower():
                    print(f"  Tentando tabela: {table_name}")

    # Alternativa: tentar carregar diretamente do ChemSep
    print("  Tentando carregar de arquivos JSON da biblioteca...")

    try:
        import os
        from thermo import interaction_parameters

        # Caminho dos dados da thermo
        thermo_path = os.path.dirname(interaction_parameters.__file__)
        print(f"  Caminho da thermo: {thermo_path}")

        # Procurar por arquivos de dados
        for root, dirs, files in os.walk(thermo_path):
            for file in files:
                if 'nrtl' in file.lower() and (file.endswith('.json') or file.endswith('.tsv')):
                    print(f"    Encontrado: {file}")
    except:
        pass

    print(f"  ✓ Extraídos {len(nrtl_complete)} pares NRTL")

    if len(nrtl_complete) > 0:
        with open("ell_nrtl_params_complete.json", "w", encoding="utf-8") as f:
            json.dump(nrtl_complete, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Salvo em: ell_nrtl_params_complete.json")
    else:
        print("  ℹ NRTL: usando parâmetros diretos da thermo.nrtl.NRTL em tempo de execução")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 2. EXTRAÇÃO DE PARÂMETROS UNIQUAC COMPLETOS
# ==============================================================================
print("\n[2/3] Extraindo parâmetros UNIQUAC...")

try:
    from thermo.chemical import Chemical

    # 2.1 - Parâmetros de substância pura (r, q)
    print("  [2.1] Extraindo parâmetros r e q de componentes puros...")

    pure_params = {}

    # Lista expandida de componentes comuns
    common_cas = [
        "7732-18-5",  # Water
        "67-56-1",    # Methanol
        "64-17-5",    # Ethanol
        "67-63-0",    # Isopropanol
        "71-23-8",    # 1-Propanol
        "71-36-3",    # 1-Butanol
        "78-83-1",    # Isobutanol
        "75-65-0",    # tert-Butanol
        "71-41-0",    # 1-Pentanol
        "78-93-3",    # 2-Butanone (MEK)
        "67-64-1",    # Acetone
        "96-22-0",    # 3-Pentanone
        "141-78-6",   # Ethyl acetate
        "79-20-9",    # Methyl acetate
        "109-60-4",   # n-Propyl acetate
        "123-86-4",   # n-Butyl acetate
        "64-19-7",    # Acetic acid
        "79-09-4",    # Propionic acid
        "107-92-6",   # Butyric acid
        "110-54-3",   # n-Hexane
        "109-66-0",   # n-Pentane
        "106-97-8",   # n-Butane
        "74-98-6",    # Propane
        "71-43-2",    # Benzene
        "108-88-3",   # Toluene
        "100-41-4",   # Ethylbenzene
        "108-38-3",   # m-Xylene
        "67-66-3",    # Chloroform
        "56-23-5",    # Carbon tetrachloride
        "75-09-2",    # Dichloromethane
        "107-06-2",   # 1,2-Dichloroethane
        "109-99-9",   # Tetrahydrofuran
        "60-29-7",    # Diethyl ether
        "123-91-1",   # 1,4-Dioxane
        "67-68-5",    # Dimethyl sulfoxide (DMSO)
        "75-05-8",    # Acetonitrile
        "110-82-7",   # Cyclohexane
        "108-94-1",   # Cyclohexanone
    ]

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
        except Exception as e:
            pass

    print(f"    ✓ Extraídos parâmetros r/q de {len(pure_params)} componentes")

    # 2.2 - Parâmetros binários (vazio por enquanto - usar thermo em runtime)
    uniquac_binary = {}
    print(f"    ℹ Parâmetros binários: usar thermo.uniquac.UNIQUAC em tempo de execução")

    # Estrutura completa
    uniquac_complete = {
        "pure_component_params": pure_params,
        "binary_params": uniquac_binary,
        "note": "Use thermo.uniquac.UNIQUAC class with tau_coeffs for binary parameters at runtime"
    }

    with open("ell_uniquac_params_complete.json", "w", encoding="utf-8") as f:
        json.dump(uniquac_complete, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Salvo em: ell_uniquac_params_complete.json")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 3. EXTRAÇÃO DE PARÂMETROS UNIFAC COMPLETOS
# ==============================================================================
print("\n[3/3] Extraindo parâmetros UNIFAC...")

try:
    from thermo.unifac import UFSG, UFMG, load_unifac_ip
    from thermo.chemical import Chemical

    # 3.1 - Parâmetros dos grupos (Rk, Qk)
    print("  [3.1] Extraindo parâmetros Rk e Qk dos grupos UNIFAC...")

    group_params = {}

    # UFSG contém objetos UNIFAC_subgroup
    for subgroup_id, subgroup_obj in UFSG.items():
        group_params[str(subgroup_id)] = {
            "subgroup_id": subgroup_id,
            "subgroup_name": str(subgroup_obj),  # Usa __str__ do objeto
            "main_group_id": subgroup_obj.main_group_id,
            "R": float(subgroup_obj.R),
            "Q": float(subgroup_obj.Q)
        }

    print(f"    ✓ Extraídos parâmetros de {len(group_params)} subgrupos UNIFAC")

    # 3.2 - Informações dos grupos principais
    print("  [3.2] Extraindo informações dos grupos principais...")

    main_groups = {}
    for group_id, (group_name, subgroup_ids) in UFMG.items():
        main_groups[str(group_id)] = {
            "group_id": group_id,
            "group_name": group_name,
            "subgroup_ids": subgroup_ids
        }

    print(f"    ✓ Extraídos {len(main_groups)} grupos principais")

    # 3.3 - Parâmetros de interação entre grupos
    print("  [3.3] Carregando parâmetros de interação entre grupos...")

    group_interactions = {}

    try:
        # load_unifac_ip retorna uma matriz ou dicionário
        unifac_ip_data = load_unifac_ip()

        if unifac_ip_data is not None:
            # Verificar o tipo retornado
            if hasattr(unifac_ip_data, 'shape'):  # É uma matriz numpy
                print(f"    Matriz de interações: {unifac_ip_data.shape}")

                # Converter matriz para dicionário
                n_groups = unifac_ip_data.shape[0]
                for i in range(n_groups):
                    for j in range(n_groups):
                        if i != j:
                            amn = float(unifac_ip_data[i, j])
                            if amn != 0:  # Só salvar interações não-zero
                                dict_key = f"{i+1}__{j+1}"  # IDs começam em 1
                                group_interactions[dict_key] = {
                                    "group1": i+1,
                                    "group2": j+1,
                                    "amn": amn
                                }
            elif isinstance(unifac_ip_data, dict):
                group_interactions = unifac_ip_data

        print(f"    ✓ Extraídos {len(group_interactions)} pares de interação")
    except Exception as e:
        print(f"    ⚠ Erro ao carregar interações: {e}")

    # 3.4 - Decomposição de componentes
    print("  [3.4] Extraindo decomposição de componentes em grupos...")

    component_groups = {}

    # Tentar carregar assignments
    try:
        from thermo.unifac import DDBST_UNIFAC_assignments

        if DDBST_UNIFAC_assignments and len(DDBST_UNIFAC_assignments) > 0:
            for cas, groups_dict in DDBST_UNIFAC_assignments.items():
                if groups_dict:
                    component_groups[cas] = {
                        "cas": cas,
                        "groups": groups_dict
                    }
    except:
        pass

    # Se não houver assignments, extrair manualmente dos componentes comuns
    if len(component_groups) == 0:
        print("    ℹ DDBST_UNIFAC_assignments vazio, extraindo de Chemical...")

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

    print(f"    ✓ Extraídos assignments de {len(component_groups)} componentes")

    # Estrutura completa
    unifac_complete = {
        "group_params": group_params,
        "main_groups": main_groups,
        "group_interactions": group_interactions,
        "component_groups": component_groups,
        "note": "Use thermo.unifac.UNIFAC class for calculations. For missing components, use Chemical(cas).UNIFAC_groups"
    }

    with open("ell_unifac_params_complete.json", "w", encoding="utf-8") as f:
        json.dump(unifac_complete, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Salvo em: ell_unifac_params_complete.json")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# RESUMO FINAL
# ==============================================================================
print("\n" + "=" * 80)
print("RESUMO DA EXTRAÇÃO")
print("=" * 80)

uniquac_pure = len(pure_params) if 'pure_params' in locals() else 0
unifac_groups = len(group_params) if 'group_params' in locals() else 0
unifac_inter = len(group_interactions) if 'group_interactions' in locals() else 0
unifac_comps = len(component_groups) if 'component_groups' in locals() else 0

print(f"\n✓ UNIQUAC: {uniquac_pure} componentes com parâmetros r/q")
print(f"✓ UNIFAC:  {unifac_groups} subgrupos + {unifac_inter} interações + {unifac_comps} componentes")

print("\nArquivos gerados:")
print("  ✓ ell_uniquac_params_complete.json")
print("  ✓ ell_unifac_params_complete.json")

print("\n" + "=" * 80)
print("NOTA IMPORTANTE:")
print("=" * 80)
print("""
Para NRTL e parâmetros binários de UNIQUAC, a biblioteca thermo não expõe
facilmente os dados em formato extraível. 

RECOMENDAÇÃO:
Use as classes thermo.nrtl.NRTL e thermo.uniquac.UNIQUAC diretamente em
tempo de execução, fornecendo as matrizes tau_coeffs conforme necessário.

Os parâmetros extraídos (r, q, grupos UNIFAC) são suficientes para:
1. Cálculos UNIQUAC (parte combinatorial)
2. Cálculos UNIFAC completos (com interações de grupos)

Para NRTL, você pode:
1. Usar a classe NRTL da thermo com tau_coeffs da literatura
2. Ou buscar parâmetros em bases como DECHEMA, Dortmund Data Bank
""")
print("=" * 80)