"""
fit_uniquac_ternary_lle.py
Fitting de parâmetros UNIQUAC para sistema ternário LLE
Baseado em Abrams & Prausnitz (1975)
"""

import numpy as np
from scipy.optimize import minimize, differential_evolution
from ell_flash_uniquac import UNIQUACModel, ELLFlash
from typing import List, Tuple, Dict


class UNIQUACFitter:
    """Classe para ajustar parâmetros UNIQUAC a dados experimentais LLE"""
    
    def __init__(self, r_values: List[float], q_values: List[float], 
                 exp_data: List[Dict], T: float):
        """
        Args:
            r_values: [r1, r2, r3] parâmetros estruturais
            q_values: [q1, q2, q3] parâmetros estruturais
            exp_data: lista de dicts com tie-lines experimentais
                     [{'phase1': [x1, x2, x3], 'phase2': [x1, x2, x3]}, ...]
            T: temperatura em K
        """
        self.r = r_values
        self.q = q_values
        self.exp_data = exp_data
        self.T = T
        self.n_comp = len(r_values)
        
    def params_to_dict(self, params: np.ndarray) -> Dict:
        """
        Converte array de parâmetros para dicionário
        
        Para sistema ternário (1, 2, 3):
        params = [u21-u22, u12-u11, u31-u33, u13-u11, u32-u33, u23-u22]
        
        Ordem:
        - params[0] = u21 - u22  (1->2, water-ethyl acetate)
        - params[1] = u12 - u11  (2->1, ethyl acetate-water)
        - params[2] = u31 - u33  (1->3, ethanol-ethyl acetate)
        - params[3] = u13 - u11  (3->1, ethyl acetate-ethanol)
        - params[4] = u32 - u33  (2->3, ethanol-water)
        - params[5] = u23 - u22  (3->2, water-ethanol)
        """
        u_params = {
            (0, 1): {'u_delta': params[0]},  # u21 - u22
            (1, 0): {'u_delta': params[1]},  # u12 - u11
            (0, 2): {'u_delta': params[2]},  # u31 - u33
            (2, 0): {'u_delta': params[3]},  # u13 - u11
            (1, 2): {'u_delta': params[4]},  # u32 - u33
            (2, 1): {'u_delta': params[5]},  # u23 - u22
        }
        return u_params
    
    def objective_function(self, params: np.ndarray) -> float:
        """
        Função objetivo: soma dos erros quadráticos entre
        composições experimentais e calculadas
        """
        u_params = self.params_to_dict(params)
        
        try:
            model = UNIQUACModel(self.r, self.q, u_params)
            flash = ELLFlash(model)
        except:
            return 1e10  # Penalidade alta se modelo falhar
        
        total_error = 0.0
        n_converged = 0
        
        for tie_line in self.exp_data:
            x1_exp = np.array(tie_line['phase1'])
            x2_exp = np.array(tie_line['phase2'])
            
            # Composição global (média das fases)
            z = 0.5 * (x1_exp + x2_exp)
            
            # Chute inicial = dados experimentais
            initial_guess = (x1_exp, x2_exp)
            
            # Resolver flash
            result = flash.flash_lle(z, self.T, initial_guess=initial_guess)
            
            if not result['converged'] or result['stable']:
                # Penalidade se não convergir ou se for estável
                total_error += 100.0
                continue
            
            x1_calc = result['x_phase1']
            x2_calc = result['x_phase2']
            
            # Erro quadrático médio
            # Precisa testar ambas as ordens (fase1↔fase2 pode trocar)
            error1 = np.sum((x1_calc - x1_exp)**2 + (x2_calc - x2_exp)**2)
            error2 = np.sum((x1_calc - x2_exp)**2 + (x2_calc - x1_exp)**2)
            
            total_error += min(error1, error2)
            n_converged += 1
        
        # Se nenhuma tie-line convergiu, penalidade máxima
        if n_converged == 0:
            return 1e10
        
        # Normalizar pelo número de tie-lines
        avg_error = total_error / len(self.exp_data)
        
        return avg_error
    
    def fit(self, method='differential_evolution', bounds=None) -> Dict:
        """
        Executa o fitting
        
        Args:
            method: 'differential_evolution' (global) ou 'nelder-mead' (local)
            bounds: lista de tuplas [(min, max), ...] para cada parâmetro
                   Se None, usa [-2000, 2000] cal/mol
        
        Returns:
            dict com resultados do fitting
        """
        n_params = 6  # 3 binários × 2 parâmetros cada
        
        if bounds is None:
            bounds = [(-2000, 2000)] * n_params
        
        print(f"\n{'='*70}")
        print(f"FITTING DE PARÂMETROS UNIQUAC - SISTEMA TERNÁRIO LLE")
        print(f"{'='*70}")
        print(f"\nNúmero de tie-lines experimentais: {len(self.exp_data)}")
        print(f"Temperatura: {self.T - 273.15:.1f}°C")
        print(f"Método de otimização: {method}")
        
        if method == 'differential_evolution':
            # Otimização global (mais lenta, mas melhor)
            print(f"\nExecutando otimização global...")
            print(f"Isso pode levar alguns minutos...\n")
            
            result = differential_evolution(
                self.objective_function,
                bounds=bounds,
                maxiter=1000,
                popsize=15,
                tol=1e-6,
                workers=1,
                updating='deferred',
                disp=True
            )
            
        else:
            # Otimização local (mais rápida)
            # Chute inicial = zero (parâmetros athermal)
            x0 = np.zeros(n_params)
            
            print(f"\nExecutando otimização local...")
            
            result = minimize(
                self.objective_function,
                x0,
                method='Nelder-Mead',
                options={'maxiter': 5000, 'disp': True}
            )
        
        print(f"\n{'='*70}")
        print(f"RESULTADOS DO FITTING")
        print(f"{'='*70}")
        print(f"\nStatus: {'SUCESSO' if result.success else 'FALHOU'}")
        print(f"Erro final: {result.fun:.6f}")
        print(f"\nParâmetros otimizados (cal/mol):")
        print(f"  u₂₁ - u₂₂ (water → ethyl acetate) = {result.x[0]:8.1f}")
        print(f"  u₁₂ - u₁₁ (ethyl acetate → water) = {result.x[1]:8.1f}")
        print(f"  u₃₁ - u₃₃ (ethanol → ethyl acetate) = {result.x[2]:8.1f}")
        print(f"  u₁₃ - u₁₁ (ethyl acetate → ethanol) = {result.x[3]:8.1f}")
        print(f"  u₃₂ - u₃₃ (ethanol → water) = {result.x[4]:8.1f}")
        print(f"  u₂₃ - u₂₂ (water → ethanol) = {result.x[5]:8.1f}")
        
        return {
            'success': result.success,
            'params': result.x,
            'error': result.fun,
            'u_params_dict': self.params_to_dict(result.x),
            'result': result
        }


# ==============================================================================
# EXEMPLO DE USO COM DADOS SINTÉTICOS
# ==============================================================================

if __name__ == "__main__":
    
    # Parâmetros estruturais (Tabela 1 do artigo)
    r_values = [3.48, 0.92, 2.11]  # ethyl acetate, water, ethanol
    q_values = [3.12, 1.40, 1.97]
    
    # Temperatura
    T = 25.0 + 273.15  # K
    
    # ===================================================================
    # DADOS EXPERIMENTAIS (EXEMPLO - SUBSTITUIR POR DADOS REAIS!)
    # ===================================================================
    # Formato: frações molares [ethyl acetate, water, ethanol]
    
    exp_data = [
        # Tie-line 1
        {
            'phase1': [0.850, 0.030, 0.120],  # Fase rica em ethyl acetate
            'phase2': [0.020, 0.900, 0.080]   # Fase rica em water
        },
        # Tie-line 2
        {
            'phase1': [0.780, 0.050, 0.170],
            'phase2': [0.040, 0.850, 0.110]
        },
        # Tie-line 3
        {
            'phase1': [0.700, 0.080, 0.220],
            'phase2': [0.070, 0.780, 0.150]
        },
        # Adicionar mais tie-lines conforme dados experimentais...
    ]
    
    print("\n⚠️  ATENÇÃO: Usando dados SINTÉTICOS de exemplo!")
    print("Para resultados reais, substitua por dados experimentais.")
    
    # Criar objeto de fitting
    fitter = UNIQUACFitter(r_values, q_values, exp_data, T)
    
    # Executar fitting
    # Método 1: Otimização global (recomendado, mas mais lento)
    fit_result = fitter.fit(method='differential_evolution')
    
    # Método 2: Otimização local (mais rápido, pode ficar preso em mínimo local)
    # fit_result = fitter.fit(method='nelder-mead')
    
    # Salvar parâmetros otimizados
    if fit_result['success']:
        print(f"\n{'='*70}")
        print("PARÂMETROS PRONTOS PARA USO:")
        print(f"{'='*70}")
        print("\nu_params = {")
        for key, val in fit_result['u_params_dict'].items():
            print(f"    {key}: {{'u_delta': {val['u_delta']:.1f}}},")
        print("}")
