#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE: Diagrama Ternário - Sistema Benzene/2-Propanol/Water
============================================================
Sistema 508 de Sørensen et al. (1979)
Tipo 1: Um binário parcialmente miscível (Benzene-Water)
Temperatura: 25°C
"""

import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# DADOS EXPERIMENTAIS - Sistema 508: Benzene (1) / 2-Propanol (2) / Water (3)
# ============================================================================

# Tie-lines experimentais (composição em fração molar)
# Fase I (rica em Benzene), Fase II (rica em Water)
tielines_exp = [
    # x1_I, x2_I, x3_I, x1_II, x2_II, x3_II
    [0.9542, 0.0447, 0.0011, 0.0009, 0.0573, 0.9418],  # Tie-line 1
    [0.9032, 0.0938, 0.0030, 0.0019, 0.1163, 0.8818],  # Tie-line 2
    [0.8301, 0.1648, 0.0051, 0.0035, 0.1965, 0.8000],  # Tie-line 3
    [0.7234, 0.2679, 0.0087, 0.0063, 0.3122, 0.6815],  # Tie-line 4
    [0.5562, 0.4249, 0.0189, 0.0128, 0.4758, 0.5114],  # Tie-line 5
    [0.3021, 0.6580, 0.0399, 0.0285, 0.7089, 0.2626],  # Tie-line 6
]

# Solubilidades mútuas do binário Benzene-Water
benzene_in_water = [0.0009, 0.0, 0.9991]   # x1, x2, x3 na fase aquosa
water_in_benzene = [0.9980, 0.0, 0.0020]   # x1, x2, x3 na fase orgânica

# ============================================================================
# FUNÇÕES AUXILIARES PARA DIAGRAMA TERNÁRIO
# ============================================================================

def ternary_to_cartesian(x1, x2, x3):
    """
    Converte coordenadas ternárias para cartesianas

    Sistema de coordenadas:
    - Vértice inferior esquerdo: Componente 3 (Water) = (0, 0)
    - Vértice inferior direito: Componente 1 (Benzene) = (1, 0)  
    - Vértice superior: Componente 2 (2-Propanol) = (0.5, √3/2)
    """
    x = 0.5 * (2*x2 + x1) / (x1 + x2 + x3)
    y = (np.sqrt(3)/2) * x1 / (x1 + x2 + x3)
    return x, y

def plot_ternary_grid(ax):
    """Plota grid do diagrama ternário"""

    # Linhas de grid a cada 10%
    for i in range(1, 10):
        val = i / 10.0

        # Linhas paralelas ao lado 1-3 (constante em x2)
        x_line = np.array([val, 0.5*(1 + val)])
        y_line = np.array([0, np.sqrt(3)/2 * (1-val)])
        ax.plot(x_line, y_line, 'k-', linewidth=0.3, alpha=0.3)

        # Linhas paralelas ao lado 2-3 (constante em x1)
        x_line = np.array([0.5*val, 0.5 + 0.5*val])
        y_line = np.array([np.sqrt(3)/2 * val, np.sqrt(3)/2 * (1-val)])
        ax.plot(x_line, y_line, 'k-', linewidth=0.3, alpha=0.3)

        # Linhas paralelas ao lado 1-2 (constante em x3)
        x_line = np.array([0.5*(1-val), 1-val])
        y_line = np.array([np.sqrt(3)/2 * (1-val), 0])
        ax.plot(x_line, y_line, 'k-', linewidth=0.3, alpha=0.3)

def plot_ternary_frame(ax):
    """Plota moldura do diagrama ternário"""

    # Triângulo externo
    triangle = np.array([
        [0, 0],      # Vértice 3 (Water)
        [1, 0],      # Vértice 1 (Benzene)
        [0.5, np.sqrt(3)/2],  # Vértice 2 (2-Propanol)
        [0, 0]       # Fechar
    ])
    ax.plot(triangle[:, 0], triangle[:, 1], 'k-', linewidth=2)

    # Labels dos componentes
    ax.text(0, -0.08, 'Water (3)', ha='center', va='top', fontsize=12, fontweight='bold')
    ax.text(1, -0.08, 'Benzene (1)', ha='center', va='top', fontsize=12, fontweight='bold')
    ax.text(0.5, np.sqrt(3)/2 + 0.05, '2-Propanol (2)', ha='center', va='bottom', 
            fontsize=12, fontweight='bold')

    # Labels nas escalas (0.0, 0.2, 0.4, ..., 1.0)
    for i in range(0, 11, 2):
        val = i / 10.0

        # Escala do componente 1 (Benzene) - lado inferior
        x, y = ternary_to_cartesian(val, 0, 1-val)
        ax.text(x, y-0.03, f'{val:.1f}', ha='center', va='top', fontsize=8)

        # Escala do componente 2 (2-Propanol) - lado esquerdo
        x, y = ternary_to_cartesian(0, val, 1-val)
        ax.text(x-0.03, y, f'{val:.1f}', ha='right', va='center', fontsize=8)

        # Escala do componente 3 (Water) - lado direito
        x, y = ternary_to_cartesian(1-val, val, 0)
        ax.text(x+0.03, y, f'{val:.1f}', ha='left', va='center', fontsize=8)

# ============================================================================
# CRIAR DIAGRAMA
# ============================================================================

print("Gerando diagrama ternário...")

fig, ax = plt.subplots(figsize=(10, 9))
ax.set_aspect('equal')
ax.axis('off')

# Plotar frame e grid
plot_ternary_frame(ax)
plot_ternary_grid(ax)

# ============================================================================
# PLOTAR DADOS EXPERIMENTAIS
# ============================================================================

# 1. Plotar solubilidades mútuas do binário
x_benz, y_benz = ternary_to_cartesian(*water_in_benzene)
x_water, y_water = ternary_to_cartesian(*benzene_in_water)
ax.plot([x_benz, x_water], [y_benz, y_water], 'b--', linewidth=1.5, 
        label='Binário Benzene-Water', alpha=0.7)
ax.plot(x_benz, y_benz, 'bs', markersize=8)
ax.plot(x_water, y_water, 'bs', markersize=8)

# 2. Plotar tie-lines experimentais
for i, tieline in enumerate(tielines_exp):
    x1_I, x2_I, x3_I, x1_II, x2_II, x3_II = tieline

    # Converter para coordenadas cartesianas
    x_I, y_I = ternary_to_cartesian(x1_I, x2_I, x3_I)
    x_II, y_II = ternary_to_cartesian(x1_II, x2_II, x3_II)

    # Plotar tie-line
    if i == 0:
        ax.plot([x_I, x_II], [y_I, y_II], 'r-', linewidth=1.5, 
                label='Tie-lines Experimentais', alpha=0.8)
    else:
        ax.plot([x_I, x_II], [y_I, y_II], 'r-', linewidth=1.5, alpha=0.8)

    # Plotar pontos nas extremidades
    ax.plot(x_I, y_I, 'ro', markersize=6)
    ax.plot(x_II, y_II, 'ro', markersize=6)

# 3. Desenhar curva binodal aproximada
phase_I_points = []
phase_II_points = []

for tieline in tielines_exp:
    x1_I, x2_I, x3_I, x1_II, x2_II, x3_II = tieline
    phase_I_points.append(ternary_to_cartesian(x1_I, x2_I, x3_I))
    phase_II_points.append(ternary_to_cartesian(x1_II, x2_II, x3_II))

# Adicionar pontos das solubilidades binárias
phase_I_points.insert(0, (x_benz, y_benz))
phase_II_points.insert(0, (x_water, y_water))

# Converter para arrays
phase_I_x = [p[0] for p in phase_I_points]
phase_I_y = [p[1] for p in phase_I_points]
phase_II_x = [p[0] for p in phase_II_points]
phase_II_y = [p[1] for p in phase_II_points]

# Plotar curvas binodais
ax.plot(phase_I_x, phase_I_y, 'g-', linewidth=2.5, label='Curva Binodal', alpha=0.9)
ax.plot(phase_II_x, phase_II_y, 'g-', linewidth=2.5, alpha=0.9)

# Conectar as duas fases
ax.plot([phase_I_x[-1], phase_II_x[-1]], [phase_I_y[-1], phase_II_y[-1]], 
        'g-', linewidth=2.5, alpha=0.9)

# ============================================================================
# ADICIONAR INFORMAÇÕES
# ============================================================================

# Título
ax.text(0.5, -0.20, 'Sistema 508: Benzene / 2-Propanol / Water', 
        ha='center', fontsize=14, fontweight='bold')
ax.text(0.5, -0.24, 'Sorensen et al. (1979) | T = 25C | Tipo 1', 
        ha='center', fontsize=11, style='italic')

# Legenda
ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.0), fontsize=10)

# Informações adicionais
info_text = 'Dados Experimentais:\n6 tie-lines\nResiduo UNIQUAC: 0.91 mol%\nResiduo NRTL: 4.72 mol%'
ax.text(0.5, -0.35, info_text, ha='center', va='top', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Ajustar limites
ax.set_xlim(-0.15, 1.15)
ax.set_ylim(-0.45, 1.0)

plt.tight_layout()

# Salvar figura
plt.savefig('diagrama_ternario_sistema508.png', dpi=300, bbox_inches='tight')
print("Diagrama salvo em: diagrama_ternario_sistema508.png")

# Mostrar figura
plt.show()

# ============================================================================
# ESTATÍSTICAS DO SISTEMA
# ============================================================================

print("\n" + "="*70)
print("ESTATISTICAS DO SISTEMA 508")
print("="*70)

print(f"\nComponentes:")
print(f"  1. Benzene")
print(f"  2. 2-Propanol") 
print(f"  3. Water")

print(f"\nSolubilidades mutuas (binario 1-3):")
print(f"  Benzene em Water: x1 = {benzene_in_water[0]:.4f} (0.09 mol%)")
print(f"  Water em Benzene: x3 = {water_in_benzene[2]:.4f} (0.20 mol%)")

print(f"\nNumero de tie-lines: {len(tielines_exp)}")

print(f"\nFaixa de composicao (Fase I - rica em Benzene):")
print(f"  x1: {tielines_exp[-1][0]:.4f} - {tielines_exp[0][0]:.4f}")
print(f"  x2: {tielines_exp[0][1]:.4f} - {tielines_exp[-1][1]:.4f}")

print(f"\nFaixa de composicao (Fase II - rica em Water):")
print(f"  x2: {tielines_exp[0][4]:.4f} - {tielines_exp[-1][4]:.4f}")
print(f"  x3: {tielines_exp[-1][5]:.4f} - {tielines_exp[0][5]:.4f}")

print(f"\nCoeficiente de distribuicao do soluto (beta = x2_I / x2_II):")
for i, tieline in enumerate(tielines_exp, 1):
    beta = tieline[1] / tieline[4]
    print(f"  Tie-line {i}: beta = {beta:.4f}")

print(f"\nDesempenho dos modelos:")
print(f"  UNIQUAC (4 params): 0.91 mol%  <- MELHOR")
print(f"  NRTL (alpha=0.2):   4.72 mol%")
print(f"  Predicao UNIQUAC:   0.55 mol%")

print(f"\nReferencia:")
print(f"  Nikurashina, N.I. et al.")
print(f"  J. Gen. Chem. USSR (Engl. Transl.), 43 (1973) 2093")

print("\n" + "="*70)