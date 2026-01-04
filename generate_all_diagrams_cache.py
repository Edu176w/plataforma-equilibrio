"""
Gerador de Cache Completo para Diagramas Ternários ELL
Pré-calcula TODOS os sistemas NRTL e UNIQUAC disponíveis
"""
import os
import json
import pickle
import time
from pathlib import Path
from datetime import datetime

# Importar após configurar path
import sys
sys.path.insert(0, os.path.abspath('.'))

from app.calculators.ell_calculator import generate_ternary_diagram_ell

# Criar diretório para cache
CACHE_DIR = Path("static/cache/diagrams")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# TODOS OS SISTEMAS NRTL - TABELA E-5 PRAUSNITZ
# ============================================================
NRTL_SYSTEMS = [
    {
        'name': 'Water + 1,1,2-Trichloroethane + Acetone (25°C)',
        'components': ['Water', '1,1,2-Trichloroethane', 'Acetone'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-5, Bender & Block (1975)'
    },
    {
        'name': 'Water + Toluene + Acetic Acid (25°C)',
        'components': ['Water', 'Toluene', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-5'
    },
    {
        'name': 'Water + MIBK + Acetic Acid (25°C)',
        'components': ['Water', 'MIBK', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-5'
    },
    {
        'name': 'Water + Ethyl Acetate + Acetic Acid (25°C)',
        'components': ['Water', 'Ethyl Acetate', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-5'
    },
    {
        'name': 'Water + Cyclohexane + Ethanol (25°C)',
        'components': ['Water', 'Cyclohexane', 'Ethanol'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-5'
    },
]

# ============================================================
# TODOS OS SISTEMAS UNIQUAC - TABELA E-6 PRAUSNITZ
# ============================================================
UNIQUAC_SYSTEMS = [
    {
        'name': 'Furfural + Cyclohexane + Benzene (25°C)',
        'components': ['Furfural', 'Cyclohexane', 'Benzene'],
        'temperature': 25.0,
        'model': 'UNIQUAC',
        'ntielines': 6,
        'reference': 'Prausnitz Table E-6, System 1 (Anderson & Prausnitz, 1978a)'
    },
    {
        'name': 'Sulfolane + n-Octane + Toluene (25°C)',
        'components': ['Sulfolane', 'n-Octane', 'Toluene'],
        'temperature': 25.0,
        'model': 'UNIQUAC',
        'ntielines': 6,
        'reference': 'Prausnitz Table E-6, System 2 (Anderson & Prausnitz, 1978a)'
    },
    {
        'name': '2,5-Hexanedione + 1-Hexene + n-Hexane (25°C)',
        'components': ['2,5-Hexanedione', '1-Hexene', 'n-Hexane'],
        'temperature': 25.0,
        'model': 'UNIQUAC',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-6, System 3 (Anderson & Prausnitz, 1978a)'
    },
    {
        'name': '1,4-Dioxane + n-Hexane + Methylcyclopentane (25°C)',
        'components': ['1,4-Dioxane', 'n-Hexane', 'Methylcyclopentane'],
        'temperature': 25.0,
        'model': 'UNIQUAC',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-6, System 4 (Anderson & Prausnitz, 1978a)'
    },
]

# ============================================================
# SISTEMAS ADICIONAIS EM OUTRAS TEMPERATURAS
# ============================================================
ADDITIONAL_SYSTEMS = [
    {
        'name': 'Water + 1,1,2-Trichloroethane + Acetone (30°C)',
        'components': ['Water', '1,1,2-Trichloroethane', 'Acetone'],
        'temperature': 30.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-5 (extrapolated)'
    },
    {
        'name': 'Water + 1,1,2-Trichloroethane + Acetone (20°C)',
        'components': ['Water', '1,1,2-Trichloroethane', 'Acetone'],
        'temperature': 20.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Prausnitz Table E-5 (extrapolated)'
    },
]

# Combinar todos os sistemas
ALL_SYSTEMS = NRTL_SYSTEMS + UNIQUAC_SYSTEMS + ADDITIONAL_SYSTEMS

def generate_cache_key(components, temperature, model):
    """Mesma função do ell.py"""
    comp_sorted = sorted(components)
    comp_str = "-".join(comp_sorted)
    return f"{comp_str}_{temperature:.1f}_{model}"

def main():
    print("="*80)
    print("GERADOR DE CACHE COMPLETO - DIAGRAMAS TERNÁRIOS ELL")
    print("="*80)
    print(f"Total de sistemas a processar: {len(ALL_SYSTEMS)}")
    print(f"- NRTL: {len(NRTL_SYSTEMS)} sistemas")
    print(f"- UNIQUAC: {len(UNIQUAC_SYSTEMS)} sistemas")
    print(f"- Adicionais: {len(ADDITIONAL_SYSTEMS)} sistemas")
    print(f"Cache será salvo em: {CACHE_DIR.absolute()}")
    print("="*80)
    
    start_time_total = time.time()
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for idx, system in enumerate(ALL_SYSTEMS, 1):
        components = system['components']
        temperature = system['temperature']
        model = system['model']
        ntielines = system['ntielines']
        name = system['name']
        reference = system['reference']
        
        cache_key = generate_cache_key(components, temperature, model)
        filename = CACHE_DIR / f"{cache_key}.json"
        
        print(f"\n[{idx}/{len(ALL_SYSTEMS)}] {name}")
        print(f"  Componentes: {' + '.join(components)}")
        print(f"  Modelo: {model}, T={temperature}°C, Tie-lines={ntielines}")
        print(f"  Referência: {reference}")
        
        # Verificar se já existe
        if filename.exists():
            file_size = filename.stat().st_size / 1024
            print(f"  ⏭️  JÁ EXISTE: {cache_key[:40]}... ({file_size:.1f} KB)")
            skipped_count += 1
            continue
        
        try:
            # Calcular diagrama
            start_time = time.time()
            print(f"  ⏳ Calculando...")
            
            result = generate_ternary_diagram_ell(
                components=components,
                temperature_C=temperature,
                model=model,
                n_tie_lines=ntielines
            )
            
            elapsed = time.time() - start_time
            
            if result['success']:
                res = result['results']
                n_binodal = res.get('n_binodal_points', 0)
                n_tielines = res.get('n_tie_lines', 0)
                
                # ACEITAR SE TIVER TIE-LINES, MESMO SEM BINODAL
                if n_tielines > 0:
                    print(f"  ✅ GERADO em {elapsed:.1f}s: {n_binodal} pontos binodal, {n_tielines} tie-lines")
                    
                    if n_binodal == 0:
                        print(f"  ⚠️  AVISO: Binodal não gerada (algoritmo não convergiu), mas tie-lines são válidas")
                    
                    # Salvar como JSON
                    cache_data = {
                        'success': True,
                        'results': res,
                        'aisuggestion': result.get('aisuggestion'),
                        'from_cache': True,
                        'precomputed': True,
                        'metadata': {
                            'generated_at': datetime.utcnow().isoformat(),
                            'cache_key': cache_key,
                            'system_name': name,
                            'reference': reference,
                            'computation_time_seconds': round(elapsed, 2),
                            'binodal_available': n_binodal > 0,
                            'tielines_count': n_tielines
                        }
                    }
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    
                    file_size = filename.stat().st_size / 1024
                    print(f"  💾 SALVO: {cache_key[:40]}... ({file_size:.1f} KB)")
                    success_count += 1
                else:
                    print(f"  ❌ ERRO: Nenhuma tie-line válida gerada")
                    error_count += 1
            else:
                error_msg = result.get('error', 'Erro desconhecido')
                print(f"  ❌ ERRO: {error_msg}")
                error_count += 1
        
        except Exception as e:
            print(f"  ❌ EXCEÇÃO: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1
    
    # Resumo final
    elapsed_total = time.time() - start_time_total
    minutes = int(elapsed_total // 60)
    seconds = int(elapsed_total % 60)
    
    print("\n" + "="*80)
    print("📊 RESUMO DA GERAÇÃO DE CACHE")
    print("="*80)
    print(f"✅ Sucesso:  {success_count}/{len(ALL_SYSTEMS)} sistemas")
    print(f"⏭️  Pulados:  {skipped_count}/{len(ALL_SYSTEMS)} sistemas (já existiam)")
    print(f"❌ Erros:    {error_count}/{len(ALL_SYSTEMS)} sistemas")
    print(f"⏱️  Tempo total: {minutes}m {seconds}s")
    print(f"📁 Cache salvo em: {CACHE_DIR.absolute()}")
    print(f"📊 Total de arquivos: {len(list(CACHE_DIR.glob('*.json')))}")
    
    # Listar arquivos gerados
    if success_count > 0:
        print("\n📦 Arquivos gerados:")
        for json_file in sorted(CACHE_DIR.glob('*.json')):
            size_kb = json_file.stat().st_size / 1024
            print(f"  • {json_file.name} ({size_kb:.1f} KB)")
    
    print("="*80)
    
    if error_count > 0:
        print(f"\n⚠️  ATENÇÃO: {error_count} sistemas falharam. Verifique os erros acima.")
        return 1
    else:
        print("\n🎉 CACHE GERADO COM SUCESSO!")
        print("Faça commit e push para o Render:")
        print("  git add static/cache/diagrams/")
        print("  git commit -m 'Add pre-calculated ternary diagrams cache'")
        print("  git push")
        return 0

if __name__ == '__main__':
    exit(main())
