from app.data.uniquac_params import UNIQUAC_R_Q, UNIQUAC_PARAMS, COMPONENT_TRANSLATIONS

print('\n' + '='*75)
print('VERIFICACAO DE PARAMETROS UNIQUAC')
print('='*75)

print(f'\n📊 COMPONENTES COM r e q: {len(UNIQUAC_R_Q)}')
print('-'*75)
for comp, params in sorted(UNIQUAC_R_Q.items()):
    traduzido = COMPONENT_TRANSLATIONS.get(comp, comp.title())
    print(f'  {traduzido:30s} r={params["r"]:5.2f}  q={params["q"]:5.2f}')

print(f'\n🔗 PARES BINARIOS: {len(UNIQUAC_PARAMS)}')
print('-'*75)
for (c1, c2), params in sorted(UNIQUAC_PARAMS.items()):
    t1 = COMPONENT_TRANSLATIONS.get(c1, c1.title())
    t2 = COMPONENT_TRANSLATIONS.get(c2, c2.title())
    print(f'  {t1:30s} / {t2:30s}  a12={params["a12"]:8.2f}  a21={params["a21"]:8.2f}')

print('\n' + '='*75)
print('VERIFICACAO DOS SISTEMAS DA FIGURA 6-23 (PRAUSNITZ)')
print('='*75)

# Sistema (a)
if ('propionic acid', 'methyl isobutyl ketone') in UNIQUAC_PARAMS:
    print('✅ Sistema 6-23(a): Propionic acid / MIBK ENCONTRADO')
else:
    print('❌ Sistema 6-23(a): Propionic acid / MIBK NAO ENCONTRADO')

# Sistema (b)
if ('formic acid', 'acetic acid') in UNIQUAC_PARAMS:
    print('✅ Sistema 6-23(b): Formic acid / Acetic acid ENCONTRADO')
else:
    print('❌ Sistema 6-23(b): Formic acid / Acetic acid NAO ENCONTRADO')

print('='*75 + '\n')
