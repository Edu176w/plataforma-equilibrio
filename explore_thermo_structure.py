"""
Script para explorar a estrutura da biblioteca thermo e descobrir onde 
estão os parâmetros de interação binária.
"""

import sys
import inspect

print("="*80)
print("EXPLORANDO A BIBLIOTECA THERMO")
print("="*80)

# ==============================================================================
# 1. EXPLORAR MÓDULO NRTL
# ==============================================================================
print("\n[1/3] Explorando módulo thermo.nrtl...")

try:
    import thermo.nrtl as nrtl_module

    print("\nClasses e funções disponíveis em thermo.nrtl:")
    members = inspect.getmembers(nrtl_module)
    for name, obj in members:
        if not name.startswith('_'):
            print(f"  - {name}: {type(obj).__name__}")

    # Tentar encontrar onde estão os dados
    if hasattr(nrtl_module, 'NRTL'):
        print("\n✓ Classe NRTL encontrada")
        nrtl_class = nrtl_module.NRTL
        print(f"  Atributos: {[attr for attr in dir(nrtl_class) if not attr.startswith('_')][:10]}")

except Exception as e:
    print(f"  Erro: {e}")

# ==============================================================================
# 2. EXPLORAR INTERACTION PARAMETERS
# ==============================================================================
print("\n[2/3] Explorando módulo de parâmetros de interação...")

try:
    # Tentar várias possibilidades
    try:
        from thermo import interaction_parameters
        print("\n✓ Módulo thermo.interaction_parameters encontrado")
        members = inspect.getmembers(interaction_parameters)
        print("\nConteúdo:")
        for name, obj in members:
            if not name.startswith('_') and name.isupper():
                print(f"  - {name}: {type(obj).__name__}")
    except:
        print("  ✗ Não há módulo interaction_parameters direto")

    # Tentar ChemSep database
    try:
        from thermo.interaction_parameters import IPDB
        print("\n✓ IPDB encontrado")
    except:
        print("  ✗ IPDB não encontrado")

    # Tentar buscar em chemical_package
    try:
        from thermo.chemical_package import ChemicalConstantsPackage
        print("\n✓ ChemicalConstantsPackage encontrado")
    except:
        pass

except Exception as e:
    print(f"  Erro: {e}")

# ==============================================================================
# 3. EXPLORAR UNIQUAC
# ==============================================================================
print("\n[3/3] Explorando módulo thermo.uniquac...")

try:
    import thermo.uniquac as uniquac_module

    print("\nClasses e funções disponíveis em thermo.uniquac:")
    members = inspect.getmembers(uniquac_module)
    for name, obj in members:
        if not name.startswith('_'):
            print(f"  - {name}: {type(obj).__name__}")

    if hasattr(uniquac_module, 'UNIQUAC'):
        print("\n✓ Classe UNIQUAC encontrada")

except Exception as e:
    print(f"  Erro: {e}")

# ==============================================================================
# 4. EXPLORAR UNIFAC
# ==============================================================================
print("\n[4/3] Explorando módulo thermo.unifac...")

try:
    import thermo.unifac as unifac_module

    print("\nClasses e funções disponíveis em thermo.unifac:")
    members = inspect.getmembers(unifac_module)
    for name, obj in members:
        if not name.startswith('_'):
            print(f"  - {name}: {type(obj).__name__}")

    # Procurar por dados de grupos
    for name, obj in members:
        if 'group' in name.lower() or 'ip' in name.lower():
            print(f"\n✓ Possível fonte de dados: {name}")
            print(f"  Tipo: {type(obj).__name__}")
            if isinstance(obj, dict):
                print(f"  Tamanho: {len(obj)} entradas")
                if len(obj) > 0:
                    first_key = list(obj.keys())[0]
                    print(f"  Exemplo de chave: {first_key}")
                    print(f"  Exemplo de valor: {obj[first_key]}")

except Exception as e:
    print(f"  Erro: {e}")

# ==============================================================================
# 5. TENTAR ACESSAR DADOS DIRETAMENTE
# ==============================================================================
print("\n" + "="*80)
print("TENTANDO ACESSAR DADOS DIRETAMENTE")
print("="*80)

# Tentar pegar parâmetros de um componente conhecido
print("\nTestando com Methanol (CAS: 67-56-1)...")
try:
    from thermo.chemical import Chemical

    methanol = Chemical('67-56-1')
    print(f"\n✓ Chemical carregado: {methanol.name}")

    # Verificar atributos relacionados a UNIFAC
    unifac_attrs = [attr for attr in dir(methanol) if 'UNIFAC' in attr or 'unifac' in attr]
    print(f"\nAtributos UNIFAC/UNIQUAC disponíveis:")
    for attr in unifac_attrs:
        val = getattr(methanol, attr, None)
        if val is not None:
            print(f"  - {attr}: {val}")

    # Verificar se há parâmetros r e q
    if hasattr(methanol, 'UNIFAC_R'):
        print(f"\n✓ UNIFAC_R disponível: {methanol.UNIFAC_R}")
    if hasattr(methanol, 'UNIFAC_Q'):
        print(f"\n✓ UNIFAC_Q disponível: {methanol.UNIFAC_Q}")
    if hasattr(methanol, 'UNIFAC_groups'):
        print(f"\n✓ UNIFAC_groups disponível: {methanol.UNIFAC_groups}")

except Exception as e:
    print(f"  Erro: {e}")

print("\n" + "="*80)
print("EXPLORAÇÃO CONCLUÍDA")
print("="*80)
print("\nExecute este script e cole a saída aqui para corrigir o extrator.")