"""
Script para extrair os parâmetros que faltaram:
1. Interações entre grupos UNIFAC (amn) - CRÍTICO
2. Parâmetros NRTL do arquivo JSON encontrado
"""

import json
import os
import numpy as np

print("=" * 80)
print("EXTRAÇÃO DE PARÂMETROS FALTANTES")
print("=" * 80)

# ==============================================================================
# 1. EXTRAIR INTERAÇÕES UNIFAC
# ==============================================================================
print("\n[1/2] Extraindo interações entre grupos UNIFAC...")

try:
    from thermo.unifac import load_unifac_ip

    print("  Carregando matriz de interações...")
    unifac_ip_matrix = load_unifac_ip()

    print(f"  Tipo retornado: {type(unifac_ip_matrix)}")

    if unifac_ip_matrix is not None:
        group_interactions = {}

        if hasattr(unifac_ip_matrix, 'shape'):
            # É uma matriz numpy
            n_groups = unifac_ip_matrix.shape[0]
            print(f"  ✓ Matriz {n_groups}x{n_groups} carregada")

            count = 0
            for i in range(n_groups):
                for j in range(n_groups):
                    if i != j:
                        amn = float(unifac_ip_matrix[i, j])
                        # Verificar se o valor é válido (não NaN, não inf, não zero)
                        if not np.isnan(amn) and not np.isinf(amn) and amn != 0:
                            dict_key = f"{i+1}__{j+1}"
                            group_interactions[dict_key] = {
                                "group1": i + 1,
                                "group2": j + 1,
                                "amn": amn
                            }
                            count += 1

            print(f"  ✓ Extraídas {count} interações não-zero")

            # Mostrar alguns exemplos
            if count > 0:
                print("\n  Exemplos de interações:")
                for i, (key, val) in enumerate(list(group_interactions.items())[:5]):
                    print(f"    {key}: amn = {val['amn']:.4f}")

        elif isinstance(unifac_ip_matrix, dict):
            group_interactions = unifac_ip_matrix
            print(f"  ✓ Extraídas {len(group_interactions)} interações do dict")

        # Salvar
        if len(group_interactions) > 0:
            with open("unifac_group_interactions.json", "w") as f:
                json.dump(group_interactions, f, indent=2)
            print(f"  ✓ Salvo em: unifac_group_interactions.json")

            # Atualizar o arquivo completo
            print("\n  Atualizando ell_unifac_params_complete.json...")
            try:
                with open("ell_unifac_params_complete.json", "r") as f:
                    unifac_data = json.load(f)

                unifac_data["group_interactions"] = group_interactions

                with open("ell_unifac_params_complete.json", "w") as f:
                    json.dump(unifac_data, f, indent=2)

                print(f"  ✓ Arquivo atualizado com {len(group_interactions)} interações")
            except:
                print("  ⚠ Não foi possível atualizar o arquivo completo")
        else:
            print("  ⚠ Nenhuma interação válida encontrada")
    else:
        print("  ✗ load_unifac_ip() retornou None")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 2. EXTRAIR PARÂMETROS NRTL DO ARQUIVO JSON
# ==============================================================================
print("\n[2/2] Extraindo parâmetros NRTL do arquivo JSON...")

try:
    from thermo import interaction_parameters

    thermo_path = os.path.dirname(interaction_parameters.__file__)
    nrtl_json_path = os.path.join(thermo_path, "nrtl.json")

    if os.path.exists(nrtl_json_path):
        print(f"  ✓ Arquivo encontrado: {nrtl_json_path}")

        with open(nrtl_json_path, "r") as f:
            nrtl_data_raw = json.load(f)

        print(f"  Estrutura do JSON:")
        print(f"    Tipo: {type(nrtl_data_raw)}")
        if isinstance(nrtl_data_raw, dict):
            print(f"    Chaves principais: {list(nrtl_data_raw.keys())[:10]}")

        # Tentar processar os dados
        nrtl_complete = {}

        if isinstance(nrtl_data_raw, dict):
            for key, value in nrtl_data_raw.items():
                # Tentar diferentes estruturas possíveis
                if isinstance(key, str) and '__' in key:
                    # Formato: "CAS1__CAS2"
                    nrtl_complete[key] = value
                elif isinstance(key, tuple) and len(key) == 2:
                    # Formato: ("CAS1", "CAS2")
                    cas1, cas2 = key
                    dict_key = f"{cas1}__{cas2}"
                    nrtl_complete[dict_key] = value

        if len(nrtl_complete) > 0:
            print(f"  ✓ Extraídos {len(nrtl_complete)} pares NRTL")

            # Mostrar exemplo
            example_key = list(nrtl_complete.keys())[0]
            print(f"\n  Exemplo:")
            print(f"    {example_key}: {nrtl_complete[example_key]}")

            with open("ell_nrtl_params_complete.json", "w") as f:
                json.dump(nrtl_complete, f, indent=2)
            print(f"  ✓ Salvo em: ell_nrtl_params_complete.json")
        else:
            print("  ⚠ Não foi possível processar os dados do JSON")
            print(f"  Estrutura raw (primeiros 500 chars):")
            print(f"    {str(nrtl_data_raw)[:500]}")
    else:
        print(f"  ✗ Arquivo não encontrado: {nrtl_json_path}")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 3. TENTAR EXTRAIR DADOS CHEMSEP DIRETAMENTE
# ==============================================================================
print("\n[3/2 EXTRA] Tentando extrair dados ChemSep...")

try:
    from thermo.interaction_parameters import IPDB

    # Verificar tabela ChemSep NRTL
    if hasattr(IPDB, 'tables'):
        if 'ChemSep NRTL' in IPDB.tables:
            print("  ✓ Tabela 'ChemSep NRTL' encontrada")

            chemsep_table = IPDB.tables['ChemSep NRTL']
            print(f"  Tipo da tabela: {type(chemsep_table)}")
            print(f"  Atributos: {[attr for attr in dir(chemsep_table) if not attr.startswith('_')][:15]}")

            # Tentar acessar dados
            if hasattr(chemsep_table, 'data'):
                print(f"  ✓ Atributo 'data' existe")
                data = chemsep_table.data
                print(f"    Tipo: {type(data)}")
                print(f"    Tamanho: {len(data) if hasattr(data, '__len__') else 'N/A'}")

                if len(data) > 0:
                    first_item = list(data.items())[0] if isinstance(data, dict) else data[0]
                    print(f"    Exemplo: {first_item}")

            if hasattr(chemsep_table, 'rows'):
                print(f"  ✓ Atributo 'rows' existe: {len(chemsep_table.rows)} linhas")

            if hasattr(chemsep_table, '__iter__'):
                print("  Tentando iterar sobre a tabela...")
                for i, item in enumerate(chemsep_table):
                    if i < 3:
                        print(f"    Item {i}: {item}")
                    else:
                        break

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("EXTRAÇÃO CONCLUÍDA")
print("=" * 80)