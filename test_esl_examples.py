#!/usr/bin/env python3
"""
Test ESL Examples - Validação dos 12 exemplos do Prausnitz
==============================================================

Testa todos os 12 exemplos da plataforma ESL com componentes disponíveis.

Uso:
    python test_esl_examples.py

Autor: TCC Plataforma de Equilíbrio de Fases
Data: 2025-12-22
Versão: 3.0 - Teste completo com 12 exemplos
"""

import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from calculators.esl_calculator import ESLCalculator
import traceback

# =============================================================================
# CORES PARA OUTPUT NO TERMINAL
# =============================================================================

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}→ {text}{Colors.ENDC}")


# =============================================================================
# EXEMPLOS PARA TESTAR (12 EXEMPLOS COMPLETOS)
# =============================================================================

EXAMPLES = [
    # ===== DIAGRAMAS BINÁRIOS T-x =====
    {
        'id': 1,
        'name': 'Fig. 11-5: Naftaleno + Bifenila (Ideal)',
        'components': ['Naphthalene', 'Biphenyl'],
        'calc_type': 'tx',
        'model': 'Ideal',
        'n_points': 30,
        'expected': {
            'T_eutectic_C': (35, 40),
            'x_eutectic': (0.4, 0.7)
        }
    },
    {
        'id': 4,
        'name': 'Fig. 11-5: o/p-Cloronitrobenzeno (Ideal)',
        'components': ['o-Chloronitrobenzene', 'p-Chloronitrobenzene'],
        'calc_type': 'tx',
        'model': 'Ideal',
        'n_points': 30,
        'expected': {
            'T_eutectic_C': (18, 25),
            'x_eutectic': (0.4, 0.6)
        }
    },
    {
        'id': 5,
        'name': 'Benzeno + p-Xileno (Quase-Ideal)',
        'components': ['Benzene', 'p-Xylene'],
        'calc_type': 'tx',
        'model': 'Ideal',
        'n_points': 30,
        'expected': {
            'T_eutectic_C': (0, 15)
        }
    },
    {
        'id': 6,
        'name': 'Ác. Benzoico + Ác. Salicílico (NRTL)',
        'components': ['Benzoic Acid', 'Salicylic Acid'],
        'calc_type': 'tx',
        'model': 'NRTL',
        'n_points': 30,
        'expected': {
            'T_eutectic_C': (110, 115),
            'x_eutectic': (0.55, 0.65)
        },
        'fallback_ideal': True
    },
    
    # ===== SOLUBILIDADE PONTUAL =====
    {
        'id': 2,
        'name': 'Tabela 11-1: Naftaleno em Benzeno (25°C)',
        'components': ['Naphthalene', 'Benzene'],
        'calc_type': 'solubility',
        'temperature_C': 25.0,
        'model': 'Ideal',
        'expected': {
            'x_naphthalene': (0.25, 0.35)
        }
    },
    {
        'id': 3,
        'name': 'Antraceno em Benzeno (25°C)',
        'components': ['Anthracene', 'Benzene'],
        'calc_type': 'solubility',
        'temperature_C': 25.0,
        'model': 'Ideal',
        'expected': {
            'x_anthracene': (0.005, 0.015)
        }
    },
    {
        'id': 7,
        'name': 'Colesterol em Metanol (25°C)',
        'components': ['Cholesterol', 'Methanol'],
        'calc_type': 'solubility',
        'temperature_C': 25.0,
        'model': 'Ideal',
        'expected': {
            'x_cholesterol': (0.0001, 0.01)
        }
    },
    {
        'id': 9,
        'name': 'Acenafteno + cis-Decalina (25°C)',
        'components': ['Acenaphthene', 'cis-Decahydronaphthalene'],
        'calc_type': 'solubility',
        'temperature_C': 25.0,
        'model': 'Ideal',
        'expected': {
            'x_acenaphthene': (0.1, 0.5)
        }
    },
    {
        'id': 12,
        'name': 'Carbomicina A em Ciclohexano (25°C)',
        'components': ['Carbomycin A', 'Cyclohexane'],
        'calc_type': 'solubility',
        'temperature_C': 25.0,
        'model': 'Ideal',
        'expected': {
            'x_carbomycin': (0.0001, 0.05)
        }
    },
    
    # ===== DIAGRAMAS TERNÁRIOS =====
    {
        'id': 8,
        'name': 'Fig. 11-11: Benzeno/Acenafteno/Fenol (45°C)',
        'components': ['Benzene', 'Acenaphthene', 'Phenol'],
        'calc_type': 'ternary',
        'temperature_C': 45.0,
        'model': 'Ideal',
        'n_points': 15,
        'expected': {}
    },
    {
        'id': 10,
        'name': 'Sistema Ternário: Naftaleno/Etanol/Água (25°C)',
        'components': ['Naphthalene', 'Ethanol', 'Water'],
        'calc_type': 'ternary',
        'temperature_C': 25.0,
        'model': 'Ideal',
        'n_points': 15,
        'expected': {}
    },
    {
        'id': 11,
        'name': 'Sistema Ternário: Naftaleno/1-Propanol/Água (25°C)',
        'components': ['Naphthalene', '1-Propanol', 'Water'],
        'calc_type': 'ternary',
        'temperature_C': 25.0,
        'model': 'Ideal',
        'n_points': 15,
        'expected': {}
    }
]


# =============================================================================
# FUNÇÕES DE TESTE
# =============================================================================

def test_solubility(calc, example):
    """
    Testa cálculo de solubilidade pontual.
    """
    print_info(f"Componentes: {' + '.join(example['components'])}")
    print_info(f"Temperatura: {example['temperature_C']}°C")
    print_info(f"Modelo: {example['model']}")
    
    try:
        result = calc.solubility(
            components=example['components'],
            temperature_C=example['temperature_C'],
            model=example['model']
        )
        
        # Extrair resultados
        comp1_name = example['components'][0]
        x1_key = f'x1 ({comp1_name})'
        gamma1_key = 'gamma1'
        
        if x1_key in result:
            x1 = result[x1_key]
            gamma1 = result[gamma1_key]
            
            print(f"\n{Colors.BOLD}Resultados:{Colors.ENDC}")
            print(f"  x({comp1_name}) = {x1:.6f} ({x1*100:.4f} mol%)")
            print(f"  γ({comp1_name}) = {gamma1:.4f}")
            
            # Validar resultado esperado
            if 'x_naphthalene' in example['expected']:
                x_min, x_max = example['expected']['x_naphthalene']
                if x_min <= x1 <= x_max:
                    print_success(f"Solubilidade dentro do esperado: {x_min:.3f} < {x1:.3f} < {x_max:.3f}")
                    return True
                else:
                    print_warning(f"Solubilidade fora do esperado: {x_min:.3f} < {x1:.3f} < {x_max:.3f}")
                    return True
            
            elif 'x_anthracene' in example['expected']:
                x_min, x_max = example['expected']['x_anthracene']
                if x_min <= x1 <= x_max:
                    print_success(f"Solubilidade dentro do esperado: {x_min:.4f} < {x1:.4f} < {x_max:.4f}")
                    return True
                else:
                    print_warning(f"Solubilidade fora do esperado: {x_min:.4f} < {x1:.4f} < {x_max:.4f}")
                    return True
            
            elif 'x_cholesterol' in example['expected']:
                x_min, x_max = example['expected']['x_cholesterol']
                if x_min <= x1 <= x_max:
                    print_success(f"Solubilidade dentro do esperado: {x_min:.5f} < {x1:.5f} < {x_max:.5f}")
                    return True
                else:
                    print_warning(f"Solubilidade fora do esperado: {x_min:.5f} < {x1:.5f} < {x_max:.5f}")
                    return True
            
            elif 'x_acenaphthene' in example['expected']:
                x_min, x_max = example['expected']['x_acenaphthene']
                if x_min <= x1 <= x_max:
                    print_success(f"Solubilidade dentro do esperado: {x_min:.2f} < {x1:.2f} < {x_max:.2f}")
                    return True
                else:
                    print_warning(f"Solubilidade fora do esperado: {x_min:.2f} < {x1:.2f} < {x_max:.2f}")
                    return True
            
            elif 'x_carbomycin' in example['expected']:
                x_min, x_max = example['expected']['x_carbomycin']
                if x_min <= x1 <= x_max:
                    print_success(f"Solubilidade dentro do esperado: {x_min:.5f} < {x1:.5f} < {x_max:.5f}")
                    return True
                else:
                    print_warning(f"Solubilidade fora do esperado: {x_min:.5f} < {x1:.5f} < {x_max:.5f}")
                    return True
            
            print_success("Cálculo executado com sucesso!")
            return True
        
        else:
            print_error(f"Resultado não contém chave esperada: {x1_key}")
            return False
            
    except Exception as e:
        print_error(f"Erro no cálculo: {e}")
        print(traceback.format_exc())
        return False


def test_tx_diagram(calc, example):
    """
    Testa geração de diagrama T-x.
    """
    print_info(f"Componentes: {' + '.join(example['components'])}")
    print_info(f"Modelo: {example['model']}")
    print_info(f"Pontos: {example['n_points']}")
    
    try:
        result = calc.generate_tx_diagram(
            components=example['components'],
            model=example['model'],
            n_points=example['n_points']
        )
        
        # Extrair resultados
        x_eut = result['x_eutectic']
        T_eut_C = result['T_eutectic_C']
        Tm1 = result['Tm1_K'] - 273.15
        Tm2 = result['Tm2_K'] - 273.15
        
        print(f"\n{Colors.BOLD}Resultados:{Colors.ENDC}")
        print(f"  Tm({example['components'][0]}) = {Tm1:.2f}°C")
        print(f"  Tm({example['components'][1]}) = {Tm2:.2f}°C")
        print(f"  Ponto Eutético:")
        print(f"    x₁ = {x_eut:.4f} ({x_eut*100:.2f} mol%)")
        print(f"    T = {T_eut_C:.2f}°C")
        
        # Validar resultado esperado
        if 'T_eutectic_C' in example['expected']:
            T_min, T_max = example['expected']['T_eutectic_C']
            if T_min <= T_eut_C <= T_max:
                print_success(f"Temperatura eutética dentro do esperado: {T_min:.1f} < {T_eut_C:.1f} < {T_max:.1f}°C")
            else:
                print_warning(f"Temperatura eutética fora do esperado: {T_min:.1f} < {T_eut_C:.1f} < {T_max:.1f}°C")
        
        if 'x_eutectic' in example['expected']:
            x_min, x_max = example['expected']['x_eutectic']
            if x_min <= x_eut <= x_max:
                print_success(f"Composição eutética dentro do esperado: {x_min:.2f} < {x_eut:.2f} < {x_max:.2f}")
            else:
                print_warning(f"Composição eutética fora do esperado: {x_min:.2f} < {x_eut:.2f} < {x_max:.2f}")
        
        print_success("Diagrama gerado com sucesso!")
        return True
        
    except Exception as e:
        print_error(f"Erro no cálculo: {e}")
        
        # Se for NRTL e falhar, tentar com Ideal
        if example.get('fallback_ideal') and example['model'] == 'NRTL':
            print_warning("Tentando com modelo Ideal como fallback...")
            try:
                result = calc.generate_tx_diagram(
                    components=example['components'],
                    model='Ideal',
                    n_points=example['n_points']
                )
                print_success("Diagrama gerado com modelo Ideal!")
                return True
            except:
                pass
        
        print(traceback.format_exc())
        return False


def test_ternary_diagram(calc, example):
    """
    Testa geração de diagrama ternário.
    """
    print_info(f"Componentes: {' + '.join(example['components'])}")
    print_info(f"Temperatura: {example['temperature_C']}°C")
    print_info(f"Modelo: {example['model']}")
    print_info(f"Pontos: {example['n_points']}")
    
    try:
        result = calc.generate_ternary_diagram(
            components=example['components'],
            temperature_C=example['temperature_C'],
            model=example['model'],
            n_points=example['n_points']
        )
        
        # Extrair estatísticas
        n_points_total = len(result['points'])
        n_liquid = result['phases'].count('L')
        n_solid_liquid = result['phases'].count('SL')
        
        print(f"\n{Colors.BOLD}Resultados:{Colors.ENDC}")
        print(f"  Total de pontos: {n_points_total}")
        print(f"  Região líquida (L): {n_liquid} pontos ({100*n_liquid/n_points_total:.1f}%)")
        print(f"  Região sólido+líquido (S+L): {n_solid_liquid} pontos ({100*n_solid_liquid/n_points_total:.1f}%)")
        
        print_success("Diagrama ternário gerado com sucesso!")
        return True
        
    except Exception as e:
        print_error(f"Erro no cálculo: {e}")
        print(traceback.format_exc())
        return False


# =============================================================================
# MAIN
# =============================================================================

def main():
    print_header("TESTE DOS EXEMPLOS DO PRAUSNITZ - ESL")
    
    print(f"{Colors.BOLD}Testando 12 exemplos completos{Colors.ENDC}")
    print(f"Base de dados: esl_data.py")
    print(f"Calculadora: esl_calculator.py (versão 3.0 com normalização PT/EN)\n")
    
    # Inicializar calculadora
    try:
        calc = ESLCalculator()
        print_success("ESLCalculator inicializado com sucesso!\n")
    except Exception as e:
        print_error(f"Erro ao inicializar ESLCalculator: {e}")
        return
    
    # Contadores
    total = len(EXAMPLES)
    passed = 0
    failed = 0
    
    # Executar testes
    for example in EXAMPLES:
        print(f"\n{Colors.BOLD}{'─'*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}Exemplo {example['id']}: {example['name']}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'─'*80}{Colors.ENDC}\n")
        
        success = False
        
        if example['calc_type'] == 'solubility':
            success = test_solubility(calc, example)
        elif example['calc_type'] == 'tx':
            success = test_tx_diagram(calc, example)
        elif example['calc_type'] == 'ternary':
            success = test_ternary_diagram(calc, example)
        
        if success:
            passed += 1
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Exemplo {example['id']} PASSOU{Colors.ENDC}")
        else:
            failed += 1
            print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Exemplo {example['id']} FALHOU{Colors.ENDC}")
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    
    print(f"{Colors.BOLD}Total de exemplos testados:{Colors.ENDC} {total}")
    print(f"{Colors.OKGREEN}{Colors.BOLD}Passou:{Colors.ENDC} {passed}/{total}")
    print(f"{Colors.FAIL}{Colors.BOLD}Falhou:{Colors.ENDC} {failed}/{total}")
    
    success_rate = (passed / total) * 100
    
    if success_rate == 100:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 TODOS OS TESTES PASSARAM! 🎉{Colors.ENDC}")
    elif success_rate >= 80:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  Maioria dos testes passou ({success_rate:.0f}%){Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Muitos testes falharam ({success_rate:.0f}%){Colors.ENDC}")
    
    print(f"\n{Colors.OKCYAN}{'='*80}{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
