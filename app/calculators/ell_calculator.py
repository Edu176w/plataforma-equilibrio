"""
app/calculators/ell_calculator.py

CALCULADORA DE EQUILÍBRIO LÍQUIDO-LÍQUIDO (ELL)
================================================

VERSÃO 3.0 - Corrigida conforme Prausnitz Cap. 12 e Apêndice E

IMPLEMENTAÇÃO:
    - Modelos: NRTL (Tabela E-5), UNIQUAC (Tabela E-6)
    - Flash L1-L2 isotérmico com teste de estabilidade
    - Diagrama ternário com binodal e tie-lines
    - Algoritmo de binodal CORRIGIDO: varre INTERIOR do triângulo

REFERÊNCIAS:
    [1] Prausnitz, J.M., Lichtenthaler, R.N., Azevedo, E.G. (1999)
        "Molecular Thermodynamics of Fluid-Phase Equilibria", 3rd Ed.
        - Cap. 6: Activity Coefficient Models
        - Cap. 12: Phase Equilibria in Partially Miscible Systems
        - Apêndice E: Binary Parameters (Tabelas E-5, E-6)
    
    [2] Michelsen, M.L. (1982)
        "The isothermal flash problem. Part I. Stability"
        Fluid Phase Equilibria, 9, 1-19
    
    [3] Baker, L.E., Pierce, A.C., Luks, K.D. (1982)
        "Gibbs energy analysis of phase equilibria"
        SPE Journal, 22(5), 731-742

AUTOR: Desenvolvido para TCC
DATA: Dezembro 2024
"""

import numpy as np
from scipy.optimize import fsolve, minimize, root
from typing import Dict, List, Tuple, Optional
import sys
import os

# Adicionar caminho para módulos de dados
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

# Importar parâmetros ELL do Apêndice E
try:
    from ell_nrtl_params import ELL_NRTL_PARAMS, get_nrtl_params_ell
    HAS_NRTL = True
except ImportError:
    HAS_NRTL = False
    print("[WARNING] ell_nrtl_params.py não encontrado")

try:
    from ell_uniquac_params import ELL_UNIQUAC_PARAMS, get_uniquac_params_ell
    HAS_UNIQUAC = True
except ImportError:
    HAS_UNIQUAC = False
    print("[WARNING] ell_uniquac_params.py não encontrado")
    
# ========================================================================
# ⭐ IMPORTAR PARÂMETROS UNIFAC PREDITIVO
# ========================================================================
try:
    from ell_unifac_params import calculate_unifac_gamma
    HAS_UNIFAC = True
    print("✓ UNIFAC preditivo carregado com sucesso!")
except ImportError:
    HAS_UNIFAC = False
    print("WARNING: ell_unifac_params.py não encontrado")


# Importar recomendações IA
# Importar recomendações IA
try:
    from app.utils.ai_ell import recommend_model_for_ell
    HAS_AI = True
except ImportError:
    HAS_AI = False

# ============================================================================
# CONSTANTES FÍSICAS
# ============================================================================

R = 8.314  # J/(mol·K) - Constante universal dos gases

# ============================================================================
# FUNÇÕES AUXILIARES PARA FILTRAR COMPONENTES E MODELOS DISPONÍVEIS
# ============================================================================

def get_available_components_for_ell(model: str = 'NRTL') -> List[Dict]:
    """
    Retorna APENAS componentes que possuem parâmetros ELL para o modelo especificado.

    ⭐ UNIFAC: Retorna TODOS os componentes orgânicos (não requer parâmetros binários)
    """
    model_upper = model.upper()
    components = []

    try:
        if model_upper == 'NRTL' and HAS_NRTL:
            from ell_nrtl_params import get_available_components_ell_nrtl
            components = get_available_components_ell_nrtl()

        elif model_upper == 'UNIQUAC' and HAS_UNIQUAC:
            from ell_uniquac_params import get_available_components_ell_uniquac
            components = get_available_components_ell_uniquac()

        # ⭐ UNIFAC: PREDITIVO - Todos componentes orgânicos são suportados
        elif model_upper == 'UNIFAC' and HAS_UNIFAC:
            from ell_unifac_params import get_available_components_ell_unifac
            components = get_available_components_ell_unifac()

        else:
            components = []

    except Exception as e:
        print(f"WARNING: Erro ao carregar componentes ELL para {model}: {e}")
        components = []

    return components




def get_available_models_for_components(components: List[str]) -> List[str]:
    """
    Verifica quais modelos têm parâmetros disponíveis.
    
    ⭐ UNIFAC sempre disponível (preditivo)
    """
    if len(components) != 3:
        return []
    
    available_models = []
    
    # NRTL (requer parâmetros)
    if HAS_NRTL:
        try:
            from ell_nrtl_params import validate_ternary_system_nrtl
            validation = validate_ternary_system_nrtl(components)
            if validation.get('valid'):
                available_models.append('NRTL')
        except Exception:
            pass
    
    # UNIQUAC (requer parâmetros)
    if HAS_UNIQUAC:
        try:
            from ell_uniquac_params import validate_ternary_system_uniquac
            validation = validate_ternary_system_uniquac(components)
            if validation.get('valid'):
                available_models.append('UNIQUAC')
        except Exception:
            pass
    
    # ⭐ UNIFAC: SEMPRE DISPONÍVEL (preditivo)
    if HAS_UNIFAC:
        available_models.append('UNIFAC')
    
    return available_models



def check_ell_parameters_available(components: List[str], model: str, temperature_C: float = 25.0) -> Dict:
    """
    Verifica se os parâmetros ELL estão disponíveis para os componentes e modelo.
    
    USA AS FUNÇÕES get_nrtl_params_ell() e get_uniquac_params_ell() JÁ EXISTENTES.
    
    ⭐ UNIFAC: Sempre disponível (modelo preditivo)
    
    Args:
        components: Lista com 3 nomes de componentes (ORDEM IMPORTA!)
        model: 'NRTL', 'UNIQUAC' ou 'UNIFAC'
        temperature_C: Temperatura em °C (padrão: 25.0)
    
    Returns:
        Dict com:
            - available (bool): Se parâmetros estão disponíveis
            - model (str): Modelo testado
            - components (list): Componentes testados
            - message (str): Mensagem descritiva
            - temperature_warning (str): Aviso de temperatura (se houver)
            - reference (str): Referência bibliográfica (se disponível)
            - params (dict): Parâmetros completos (se disponíveis)
    
    Example:
        >>> # Verificar NRTL para Water/TCE/Acetone
        >>> result = check_ell_parameters_available(
        ...     ['Water', '1,1,2-Trichloroethane', 'Acetone'], 
        ...     'NRTL', 
        ...     25.0
        ... )
        >>> if result['available']:
        >>>     print(f"✅ {result['message']}")
        >>>     print(f"📚 {result['reference']}")
        ✅ Parâmetros NRTL disponíveis para Water / 1,1,2-Trichloroethane / Acetone
        📚 Prausnitz Table E-5, Bender & Block (1975)
    """
    
    if len(components) != 3:
        return {
            'available': False,
            'model': model,
            'components': components,
            'message': 'ELL requer exatamente 3 componentes',
            'params': None
        }
    
    model_upper = model.upper()
    
    try:
        # ====================================================================
        # NRTL
        # ====================================================================
        if model_upper == 'NRTL':
            if not HAS_NRTL:
                return {
                    'available': False,
                    'model': model_upper,
                    'components': components,
                    'message': '❌ Módulo ell_nrtl_params.py não disponível',
                    'params': None
                }
            
            # Usar função já existente
            params = get_nrtl_params_ell(components, temperature_C)
            
            if params and params.get('success'):
                message = f"✅ Parâmetros NRTL disponíveis para {' / '.join(components)}"
                
                # Adicionar aviso de temperatura se houver
                if params.get('warning'):
                    message += f"\n{params['warning']}"
                
                return {
                    'available': True,
                    'model': model_upper,
                    'components': components,
                    'message': message,
                    'temperature_warning': params.get('warning'),
                    'reference': params.get('reference'),
                    'params': params
                }
            else:
                return {
                    'available': False,
                    'model': model_upper,
                    'components': components,
                    'message': params.get('error', '❌ Parâmetros NRTL não encontrados'),
                    'params': None
                }
        
        # ====================================================================
        # UNIQUAC
        # ====================================================================
        elif model_upper == 'UNIQUAC':
            if not HAS_UNIQUAC:
                return {
                    'available': False,
                    'model': model_upper,
                    'components': components,
                    'message': '❌ Módulo ell_uniquac_params.py não disponível',
                    'params': None
                }
            
            # Usar função já existente
            params = get_uniquac_params_ell(components, temperature_C)
            
            if params and params.get('success'):
                message = f"✅ Parâmetros UNIQUAC disponíveis para {' / '.join(components)}"
                
                if params.get('warning'):
                    message += f"\n{params['warning']}"
                
                return {
                    'available': True,
                    'model': model_upper,
                    'components': components,
                    'message': message,
                    'temperature_warning': params.get('warning'),
                    'reference': params.get('reference'),
                    'params': params
                }
            else:
                return {
                    'available': False,
                    'model': model_upper,
                    'components': components,
                    'message': params.get('error', '❌ Parâmetros UNIQUAC não encontrados'),
                    'params': None
                }
        
        # ====================================================================
        # ⭐ UNIFAC - PREDITIVO (SEMPRE DISPONÍVEL)
        # ====================================================================
        elif model_upper == 'UNIFAC':
            if not HAS_UNIFAC:
                return {
                    'available': False,
                    'model': model_upper,
                    'components': components,
                    'message': '❌ Módulo ell_unifac_params.py não disponível',
                    'params': None
                }
            
            # UNIFAC é preditivo - não requer parâmetros binários
            message = f"✅ UNIFAC preditivo disponível para {' / '.join(components)}"
            message += "\n🔮 Modelo preditivo baseado em contribuição de grupos funcionais"
            
            return {
                'available': True,
                'model': model_upper,
                'components': components,
                'message': message,
                'temperature_warning': None,
                'reference': 'Fredenslund, Å., Jones, R.L., Prausnitz, J.M. (1975) - AIChE J., 21, 1086-1099',
                'params': {
                    'success': True,
                    'model': 'UNIFAC',
                    'reference': 'Fredenslund et al. (1975) - UNIFAC Original'
                }
            }
        
        # ====================================================================
        # MODELO NÃO SUPORTADO
        # ====================================================================
        else:
            return {
                'available': False,
                'model': model_upper,
                'components': components,
                'message': f'❌ Modelo {model_upper} não suportado (use NRTL, UNIQUAC ou UNIFAC)',
                'params': None
            }
    
    except Exception as e:
        return {
            'available': False,
            'model': model_upper,
            'components': components,
            'message': f'❌ Erro ao verificar parâmetros: {str(e)}',
            'params': None
        }


# ============================================================================
# CLASSE PRINCIPAL: ELL CALCULATOR
# ============================================================================

class ELLCalculator:
    """
    Calculadora de Equilíbrio Líquido-Líquido para sistemas ternários
    
    Implementa:
        - Flash L1-L2 isotérmico (Rachford-Rice modificado)
        - Teste de estabilidade (Tangent Plane Distance - TPD)
        - Diagrama ternário (binodal + tie-lines)
        - Modelos: NRTL, UNIQUAC
    
    Attributes:
        components (list): Nomes dos 3 componentes (ordem importa!)
        T_C (float): Temperatura em °C
        T_K (float): Temperatura em K
        model (str): Modelo termodinâmico ('NRTL' ou 'UNIQUAC')
        params (dict): Parâmetros do modelo
    """
    
    def __init__(self, components: List[str], temperature_C: float, model: str = 'NRTL'):
        if len(components) != 3:
            raise ValueError(f"ELL requer exatamente 3 componentes. Fornecidos: {len(components)}")
        
        self.components = components
        self.TC = temperature_C
        self.TK = temperature_C + 273.15
        self.model = model.upper()
        
        # ⭐ UNIFAC não requer validação de parâmetros (preditivo)
        if self.model == 'UNIFAC':
            if not HAS_UNIFAC:
                raise ValueError("UNIFAC não disponível: ell_unifac_params.py não encontrado")
            self.params = {'success': True, 'model': 'UNIFAC'}
        else:
            # NRTL e UNIQUAC requerem parâmetros binários
            self.params = self.load_parameters()
            if not self.params or not self.params.get('success'):
                raise ValueError(
                    f"Parâmetros {self.model} não encontrados para sistema {' / '.join(components)}. "
                    f"Verifique se os componentes estão na ordem correta da Tabela E-5 (NRTL) ou E-6 (UNIQUAC)."
                )

    
    def load_parameters(self) -> Dict:
        """Carrega parâmetros do modelo (NRTL, UNIQUAC, UNIFAC)"""
        if self.model == 'NRTL':
            if not HAS_NRTL:
                return {'success': False, 'error': 'ell_nrtl_params.py não disponível'}
            return get_nrtl_params_ell(self.components, self.TC)
        
        elif self.model == 'UNIQUAC':
            if not HAS_UNIQUAC:
                return {'success': False, 'error': 'ell_uniquac_params.py não disponível'}
            return get_uniquac_params_ell(self.components, self.TC)
        
        # ⭐ UNIFAC: Preditivo (não requer parâmetros binários)
        elif self.model == 'UNIFAC':
            return {'success': True, 'model': 'UNIFAC'}
        
        else:
            return {'success': False, 'error': f'Modelo {self.model} não implementado'}

    
    # ========================================================================
    # COEFICIENTES DE ATIVIDADE
    # ========================================================================
    
    def activity_coefficients(self, x: np.ndarray) -> np.ndarray:
        """
        Calcula coeficientes de atividade γ_i para sistema ternário.
        
        Suporta:
        - NRTL: Prausnitz Eq. 6.11-6
        - UNIQUAC: Prausnitz Eq. 6.12-1 a 6.12-5
        - ⭐ UNIFAC: Fredenslund et al. (1975) - Preditivo
        """
        if self.model == 'NRTL':
            return self._gamma_nrtl(x)
        elif self.model == 'UNIQUAC':
            return self._gamma_uniquac(x)
        elif self.model == 'UNIFAC':
            return self._gamma_unifac(x)
        else:
            return np.ones(3)  # Fallback: solução ideal

    
    def _gamma_nrtl(self, x: np.ndarray) -> np.ndarray:
        """
        Coeficientes de atividade NRTL (Renon-Prausnitz)
        
        Equação NRTL (Prausnitz Eq. 6.11-6):
            ln(γ_i) = [Σ_j τ_ji G_ji x_j / Σ_k G_ki x_k] + 
                      Σ_j [x_j G_ij / Σ_k G_kj x_k] [τ_ij - (Σ_m x_m τ_mj G_mj / Σ_k G_kj x_k)]
        
        Onde:
            τ_ij = b_ij / T  (parâmetro de interação, b_ij em K)
            G_ij = exp(-α_ij * τ_ij)  (fator de não-aleatoriedade)
            α_ij = α_ji  (parâmetro de não-aleatoriedade, tipicamente 0.2-0.4)
        
        Args:
            x: Frações molares [x1, x2, x3]
        
        Returns:
            Array com [γ1, γ2, γ3]
        """
        # Extrair parâmetros do Apêndice E
        tau_dict = self.params['tau']
        G_dict = self.params['G']
        
        # Montar matrizes τ e G (3x3)
        tau = np.zeros((3, 3))
        G = np.zeros((3, 3))
        
        # Diagonal: τ_ii = 0, G_ii = 1
        for i in range(3):
            tau[i, i] = 0.0
            G[i, i] = 1.0
        
        # Off-diagonal: usar parâmetros binários
        for (i, j), params_ij in tau_dict.items():
            tau[i-1, j-1] = params_ij['tau_ij']
            tau[j-1, i-1] = params_ij['tau_ji']
        
        for (i, j), params_ij in G_dict.items():
            G[i-1, j-1] = params_ij['G_ij']
            G[j-1, i-1] = params_ij['G_ji']
        
        # Calcular ln(γ) usando equação NRTL
        ln_gamma = np.zeros(3)
        
        for i in range(3):
            # Termo 1: Σ_j τ_ji G_ji x_j / Σ_k G_ki x_k
            numerator1 = sum(tau[j, i] * G[j, i] * x[j] for j in range(3))
            denominator1 = sum(G[k, i] * x[k] for k in range(3))
            term1 = numerator1 / (denominator1 + 1e-12)
            
            # Termo 2: Σ_j [x_j G_ij / Σ_k G_kj x_k] [τ_ij - (Σ_m x_m τ_mj G_mj / Σ_k G_kj x_k)]
            term2 = 0.0
            for j in range(3):
                denom_j = sum(G[k, j] * x[k] for k in range(3))
                if denom_j < 1e-12:
                    continue
                
                numerator_inner = sum(x[m] * tau[m, j] * G[m, j] for m in range(3))
                inner_term = tau[i, j] - (numerator_inner / denom_j)
                
                term2 += (x[j] * G[i, j] / denom_j) * inner_term
            
            ln_gamma[i] = term1 + term2
        
        # γ = exp(ln γ)
        gamma = np.exp(ln_gamma)
        
        # Limitar valores extremos (estabilidade numérica)
        gamma = np.clip(gamma, 1e-6, 1e6)
        
        return gamma
    
    def _gamma_uniquac(self, x: np.ndarray) -> np.ndarray:
        """
        Coeficientes de atividade UNIQUAC (Abrams-Prausnitz)
        
        Equação UNIQUAC (Prausnitz Eq. 6.12-1):
            ln(γ_i) = ln(γ_i^C) + ln(γ_i^R)
        
        Parte combinatorial (Eq. 6.12-2):
            ln(γ_i^C) = ln(Φ_i/x_i) + (z/2) q_i ln(θ_i/Φ_i) + l_i - (Φ_i/x_i) Σ_j x_j l_j
        
        Parte residual (Eq. 6.12-3):
            ln(γ_i^R) = q_i [1 - ln(Σ_j θ_j τ_ji) - Σ_j (θ_j τ_ij / Σ_k θ_k τ_kj)]
        
        Onde:
            Φ_i = r_i x_i / Σ_j r_j x_j  (fração de volume)
            θ_i = q_i x_i / Σ_j q_j x_j  (fração de área)
            l_i = (z/2)(r_i - q_i) - (r_i - 1)  (parâmetro de forma, z=10)
            τ_ij = exp(-a_ij / T)  (parâmetro de interação)
        
        Args:
            x: Frações molares [x1, x2, x3]
        
        Returns:
            Array com [γ1, γ2, γ3]
        """
        # Extrair parâmetros do Apêndice E
        r = self.params['r']  # Parâmetros de volume [r1, r2, r3]
        q = self.params['q']  # Parâmetros de área [q1, q2, q3]
        tau_dict = self.params['tau']  # Parâmetros τ_ij
        
        z = 10  # Número de coordenação (padrão UNIQUAC)
        
        # Montar matriz τ (3x3)
        tau = np.ones((3, 3))  # Diagonal τ_ii = 1
        
        for (i, j), params_ij in tau_dict.items():
            tau[i-1, j-1] = params_ij['tau_ij']
            tau[j-1, i-1] = params_ij['tau_ji']
        
        # Calcular frações de volume (Φ) e área (θ)
        sum_rx = sum(r[i] * x[i] for i in range(3))
        sum_qx = sum(q[i] * x[i] for i in range(3))
        
        phi = np.array([(r[i] * x[i]) / (sum_rx + 1e-12) for i in range(3)])
        theta = np.array([(q[i] * x[i]) / (sum_qx + 1e-12) for i in range(3)])
        
        # Parâmetro de forma l_i
        l = np.array([(z/2) * (r[i] - q[i]) - (r[i] - 1) for i in range(3)])
        
        # PARTE COMBINATORIAL
        ln_gamma_C = np.zeros(3)
        sum_xl = sum(x[j] * l[j] for j in range(3))
        
        for i in range(3):
            if x[i] < 1e-12:
                ln_gamma_C[i] = 0.0
                continue
            
            term1 = np.log(phi[i] / x[i])
            term2 = (z/2) * q[i] * np.log(theta[i] / phi[i])
            term3 = l[i]
            term4 = -(phi[i] / x[i]) * sum_xl
            
            ln_gamma_C[i] = term1 + term2 + term3 + term4
        
        # PARTE RESIDUAL
        ln_gamma_R = np.zeros(3)
        
        for i in range(3):
            # Termo 1: Σ_j θ_j τ_ji
            sum_theta_tau = sum(theta[j] * tau[j, i] for j in range(3))
            
            # Termo 2: Σ_j (θ_j τ_ij / Σ_k θ_k τ_kj)
            term2 = 0.0
            for j in range(3):
                denom = sum(theta[k] * tau[k, j] for k in range(3))
                if denom > 1e-12:
                    term2 += (theta[j] * tau[i, j]) / denom
            
            ln_gamma_R[i] = q[i] * (1 - np.log(sum_theta_tau + 1e-12) - term2)
        
        # TOTAL: ln(γ) = ln(γ^C) + ln(γ^R)
        ln_gamma = ln_gamma_C + ln_gamma_R
        
        # γ = exp(ln γ)
        gamma = np.exp(ln_gamma)
        
        # Limitar valores extremos
        gamma = np.clip(gamma, 1e-6, 1e6)
        
        return gamma
    
    def _gamma_unifac(self, x: np.ndarray) -> np.ndarray:
        """
        Coeficientes de atividade UNIFAC (Fredenslund et al. 1975)
        
        UNIFAC é um modelo PREDITIVO que usa contribuição de grupos funcionais.
        Não requer parâmetros binários experimentais.
        
        Args:
            x: Fraões molares [x1, x2, x3]
        
        Returns:
            Array com [γ1, γ2, γ3]
        
        References:
            - Fredenslund, Å., Jones, R.L., Prausnitz, J.M. (1975)
            "Group-contribution estimation of activity coefficients in nonideal liquid mixtures"
            AIChE J., 21, 1086-1099
        """
        try:
            from ell_unifac_params import calculate_unifac_gamma
            
            # Calcular γ usando UNIFAC preditivo
            gamma = calculate_unifac_gamma(
                components=self.components,
                x=x,
                T=self.TK  # Temperatura em Kelvin
            )
            
            # Limitar valores extremos (estabilidade numérica)
            gamma = np.clip(gamma, 1e-6, 1e6)
            
            return gamma
        
        except Exception as e:
            print(f"⚠️ Erro no cálculo UNIFAC: {e}")
            print(f"   Usando γ = 1 (solução ideal) como fallback")
            return np.ones(3)

    
    # ========================================================================
    # TESTE DE ESTABILIDADE (TANGENT PLANE DISTANCE - TPD)
    # ========================================================================
    
    def tangent_plane_distance(self, x_feed: np.ndarray, x_trial: np.ndarray) -> float:
        """
        Calcula Tangent Plane Distance (TPD) para teste de estabilidade
        
        TPD(w) = Σ_i w_i [ln(w_i) + ln(γ_i(w)) - ln(z_i) - ln(γ_i(z))]
        
        Se TPD < 0 em algum ponto, o sistema é INSTÁVEL (2 fases)
        Se TPD ≥ 0 em todos os pontos, o sistema é ESTÁVEL (1 fase)
        
        References:
            - Michelsen (1982), Eq. 10
            - Baker et al. (1982), Eq. 2
        
        Args:
            x_feed: Composição global [z1, z2, z3]
            x_trial: Composição de teste [w1, w2, w3]
        
        Returns:
            Valor de TPD(w)
        """
        # Evitar x = 0 (log singularidade)
        x_feed = np.clip(x_feed, 1e-10, 1.0)
        x_trial = np.clip(x_trial, 1e-10, 1.0)
        
        # Normalizar
        x_feed = x_feed / np.sum(x_feed)
        x_trial = x_trial / np.sum(x_trial)
        
        # Coeficientes de atividade
        gamma_feed = self.activity_coefficients(x_feed)
        gamma_trial = self.activity_coefficients(x_trial)
        
        # TPD = Σ_i w_i [ln(w_i γ_i(w)) - ln(z_i γ_i(z))]
        tpd = 0.0
        for i in range(3):
            log_fugacity_trial = np.log(x_trial[i]) + np.log(gamma_trial[i])
            log_fugacity_feed = np.log(x_feed[i]) + np.log(gamma_feed[i])
            
            tpd += x_trial[i] * (log_fugacity_trial - log_fugacity_feed)
        
        return tpd
    
    def is_stable(self, x: np.ndarray, n_trials: int = 20) -> bool:
        """
        Testa se uma composição é ESTÁVEL (1 fase) ou INSTÁVEL (2 fases)
        
        Algoritmo:
            1. Gerar múltiplos pontos de teste no triângulo de composição
            2. Calcular TPD(w) para cada ponto
            3. Se algum TPD < -1e-6, sistema é INSTÁVEL
            4. Caso contrário, sistema é ESTÁVEL
        
        Args:
            x: Composição global [z1, z2, z3]
            n_trials: Número de pontos de teste (padrão: 20)
        
        Returns:
            True se ESTÁVEL (1 fase), False se INSTÁVEL (2 fases)
        """
        # Normalizar composição
        x = np.clip(x, 0, 1)
        x = x / np.sum(x)
        
        # Gerar pontos de teste no triângulo
        trial_points = self._generate_triangle_points(n_trials)
        
        # Calcular TPD para cada ponto
        min_tpd = 0.0
        
        for x_trial in trial_points:
            tpd = self.tangent_plane_distance(x, x_trial)
            
            if tpd < min_tpd:
                min_tpd = tpd
        
        # Critério de estabilidade: TPD >= 0 para todos os pontos
        # Usar tolerância numérica de -1e-6
        is_stable = (min_tpd >= -1e-6)
        
        return is_stable
    
    def _generate_triangle_points(self, n: int) -> List[np.ndarray]:
        """
        Gera pontos aleatórios dentro do triângulo de composição
        
        Método:
            1. Gerar 2 números aleatórios u, v ~ U(0,1)
            2. Se u + v > 1, refletir: (u, v) → (1-u, 1-v)
            3. Composição: [u, v, 1-u-v]
        
        Args:
            n: Número de pontos
        
        Returns:
            Lista de arrays [x1, x2, x3]
        """
        points = []
        
        for _ in range(n):
            u = np.random.uniform(0, 1)
            v = np.random.uniform(0, 1)
            
            # Refletir se fora do triângulo
            if u + v > 1:
                u = 1 - u
                v = 1 - v
            
            # Composição ternária
            x = np.array([u, v, 1 - u - v])
            points.append(x)
        
        # Adicionar vértices do triângulo
        points.append(np.array([1.0, 0.0, 0.0]))
        points.append(np.array([0.0, 1.0, 0.0]))
        points.append(np.array([0.0, 0.0, 1.0]))
        
        # Adicionar pontos nas arestas
        for alpha in [0.1, 0.3, 0.5, 0.7, 0.9]:
            points.append(np.array([alpha, 1-alpha, 0.0]))
            points.append(np.array([alpha, 0.0, 1-alpha]))
            points.append(np.array([0.0, alpha, 1-alpha]))
        
        return points
    
    # ========================================================================
    # FLASH L1-L2 (RACHFORD-RICE MODIFICADO)
    # ========================================================================
    
    def flash_ell(self, z_feed: np.ndarray) -> Dict:
        """
        Flash L1-L2 usando minimização da energia livre de Gibbs
        
        VERSÃO 3.2 - COMPLETAMENTE REESCRITA
        
        Método: Minimizar G_mix = Σ_i n_i [ln(x_i) + ln(γ_i)]
        Restrições: 
            - Balanço material: n_L1 + n_L2 = 1
            - Σ x_L1,i = 1, Σ x_L2,i = 1
        
        References:
            - Baker et al. (1982), Eq. 5-7
            - Michelsen (1982), Eq. 15
        """
        from scipy.optimize import minimize
        
        # Normalizar z_feed
        z_feed = np.clip(z_feed, 1e-10, 1.0)
        z_feed = z_feed / np.sum(z_feed)
        
        # ETAPA 1: Teste de estabilidade
        stable = self.is_stable(z_feed)
        
        if stable:
            gamma = self.activity_coefficients(z_feed)
            return {
                'converged': True,
                'two_phase': False,
                'beta': 0.0,
                'x_L1': z_feed,
                'x_L2': z_feed,
                'K': np.ones(3),
                'gamma_L1': gamma,
                'gamma_L2': gamma,
                'residual': 0.0,
                'iterations': 0,
                'warning': 'Sistema completamente miscível (1 fase estável)'
            }
        
        # ETAPA 2: Sistema BIFÁSICO - Minimizar energia livre de Gibbs
        
        def gibbs_energy(vars):
            """
            Energia livre de Gibbs total do sistema bifásico
            
            vars = [x_L1[0], x_L1[1], x_L2[0], x_L2[1], beta]
            x_L1[2] = 1 - x_L1[0] - x_L1[1]
            x_L2[2] = 1 - x_L2[0] - x_L2[1]
            """
            # Extrair variáveis
            x1_L1 = vars[0]
            x2_L1 = vars[1]
            x1_L2 = vars[2]
            x2_L2 = vars[3]
            beta = vars[4]
            
            # Calcular terceira componente
            x3_L1 = 1 - x1_L1 - x2_L1
            x3_L2 = 1 - x1_L2 - x2_L2
            
            # Limites físicos
            if x3_L1 < 0 or x3_L2 < 0:
                return 1e10
            if beta < 0 or beta > 1:
                return 1e10
            
            x_L1 = np.array([x1_L1, x2_L1, x3_L1])
            x_L2 = np.array([x1_L2, x2_L2, x3_L2])
            
            # Evitar valores muito pequenos
            x_L1 = np.clip(x_L1, 1e-10, 1.0)
            x_L2 = np.clip(x_L2, 1e-10, 1.0)
            
            # Normalizar
            x_L1 = x_L1 / np.sum(x_L1)
            x_L2 = x_L2 / np.sum(x_L2)
            
            # Coeficientes de atividade
            gamma_L1 = self.activity_coefficients(x_L1)
            gamma_L2 = self.activity_coefficients(x_L2)
            
            # Energia livre de Gibbs de mistura
            # G/RT = (1-β) Σ x_L1,i ln(x_L1,i γ_L1,i) + β Σ x_L2,i ln(x_L2,i γ_L2,i)
            G_L1 = np.sum(x_L1 * (np.log(x_L1) + np.log(gamma_L1)))
            G_L2 = np.sum(x_L2 * (np.log(x_L2) + np.log(gamma_L2)))
            
            G_total = (1 - beta) * G_L1 + beta * G_L2
            
            # Penalizar violação do balanço material
            # z = (1-β) x_L1 + β x_L2
            x_calc = (1 - beta) * x_L1 + beta * x_L2
            penalty = 1e6 * np.sum((x_calc - z_feed)**2)
            
            return G_total + penalty
        
        # Estimativa inicial
        # Tentar várias estimativas e escolher a melhor
        best_result = None
        best_energy = 1e10
        
        initial_guesses = [
            # [x1_L1, x2_L1, x1_L2, x2_L2, beta]
            [0.8, 0.1, 0.1, 0.8, 0.5],  # Água rica vs TCE rica
            [0.1, 0.8, 0.8, 0.1, 0.5],  # TCE rica vs Água rica
            [0.6, 0.3, 0.3, 0.6, 0.5],  # Moderada
            [0.7, 0.2, 0.2, 0.7, 0.3],  # Assimétrica
            [0.4, 0.5, 0.5, 0.4, 0.6],  # Invertida
        ]
        
        for x0 in initial_guesses:
            try:
                # Bounds: 0.001 ≤ x_i ≤ 0.998, 0.001 ≤ β ≤ 0.999
                bounds = [
                    (0.001, 0.998),  # x1_L1
                    (0.001, 0.998),  # x2_L1
                    (0.001, 0.998),  # x1_L2
                    (0.001, 0.998),  # x2_L2
                    (0.001, 0.999),  # beta
                ]
                
                # Minimizar
                result = minimize(
                    gibbs_energy,
                    x0=x0,
                    method='L-BFGS-B',
                    bounds=bounds,
                    options={'maxiter': 200}
                )
                
                if result.success and result.fun < best_energy:
                    best_energy = result.fun
                    best_result = result
            except:
                continue
        
        # Verificar se encontrou solução
        if best_result is None or best_energy > 1e9:
            # Não convergiu
            return {
                'converged': False,
                'two_phase': True,
                'beta': 0.5,
                'x_L1': z_feed,
                'x_L2': z_feed,
                'K': np.ones(3),
                'gamma_L1': self.activity_coefficients(z_feed),
                'gamma_L2': self.activity_coefficients(z_feed),
                'residual': 1e10,
                'iterations': 0,
                'warning': 'Flash não convergiu - método de minimização falhou'
            }
        
        # Extrair solução
        vars_opt = best_result.x
        x_L1 = np.array([vars_opt[0], vars_opt[1], 1 - vars_opt[0] - vars_opt[1]])
        x_L2 = np.array([vars_opt[2], vars_opt[3], 1 - vars_opt[2] - vars_opt[3]])
        beta = vars_opt[4]
        
        # Normalizar
        x_L1 = np.clip(x_L1, 1e-10, 1.0)
        x_L2 = np.clip(x_L2, 1e-10, 1.0)
        x_L1 = x_L1 / np.sum(x_L1)
        x_L2 = x_L2 / np.sum(x_L2)
        
        # Calcular propriedades finais
        gamma_L1 = self.activity_coefficients(x_L1)
        gamma_L2 = self.activity_coefficients(x_L2)
        K = gamma_L2 / (gamma_L1 + 1e-12)
        
        # Calcular resíduo (balanço material)
        x_calc = (1 - beta) * x_L1 + beta * x_L2
        residual = np.linalg.norm(x_calc - z_feed)
        
        # Verificar se é solução trivial
        trivial_distance = np.linalg.norm(x_L1 - x_L2)
        
        if trivial_distance < 0.05:
            # Solução trivial
            return {
                'converged': False,
                'two_phase': False,
                'beta': 0.0,
                'x_L1': z_feed,
                'x_L2': z_feed,
                'K': np.ones(3),
                'gamma_L1': self.activity_coefficients(z_feed),
                'gamma_L2': self.activity_coefficients(z_feed),
                'residual': residual,
                'iterations': best_result.nit,
                'warning': 'Flash convergiu para solução trivial (fases idênticas)'
            }
        
        # Solução válida
        return {
            'converged': True,
            'two_phase': True,
            'beta': float(beta),
            'x_L1': x_L1,
            'x_L2': x_L2,
            'K': K,
            'gamma_L1': gamma_L1,
            'gamma_L2': gamma_L2,
            'residual': float(residual),
            'iterations': best_result.nit,
            'warning': None if residual < 1e-3 else f'Resíduo de balanço material: {residual:.2e}'
        }


    
    def _estimate_initial_phases(self, z: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Estima composições iniciais das fases L1 e L2 para flash
        
        Método: Encontrar os 2 pontos com menor TPD
        
        Args:
            z: Composição global
        
        Returns:
            (x_L1_init, x_L2_init)
        """
        # Gerar pontos de teste
        trial_points = self._generate_triangle_points(50)
        
        # Calcular TPD para cada ponto
        tpd_values = []
        for x_trial in trial_points:
            tpd = self.tangent_plane_distance(z, x_trial)
            tpd_values.append((tpd, x_trial))
        
        # Ordenar por TPD crescente
        tpd_values.sort(key=lambda pair: pair[0])
        
        # Pegar os 2 pontos com menor TPD
        x_L1_init = tpd_values[0][1]
        x_L2_init = tpd_values[1][1]
        
        return x_L1_init, x_L2_init
    
    
    # ============================================================================
    # EXTRAÇÃO LÍQUIDO-LÍQUIDO MULTI-ESTÁGIOS
    # ============================================================================

    def calculate_multistage_extraction(
        self,
        z_feed: np.ndarray,
        S_F_ratio: float,
        target_recovery: float = 0.95,
        efficiency: float = 1.0,
        solute_index: Optional[int] = None
    ) -> Dict:
        """
        Extração líquido-líquido multi-estágios (Kremser-Souders-Brown)
        VERSÃO 3.0 - Lógica corrigida de identificação de componentes
        """
        
        # Normalizar entrada
        z_feed = np.clip(z_feed, 1e-10, 1.0)
        z_feed = z_feed / np.sum(z_feed)
        
        print("="*70)
        print("EXTRAÇÃO LÍQUIDO-LÍQUIDO MULTI-ESTÁGIOS")
        print("="*70)
        print(f"Componentes: {self.components}")
        print(f"z_feed: {z_feed}")
        print(f"S/F: {S_F_ratio:.2f}, η_target: {target_recovery*100:.0f}%, E_M: {efficiency*100:.0f}%")
        
        # ========================================================================
        # ETAPA 1: IDENTIFICAR SOLVENTE (componente ausente no feed)
        # ========================================================================
        print(f"\n{'ETAPA 1: IDENTIFICAR COMPONENTES':-^70}")
        
        solvent_idx = None
        for i in range(3):
            if z_feed[i] < 1e-6:
                solvent_idx = i
                print(f"✅ Solvente: {self.components[i]} (ausente no feed)")
                break
        
        if solvent_idx is None:
            return {
                'converged': False,
                'warning': 'Extração requer solvente puro (z=0 no feed)'
            }
        
        # ========================================================================
        # ETAPA 2: FLASH COM COMPOSIÇÃO MÉDIA (feed + solvente)
        # ========================================================================
        print(f"\n{'ETAPA 2: FLASH L1-L2':-^70}")
        
        # Criar z_avg = 70% feed + 30% solvente
        z_avg = z_feed.copy()
        z_avg[solvent_idx] = 0.30
        z_avg = z_avg / np.sum(z_avg)
        
        print(f"Composição para flash: {z_avg}")
        
        flash_result = self.flash_ell(z_avg)
        
        if not flash_result.get('two_phase', False):
            return {
                'converged': False,
                'warning': 'Sistema miscível mesmo com solvente'
            }
        
        x_L1 = flash_result['x_L1']
        x_L2 = flash_result['x_L2']
        K = flash_result['K']
        
        print(f"✅ Bifásico: x_L1={x_L1}, x_L2={x_L2}")
        print(f"   K = {K}")
        
        # ========================================================================
        # ETAPA 3: IDENTIFICAR SOLUTO (nem solvente, nem diluente principal)
        # ========================================================================
        print(f"\n{'ETAPA 3: IDENTIFICAR SOLUTO':-^70}")
        
        # Diluente = componente com MAIOR fração no feed (geralmente água)
        diluent_idx = int(np.argmax(z_feed))
        
        # Soluto = o terceiro componente (nem solvente, nem diluente)
        solute_idx = [i for i in range(3) if i != solvent_idx and i != diluent_idx][0]
        
        print(f"  Diluente: {self.components[diluent_idx]} (maior fração no feed)")
        print(f"⭐ Soluto: {self.components[solute_idx]}")
        print(f"  Solvente: {self.components[solvent_idx]}")
        print(f"  K(soluto) = {K[solute_idx]:.4f}")
        
        solute_name = self.components[solute_idx]
        K_solute = K[solute_idx]
        
        # ========================================================================
        # ETAPA 4: FATOR DE EXTRAÇÃO
        # ========================================================================
        print(f"\n{'ETAPA 4: FATOR DE EXTRAÇÃO':-^70}")
        
        # ---------------------- ETAPA 4: FATOR DE EXTRAÇÃO ----------------------
        E = (S_F_ratio) * K_solute

        if E < 0.5:
            # E muito baixo - extração inviável
            return {
                'converged': False,
                'warning': f'Extração inviável: Fator de extração E={E:.4f} muito baixo (E < 0.5). '
                        f'O soluto {solute_name} não se distribui adequadamente para a fase solvente. '
                        f'K_distribuição = {K_solute:.4f}. '
                        f'Sugestões: (1) Aumentar razão S/F, (2) Tentar outro solvente, (3) Usar modelo NRTL/UNIQUAC com parâmetros experimentais.',
                'K_distribution': float(K_solute),
                'extraction_factor': float(E),
                'S_F_ratio': S_F_ratio,
                'solute_index': solute_idx,
                'solute_name': solute_name,
                'TC': self.TC,
                'TK': self.TK,
                'model': self.model
            }
        elif E < 1:
            print(f"⚠️  0.5 < E < 1: Desfavorável (muitos estágios necessários)")
        else:
            print(f"  ✅ E > 1: Viável")

        
        # ========================================================================
        # ETAPA 5: KREMSER-SOUDERS-BROWN
        # ========================================================================
        print(f"\n{'ETAPA 5: KREMSER':-^70}")
        
        X_f = z_feed[solute_idx]
        X_r = X_f * (1.0 - target_recovery)
        Y_s = 0.0
        
        print(f"  X_f = {X_f:.4f}, X_r = {X_r:.4f}, Y_s = {Y_s:.4f}")
        
        if abs(E - 1.0) > 1e-6:
            # Perry's Eq. 15-48
            num = (X_f - Y_s/K_solute) / (X_r - Y_s/K_solute)
            denom = (E - 1)/E + 1/E
            
            if num <= 0 or denom <= 0:
                return {
                    'converged': False,
                    'warning': f'Termo negativo: num={num:.2e}, denom={denom:.2e}'
                }
            
            N_theoretical = np.log(num * denom) / np.log(E)
        else:
            N_theoretical = (X_f - Y_s/K_solute) / (X_r - Y_s/K_solute) - 1
        
        N_actual = N_theoretical / efficiency
        N_rounded = int(np.ceil(N_actual))
        
        print(f"  N_teórico = {N_theoretical:.2f}")
        print(f"  N_real = {N_actual:.2f}")
        print(f"  N_arredondado = {N_rounded}")
        
        # ========================================================================
        # ETAPA 6: RECUPERAÇÃO REAL COM N ARREDONDADO
        # ========================================================================
        print(f"\n{'ETAPA 6: RECUPERAÇÃO':-^70}")
        
        if abs(E - 1.0) > 1e-6:
            E_N = E ** (N_rounded)
            recovery_achieved = (E_N - 1) / (E_N - 1/E)
        else:
            recovery_achieved = N_rounded / (N_rounded + 1)
        
        recovery_achieved = np.clip(recovery_achieved, 0, 1)
        
        print(f"  Recuperação = {recovery_achieved*100:.1f}%")
        
        # Composições finais
        x_raffinate = z_feed.copy()
        x_raffinate[solute_idx] *= (1.0 - recovery_achieved)
        x_raffinate = x_raffinate / np.sum(x_raffinate)
        
        x_extract = x_L2.copy()
        
        print(f"  x_rafinado: {x_raffinate}")
        print(f"  x_extrato: {x_extract}")
        
        print(f"\n{'='*70}")
        print(f"✅ {N_rounded} estágios, recuperação {recovery_achieved*100:.1f}%")
        print(f"{'='*70}\n")
        
        return {
            'converged': True,
            'two_phase': True,
            'N_theoretical': float(N_theoretical),
            'N_actual': float(N_actual),
            'N_rounded': N_rounded,
            'extraction_factor': float(E),
            'K_distribution': float(K_solute),
            'S_F_ratio': S_F_ratio,
            'efficiency': efficiency,
            'z_feed': z_feed.tolist(),
            'x_raffinate': x_raffinate.tolist(),
            'x_extract': x_extract.tolist(),
            'recovery_achieved': float(recovery_achieved),
            'target_recovery': target_recovery,
            'solute_index': solute_idx,
            'solute_name': solute_name,
            'TC': self.TC,
            'TK': self.TK,
            'model': self.model,
            'warning': None
        }




    # ============================================================================
    # FUNÇÃO AUXILIAR: EXTRAÇÃO COM NÚMERO FIXO DE ESTÁGIOS
    # ============================================================================

    def calculate_extraction_with_fixed_stages(
        self,
        z_feed: np.ndarray,
        S_F_ratio: float,
        N_stages: int,
        efficiency: float = 1.0,
        solute_index: Optional[int] = None  # ⭐ AGORA OPCIONAL
    ) -> Dict:
        """
        Calcula recuperação alcançada com número FIXO de estágios
        (inverso da função anterior)
        
        Usa equação de Kremser-Souders-Brown invertida (Perry's Eq. 15-49):
            ε = (E^(N+1) - E) / (E^(N+1) - 1)
        
        VERSÃO 2.0 - Auto-detecção do soluto
        
        Args:
            z_feed: Composição da alimentação
            S_F_ratio: Razão Solvente/Alimentação
            N_stages: Número de estágios disponíveis
            efficiency: Eficiência de estágio
            solute_index: Índice do soluto (opcional, auto-detecta se None)
        
        Returns:
            Dict com recuperação alcançada e outras propriedades:
                - converged: True se cálculo bem-sucedido
                - N_stages: Número de estágios fornecido
                - N_theoretical: Número de estágios teóricos (N_stages * efficiency)
                - extraction_factor: Fator de extração E
                - K_distribution: Coeficiente de distribuição K
                - recovery_achieved: Recuperação real alcançada
                - solute_index: Índice do soluto usado
                - solute_name: Nome do soluto
                - ... (demais campos)
        
        Example:
            >>> result = calc.calculate_extraction_with_fixed_stages(
            ...     z, S_F_ratio=2.0, N_stages=5
            ... )
            >>> print(f"Com 5 estágios, recuperação = {result['recovery_achieved']*100:.1f}%")
        """
        
        # ========================================================================
        # ETAPA 1: FLASH E AUTO-DETECÇÃO DE SOLUTO
        # ========================================================================
        z_feed = np.clip(z_feed, 1e-10, 1.0)
        z_feed = z_feed / np.sum(z_feed)
        
        print(f"\n[ELL EXTRAÇÃO-FIXED] {N_stages} estágios, S/F={S_F_ratio}, η={efficiency*100:.0f}%")
        
        flash_result = self.flash_ell(z_feed)
        
        if not flash_result.get('two_phase', False):
            return {
                'converged': False,
                'warning': 'Sistema monofsico. Extração não aplicável.'
            }
        
        K = flash_result['K']
        
        # ⭐ Auto-detectar soluto
        if solute_index is None:
            solute_index = int(np.argmin(K))
            print(f"⭐ Soluto auto-detectado: {self.components[solute_index]} (K={K[solute_index]:.4f})")
        
        solute_name = self.components[solute_index]
        K_solute = K[solute_index]
        # Calcular fator de extração
        E = (S_F_ratio) * K_solute

        # ✅ ADICIONAR VALIDAÇÃO
        if E < 0.5:
            return {
                'converged': False,
                'warning': f'Extração inviável: Fator de extração E={E:.4f} muito baixo (E < 0.5). '
                        f'O soluto não se distribui adequadamente. K = {K_solute:.4f}',
                'K_distribution': float(K_solute),
                'extraction_factor': float(E),
                'S_F_ratio': S_F_ratio,
                'Nstages': N_stages,
                'recovery_achieved': 0.0,
                'TC': self.TC,
                'TK': self.TK,
                'model': self.model
            }

        # Resto do código continua...

        
        # ========================================================================
        # ETAPA 2: CALCULAR RECUPERAÇÃO COM N FIXO
        # ========================================================================
        N_theoretical = N_stages * efficiency
        
        if abs(E - 1.0) > 1e-6:
            # Caso geral: E ≠ 1
            E_N = E ** (N_theoretical + 1)
            recovery = (E_N - E) / (E_N - 1)
        else:
            # Caso limite: E = 1
            recovery = N_theoretical / (N_theoretical + 1)
        
        recovery = np.clip(recovery, 0, 1)
        
        print(f"[ELL EXTRAÇÃO-FIXED] ✅ Recuperação alcançada: {recovery*100:.1f}%")
        
        return {
            'converged': True,
            'N_stages': N_stages,
            'N_theoretical': float(N_theoretical),
            'extraction_factor': float(E),
            'K_distribution': float(K_solute),
            'recovery_achieved': float(recovery),
            'S_F_ratio': S_F_ratio,
            'efficiency': efficiency,
            'solute_index': solute_index,
            'solute_name': solute_name,
            'TC': self.TC,
            'TK': self.TK,
            'model': self.model,
            'z_feed': z_feed.tolist(),
            'warning': None
        }


    
    # ========================================================================
    # DIAGRAMA TERNÁRIO (BINODAL + TIE-LINES)
    # ========================================================================
    
    def generate_binodal_curve(self, n_points: int = 50) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Gera curva binodal usando método adaptativo (Convex Hull ou Setores Radiais)
        VERSÃO 9.2 - OTIMIZADA PARA RENDER (512MB RAM)
        
        Otimizações para produção:
        - n_grid: 20 → 10 no Render (75% menos pontos)
        - is_stable: 10 → 5 trials no Render (50% mais rápido)
        - Garbage collection explícito
        """
        print("\n🔬 [BINODAL] Iniciando geração da curva binodal...")
        
        # ⚡ OTIMIZAÇÃO PARA RENDER (512MB RAM)
        import os
        import gc
        
        if os.environ.get('RENDER'):
            n_grid = 10
            n_stability_trials = 5
            print("   🎯 Render detectado: grid=10x10, trials=5")
        else:
            n_grid = 20
            n_stability_trials = 10
            print("   🏠 Ambiente local: grid=20x20, trials=10")
        
        all_L1_points = []
        all_L2_points = []
        
        tested = 0
        unstable = 0
        
        # ========================================================================
        # ETAPA 1: VARREDURA
        # ========================================================================
        
        for i in range(n_grid + 1):
            for j in range(n_grid + 1):
                u = i / n_grid
                v = j / n_grid
                
                if u + v > 1.0:
                    continue
                
                x1 = u
                x2 = v
                x3 = 1 - u - v
                
                if max(x1, x2, x3) > 0.98 or min(x1, x2, x3) < 0.01:
                    continue
                
                x = np.array([x1, x2, x3])
                tested += 1
                
                stable = self.is_stable(x, n_trials=n_stability_trials)
                
                if not stable:
                    unstable += 1
                    try:
                        flash_result = self.flash_ell(x)
                        if flash_result['converged'] and flash_result['two_phase']:
                            xL1 = flash_result['xL1']
                            xL2 = flash_result['xL2']
                            distance = np.linalg.norm(xL1 - xL2)
                            
                            if distance > 0.08:
                                all_L1_points.append(xL1.copy())
                                all_L2_points.append(xL2.copy())
                    except:
                        pass
            
            # Liberar memória a cada linha do grid
            if i % 5 == 0:
                gc.collect()
        
        print(f"   Testados: {tested} pontos")
        print(f"   Instáveis: {unstable} pontos")
        print(f"   Pontos bifásicos: {len(all_L1_points)}")
        
        if len(all_L1_points) < 10:
            print("   ⚠️ Poucos pontos encontrados!")
            return [], []
        
        # ========================================================================
        # ETAPA 2: UNIR L1 + L2 (Todos os pontos da região bifásica)
        # ========================================================================
        
        all_points = all_L1_points + all_L2_points
        
        # ========================================================================
        # ETAPA 3: EXTRAIR BORDA (Convex Hull ou Setores Radiais)
        # ========================================================================
        
        print("\n🔧 Extraindo pontos da borda...")
        
        def to_2d(points_3d):
            """Projeta pontos ternários para 2D"""
            if len(points_3d) == 0:
                return np.array([])
            points_2d = []
            sqrt3_2 = np.sqrt(3) / 2
            for p in points_3d:
                x = p[1] + 0.5 * p[2]
                y = sqrt3_2 * p[2]
                points_2d.append([x, y])
            return np.array(points_2d)
        
        all_points_2d = to_2d(all_points)
        print(f"   Total de pontos 2D: {len(all_points_2d)}")
        
        try:
            from scipy.spatial import ConvexHull
            
            hull = ConvexHull(all_points_2d)
            hull_indices = hull.vertices
            print(f"   ✅ Convex Hull: {len(hull_indices)} pontos na borda")
            
            # Teste de convexidade
            hull_area = hull.volume
            x_coords = all_points_2d[:, 0]
            y_coords = all_points_2d[:, 1]
            bbox_area = (np.max(x_coords) - np.min(x_coords)) * (np.max(y_coords) - np.min(y_coords))
            area_ratio = hull_area / bbox_area if bbox_area > 0 else 0
            
            print(f"   Hull área: {hull_area:.4f}, BBox área: {bbox_area:.4f}, Razão: {area_ratio:.3f}")
            
            if area_ratio < 0.65:
                print(f"   ⚠️ Curva côncava detectada! Usando método alternativo...")
                
                # Método alternativo: Setores radiais
                centroid = np.mean(all_points_2d, axis=0)
                n_sectors = 30
                angle_bins = np.linspace(-np.pi, np.pi, n_sectors + 1)
                
                angles = []
                distances = []
                for pt in all_points_2d:
                    dx = pt[0] - centroid[0]
                    dy = pt[1] - centroid[1]
                    angle = np.arctan2(dy, dx)
                    distance = np.sqrt(dx**2 + dy**2)
                    angles.append(angle)
                    distances.append(distance)
                
                angles = np.array(angles)
                distances = np.array(distances)
                
                border_indices = []
                for i in range(n_sectors):
                    mask = (angles >= angle_bins[i]) & (angles < angle_bins[i+1])
                    sector_indices = np.where(mask)[0]
                    if len(sector_indices) > 0:
                        farthest_idx = sector_indices[np.argmax(distances[sector_indices])]
                        border_indices.append(farthest_idx)
                
                print(f"   ✅ Extraídos {len(border_indices)} pontos (método radial)")
                binodal_points_3d = [all_points[i] for i in border_indices]
            else:
                print(f"   ✅ Curva convexa, usando Convex Hull")
                binodal_points_3d = [all_points[i] for i in hull_indices]
        
        except Exception as e:
            print(f"   ⚠️ Erro no Convex Hull: {e}")
            print(f"   ⚠️ Usando fallback simples...")
            binodal_points_3d = all_points
        
        # Remover duplicatas
        binodal_unique = self.remove_duplicates(binodal_points_3d, tol=0.01)
        print(f"   ✅ Após remover duplicatas: {len(binodal_unique)} pontos")
        
        if len(binodal_unique) < 3:
            print(f"   ❌ Poucos pontos únicos!")
            gc.collect()
            return [], []
        
        # ========================================================================
        # ETAPA 3.5: ORDENAR PONTOS (Nearest Neighbor)
        # ========================================================================
        
        print("\n🔧 Ordenando pontos ao longo da curva...")
        
        points_2d_border = to_2d(binodal_unique)
        
        # Nearest neighbor (TSP greedy)
        ordered_indices = [0]  # Começar no primeiro ponto
        remaining = list(range(1, len(binodal_unique)))
        max_iterations = len(binodal_unique)
        iterations = 0
        
        while remaining and iterations < max_iterations:
            iterations += 1
            current_pt = points_2d_border[ordered_indices[-1]]
            min_dist = float('inf')
            closest_idx = None
            
            for idx in remaining:
                pt = points_2d_border[idx]
                dist = np.linalg.norm(pt - current_pt)
                if dist < min_dist:
                    min_dist = dist
                    closest_idx = idx
            
            if closest_idx is not None:
                ordered_indices.append(closest_idx)
                remaining.remove(closest_idx)
            else:
                break
        
        binodal_ordered = [binodal_unique[i] for i in ordered_indices]
        print(f"   ✅ Pontos ordenados: {len(binodal_ordered)} pontos")
        
        # ========================================================================
        # ETAPA 4: FECHAR CURVA (NÃO DIVIDIR EM L1/L2)
        # ========================================================================
        
        print("\n🔧 [ETAPA 4: FECHAR CURVA]")
        
        # Garantir que a curva está fechada
        first_point = binodal_ordered[0]
        last_point = binodal_ordered[-1]
        distance_to_close = np.linalg.norm(first_point - last_point)
        
        if distance_to_close > 0.05:
            print(f"   ⚠️ Curva aberta (distância: {distance_to_close:.3f})")
            print(f"   ✅ Fechando curva (adicionando primeiro ponto ao final)")
            binodal_ordered.append(first_point.copy())
        else:
            print(f"   ✅ Curva já está fechada (distância: {distance_to_close:.3f})")
        
        print(f"   ✅ Curva binodal única: {len(binodal_ordered)} pontos\n")
        
        # Liberar memória antes de retornar
        del all_L1_points, all_L2_points, all_points, all_points_2d
        gc.collect()
        
        # RETORNAR CURVA ÚNICA (toda em L1, L2 vazio)
        return binodal_ordered, []



    
    def _remove_duplicates(self, points: List[np.ndarray], tol: float = 1e-3) -> List[np.ndarray]:
        """
        Remove pontos duplicados de uma lista
        
        Args:
            points: Lista de arrays [x1, x2, x3]
            tol: Tolerância para considerar pontos iguais
        
        Returns:
            Lista sem duplicatas
        """
        if len(points) == 0:
            return []
        
        unique = [points[0]]
        
        for p in points[1:]:
            is_duplicate = False
            
            for u in unique:
                if np.linalg.norm(p - u) < tol:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(p)
        
        return unique
    
    def _sort_binodal_by_component(self, points: List[np.ndarray], component_idx: int = 0) -> List[np.ndarray]:
        """
        Ordena pontos da binodal por fração de um componente específico
        
        VERSÃO 5.0 - Ordenação simples e eficaz para curvas binodais
        
        Args:
            points: Lista de pontos [x1, x2, x3]
            component_idx: Índice do componente para ordenar (0=Water, 1=TCE, 2=Acetone)
        
        Returns:
            Pontos ordenados
        """
        if len(points) <= 2:
            return points
        
        # Converter para array numpy
        points_array = np.array(points)
        
        # Ordenar por fração do componente especificado
        sorted_indices = np.argsort(points_array[:, component_idx])
        
        # Retornar pontos ordenados
        return [points[i] for i in sorted_indices]

    
    def _sort_curve_points(self, points: List[np.ndarray]) -> List[np.ndarray]:
        """
        Ordena pontos conectando cada ponto ao seu vizinho mais próximo
        
        VERSÃO 3.6 - NEAREST NEIGHBOR (GREEDY TSP)
        
        Algoritmo:
            1. Começar no ponto mais à esquerda (menor componente 1)
            2. Conectar ao vizinho não-visitado mais próximo
            3. Repetir até visitar todos os pontos
        
        Garante curva SEM "pulos" ou "ziguezagues"
        """
        if len(points) <= 2:
            return points
        
        # Converter para array numpy
        points_array = np.array(points)
        n_points = len(points_array)
        
        # Encontrar ponto inicial: menor fração de componente 1 (Water)
        # Isso garante que começamos em uma extremidade da curva
        start_idx = np.argmin(points_array[:, 0])
        
        # Lista de pontos ordenados
        ordered_points = [points[start_idx]]
        visited = {start_idx}
        current_idx = start_idx
        
        # Conectar ao vizinho mais próximo (Greedy nearest neighbor)
        while len(visited) < n_points:
            min_distance = float('inf')
            nearest_idx = None
            
            # Procurar o vizinho não-visitado mais próximo
            for i in range(n_points):
                if i in visited:
                    continue
                
                # Distância euclidiana no espaço ternário
                distance = np.linalg.norm(points_array[current_idx] - points_array[i])
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = i
            
            # Adicionar vizinho mais próximo
            if nearest_idx is not None:
                ordered_points.append(points[nearest_idx])
                visited.add(nearest_idx)
                current_idx = nearest_idx
            else:
                # Segurança: se não encontrou vizinho, parar
                break
        
        return ordered_points



    
    def generate_tie_lines(self, n_lines: int = 5) -> List[Dict]:
        """Gera tie-lines válidas com distância mínima garantida"""
        
        print(f"\n[DEBUG] Gerando {n_lines} tie-lines...")
        tie_lines = []
        
        # Grade mais densa
        test_compositions = []
        for x1 in np.linspace(0.10, 0.80, 15):
            for x2 in np.linspace(0.10, 0.80, 15):
                x3 = 1 - x1 - x2
                if 0.05 < x3 < 0.85:
                    test_compositions.append(np.array([x1, x2, x3]))
        
        print(f"[DEBUG] Testando {len(test_compositions)} composições...")
        
        for z in test_compositions:
            try:
                flash_result = self.flash_ell(z)
                
                if not (flash_result['converged'] and flash_result['two_phase']):
                    continue
                
                x_L1 = np.array(flash_result['x_L1'])
                x_L2 = np.array(flash_result['x_L2'])
                beta = float(flash_result['beta'])
                
                # ⚠️ CORREÇÃO CRÍTICA: Distância mínima AUMENTADA
                phase_distance = np.linalg.norm(x_L1 - x_L2)
                
                if phase_distance < 0.30:  # ← MUDADO de 0.05 para 0.30
                    continue
                
                # Beta razoável
                if beta < 0.05 or beta > 0.95:
                    continue
                
                # Verificar duplicatas
                is_duplicate = False
                for existing in tie_lines:
                    d1 = np.linalg.norm(x_L1 - np.array(existing['x_L1']))
                    d2 = np.linalg.norm(x_L2 - np.array(existing['x_L2']))
                    if d1 < 0.10 and d2 < 0.10:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    tie_lines.append({
                        'x_L1': x_L1.tolist(),
                        'x_L2': x_L2.tolist(),
                        'beta': beta,
                        'distance': float(phase_distance)
                    })
                    
                    print(f"[DEBUG] ✅ Tie-line {len(tie_lines)}: dist={phase_distance:.3f}, β={beta:.3f}")
                
                if len(tie_lines) >= n_lines * 3:
                    break
            
            except:
                pass
        
        print(f"[DEBUG] Total válidas: {len(tie_lines)}")
        
        if len(tie_lines) == 0:
            print("[WARNING] Nenhuma tie-line válida!")
            return []
        
        # Ordenar por distância DECRESCENTE (maiores primeiro)
        tie_lines.sort(key=lambda t: t['distance'], reverse=True)
        
        # Selecionar as n_lines MAIORES
        return tie_lines[:n_lines]
    
    def _remove_duplicate_tielines(self, tie_lines: List[Dict], tol: float = 1e-3) -> List[Dict]:
        """
        Remove tie-lines duplicadas
        
        Args:
            tie_lines: Lista de dicts com x_L1, x_L2
            tol: Tolerância
        
        Returns:
            Lista sem duplicatas
        """
        if len(tie_lines) == 0:
            return []
        
        unique = [tie_lines[0]]
        
        for t in tie_lines[1:]:
            is_duplicate = False
            
            for u in unique:
                dist_L1 = np.linalg.norm(t['x_L1'] - u['x_L1'])
                dist_L2 = np.linalg.norm(t['x_L2'] - u['x_L2'])
                
                if dist_L1 < tol and dist_L2 < tol:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(t)
        
        return unique


# ============================================================================
# FUNÇÕES DE INTERFACE (PARA ROTAS FLASK)
# ============================================================================

def calculate_ell_flash(components: List[str], z_feed: List[float], 
                       temperature_C: float, model: str = 'NRTL') -> Dict:
    """
    Calcula flash L1-L2 isotérmico
    
    Args:
        components: Lista com 3 nomes de componentes
        z_feed: Composição global [z1, z2, z3]
        temperature_C: Temperatura em °C
        model: 'NRTL' ou 'UNIQUAC'
    
    Returns:
        dict com success, results, ai_suggestion
    """
    try:
        # Criar calculadora
        calc = ELLCalculator(components, temperature_C, model)
        
        # Converter para array
        z = np.array(z_feed)
        
        # Calcular flash
        flash_result = calc.flash_ell(z)
        
        # Formatar resultados
        results = {
            'TC': calc.TC,
            'TK': calc.TK,
            'model': calc.model,
            'components': components,
            'z_feed': z.tolist(),
            'converged': flash_result['converged'],
            'two_phase': flash_result['two_phase'],
            'beta': flash_result['beta'],
            'x_L1': flash_result['x_L1'].tolist(),
            'x_L2': flash_result['x_L2'].tolist(),
            'K': flash_result['K'].tolist(),
            'gamma_L1': flash_result['gamma_L1'].tolist(),
            'gamma_L2': flash_result['gamma_L2'].tolist(),
            'residual': flash_result['residual'],
            'iterations': flash_result['iterations'],
            'warning': flash_result.get('warning')
        }
        
        # Recomendação IA
        ai_suggestion = None
        if HAS_AI:
            try:
                ai_suggestion = analyze_ell_system(components, 'flash')
            except:
                pass
        
        return {
            'success': True,
            'results': results,
            'ai_suggestion': ai_suggestion
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def generate_ternary_diagram_ell(components: List[str], temperature_C: float, 
                                 model: str = 'NRTL', n_tie_lines: int = 5) -> Dict:
    """
    Gera diagrama ternário com binodal e tie-lines
    
    VERSÃO 3.6 - NEAREST NEIGHBOR (CURVA GARANTIDA)
    """
    import time
    start_time = time.time()
    
    try:
        calc = ELLCalculator(components, temperature_C, model)
        
        print("\n" + "="*70)
        print("[ELL DIAGRAMA] Gerando diagrama ternário")
        print(f"  Componentes: {components}")
        print(f"  Temperatura: {temperature_C}°C")
        print(f"  Modelo: {model}")
        print(f"  n_tie_lines: {n_tie_lines}")
        print("="*70)
        print()
        
        # Gerar binodal
        binodal_L1, binodal_L2 = calc.generate_binodal_curve(n_points=50)
        
        # 🔧 APLICAR ORDENAÇÃO NEAREST NEIGHBOR (garante curva sem pulos)
        if len(binodal_L1) > 3:
            binodal_L1 = calc._sort_curve_points(binodal_L1)
        if len(binodal_L2) > 3:
            binodal_L2 = calc._sort_curve_points(binodal_L2)
        
        # Gerar tie-lines
        tie_lines = calc.generate_tie_lines(n_lines=n_tie_lines)
        
        print("\n" + "="*70)
        print("[ELL DIAGRAMA] ✅ DIAGRAMA GERADO")
        print(f"  Binodal: {len(binodal_L1) + len(binodal_L2)} pontos")
        print(f"  Tie-lines: {len(tie_lines)} linhas")
        print("="*70)
        print()
        
        elapsed = time.time() - start_time
        print(f"[ELL DIAGRAMA] ✅ Diagrama gerado em {elapsed:.2f}s")
        
        # Formatar resultados
        results = {
            'TC': calc.TC,
            'TK': calc.TK,
            'model': calc.model,
            'components': components,
            'binodal_L1': [p.tolist() if isinstance(p, np.ndarray) else p for p in binodal_L1],
            'binodal_L2': [p.tolist() if isinstance(p, np.ndarray) else p for p in binodal_L2],
            'tie_lines': [
                {
                    'x_L1': t['x_L1'] if isinstance(t['x_L1'], list) else t['x_L1'].tolist(),
                    'x_L2': t['x_L2'] if isinstance(t['x_L2'], list) else t['x_L2'].tolist(),
                    'beta': t['beta']
                }
                for t in tie_lines
            ],
            'n_binodal_points': len(binodal_L1) + len(binodal_L2),
            'n_tie_lines': len(tie_lines)
        }
        
        # Recomendação IA
        ai_suggestion = None
        if HAS_AI:
            try:
                ai_suggestion = analyze_ell_system(components, 'ternary')
            except:
                pass
        
        return {
            'success': True,
            'results': results,
            'ai_suggestion': ai_suggestion
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

# ============================================================================
# TESTE DE VALIDAÇÃO
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("TESTE: ell_calculator.py (VERSÃO 3.0)")
    print("=" * 80)
    print()
    
    # Sistema: Water / TCE / Acetone (NRTL - Tabela E-5)
    components = ['Water', '1,1,2-Trichloroethane', 'Acetone']
    T_C = 25.0
    model = 'NRTL'
    
    print(f"📚 Sistema: {' / '.join(components)}")
    print(f"🌡️  Temperatura: {T_C}°C")
    print(f"⚙️  Modelo: {model}")
    print()
    
    # Teste 1: Flash
    print("🧪 TESTE 1: Flash L1-L2")
    print("-" * 80)
    
    z_feed = [0.30, 0.40, 0.30]
    result = calculate_ell_flash(components, z_feed, T_C, model)
    
    if result['success']:
        res = result['results']
        print(f"✅ Flash convergiu: {res['converged']}")
        print(f"✅ Sistema bifásico: {res['two_phase']}")
        
        if res['two_phase']:
            print(f"\n📊 Resultados:")
            print(f"  β (fração L2) = {res['beta']:.4f}")
            print(f"  x_L1 = [{res['x_L1'][0]:.4f}, {res['x_L1'][1]:.4f}, {res['x_L1'][2]:.4f}]")
            print(f"  x_L2 = [{res['x_L2'][0]:.4f}, {res['x_L2'][1]:.4f}, {res['x_L2'][2]:.4f}]")
            print(f"  K    = [{res['K'][0]:.4f}, {res['K'][1]:.4f}, {res['K'][2]:.4f}]")
            print(f"  Iterações: {res['iterations']}")
        else:
            print(f"⚠️ {res['warning']}")
    else:
        print(f"❌ Erro: {result['error']}")
    
    print()
    
    # Teste 2: Diagrama ternário
    print("🧪 TESTE 2: Diagrama Ternário")
    print("-" * 80)
    
    result = generate_ternary_diagram_ell(components, T_C, model, n_tie_lines=5)
    
    if result['success']:
        res = result['results']
        print(f"✅ Binodal gerada: {res['n_binodal_points']} pontos")
        print(f"✅ Tie-lines: {res['n_tie_lines']} linhas")
        
        if res['n_binodal_points'] > 0:
            print(f"\n📊 Primeiros pontos da binodal (fase L1):")
            for i, p in enumerate(res['binodal_L1'][:3]):
                print(f"  Ponto {i+1}: [{p[0]:.4f}, {p[1]:.4f}, {p[2]:.4f}]")
        
        if res['n_tie_lines'] > 0:
            print(f"\n📊 Primeira tie-line:")
            t = res['tie_lines'][0]
            print(f"  L1: [{t['x_L1'][0]:.4f}, {t['x_L1'][1]:.4f}, {t['x_L1'][2]:.4f}]")
            print(f"  L2: [{t['x_L2'][0]:.4f}, {t['x_L2'][1]:.4f}, {t['x_L2'][2]:.4f}]")
            print(f"  β = {t['beta']:.4f}")
    else:
        print(f"❌ Erro: {result['error']}")
    
    print()
    print("=" * 80)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 80)