"""
Script para investigar a estrutura dos arquivos TSV
"""

import json
import csv
import os

print("=" * 80)
print("INVESTIGANDO ESTRUTURA DOS ARQUIVOS TSV")
print("=" * 80)

# Carregar caminhos
with open('tsv_paths.json', 'r') as f:
    tsv_paths = json.load(f)

# ==============================================================================
# INVESTIGAR UNIFAC ORIGINAL
# ==============================================================================
print("\n" + "=" * 80)
print("[1] UNIFAC ORIGINAL")
print("=" * 80)

unifac_original_path = tsv_paths['unifac_original']

if unifac_original_path and os.path.exists(unifac_original_path):
    print(f"Arquivo: {os.path.basename(unifac_original_path)}")
    print(f"Tamanho: {os.path.getsize(unifac_original_path):,} bytes")

    with open(unifac_original_path, 'r', encoding='utf-8') as f:
        # Ler primeiras 5 linhas
        print("\nPrimeiras 5 linhas do arquivo:")
        print("-" * 80)
        for i in range(5):
            line = f.readline()
            print(f"{i+1}: {line.strip()}")
        print("-" * 80)

        # Voltar ao início e ler como CSV
        f.seek(0)

        # Tentar detectar delimitador
        sample = f.read(1024)
        f.seek(0)

        print(f"\nDetecção de delimitador:")
        print(f"  Tabs (\\t): {sample.count(chr(9))}")
        print(f"  Vírgulas (,): {sample.count(',')}")
        print(f"  Pontos-e-vírgulas (;): {sample.count(';')}")

        # Ler como TSV
        reader = csv.DictReader(f, delimiter='\t')

        print(f"\nCabeçalho (fieldnames):")
        print(f"  {reader.fieldnames}")

        print(f"\nPrimeiros 3 registros:")
        for i, row in enumerate(reader):
            if i >= 3:
                break
            print(f"\n  Registro {i+1}:")
            for key, val in row.items():
                print(f"    {key}: {val}")

# ==============================================================================
# INVESTIGAR UNIFAC LLE
# ==============================================================================
print("\n" + "=" * 80)
print("[2] UNIFAC LLE")
print("=" * 80)

unifac_lle_path = tsv_paths['unifac_lle']

if unifac_lle_path and os.path.exists(unifac_lle_path):
    print(f"Arquivo: {os.path.basename(unifac_lle_path)}")
    print(f"Tamanho: {os.path.getsize(unifac_lle_path):,} bytes")

    with open(unifac_lle_path, 'r', encoding='utf-8') as f:
        print("\nPrimeiras 5 linhas:")
        print("-" * 80)
        for i in range(5):
            line = f.readline()
            print(f"{i+1}: {line.strip()}")
        print("-" * 80)

        f.seek(0)
        reader = csv.DictReader(f, delimiter='\t')

        print(f"\nCabeçalho: {reader.fieldnames}")

        print(f"\nPrimeiros 3 registros:")
        for i, row in enumerate(reader):
            if i >= 3:
                break
            print(f"\n  Registro {i+1}:")
            for key, val in row.items():
                print(f"    {key}: {val}")

# ==============================================================================
# INVESTIGAR DDBST
# ==============================================================================
print("\n" + "=" * 80)
print("[3] DDBST UNIFAC ASSIGNMENTS")
print("=" * 80)

ddbst_path = tsv_paths['ddbst']

if ddbst_path and os.path.exists(ddbst_path):
    print(f"Arquivo: {os.path.basename(ddbst_path)}")
    print(f"Tamanho: {os.path.getsize(ddbst_path):,} bytes")

    with open(ddbst_path, 'r', encoding='utf-8') as f:
        print("\nPrimeiras 3 linhas:")
        print("-" * 80)
        for i in range(3):
            line = f.readline()
            # Mostrar só primeiros 200 chars
            print(f"{i+1}: {line.strip()[:200]}...")
        print("-" * 80)

        f.seek(0)
        reader = csv.DictReader(f, delimiter='\t')

        print(f"\nCabeçalho (primeiras 20 colunas):")
        print(f"  {reader.fieldnames[:20]}")

        print(f"\nPrimeiro registro (primeiros campos):")
        first_row = next(reader)
        for i, (key, val) in enumerate(first_row.items()):
            if i >= 20:
                print(f"  ... ({len(first_row)} campos no total)")
                break
            print(f"  {key}: {val}")

print("\n" + "=" * 80)
print("INVESTIGAÇÃO CONCLUÍDA")
print("=" * 80)