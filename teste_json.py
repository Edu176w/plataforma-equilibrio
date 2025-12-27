import json
from datetime import datetime

# Ler o JSON
with open('app/data/simulation_history.json', 'r') as f:
    data = json.load(f)

print(f"Total de simulações: {len(data)}")

# Contar por data
hoje_str = datetime.now().strftime('%Y-%m-%d')
hoje_count = sum(1 for sim in data if hoje_str in sim.get('timestamp', ''))
print(f"Simulações hoje ({hoje_str}): {hoje_count}")

# Mostrar as 3 mais recentes
print("\n3 mais recentes:")
for sim in sorted(data, key=lambda x: x['timestamp'], reverse=True)[:3]:
    print(f"  {sim['timestamp']} - {sim['module'].upper()} - {sim['model']} - {sim['components']}")
