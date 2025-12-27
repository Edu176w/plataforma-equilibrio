# test_ternary_lle_completo.py
"""
Reproduzindo Figura 11 do Abrams & Prausnitz (1975)
Sistema: Ethyl acetate (1) - Water (2) - Ethanol (3)
Todos os parâmetros binários vêm da Tabela 4
"""

import numpy as np
from ell_flash_uniquac import UNIQUACModel, ELLFlash  # <-- trocar para UNIQUACModel



print("="*70)
print("DIAGRAMA TERNÁRIO LLE - UNIQUAC")
print("Sistema: Ethyl acetate - Water - Ethanol")
print("Reproduzindo Figura 11 (Abrams & Prausnitz, 1975)")
print("="*70)
print()

# Componentes
# 1: Ethyl acetate (CAS: 141-78-6)
# 2: Water (CAS: 7732-18-5)
# 3: Ethanol (CAS: 64-17-5)

# Parâmetros estruturais r, q (da Tabela 1 do artigo)
r1, q1 = 3.48, 3.12  # ethyl acetate
r2, q2 = 0.92, 1.40  # water
r3, q3 = 2.11, 1.97  # ethanol

r_values = [r1, r2, r3]
q_values = [q1, q2, q3]

print("Parâmetros estruturais (Tabela 1):")
print(f"  Ethyl acetate:  r = {r1:.2f}, q = {q1:.2f}")
print(f"  Water:          r = {r2:.2f}, q = {q2:.2f}")
print(f"  Ethanol:        r = {r3:.2f}, q = {q3:.2f}")
print()

# Parâmetros binários da Tabela 4
print("Parâmetros binários (Tabela 4):")
print()

# Sistema 10: Ethyl acetate (1) - Ethanol (3) a 70°C
u13_minus_u11 = -292.3  # cal/mol
u31_minus_u33 = 446.5   # cal/mol
print("1. Ethyl acetate - Ethanol (70°C):")
print(f"   u₁₃ - u₁₁ = {u13_minus_u11:7.1f} cal/mol")
print(f"   u₃₁ - u₃₃ = {u31_minus_u33:7.1f} cal/mol")
print()

# Sistema 9: Water (2) - Ethanol (3) a 70°C  
u23_minus_u22 = 258.4  # cal/mol
u32_minus_u33 = 378.1  # cal/mol
print("2. Water - Ethanol (70°C):")
print(f"   u₂₃ - u₂₂ = {u23_minus_u22:7.1f} cal/mol")
print(f"   u₃₂ - u₃₃ = {u32_minus_u33:7.1f} cal/mol")
print()

# Sistema ?: Ethyl acetate (1) - Water (2)
# NÃO ESTÁ NA TABELA 4!
# Vamos buscar na literatura ou estimar

# Da literatura (exemplo), sistema ethyl acetate-water é parcialmente miscível
# Parâmetros típicos (estimados baseados em sistemas similares):
u12_minus_u11 = 591.7   # cal/mol (estimado de fontes DECHEMA)
u21_minus_u22 = -25.1   # cal/mol
print("3. Ethyl acetate - Water (ESTIMADO da literatura):")
print(f"   u₁₂ - u₁₁ = {u12_minus_u11:7.1f} cal/mol")
print(f"   u₂₁ - u₂₂ = {u21_minus_u22:7.1f} cal/mol")
print("   ⚠️  Esses valores são aproximados!")
print()

# Temperatura de trabalho
T_C = 25.0  # °C (vamos usar 25°C para testar)
T = T_C + 273.15

print(f"Temperatura: {T_C}°C")
print()

# Montar dicionário de parâmetros u
# Formato: (i, j): {'u_delta': u_ij - u_ii}
u_params = {
    # Ethyl acetate (0) - Water (1)
    (0, 1): {'u_delta': u12_minus_u11},
    (1, 0): {'u_delta': u21_minus_u22},
    
    # Ethyl acetate (0) - Ethanol (2)
    (0, 2): {'u_delta': u13_minus_u11},
    (2, 0): {'u_delta': u31_minus_u33},
    
    # Water (1) - Ethanol (2)
    (1, 2): {'u_delta': u23_minus_u22},
    (2, 1): {'u_delta': u32_minus_u33},
}

# Criar modelo
model = UNIQUACModel(r_values, q_values, u_params)  # CORRETO

print("✓ Modelo UNIQUAC criado")
print()

# Testar alguns pontos
print("="*70)
print("TESTES DE COEFICIENTES DE ATIVIDADE")
print("="*70)
print()

test_compositions = [
    ([0.9, 0.05, 0.05], "Rico em ethyl acetate"),
    ([0.05, 0.9, 0.05], "Rico em water"),
    ([0.05, 0.05, 0.9], "Rico em ethanol"),
    ([0.33, 0.33, 0.34], "Mistura equimolar"),
]

for x_test, desc in test_compositions:
    gamma = model.activity_coefficients(np.array(x_test), T)
    print(f"{desc}:")
    print(f"  x = [{x_test[0]:.2f}, {x_test[1]:.2f}, {x_test[2]:.2f}]")
    print(f"  γ₁ (ethyl acetate) = {gamma[0]:.3f}")
    print(f"  γ₂ (water)         = {gamma[1]:.3f}")
    print(f"  γ₃ (ethanol)       = {gamma[2]:.3f}")
    print()

# Teste de flash LLE
print("="*70)
print("TESTE DE FLASH LLE")
print("="*70)
print()

flash = ELLFlash(model)

# Testar uma composição que deve estar na região bifásica
# (ethyl acetate + water são parcialmente miscíveis)
z_test = np.array([0.5, 0.4, 0.1])  # meio a meio ethyl acetate-water

print(f"Composição global: z = [{z_test[0]:.2f}, {z_test[1]:.2f}, {z_test[2]:.2f}]")
print()

result = flash.flash_lle(z_test, T)

print(f"Convergiu: {result['converged']}")
print(f"Sistema estável (1 fase): {result['stable']}")
print()

if not result['stable'] and result['converged']:
    print("✓ DUAS FASES LÍQUIDAS DETECTADAS!")
    print()
    print(f"Fração de fase orgânica (β): {result['beta']:.4f}")
    print()
    
    x1 = result['x_phase1']
    x2 = result['x_phase2']
    
    print("Fase 1 (aquosa):")
    print(f"  x₁ (ethyl acetate) = {x1[0]:.4f}")
    print(f"  x₂ (water)         = {x1[1]:.4f}")
    print(f"  x₃ (ethanol)       = {x1[2]:.4f}")
    print()
    
    print("Fase 2 (orgânica):")
    print(f"  x₁ (ethyl acetate) = {x2[0]:.4f}")
    print(f"  x₂ (water)         = {x2[1]:.4f}")
    print(f"  x₃ (ethanol)       = {x2[2]:.4f}")
else:
    print("Sistema em UMA ÚNICA FASE")
    print("(Composição pode estar fora da região bifásica)")

print()
print("="*70)
print("PRÓXIMOS PASSOS:")
print("="*70)
print("1. Ajustar parâmetros ethyl acetate-water (buscar valor exato)")
print("2. Gerar curva binodal completa")
print("3. Calcular tie-lines")
print("4. Comparar com Figura 11 do artigo")
print("5. Criar endpoint API /api/ell/ternary-diagram")
print("="*70)
