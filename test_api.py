import requests
import json

BASE_URL = 'http://localhost:5000'

print('='*70)
print('TESTES DA PLATAFORMA DE EQUILÍBRIO DE FASES')
print('='*70)

# Teste 1: Ponto de Bolha - Água-Etanol (Ideal)
print('\n1. Ponto de Bolha - Água-Etanol (Modelo Ideal)')
print('-'*70)
data = {
    'components': ['Água', 'Etanol'],
    'x': [0.3, 0.7],
    'temperature': 353.15,
    'model': 'ideal'
}
response = requests.post(f'{BASE_URL}/elv/bubble-point', json=data)
print(f'Status Code: {response.status_code}')
print(f'Response Text: {response.text}')

try:
    result = response.json()
    if result['success']:
        r = result['result']
        print(f'Temperatura: {r["temperature"]-273.15:.2f} °C')
        print(f'Pressão: {r["pressure"]/1000:.2f} kPa')
        print(f'x = {r["x"]}')
        print(f'y = {r["y"]}')
    else:
        print(f'Erro: {result["error"]}')
except Exception as e:
    print(f'Erro ao decodificar JSON: {e}')
