import json
from datetime import datetime, timedelta

# Ler JSON atual
with open('app/data/simulation_history.json', 'r') as f:
    simulations = json.load(f)

print(f"Simulações antes: {len(simulations)}")

# Adicionar 10 simulações de teste de HOJE
agora = datetime.now()
modelos = ['Ideal', 'NRTL', 'UNIQUAC', 'UNIFAC']
componentes_lista = [
    ['Ethanol', 'Water'],
    ['Acetone', 'Methanol'],
    ['Benzene', 'Toluene'],
    ['Water', 'Acetic Acid']
]

for i in range(10):
    # Criar timestamps diferentes ao longo do dia
    timestamp = agora - timedelta(hours=10-i, minutes=i*3)
    componentes = componentes_lista[i % len(componentes_lista)]
    
    nova_sim = {
        "id": timestamp.strftime('%Y%m%d%H%M%S%f')[:-3],
        "timestamp": timestamp.isoformat(),
        "module": "elv",
        "calculation_type": "bubble",
        "model": modelos[i % len(modelos)],
        "components": componentes,
        "conditions": {
            "components": [c.lower() for c in componentes],
            "model": modelos[i % len(modelos)],
            "compositions": [0.5, 0.5],
            "temperature": 80,
            "temperature_unit": "C"
        },
        "results": {
            "P (kPa)": 100.5 + i * 5,
            "T (C)": 80,
            "gamma1": 1.0 + i * 0.01,
            "gamma2": 1.0 + i * 0.01,
            "x1": 0.5,
            "x2": 0.5,
            "y1": 0.6,
            "y2": 0.4
        },
        "execution_time": 0.01 + i * 0.001,
        "success": True,
        "error_message": None
    }
    simulations.append(nova_sim)

# Salvar de volta
with open('app/data/simulation_history.json', 'w', encoding='utf-8') as f:
    json.dump(simulations, f, indent=2, ensure_ascii=False)

print(f"✅ Simulações depois: {len(simulations)}")
print(f"✅ Adicionadas 10 simulações de teste para hoje!")

# Verificar
hoje_str = datetime.now().strftime('%Y-%m-%d')
hoje_count = sum(1 for sim in simulations if hoje_str in sim.get('timestamp', ''))
print(f"\n📊 Simulações hoje ({hoje_str}): {hoje_count}")
print(f"📊 Total geral: {len(simulations)}")

# Mostrar as últimas 3
print("\n3 mais recentes:")
for sim in sorted(simulations, key=lambda x: x['timestamp'], reverse=True)[:3]:
    print(f"  {sim['timestamp']} - {sim['module'].upper()} - {sim['model']} - {sim['components']}")
