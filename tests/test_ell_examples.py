"""
Testes do módulo ELL com exemplos experimentais
Baseado em: Prausnitz et al., High-Pressure Phase Equilibria, Chapter 12
"""

from app.calculators.ell_calculator import (
    calculate_ell_equilibrium, 
    generate_ternary_diagram_ell,
    calculate_ell_extraction
)


# ============================================================================
# TESTE 1: Sistema binário clássico (Água + Amina)
# ============================================================================
def test_water_amine():
    print("="*70)
    print("TESTE 1: Água + Trietilamina (T = 25°C)")
    print("="*70)
    
    result = calculate_ell_equilibrium(
        components=['water', 'triethylamine'],
        temperature=25.0,
        model='NRTL',
        compositions=[0.5, 0.5]
    )
    
    if result['success']:
        print("✅ Cálculo convergiu!")
        res = result['results']
        
        # Extrair valores
        x_alpha_water = res.get("x'1_water", 0)
        x_alpha_amine = res.get("x'2_triethylamine", 0)
        x_beta_water = res.get('x"1_water', 0)
        x_beta_amine = res.get('x"2_triethylamine', 0)
        beta = res.get('beta_fraction', 0)
        
        print("\n📊 Composições das fases:")
        print(f"  Fase α (aquosa):")
        print(f"    x'_water = {x_alpha_water:.4f}")
        print(f"    x'_amine = {x_alpha_amine:.4f}")
        
        print(f"  Fase β (orgânica):")
        print(f"    x\"_water = {x_beta_water:.4f}")
        print(f"    x\"_amine = {x_beta_amine:.4f}")
        
        print(f"  Fração β: {beta:.4f}")
        
        # Coeficientes de atividade
        print("\n📈 Coeficientes de atividade:")
        print(f"  γα1 = {res.get('gamma_alpha_1', 1):.4f}")
        print(f"  γα2 = {res.get('gamma_alpha_2', 1):.4f}")
        print(f"  γβ1 = {res.get('gamma_beta_1', 1):.4f}")
        print(f"  γβ2 = {res.get('gamma_beta_2', 1):.4f}")
        
        # Validação
        if x_alpha_water > 0.85:
            print("\n✅ VALIDAÇÃO: Água concentrada na fase aquosa (correto!)")
        else:
            print("\n⚠️ ATENÇÃO: Distribuição inesperada!")
    else:
        print(f"❌ Erro: {result.get('error', 'Desconhecido')}")
    
    print("\n")


# ============================================================================
# TESTE 2: Sistema hidrocarboneto + polar
# ============================================================================
def test_hexane_nitromethane():
    print("="*70)
    print("TESTE 2: Hexano + Nitrometano (T = 25°C)")
    print("="*70)
    
    result = calculate_ell_equilibrium(
        components=['hexane', 'nitromethane'],
        temperature=25.0,
        model='NRTL',
        compositions=[0.5, 0.5]
    )
    
    if result['success']:
        print("✅ Cálculo convergiu!")
        res = result['results']
        
        # Extrair valores
        x_alpha_hexane = res.get("x'1_hexane", 0)
        x_alpha_nitro = res.get("x'2_nitromethane", 0)
        x_beta_hexane = res.get('x"1_hexane', 0)
        x_beta_nitro = res.get('x"2_nitromethane', 0)
        beta = res.get('beta_fraction', 0)
        
        print("\n📊 Separação de fases:")
        print(f"  Fase α:")
        print(f"    x'_hexane = {x_alpha_hexane:.4f}")
        print(f"    x'_nitromethane = {x_alpha_nitro:.4f}")
        
        print(f"  Fase β:")
        print(f"    x\"_hexane = {x_beta_hexane:.4f}")
        print(f"    x\"_nitromethane = {x_beta_nitro:.4f}")
        
        print(f"  β = {beta:.4f}")
        
        # Coeficiente de distribuição
        if x_beta_hexane > 0:
            K = x_alpha_hexane / x_beta_hexane
            print(f"\n📐 Coeficiente de distribuição K = {K:.4f}")
        
        # Coeficientes de atividade
        print("\n📈 Coeficientes de atividade:")
        print(f"  γα1 = {res.get('gamma_alpha_1', 1):.4f}")
        print(f"  γα2 = {res.get('gamma_alpha_2', 1):.4f}")
        print(f"  γβ1 = {res.get('gamma_beta_1', 1):.4f}")
        print(f"  γβ2 = {res.get('gamma_beta_2', 1):.4f}")
    else:
        print(f"❌ Erro: {result.get('error', 'Desconhecido')}")
    
    print("\n")


# ============================================================================
# TESTE 3: Sistema ternário simples
# ============================================================================
def test_ternary_simple():
    print("="*70)
    print("TESTE 3: Sistema Ternário Água-Etanol-Hexano")
    print("="*70)
    
    result = calculate_ell_equilibrium(
        components=['water', 'ethanol', 'hexane'],
        temperature=25.0,
        model='NRTL',
        compositions=[0.4, 0.3, 0.3]
    )
    
    if result['success']:
        print("✅ Cálculo convergiu!")
        res = result['results']
        
        # Extrair composições
        comps = ['water', 'ethanol', 'hexane']
        
        print("\n📊 Fase α (aquosa):")
        for i, comp in enumerate(comps, 1):
            key = f"x'{i}_{comp}"
            value = res.get(key, 0)
            print(f"  x'{i} ({comp}): {value:.4f}")
        
        print("\n📊 Fase β (orgânica):")
        for i, comp in enumerate(comps, 1):
            key = f'x"{i}_{comp}'
            value = res.get(key, 0)
            print(f"  x\"{i} ({comp}): {value:.4f}")
        
        alpha = res.get('alpha_fraction', 0)
        beta = res.get('beta_fraction', 0)
        print(f"\n🎯 Frações: α = {alpha:.4f}, β = {beta:.4f}")
        
        # Validação: água deve estar principalmente na fase α
        x_alpha_water = res.get("x'1_water", 0)
        x_beta_hexane = res.get('x"3_hexane', 0)
        
        if x_alpha_water > 0.7 and x_beta_hexane > 0.7:
            print("\n✅ VALIDAÇÃO: Separação correta (água na α, hexano na β)")
        else:
            print("\n⚠️ ATENÇÃO: Verificar separação")
    else:
        print(f"❌ Erro: {result.get('error', 'Desconhecido')}")
    
    print("\n")


# ============================================================================
# EXECUTAR TODOS OS TESTES
# ============================================================================
if __name__ == '__main__':
    print("\n" + "🧪 " * 35)
    print("BATERIA DE TESTES DO MÓDULO ELL")
    print("Baseado em exemplos experimentais da literatura")
    print("🧪 " * 35 + "\n")
    
    # Teste 1
    try:
        test_water_amine()
    except Exception as e:
        print(f"❌ Teste 1 falhou: {e}\n")
        import traceback
        traceback.print_exc()
    
    # Teste 2
    try:
        test_hexane_nitromethane()
    except Exception as e:
        print(f"❌ Teste 2 falhou: {e}\n")
        import traceback
        traceback.print_exc()
    
    # Teste 3
    try:
        test_ternary_simple()
    except Exception as e:
        print(f"❌ Teste 3 falhou: {e}\n")
        import traceback
        traceback.print_exc()
    
    print("="*70)
    print("✅ BATERIA DE TESTES CONCLUÍDA!")
    print("="*70)
