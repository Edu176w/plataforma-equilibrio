"""
Script para extrair os dados REAIS descobertos:
1. Tabela ChemSep NRTL (que existe e está acessível!)
2. Parâmetros de interação UNIFAC (buscar em outro lugar)
"""

import json
import os

print("=" * 80)
print("EXTRAÇÃO DEFINITIVA DOS PARÂMETROS")
print("=" * 80)

# ==============================================================================
# 1. EXTRAIR DADOS DA TABELA CHEMSEP NRTL
# ==============================================================================
print("\n[1/3] Extraindo dados da tabela ChemSep NRTL...")

try:
    from thermo.interaction_parameters import IPDB

    if 'ChemSep NRTL' in IPDB.tables:
        chemsep_nrtl = IPDB.tables['ChemSep NRTL']
        print(f"  ✓ Tabela encontrada")
        print(f"  Tipo: {type(chemsep_nrtl)}")

        nrtl_complete = {}

        # A tabela é um dicionário - vamos iterar
        for key in chemsep_nrtl.keys():
            # A chave parece ser "CAS1 CAS2"
            print(f"\n  Processando chave: {key}")

            # Tentar obter o valor
            value = chemsep_nrtl[key]
            print(f"    Tipo do valor: {type(value)}")
            print(f"    Valor: {value}")

            # Tentar diferentes formas de acessar
            if hasattr(value, '__dict__'):
                print(f"    Atributos: {value.__dict__}")

            # Se conseguir 10 exemplos, parar
            if len(nrtl_complete) >= 10:
                break

        print(f"\n  Total de pares na tabela: {len(chemsep_nrtl)}")

        # Tentar usar método get_ip_specific
        print("\n  Tentando usar get_ip_specific...")
        try:
            # Pegar primeiro par da tabela
            first_key = list(chemsep_nrtl.keys())[0]
            print(f"  Testando com: {first_key}")

            # Separar CAS
            if ' ' in first_key:
                cas1, cas2 = first_key.split(' ')
                print(f"    CAS1: {cas1}, CAS2: {cas2}")

                # Tentar obter parâmetros
                params = IPDB.get_ip_specific('ChemSep NRTL', cas1, cas2)
                print(f"    Parâmetros obtidos: {params}")
                print(f"    Tipo: {type(params)}")

                if params is not None:
                    # Processar todos os pares
                    print("\n  ✓ Método funciona! Extraindo todos os pares...")

                    for key in list(chemsep_nrtl.keys())[:100]:  # Primeiros 100 para teste
                        if ' ' in key:
                            cas1, cas2 = key.split(' ')
                            params = IPDB.get_ip_specific('ChemSep NRTL', cas1, cas2)

                            if params is not None:
                                dict_key = f"{cas1}__{cas2}"

                                # Parâmetros NRTL típicos: tau12, tau21, alpha
                                # ou bij, bji, alphaij
                                nrtl_complete[dict_key] = {
                                    "cas1": cas1,
                                    "cas2": cas2,
                                    "params": params
                                }
        except Exception as e:
            print(f"    Erro ao usar get_ip_specific: {e}")

        if len(nrtl_complete) > 0:
            print(f"\n  ✓ Extraídos {len(nrtl_complete)} pares NRTL")

            # Salvar
            with open("ell_nrtl_params_complete.json", "w") as f:
                json.dump(nrtl_complete, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Salvo em: ell_nrtl_params_complete.json")

            # Mostrar exemplo
            example_key = list(nrtl_complete.keys())[0]
            print(f"\n  Exemplo:")
            print(f"    {example_key}:")
            print(f"    {json.dumps(nrtl_complete[example_key], indent=6)}")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 2. BUSCAR ARQUIVOS DE PARÂMETROS UNIFAC
# ==============================================================================
print("\n[2/3] Buscando arquivos de parâmetros UNIFAC...")

try:
    from thermo import unifac

    unifac_path = os.path.dirname(unifac.__file__)
    print(f"  Caminho do módulo UNIFAC: {unifac_path}")

    # Buscar todos os arquivos
    print("\n  Arquivos encontrados:")
    for root, dirs, files in os.walk(unifac_path):
        for file in files:
            if file.endswith(('.json', '.tsv', '.csv', '.txt')):
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path)
                print(f"    {file} ({size} bytes)")

    # Tentar carregar arquivos específicos
    potential_files = ['unifac_ip.json', 'UNIFAC.json', 'interaction_parameters.json']

    for filename in potential_files:
        filepath = os.path.join(unifac_path, filename)
        if os.path.exists(filepath):
            print(f"\n  ✓ Encontrado: {filename}")
            print(f"    Tentando carregar...")

            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                print(f"    ✓ JSON carregado")
                print(f"    Tipo: {type(data)}")
                print(f"    Tamanho: {len(data) if hasattr(data, '__len__') else 'N/A'}")
            except:
                print(f"    ✗ Não é JSON válido")

except Exception as e:
    print(f"  ✗ Erro: {e}")

# ==============================================================================
# 3. TENTAR CARREGAR PARÂMETROS UNIFAC DE FORMA ALTERNATIVA
# ==============================================================================
print("\n[3/3] Tentando carregar parâmetros UNIFAC alternativamente...")

try:
    from thermo.unifac import UNIFAC
    from thermo import unifac as unifac_module

    # Verificar se há constantes globais com os dados
    print("\n  Procurando constantes no módulo unifac...")

    for attr_name in dir(unifac_module):
        attr = getattr(unifac_module, attr_name)

        # Procurar dicts grandes que podem conter parâmetros
        if isinstance(attr, dict) and len(attr) > 50:
            print(f"\n    {attr_name}:")
            print(f"      Tipo: dict")
            print(f"      Tamanho: {len(attr)}")

            # Pegar exemplo
            if len(attr) > 0:
                first_key = list(attr.keys())[0]
                first_val = attr[first_key]
                print(f"      Exemplo: {first_key} -> {first_val}")

                # Se parecer matriz de interação
                if attr_name in ['UFIP', 'UNIFAC_IP', 'interaction_params']:
                    print(f"      ✓ POSSÍVEL MATRIZ DE INTERAÇÕES!")

    # Tentar criar instância UNIFAC e ver o que precisa
    print("\n  Tentando instanciar UNIFAC para ver estrutura...")
    try:
        # UNIFAC precisa de: T, xs, chemgroups
        # chemgroups é um dict {grupo: fração}

        print("    Documentação do UNIFAC.__init__:")
        import inspect
        sig = inspect.signature(UNIFAC.__init__)
        print(f"    {sig}")

    except Exception as e:
        print(f"    Erro: {e}")

except Exception as e:
    print(f"  ✗ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("EXTRAÇÃO CONCLUÍDA")
print("=" * 80)