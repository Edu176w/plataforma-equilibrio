"""
Gerador de Cache Completo para Diagramas Ternários ELL
Pré-calcula TODOS os sistemas NRTL, UNIQUAC e principais UNIFAC
Versão: 2.0 - Completa com todos os sistemas validados
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime
import sys
import traceback

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath('.'))

# Importar após configurar path
from app.calculators.ell_calculator import ELLCalculator
import numpy as np

# Criar diretório para cache
CACHE_DIR = Path("app/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# TODOS OS SISTEMAS NRTL - TABELA E-5 PRAUSNITZ + VALIDADOS
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
        'name': 'Water + 1-Butanol + Acetone (25°C)',
        'components': ['Water', '1-Butanol', 'Acetone'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Santos et al. (2001), Fluid Phase Equilib. 187:265-274'
    },
    {
        'name': 'Water + Toluene + Aniline (25°C)',
        'components': ['Water', 'Toluene', 'Aniline'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Grenner et al. (2006), J. Chem. Eng. Data 51(3):1009-1014'
    },
    {
        'name': 'Water + Chloroform + Acetic Acid (25°C)',
        'components': ['Water', 'Chloroform', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'Moura & Santos (2012), Am. J. Phys. Chem. 1(5):96-101'
    },
    {
        'name': 'Water + Cyclohexane + Ethanol (25°C) ⭐ VALIDADO',
        'components': ['Water', 'Cyclohexane', 'Ethanol'],
        'temperature': 25.0,
        'model': 'NRTL',
        'ntielines': 6,
        'reference': 'Plačkov (1992), Fluid Phase Equilib. - DADOS EXPERIMENTAIS COMPLETOS'
    },
]

# ============================================================
# TODOS OS SISTEMAS UNIQUAC - TABELA E-6 PRAUSNITZ + NOVOS
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
    {
        'name': 'Water + Chloroform + Acetic Acid (25°C) - UNIQUAC',
        'components': ['Water', 'Chloroform', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'UNIQUAC',
        'ntielines': 5,
        'reference': 'Moura & Santos (2012) - UNIQUAC PREFERIDO para este sistema'
    },
    {
        'name': 'Water + Ethyl Acetate + Acetic Acid (25°C) - UNIQUAC',
        'components': ['Water', 'Ethyl Acetate', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'UNIQUAC',
        'ntielines': 5,
        'reference': 'DECHEMA (1980), Magnussen et al. (1981)'
    },
    {
        'name': 'Water + MIBK + Acetic Acid (25°C) - UNIQUAC',
        'components': ['Water', 'MIBK', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'UNIQUAC',
        'ntielines': 5,
        'reference': 'Senol (2004), J. Chem. Eng. Data 49(6):1815-1820'
    },
]

# ============================================================
# SISTEMAS UNIFAC - PREDITIVOS (SEM PARÂMETROS BINÁRIOS)
# ============================================================
UNIFAC_SYSTEMS = [
    {
        'name': 'Water + Benzene + Ethanol (25°C) - UNIFAC',
        'components': ['Water', 'Benzene', 'Ethanol'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Sistema clássico água-aromático-álcool'
    },
    {
        'name': 'Water + Toluene + Ethanol (25°C) - UNIFAC',
        'components': ['Water', 'Toluene', 'Ethanol'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Extração com etanol'
    },
    {
        'name': 'Water + Toluene + Acetic Acid (25°C) - UNIFAC',
        'components': ['Water', 'Toluene', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Comparação com NRTL'
    },
    {
        'name': 'Water + n-Hexane + Ethanol (25°C) - UNIFAC',
        'components': ['Water', 'n-Hexane', 'Ethanol'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Sistema água-alcano-álcool'
    },
    {
        'name': 'Water + n-Heptane + 1-Propanol (25°C) - UNIFAC',
        'components': ['Water', 'n-Heptane', '1-Propanol'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Sistema com álcool de cadeia média'
    },
    {
        'name': 'Water + Cyclohexane + Ethanol (25°C) - UNIFAC',
        'components': ['Water', 'Cyclohexane', 'Ethanol'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 6,
        'reference': 'UNIFAC Preditivo - Comparação com NRTL experimental'
    },
    {
        'name': 'Water + n-Hexane + Acetone (25°C) - UNIFAC',
        'components': ['Water', 'n-Hexane', 'Acetone'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Sistema água-alcano-cetona'
    },
    {
        'name': 'Water + Toluene + Acetone (25°C) - UNIFAC',
        'components': ['Water', 'Toluene', 'Acetone'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Sistema água-aromático-cetona'
    },
    {
        'name': 'Water + MIBK + Acetic Acid (25°C) - UNIFAC',
        'components': ['Water', 'MIBK', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Comparação com NRTL/UNIQUAC'
    },
    {
        'name': 'Water + n-Hexane + Ethyl Acetate (25°C) - UNIFAC',
        'components': ['Water', 'n-Hexane', 'Ethyl Acetate'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Sistema água-alcano-éster'
    },
    {
        'name': 'Water + Ethyl Acetate + Acetic Acid (25°C) - UNIFAC',
        'components': ['Water', 'Ethyl Acetate', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Comparação com NRTL/UNIQUAC'
    },
    {
        'name': 'Water + Toluene + Ethyl Acetate (25°C) - UNIFAC',
        'components': ['Water', 'Toluene', 'Ethyl Acetate'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Sistema aromático-éster'
    },
    {
        'name': 'Water + Chloroform + Acetone (25°C) - UNIFAC',
        'components': ['Water', 'Chloroform', 'Acetone'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Sistema água-clorado-cetona'
    },
    {
        'name': 'Water + Chloroform + Acetic Acid (25°C) - UNIFAC',
        'components': ['Water', 'Chloroform', 'Acetic Acid'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Comparação com NRTL/UNIQUAC'
    },
    {
        'name': 'Water + 1,1,2-Trichloroethane + Acetone (25°C) - UNIFAC',
        'components': ['Water', '1,1,2-Trichloroethane', 'Acetone'],
        'temperature': 25.0,
        'model': 'UNIFAC',
        'ntielines': 5,
        'reference': 'UNIFAC Preditivo - Comparação com NRTL experimental'
    },
]

# ============================================================
# SISTEMAS ADICIONAIS - OUTRAS TEMPERATURAS
# ============================================================
ADDITIONAL_SYSTEMS = [
    {
        'name': 'Water + Cyclohexane + Ethanol (30°C) - NRTL',
        'components': ['Water', 'Cyclohexane', 'Ethanol'],
        'temperature': 30.0,
        'model': 'NRTL',
        'ntielines': 6,
        'reference': 'Extrapolação de Plačkov (1992) para 30°C'
    },
    {
        'name': 'Water + Cyclohexane + Ethanol (20°C) - NRTL',
        'components': ['Water', 'Cyclohexane', 'Ethanol'],
        'temperature': 20.0,
        'model': 'NRTL',
        'ntielines': 6,
        'reference': 'Extrapolação de Plačkov (1992) para 20°C'
    },
    {
        'name': 'Water + Toluene + Acetic Acid (30°C) - NRTL',
        'components': ['Water', 'Toluene', 'Acetic Acid'],
        'temperature': 30.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'DECHEMA (1980) - Dados a 30°C'
    },
    {
        'name': 'Water + Toluene + Acetic Acid (20°C) - NRTL',
        'components': ['Water', 'Toluene', 'Acetic Acid'],
        'temperature': 20.0,
        'model': 'NRTL',
        'ntielines': 5,
        'reference': 'DECHEMA (1980) - Dados a 20°C'
    },
]

# Combinar todos os sistemas
ALL_SYSTEMS = NRTL_SYSTEMS + UNIQUAC_SYSTEMS + UNIFAC_SYSTEMS + ADDITIONAL_SYSTEMS

def generate_cache_key(components, temperature, model):
    """
    Gera chave única para cache MANTENDO A ORDEM ORIGINAL dos componentes
    Formato: Component1-Component2-Component3_Temperature_Model
    
    Exemplos:
        - Water-1,1,2-Trichloroethane-Acetone_25.0_NRTL
        - Water-Toluene-Acetic Acid_25.0_NRTL
    """
    comp_str = "-".join(components)
    return f"{comp_str}_{temperature:.1f}_{model}"


def main():
    print("="*80)
    print("🚀 GERADOR DE CACHE COMPLETO - DIAGRAMAS TERNÁRIOS ELL")
    print("="*80)
    print(f"📊 Total de sistemas a processar: {len(ALL_SYSTEMS)}")
    print(f"   ├─ NRTL: {len(NRTL_SYSTEMS)} sistemas")
    print(f"   ├─ UNIQUAC: {len(UNIQUAC_SYSTEMS)} sistemas")
    print(f"   ├─ UNIFAC: {len(UNIFAC_SYSTEMS)} sistemas (preditivo)")
    print(f"   └─ Adicionais: {len(ADDITIONAL_SYSTEMS)} sistemas (outras temperaturas)")
    print(f"💾 Cache será salvo em: {CACHE_DIR.absolute()}")
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
        
        print(f"\n{'─'*80}")
        print(f"[{idx}/{len(ALL_SYSTEMS)}] {name}")
        print(f"  📌 Componentes: {' + '.join(components)}")
        print(f"  🔧 Modelo: {model} | T={temperature}°C | Tie-lines={ntielines}")
        print(f"  📚 Referência: {reference}")
        
        # Verificar se já existe
        if filename.exists():
            file_size = filename.stat().st_size / 1024
            print(f"  ⏭️  JÁ EXISTE: {cache_key[:50]}... ({file_size:.1f} KB)")
            skipped_count += 1
            continue
        
        try:
            # Calcular diagrama
            start_time = time.time()
            print(f"  ⏳ Calculando...")
            
            # ⭐ INSTANCIAR CALCULADORA CORRETAMENTE
            calculator = ELLCalculator(
                components=components,
                temperature_C=temperature,
                model=model  # ⭐ ADICIONAR ESTA LINHA
            )
            
            # ⭐ GERAR BINODAL + TIE-LINES
            binodal_L1, binodal_L2 = calculator.generate_binodal_curve(n_points=50)
            tie_lines = calculator.generate_tie_lines(n_lines=ntielines)
            
            elapsed = time.time() - start_time
            
            # ⭐ MONTAR RESULTADO NO FORMATO ESPERADO
            n_binodal = len(binodal_L1) + len(binodal_L2)
            n_tielines = len(tie_lines)
            
            # Verificar se gerou dados válidos
            if n_tielines > 0:
                print(f"  ✅ GERADO em {elapsed:.1f}s:")
                print(f"     ├─ Binodal: {n_binodal} pontos")
                print(f"     └─ Tie-lines: {n_tielines} linhas")
                
                if n_binodal == 0:
                    print(f"  ⚠️  AVISO: Binodal não gerada, mas tie-lines são válidas")
                
                # Converter numpy arrays para listas (JSON serializable)
                binodal_L1_list = [p.tolist() if isinstance(p, np.ndarray) else p for p in binodal_L1]
                binodal_L2_list = [p.tolist() if isinstance(p, np.ndarray) else p for p in binodal_L2]
                
                # Montar resultado
                results = {
                    'T_C': temperature,
                    'T_K': temperature + 273.15,
                    'model': model,
                    'components': components,
                    'binodal_L1': binodal_L1_list,
                    'binodal_L2': binodal_L2_list,
                    'tie_lines': tie_lines,
                    'n_binodal_points': n_binodal,
                    'n_tie_lines': n_tielines
                }
                
                # Salvar como JSON
                cache_data = {
                    'success': True,
                    'results': results,
                    'from_cache': True,
                    'precomputed': True,
                    'metadata': {
                        'generated_at': datetime.utcnow().isoformat(),
                        'cache_key': cache_key,
                        'system_name': name,
                        'reference': reference,
                        'computation_time_seconds': round(elapsed, 2),
                        'binodal_points': n_binodal,
                        'tielines_count': n_tielines,
                        'model': model,
                        'temperature_C': temperature,
                        'components': components
                    }
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
                file_size = filename.stat().st_size / 1024
                print(f"  💾 SALVO: {cache_key[:50]}... ({file_size:.1f} KB)")
                success_count += 1
            else:
                print(f"  ❌ ERRO: Nenhuma tie-line válida gerada")
                error_count += 1
        
        except Exception as e:
            print(f"  ❌ EXCEÇÃO: {e}")
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
        print("\n📦 Novos arquivos gerados nesta execução:")
        json_files = sorted(CACHE_DIR.glob('*.json'))
        for json_file in json_files:
            # Verificar se foi gerado recentemente (últimos 5 minutos)
            if (time.time() - json_file.stat().st_mtime) < 300:
                size_kb = json_file.stat().st_size / 1024
                print(f"  • {json_file.name} ({size_kb:.1f} KB)")
    
    print("="*80)
    
    if error_count > 0:
        print(f"\n⚠️  ATENÇÃO: {error_count} sistemas falharam. Verifique os erros acima.")
        print("   Possíveis causas:")
        print("   - Parâmetros binários não disponíveis")
        print("   - Sistema não forma duas fases na temperatura especificada")
        print("   - Problema de convergência numérica")
        return 1
    else:
        print("\n🎉 CACHE GERADO COM SUCESSO!")
        print("\n📤 Próximos passos:")
        print("   1. Faça commit dos arquivos de cache:")
        print("      git add app/cache/*.json")
        print(f"      git commit -m 'Add {success_count} pre-calculated ternary diagrams'")
        print("   2. Faça push para o Render:")
        print("      git push origin main")
        print("   3. Aguarde o deploy automático (~2-3 minutos)")
        print("   4. Verifique no navegador se os diagramas carregam instantaneamente")
        return 0

if __name__ == '__main__':
    exit(main())
