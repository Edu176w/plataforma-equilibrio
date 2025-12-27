# test_ternary_lle.py
"""
Teste de diagrama ternário LLE
Sistema: hexane (1) - aniline (2) - methylcyclopentane (3) a 25°C
Reproduzindo Figura 5 do Abrams & Prausnitz (1975)
"""

import numpy as np
from ell_flash_uniquac import UNIQACModel, ELLFlash

# Dados do sistema (precisamos dos 3 pares binários)
# Da Tabela 4 e do artigo:

# Componente 1: hexane
# Componente 2: aniline  
# Componente 3: methylcyclopentane

# Parâmetros r, q (estimados da Tabela 1 do artigo)
r_values = [4.50, 3.72, 3.97]  # hexane, aniline, methylcyclopentane
q_values = [3.86, 2.83, 3.01]  # hexane, aniline, methylcyclopentane

# Parâmetros u_ij (precisamos dos 3 pares)
# PROBLEMA: só temos methylcyclopentane-benzene na Tabela 4
# Vamos usar dados aproximados baseados no artigo

T = 25.0 + 273.15  # K

# Teste simples primeiro: só verificar se o código roda
print("="*60)
print("TESTE DE DIAGRAMA TERNÁRIO LLE")
print("Sistema: Hexane - Aniline - Methylcyclopentane")
print(f"Temperatura: 25°C")
print("="*60)
print()

print("Parâmetros estruturais:")
print(f"  Hexane:              r = {r_values[0]:.2f}, q = {q_values[0]:.2f}")
print(f"  Aniline:             r = {r_values[1]:.2f}, q = {q_values[1]:.2f}")
print(f"  Methylcyclopentane:  r = {r_values[2]:.2f}, q = {q_values[2]:.2f}")
print()

# Para fazer o teste funcionar, vamos usar parâmetros simplificados
# (idealmente você pegaria todos os 3 binários da literatura)
u_params = {
    (0, 1): {'u_delta': 600.0},   # hexane-aniline (estimado, parcialmente miscível)
    (1, 0): {'u_delta': -200.0},
    (0, 2): {'u_delta': -36.9},   # hexane-methylcyclopentane (da Tabela 4 via benzene)
    (2, 0): {'u_delta': 138.1},
    (1, 2): {'u_delta': 500.0},   # aniline-methylcyclopentane (estimado)
    (2, 1): {'u_delta': -150.0},
}

print("⚠️  AVISO: Usando parâmetros ESTIMADOS")
print("   Para reproduzir exatamente a Figura 5, precisamos dos")
print("   parâmetros binários completos de hexane-aniline e")
print("   aniline-methylcyclopentane da fonte original.")
print()

# Criar modelo
try:
    model = UNIQACModel(r_values, q_values, u_params)
    print("✓ Modelo UNIQUAC criado com sucesso")
    
    # Testar cálculo de gamma em uma composição
    x_test = np.array([0.33, 0.33, 0.34])
    gamma_test = model.activity_coefficients(x_test, T)
    
    print(f"\nTeste de cálculo de γ para x = {x_test}:")
    for i, (name, g) in enumerate(zip(['hexane', 'aniline', 'methylcyc'], gamma_test)):
        print(f"  γ_{i+1} ({name:12s}) = {g:.3f}")
    
    print()
    
    # Criar flash LLE
    flash = ELLFlash(model)
    print("✓ Flash LLE inicializado")
    print()
    
    # Testar um ponto de flash
    print("Testando flash LLE para composição z = [0.5, 0.3, 0.2]:")
    z_test = np.array([0.5, 0.3, 0.2])
    
    result = flash.flash_lle(z_test, T)
    
    print(f"  Convergiu: {result['converged']}")
    print(f"  Estável (uma fase): {result['stable']}")
    
    if not result['stable']:
        print(f"  Fração de fase 2 (β): {result['beta']:.3f}")
        print(f"\n  Composição fase 1:")
        for i, (name, xi) in enumerate(zip(['hexane', 'aniline', 'methylcyc'], result['x_phase1'])):
            print(f"    x_{i+1} ({name:12s}) = {xi:.4f}")
        print(f"\n  Composição fase 2:")
        for i, (name, xi) in enumerate(zip(['hexane', 'aniline', 'methylcyc'], result['x_phase2'])):
            print(f"    x_{i+1} ({name:12s}) = {xi:.4f}")
    else:
        print("  Sistema está em uma única fase líquida")
    
    print()
    print("="*60)
    print("PRÓXIMOS PASSOS:")
    print("="*60)
    print("1. Buscar parâmetros UNIQUAC completos para os 3 binários")
    print("   - hexane-aniline")
    print("   - aniline-methylcyclopentane")
    print("   - hexane-methylcyclopentane")
    print()
    print("2. Com parâmetros corretos, gerar curva binodal completa")
    print("   usando: flash.generate_binodal_curve(T)")
    print()
    print("3. Criar endpoint API para servir ao frontend")
    print()
    print("4. Visualizar no diagrama ternário da interface")
    print("="*60)
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
