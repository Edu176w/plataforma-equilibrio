"""
Teste FINAL - Sistemas validados do artigo Abrams & Prausnitz (1975)
"""
from app.calculators.ell_calculator import run_lle_flash, run_ternary_diagram

print("=" * 70)
print("TESTE 1: Sistema Binário - Acetone-Chloroform (Pair #15)")
print("=" * 70)

result1 = run_lle_flash(
    components=['acetone', 'chloroform'],
    temperature=50.0,  # Temperatura da Tabela 4
    model='UNIQUAC',
    compositions=[0.5, 0.5]
)
print(f"Status: {result1['success']}")
print(f"Mensagem: {result1.get('error', 'OK')}\n")

print("=" * 70)
print("TESTE 2: Sistema Binário - Water-MEK (Pair #11)")
print("=" * 70)

result2 = run_lle_flash(
    components=['water', 'methyl ethyl ketone'],
    temperature=25.0,
    model='UNIQUAC',
    compositions=[0.5, 0.5]
)
print(f"Status: {result2['success']}")
print(f"Mensagem: {result2.get('error', 'OK')}\n")

print("=" * 70)
print("TESTE 3: Sistema Ternário - Benzene-Hexane-MCP")
print("=" * 70)

result3 = run_ternary_diagram(
    components=['benzene', 'hexane', 'methylcyclopentane'],
    temperature=50.0,
    model='UNIQUAC',
    n_points=30,
    n_tielines=5
)
print(f"Status: {result3['success']}")
print(f"Aproximado: {result3['results'].get('approximate', 'N/A')}")
print(f"Pontos binodal: {len(result3['results'].get('binodal_a', []))}")
print("=" * 70)
