from thermo.chemical import Chemical

# Buscar Methyl Ethyl Ketone
print('\n🔍 Buscando Methyl Ethyl Ketone (MEK):')
print('='*70)
try:
    # Testar vários aliases
    aliases = [
        'methyl ethyl ketone',
        'MEK',
        'butanone',
        '2-butanone',
        'ethyl methyl ketone',
    ]
    
    for alias in aliases:
        try:
            chem = Chemical(alias)
            print(f'✅ ENCONTRADO: "{alias}"')
            print(f'   Nome: {chem.name}')
            print(f'   CAS: {chem.CAS}')
            print(f'   Formula: {chem.formula}')
            print(f'   MW: {chem.MW}')
            break
        except:
            print(f'❌ "{alias}" não encontrado')
except Exception as e:
    print(f'Erro: {e}')

# Buscar Methyl Isobutyl Ketone
print('\n🔍 Buscando Methyl Isobutyl Ketone (MIBK):')
print('='*70)
try:
    aliases = [
        'methyl isobutyl ketone',
        'MIBK',
        '4-methyl-2-pentanone',
        'isobutyl methyl ketone',
        'hexone',
    ]
    
    for alias in aliases:
        try:
            chem = Chemical(alias)
            print(f'✅ ENCONTRADO: "{alias}"')
            print(f'   Nome: {chem.name}')
            print(f'   CAS: {chem.CAS}')
            print(f'   Formula: {chem.formula}')
            print(f'   MW: {chem.MW}')
            break
        except:
            print(f'❌ "{alias}" não encontrado')
except Exception as e:
    print(f'Erro: {e}')
