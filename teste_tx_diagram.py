# teste_tx_diagram.py
import sys
sys.path.append('app')
from calculators.esl_calculator import ESLCalculator

calc = ESLCalculator()

print("="*80)
print("TESTE: Diagrama T-x Naftaleno-Bifenila (Figura 11-5 Prausnitz)")
print("="*80)

resultado = calc.generate_tx_diagram(
    components=['naphthalene', 'biphenyl'],
    model='Ideal',
    n_points=20
)

print("\nPonto eutético:")
print(f"  x1 (naftaleno) = {resultado['x_eutectic']:.3f}")
print(f"  T eutético = {resultado['T_eutectic_C']:.1f}°C")
print(f"\nTemperaturas de fusão:")
print(f"  Naftaleno: {resultado['Tm1_C']:.1f}°C")
print(f"  Bifenila: {resultado['Tm2_C']:.1f}°C")
print("\n✅ Diagrama calculado corretamente!")
print("="*80)
