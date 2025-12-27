"""
Script para ENCONTRAR onde os arquivos TSV realmente estão
"""

import os

print("=" * 80)
print("BUSCANDO ARQUIVOS TSV NA BIBLIOTECA THERMO")
print("=" * 80)

from thermo import interaction_parameters
thermo_path = os.path.dirname(interaction_parameters.__file__)

print(f"\nCaminho base da thermo: {thermo_path}")

# Buscar RECURSIVAMENTE
print("\n" + "=" * 80)
print("BUSCA RECURSIVA POR ARQUIVOS TSV:")
print("=" * 80)

tsv_files = []

for root, dirs, files in os.walk(thermo_path):
    for file in files:
        if file.endswith('.tsv'):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, thermo_path)
            size = os.path.getsize(full_path)
            tsv_files.append({
                'name': file,
                'full_path': full_path,
                'rel_path': rel_path,
                'size': size
            })

print(f"\n✓ Encontrados {len(tsv_files)} arquivos TSV")

if len(tsv_files) > 0:
    print("\n" + "=" * 80)
    print("ARQUIVOS RELEVANTES PARA UNIFAC:")
    print("=" * 80)

    # Filtrar arquivos UNIFAC relevantes
    unifac_files = [f for f in tsv_files if 'UNIFAC' in f['name']]

    for f in unifac_files:
        print(f"\n📄 {f['name']}")
        print(f"   Caminho completo: {f['full_path']}")
        print(f"   Caminho relativo: {f['rel_path']}")
        print(f"   Tamanho: {f['size']:,} bytes")

    print("\n" + "=" * 80)
    print("ARQUIVO DDBST:")
    print("=" * 80)

    ddbst_files = [f for f in tsv_files if 'DDBST' in f['name']]
    for f in ddbst_files:
        print(f"\n📄 {f['name']}")
        print(f"   Caminho completo: {f['full_path']}")
        print(f"   Caminho relativo: {f['rel_path']}")
        print(f"   Tamanho: {f['size']:,} bytes")

    # Salvar paths em arquivo para usar depois
    import json

    paths_info = {
        'unifac_original': None,
        'unifac_lle': None,
        'ddbst': None
    }

    for f in tsv_files:
        if f['name'] == 'UNIFAC original interaction parameters.tsv':
            paths_info['unifac_original'] = f['full_path']
        elif f['name'] == 'UNIFAC LLE interaction parameters.tsv':
            paths_info['unifac_lle'] = f['full_path']
        elif f['name'] == 'DDBST UNIFAC assignments.tsv':
            paths_info['ddbst'] = f['full_path']

    with open('tsv_paths.json', 'w') as fp:
        json.dump(paths_info, fp, indent=2)

    print("\n" + "=" * 80)
    print("CAMINHOS SALVOS EM: tsv_paths.json")
    print("=" * 80)

    for key, path in paths_info.items():
        if path:
            print(f"  ✓ {key}: ENCONTRADO")
        else:
            print(f"  ✗ {key}: NÃO ENCONTRADO")

else:
    print("\n⚠ NENHUM ARQUIVO TSV ENCONTRADO!")
    print("  Isso pode indicar um problema com a instalação da biblioteca thermo")