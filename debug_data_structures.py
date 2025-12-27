"""
Script para descobrir a estrutura exata de IPDB e UFSG
"""

print("="*80)
print("INVESTIGANDO ESTRUTURAS DE DADOS")
print("="*80)

# ==============================================================================
# 1. INVESTIGAR IPDB
# ==============================================================================
print("\n[1] Investigando IPDB...")

try:
    from thermo.interaction_parameters import IPDB

    print(f"\nTipo de IPDB: {type(IPDB)}")
    print(f"IPDB é instância? {type(IPDB).__name__}")

    # IPDB já é uma instância, não uma classe
    if hasattr(IPDB, 'data'):
        print(f"\n✓ IPDB.data existe")
        print(f"  Tipo: {type(IPDB.data)}")
        print(f"  Tamanho: {len(IPDB.data)}")

        if len(IPDB.data) > 0:
            first_key = list(IPDB.data.keys())[0]
            first_value = IPDB.data[first_key]
            print(f"\n  Exemplo de entrada:")
            print(f"    Chave: {first_key}")
            print(f"    Valor tipo: {type(first_value)}")
            print(f"    Valor: {first_value}")

    # Verificar atributos
    attrs = [attr for attr in dir(IPDB) if not attr.startswith('_')]
    print(f"\n  Atributos principais: {attrs[:15]}")

except Exception as e:
    print(f"  Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 2. INVESTIGAR UFSG
# ==============================================================================
print("\n[2] Investigando UFSG...")

try:
    from thermo.unifac import UFSG

    print(f"\nTipo de UFSG: {type(UFSG)}")
    print(f"Tamanho: {len(UFSG)}")

    if len(UFSG) > 0:
        first_key = list(UFSG.keys())[0]
        first_value = UFSG[first_key]

        print(f"\n  Exemplo de entrada:")
        print(f"    Chave: {first_key}")
        print(f"    Valor tipo: {type(first_value)}")
        print(f"    Valor: {first_value}")

        # Se for um objeto, mostrar atributos
        if hasattr(first_value, '__dict__'):
            print(f"\n    Atributos do objeto:")
            for attr, val in first_value.__dict__.items():
                print(f"      {attr}: {val}")

        # Tentar diferentes formas de acesso
        print(f"\n    Tentando acessar campos:")
        for field in ['R', 'Q', 'subgroup', 'main_group_id', 'name']:
            if hasattr(first_value, field):
                print(f"      {field}: {getattr(first_value, field)}")

except Exception as e:
    print(f"  Erro: {e}")
    import traceback
    traceback.print_exc()

# ==============================================================================
# 3. INVESTIGAR UFMG
# ==============================================================================
print("\n[3] Investigando UFMG...")

try:
    from thermo.unifac import UFMG

    print(f"\nTipo de UFMG: {type(UFMG)}")
    print(f"Tamanho: {len(UFMG)}")

    if len(UFMG) > 0:
        first_key = list(UFMG.keys())[0]
        first_value = UFMG[first_key]

        print(f"\n  Exemplo de entrada:")
        print(f"    Chave: {first_key}")
        print(f"    Valor tipo: {type(first_value)}")
        print(f"    Valor: {first_value}")

        # Pegar mais alguns exemplos
        for i, (k, v) in enumerate(list(UFMG.items())[:5]):
            print(f"    {k}: {v}")

except Exception as e:
    print(f"  Erro: {e}")

# ==============================================================================
# 4. INVESTIGAR DDBST_UNIFAC_assignments
# ==============================================================================
print("\n[4] Investigando DDBST_UNIFAC_assignments...")

try:
    from thermo.unifac import DDBST_UNIFAC_assignments

    print(f"\nTipo: {type(DDBST_UNIFAC_assignments)}")
    print(f"Tamanho: {len(DDBST_UNIFAC_assignments)}")

    if len(DDBST_UNIFAC_assignments) > 0:
        # Pegar alguns exemplos
        for i, (cas, groups) in enumerate(list(DDBST_UNIFAC_assignments.items())[:5]):
            print(f"\n  {i+1}. CAS {cas}:")
            print(f"     Grupos: {groups}")

except Exception as e:
    print(f"  Erro: {e}")

print("\n" + "="*80)
print("INVESTIGAÇÃO CONCLUÍDA")
print("="*80)