"""
validate_fitted_params.py
Validação dos parâmetros UNIQUAC fitados e geração do diagrama ternário
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from ell_flash_uniquac import UNIQUACModel, ELLFlash
from experimental_lle_data import get_data

# Parâmetros estruturais
r_values = [3.48, 0.92, 2.11]  # ethyl acetate, water, ethanol
q_values = [3.12, 1.40, 1.97]

# Parâmetros otimizados do fitting
u_params_fitted = {
    (0, 1): {'u_delta': 9.0},
    (1, 0): {'u_delta': 2000.0},
    (0, 2): {'u_delta': 2000.0},
    (2, 0): {'u_delta': -1007.4},
    (1, 2): {'u_delta': 272.9},
    (2, 1): {'u_delta': -759.9},
}

T = 298.15  # K

# Criar modelo
model = UNIQUACModel(r_values, q_values, u_params_fitted)
flash = ELLFlash(model)

# Carregar dados experimentais
exp_data_full = get_data(T)
exp_tie_lines = exp_data_full['tie_lines']

print("="*80)
print("VALIDAÇÃO DOS PARÂMETROS UNIQUAC FITADOS")
print("="*80)
print(f"\nSistema: Ethyl acetate (1) + Water (2) + Ethanol (3)")
print(f"Temperatura: {T - 273.15:.2f}°C")
print(f"\nParâmetros fitados:")
for key, val in u_params_fitted.items():
    print(f"  u_{key[1]+1}{key[0]+1} - u_{key[1]+1}{key[1]+1} = {val['u_delta']:8.1f} cal/mol")

print(f"\n{'='*80}")
print("COMPARAÇÃO: EXPERIMENTAL vs CALCULADO")
print(f"{'='*80}")

# Validar tie-lines
errors = []
for i, exp_tl in enumerate(exp_tie_lines, 1):
    x1_exp = np.array(exp_tl['phase1'])
    x2_exp = np.array(exp_tl['phase2'])
    
    # Composição global
    z = 0.5 * (x1_exp + x2_exp)
    
    # Calcular com modelo
    result = flash.flash_lle(z, T, initial_guess=(x1_exp, x2_exp))
    
    if result['converged'] and not result['stable']:
        x1_calc = result['x_phase1']
        x2_calc = result['x_phase2']
        
        # Determinar qual fase é qual (pode ter trocado)
        error1 = np.linalg.norm(x1_calc - x1_exp) + np.linalg.norm(x2_calc - x2_exp)
        error2 = np.linalg.norm(x1_calc - x2_exp) + np.linalg.norm(x2_calc - x1_exp)
        
        if error2 < error1:
            x1_calc, x2_calc = x2_calc, x1_calc
        
        error = min(error1, error2)
        errors.append(error)
        
        print(f"\nTie-line {i}:")
        print(f"  Fase 1 (orgânica) - Experimental: {x1_exp}")
        print(f"  Fase 1 (orgânica) - Calculado:    {x1_calc}")
        print(f"  Erro absoluto: {np.linalg.norm(x1_calc - x1_exp):.6f}")
        print(f"  Fase 2 (aquosa)   - Experimental: {x2_exp}")
        print(f"  Fase 2 (aquosa)   - Calculado:    {x2_calc}")
        print(f"  Erro absoluto: {np.linalg.norm(x2_calc - x2_exp):.6f}")
    else:
        print(f"\nTie-line {i}: ⚠️  NÃO CONVERGIU")
        errors.append(999.0)

print(f"\n{'='*80}")
print(f"ESTATÍSTICAS DO ERRO:")
print(f"{'='*80}")
print(f"  Erro médio:  {np.mean(errors):.6f}")
print(f"  Erro máximo: {np.max(errors):.6f}")
print(f"  Desvio padrão: {np.std(errors):.6f}")

# =========================================================================
# GERAR DIAGRAMA TERNÁRIO COMPLETO
# =========================================================================

print(f"\n{'='*80}")
print("GERANDO DIAGRAMA TERNÁRIO...")
print(f"{'='*80}")

def ternary_to_cartesian(x):
    """Converte coordenadas ternárias para cartesianas"""
    x1, x2, x3 = x
    X = 0.5 * (2*x2 + x3)
    Y = (np.sqrt(3)/2) * x3
    return X, Y

# Gerar curva binodal calculada
print("\nCalculando curva binodal...")
binodal_phase1 = []
binodal_phase2 = []

# Varredura ao longo de composições
n_points = 50
for frac_ethanol in np.linspace(0.05, 0.40, n_points):
    for frac_water in np.linspace(0.01, 0.95, 20):
        frac_ethyl_acetate = 1.0 - frac_water - frac_ethanol
        
        if frac_ethyl_acetate < 0.01:
            continue
        
        z = np.array([frac_ethyl_acetate, frac_water, frac_ethanol])
        z = z / z.sum()
        
        result = flash.flash_lle(z, T, max_iter=50)
        
        if result['converged'] and not result['stable']:
            x1 = result['x_phase1']
            x2 = result['x_phase2']
            
            # Verificar se são fases distintas
            if np.linalg.norm(x1 - x2) > 0.1:
                binodal_phase1.append(x1)
                binodal_phase2.append(x2)

print(f"  Encontrados {len(binodal_phase1)} pontos na região bifásica")

# Plotar diagrama
fig, ax = plt.subplots(figsize=(12, 10))

# Triângulo externo
triangle = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
ax.plot(triangle[:, 0], triangle[:, 1], 'k-', linewidth=2)

# Labels dos vértices
ax.text(-0.05, -0.05, 'Water (2)', fontsize=14, ha='right')
ax.text(1.05, -0.05, 'Ethyl Acetate (1)', fontsize=14, ha='left')
ax.text(0.5, np.sqrt(3)/2 + 0.05, 'Ethanol (3)', fontsize=14, ha='center')

# Plotar dados experimentais
print("\nPlotando dados experimentais...")
for i, exp_tl in enumerate(exp_tie_lines):
    x1_exp = np.array(exp_tl['phase1'])
    x2_exp = np.array(exp_tl['phase2'])
    
    X1, Y1 = ternary_to_cartesian(x1_exp)
    X2, Y2 = ternary_to_cartesian(x2_exp)
    
    # Tie-line experimental
    ax.plot([X1, X2], [Y1, Y2], 'b-', linewidth=1.5, alpha=0.7, label='Exp' if i == 0 else '')
    ax.plot(X1, Y1, 'bo', markersize=8)
    ax.plot(X2, Y2, 'bo', markersize=8)

# Plotar binodal calculada
if len(binodal_phase1) > 0:
    print("Plotando curva binodal calculada...")
    
    binodal1_cart = [ternary_to_cartesian(x) for x in binodal_phase1]
    binodal2_cart = [ternary_to_cartesian(x) for x in binodal_phase2]
    
    X1_bin = [p[0] for p in binodal1_cart]
    Y1_bin = [p[1] for p in binodal1_cart]
    X2_bin = [p[0] for p in binodal2_cart]
    Y2_bin = [p[1] for p in binodal2_cart]
    
    ax.plot(X1_bin, Y1_bin, 'r--', linewidth=2, label='UNIQUAC (fitted)', alpha=0.8)
    ax.plot(X2_bin, Y2_bin, 'r--', linewidth=2, alpha=0.8)

ax.set_aspect('equal')
ax.axis('off')
ax.legend(fontsize=12, loc='upper right')
ax.set_title('Liquid-Liquid Equilibrium\nEthyl Acetate + Water + Ethanol @ 25°C', 
             fontsize=16, fontweight='bold')

plt.tight_layout()
plt.savefig('ternary_lle_diagram_fitted.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Diagrama salvo em: ternary_lle_diagram_fitted.png")
plt.show()

print(f"\n{'='*80}")
print("VALIDAÇÃO CONCLUÍDA!")
print(f"{'='*80}")
