"""
Diagnóstico do Flash LLE
"""

import numpy as np
from ell_flash_uniquac import UNIQUACModel, ELLFlash

# Parâmetros do sistema (mesmos do test_ternary_lle_completo.py)
r_values = [3.48, 0.92, 2.11]  # ethyl acetate, water, ethanol
q_values = [3.12, 1.40, 1.97]

u_params = {
    (0, 2): {'u_delta': -292.3},  # u31 - u33 (ethyl acetate-ethanol)
    (2, 0): {'u_delta': 446.5},   # u13 - u11
    (1, 2): {'u_delta': 258.4},   # u32 - u33 (water-ethanol)
    (2, 1): {'u_delta': 378.1},   # u23 - u22
    (0, 1): {'u_delta': 591.7},   # u21 - u22 (ethyl acetate-water) - ESTIMADO
    (1, 0): {'u_delta': -25.1},   # u12 - u11 - ESTIMADO
}

model = UNIQUACModel(r_values, q_values, u_params)
flash = ELLFlash(model)
T = 25.0 + 273.15  # K

print("="*70)
print("DIAGNÓSTICO DO FLASH LLE")
print("="*70)

# Teste 1: Composições conhecidas no paper (Figura 11)
# Fase I (rica em ethyl acetate): aproximadamente [0.85, 0.03, 0.12]
# Fase II (rica em water): aproximadamente [0.02, 0.90, 0.08]

print("\n1. TESTE COM FASES CONHECIDAS (da Figura 11):")
print("-" * 70)

x1_paper = np.array([0.85, 0.03, 0.12])
x2_paper = np.array([0.02, 0.90, 0.08])

gamma1 = model.activity_coefficients(x1_paper, T)
gamma2 = model.activity_coefficients(x2_paper, T)

print(f"\nFase I (rica em ethyl acetate): x = {x1_paper}")
print(f"  γ = {gamma1}")
print(f"  x·γ = {x1_paper * gamma1}")

print(f"\nFase II (rica em water): x = {x2_paper}")
print(f"  γ = {gamma2}")
print(f"  x·γ = {x2_paper * gamma2}")

print(f"\nERRO de equilíbrio (x₁·γ₁ - x₂·γ₂):")
error = x1_paper * gamma1 - x2_paper * gamma2
print(f"  {error}")
print(f"  Norma = {np.linalg.norm(error):.6f}")

# Teste 2: Varredura de composições
print("\n\n2. VARREDURA DE COMPOSIÇÕES:")
print("-" * 70)

test_compositions = [
    [0.80, 0.10, 0.10],  # Rico em ethyl acetate
    [0.60, 0.30, 0.10],  # Intermediário
    [0.50, 0.40, 0.10],  # Original
    [0.40, 0.50, 0.10],  # Rico em water
    [0.30, 0.30, 0.40],  # Rico em ethanol
]

for z in test_compositions:
    z = np.array(z)
    result = flash.flash_lle(z, T)
    
    print(f"\nz = {z}")
    print(f"  Convergiu: {result['converged']}")
    print(f"  Estável: {result['stable']}")
    if not result['stable']:
        print(f"  β = {result['beta']:.4f}")
        print(f"  Fase I:  {result['x_phase1']}")
        print(f"  Fase II: {result['x_phase2']}")

# Teste 3: Chute inicial específico
print("\n\n3. TESTE COM CHUTE INICIAL ESPECÍFICO:")
print("-" * 70)

z = np.array([0.50, 0.40, 0.10])
initial_guess = (
    np.array([0.85, 0.03, 0.12]),  # Fase rica em ethyl acetate
    np.array([0.02, 0.90, 0.08])   # Fase rica em water
)

result = flash.flash_lle(z, T, initial_guess=initial_guess)

print(f"\nz = {z}")
print(f"Convergiu: {result['converged']}")
print(f"Estável: {result['stable']}")
if not result['stable']:
    print(f"β = {result['beta']:.4f}")
    print(f"Fase I:  {result['x_phase1']}")
    print(f"Fase II: {result['x_phase2']}")
