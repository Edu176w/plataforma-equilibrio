# teste_praunitz_FINAL.py
"""
Teste SIMPLIFICADO dos exemplos do Prausnitz
"""
import sys
sys.path.append('app')

from calculators.esl_calculator import ESLCalculator

calc = ESLCalculator()

print("="*80)
print("DIAGNÓSTICO: Por que x2 está dando 0?")
print("="*80)

# Teste básico
resultado = calc.solubility(
    components=['naphthalene', 'benzene'],
    temperature_C=25.0,
    model='Ideal'
)

print("\nComponentes: ['naphthalene', 'benzene']")
print("T = 25°C")
print("\nResultado completo:")
for key, value in resultado.items():
    print(f"  {key}: {value}")

print("\n" + "="*80)
print("PROBLEMA IDENTIFICADO:")
print("="*80)
print("""
O método está retornando:
  - x1 (naphthalene) = 0.0  ← SÓLIDO
  - x2 (benzene) = 1.0      ← LÍQUIDO

Mas deveria calcular:
  - Solubilidade do naftaleno (sólido) dissolvido no benzeno (líquido)
  - Esperado: x_naftaleno ≈ 0.33 (33% de naftaleno dissolvido)

SOLUÇÃO:
  O método está identificando QUAL componente está sólido,
  mas não está calculando a SOLUBILIDADE dele no líquido.
  
  Para resolver, precisamos verificar a lógica interna do método.
""")

print("\n" + "="*80)
print("TESTE ALTERNATIVO: Diagrama TX")
print("="*80)

resultado_tx = calc.generate_tx_diagram(
    components=['naphthalene', 'biphenyl'],
    model='Ideal',
    n_points=10
)

print("\nChaves do diagrama TX:")
for key in resultado_tx.keys():
    print(f"  - {key}")

if 'x_eutectic' in resultado_tx:
    print(f"\nPonto eutético:")
    print(f"  x1 = {resultado_tx['x_eutectic']:.3f}")
    print(f"  T = {resultado_tx['T_eutectic_C']:.1f}°C")

print("\n" + "="*80)
print("TESTE: Cristalização com lista simples")
print("="*80)

try:
    # Forma correta: passar lista de frações molares
    resultado_cryst = calc.crystallization(
        components=['naphthalene', 'benzene'],
        compositions=[0.3, 0.7],  # x1=0.3, x2=0.7
        model='Ideal'
    )
    
    print("✅ Funcionou com lista!")
    print(f"  T de cristalização: {resultado_cryst.get('T_C', 'N/A')}°C")
    
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*80)
print("CONCLUSÃO")
print("="*80)
print("""
O método solubility() está calculando:
  - QUEM está sólido e QUEM está líquido a uma dada T
  
Mas NÃO está calculando:
  - QUANTO do sólido se dissolve no líquido
  
Para os exemplos do Prausnitz funcionarem, o método precisa:
  1. Identificar que naftaleno está sólido (T < Tm)
  2. CALCULAR solubilidade usando Eq. 11-15
  3. Retornar x2_soluto (não apenas 0 ou 1)

Verifique a implementação do método solubility() no esl_calculator.py
""")
