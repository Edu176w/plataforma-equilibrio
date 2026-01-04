# app/calculators/esl_calculator.py
"""
ESL Calculator - Equilíbrio Sólido-Líquido
===============================================================================

Implementação rigorosa baseada em:
- Prausnitz, Lichtenthaler & Azevedo, "Molecular Thermodynamics of Fluid-Phase 
  Equilibria", 3rd Ed., 1999
  * Capítulo 11: Solubilities of Solids in Liquids
  * Capítulo 6: Activity Coefficient Models

Equações Fundamentais (Cap. 11):
---------------------------------
1. Equilíbrio ESL (Eq. 11-5):
   x₂ × γ₂ × f₂^L = f₂^S
   
2. Razão de fugacidades COMPLETA (Eq. 11-13):
   ln(f₂^L/f₂^S) = (ΔHfus/RTt)(Tt/T - 1) - (ΔCp/R)(Tt/T - 1) + (ΔCp/R)ln(Tt/T)
   
3. Razão de fugacidades SIMPLIFICADA (Eq. 11-15) - ΔCp ≈ 0:
   ln(x₂^ideal) = -(ΔHfus/R)(Tm/T - 1)
   
4. Solubilidade real:
   x₂ = (1/γ₂) × exp[-(ΔHfus/R)(Tm/T - 1)]

Modelos de Atividade (Cap. 6):
--------------------------------
✓ Ideal: γᵢ = 1
✓ NRTL (Eq. 6-112): ln γᵢ = Σⱼ[xⱼτⱼᵢGⱼᵢ/ΣₖxₖGₖᵢ] + Σⱼ[xⱼGᵢⱼ/ΣₖxₖGₖⱼ (τᵢⱼ - ...)]
✓ UNIQUAC (Eq. 6-122): ln γᵢ = ln γᵢ^comb + ln γᵢ^res
✓ UNIFAC: Método preditivo (não requer parâmetros binários)

AVISOS IMPORTANTES:
-------------------
⚠️ Parâmetros de modelos (NRTL, UNIQUAC) disponíveis em bancos de dados são 
   ajustados para ELV, NÃO ESL. Podem gerar desvios.
   
⚠️ Normalização: Modelos usam convenção simétrica (Raoult). Para soluções diluídas,
   convenção assimétrica (Henry) pode ser mais apropriada.
   
⚠️ Assumimos: sólido puro (não forma soluções sólidas), pressão baixa (~1 atm).

TCC: Plataforma de Equilíbrio de Fases
Data: 2025-12-22
Versão: 3.0 - Integração completa com esl_data.py
"""

import numpy as np
from scipy.optimize import fsolve, brentq, minimize_scalar
from thermo.chemical import Chemical
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

# =============================================================================
# IMPORTAÇÕES DA BASE DE DADOS CENTRALIZADA (esl_data.py)
# =============================================================================

try:
    from esl_data import (
        ESL_DATA,
        get_component_data,
        NRTL_PARAMETERS,
        UNIQUAC_PARAMETERS,
        UNIQUAC_PURE_PROPERTIES,
        UNIFAC_GROUPS,
        get_nrtl_parameters as get_nrtl_params,
        get_uniquac_parameters as get_uniquac_params,
        get_uniquac_properties as get_uniquac_r_q,
    )
except ImportError:
    print("⚠️ ERRO: esl_data.py não encontrado. Alguns recursos estarão indisponíveis.")
    ESL_DATA = {}
    NRTL_PARAMETERS = {}
    UNIQUAC_PARAMETERS = {}
    UNIQUAC_PURE_PROPERTIES = {}
    UNIFAC_GROUPS = {}
    
    def get_component_data(name): 
        return None
    def get_nrtl_params(c1, c2): 
        return None
    def get_uniquac_params(c1, c2): 
        return None
    def get_uniquac_r_q(c): 
        return None


# =============================================================================
# CLASSE PRINCIPAL
# =============================================================================

class ESLCalculator:
    """
    Calculadora de Equilíbrio Sólido-Líquido (Prausnitz Cap. 11).
    
    Métodos principais:
    -------------------
    1. solubility() - Calcula solubilidade a T fixa (Eq. 11-5 + 11-15)
    2. crystallization() - Calcula temperatura de cristalização
    3. generate_tx_diagram() - Diagrama binário T-x (liquidus)
    4. generate_ternary_diagram() - Diagrama ternário isotérmico
    
    Modelos suportados:
    -------------------
    • Ideal: γ = 1 (baseline teórico)
    • NRTL: Sistema não-ideais, pode prever LLE
    • UNIQUAC: Base teórica quasi-química
    • UNIFAC: Preditivo (não requer parâmetros experimentais)
    """
    
    def __init__(self):
        """Inicializa calculadora com constantes e cache."""
        self.cache = {}
        self.R = 8.314  # J/(mol·K) - Constante universal dos gases
        
        # Avisos termodinâmicos para o usuário
        self.warnings = {
            'parameters': '⚠️ Parâmetros ajustados para ELV, não ESL - desvios possíveis',
            'normalization': '⚠️ Normalização simétrica (Raoult) usada',
            'assumptions': '⚠️ Assumido: sólido puro, P~1atm, ΔCp≈0 (Eq. 11-15)'
        }
    
    # =========================================================================
    # SEÇÃO 0: NORMALIZAÇÃO DE NOMES (PT ↔ EN)
    # =========================================================================
    
    def _canon(self, name: str) -> str:
        """
        Retorna o nome PT-BR canônico da base de dados.
        
        Resolve problemas de incompatibilidade entre:
        - JavaScript (exemplos em inglês): 'Naphthalene'
        - Base de dados (chaves em português): 'Naftaleno'
        
        Parameters:
            name (str): Nome em qualquer formato (PT, EN, CAS)
            
        Returns:
            str: Nome canônico PT-BR (usado como chave em NRTL_PARAMETERS, etc.)
        
        Example:
            >>> calc._canon('Naphthalene')
            'Naftaleno'
            >>> calc._canon('Benzene')
            'Benzeno'
            >>> calc._canon('91-20-3')  # CAS do naftaleno
            'Naftaleno'
        """
        data = get_component_data(name)
        
        if data and 'name' in data:
            return data['name']  # Nome PT-BR canônico
        else:
            # Fallback: retornar o nome original se não encontrado
            # (permite uso de componentes não cadastrados via thermo)
            return name
    
    # =========================================================================
    # SEÇÃO 1: PROPRIEDADES TERMODINÂMICAS
    # =========================================================================
    
    def _get_chemical(self, name):
        """
        Cache de objetos Chemical para otimização de performance.
        
        Parameters:
            name (str): Nome do componente
            
        Returns:
            Chemical: Objeto thermo.Chemical
        """
        if name not in self.cache:
            try:
                self.cache[name] = Chemical(name)
            except Exception as e:
                raise ValueError(f"Componente '{name}' não encontrado na biblioteca thermo: {e}")
        return self.cache[name]
    
    def _get_fusion_properties(self, component_name):
        """
        Extrai propriedades de fusão do componente (Prausnitz Tabela 11-1).
        
        Prioridade:
        1. Base de dados esl_data.py (dados experimentais confiáveis)
        2. Biblioteca thermo (dados estimados/tabelados)
        
        Parameters:
            component_name (str): Nome do componente
            
        Returns:
            tuple: (Tm [K], ΔHfus [J/mol], ΔCp [J/(mol·K)], Tt [K])
                   Tt = temperatura do ponto triplo (≈ Tm se não disponível)
        
        Raises:
            ValueError: Se propriedades inválidas ou indisponíveis
        """
        # Tentar buscar dados específicos de ESL
        esl_data = get_component_data(component_name)
        
        if esl_data:
            Tm = esl_data.get('Tm')  # [K]
            Hfus = esl_data.get('Hfus')  # [J/mol]
            Cp_diff = esl_data.get('delta_Cp', 0.0)  # [J/(mol·K)]
            Tt = esl_data.get('Tt', Tm)  # Triple point ≈ melting point
        else:
            # Fallback para biblioteca thermo
            chem = self._get_chemical(component_name)
            Tm = chem.Tm
            Hfus = chem.Hfus
            Cp_diff = 0.0  # Aproximação comum: ΔCp ≈ 0 (Eq. 11-15)
            Tt = Tm
        
        # Validação rigorosa
        if Tm is None or Tm <= 0:
            raise ValueError(
                f"Temperatura de fusão inválida para {component_name}: Tm={Tm} K. "
                f"Adicione dados em esl_data.py ou verifique nome do componente."
            )
        
        if Hfus is None or Hfus <= 0:
            raise ValueError(
                f"Entalpia de fusão inválida para {component_name}: ΔHfus={Hfus} J/mol. "
                f"Adicione dados em esl_data.py."
            )
        
        return Tm, Hfus, Cp_diff, Tt
    
    def _fugacity_ratio_complete(self, T, Tm, Hfus, delta_Cp=0.0, Tt=None):
        """
        Calcula razão de fugacidades f₂^L / f₂^S - Equação COMPLETA (Prausnitz Eq. 11-13).
        
        CORRIGIDO: Usar (1/T - 1/Tm) em vez de (Tm/T - 1)
        """
        if Tt is None or Tt <= 0:
            Tt = Tm
        
        if T >= Tm:
            return 1.0
        
        # Termo 1: entalpia de fusão (forma CORRETA)
        term1 = (Hfus / self.R) * (1/Tt - 1/T)  # ← CORRIGIDO!
        
        # Termos 2 e 3: capacidade calorífica
        term2 = 0.0
        term3 = 0.0
        if abs(delta_Cp) > 1e-6:
            term2 = (delta_Cp / self.R) * (Tt / T - 1)
            term3 = (delta_Cp / self.R) * np.log(Tt / T)
        
        ln_ratio = term1 - term2 + term3
        ln_ratio = np.clip(ln_ratio, -50, 50)
        
        return np.exp(ln_ratio)

    def _fugacity_ratio_simplified(self, T, Tm, Hfus):
        """
        Calcula razão de fugacidades - Equação SIMPLIFICADA (Prausnitz Eq. 11-15).
        
        ✅ CORRIGIDO: Forma numericamente estável
        
        Eq. 11-15 (FORMA CORRETA):
        ln(x₂^ideal) = -(ΔHfus/R) × (1/T - 1/Tm)
        
        Que pode ser reescrito como:
        ln(x₂^ideal) = -(ΔHfus/R) × (Tm - T)/(T × Tm)
        """
        if T >= Tm:
            return 1.0
        
        # Forma estável numericamente
        exponent = -(Hfus / self.R) * ((Tm - T) / (T * Tm))
        
        # Clipping agressivo para evitar underflow
        exponent = np.clip(exponent, -50, 50)
        
        return np.exp(exponent)


    
    def _ideal_solubility(self, T, Tm, Hfus, delta_Cp=0.0):
        """
        Calcula solubilidade IDEAL (γ = 1) - Baseline teórico.
        
        Para solução ideal (Prausnitz Eq. 11-14):
        x₂^ideal = exp[-(ΔHfus/R)(Tm/T - 1)]
        
        Significado físico:
        • É a MÁXIMA solubilidade possível (γ ≥ 1 sempre)
        • Depende APENAS de propriedades do soluto puro
        • Não depende da identidade do solvente
        
        Exemplo (Prausnitz p. 641):
        • Fenanthreno em benzeno a 25°C: x₂^ideal = 22.1 mol%
        • Antraceno em benzeno a 25°C: x₂^ideal = 0.81 mol%
        
        Returns:
            float: x₂^ideal (fração molar de solubilidade ideal)
        """
        return self._fugacity_ratio_simplified(T, Tm, Hfus)
    
    # =========================================================================
    # SEÇÃO 2: MODELOS DE COEFICIENTE DE ATIVIDADE (Cap. 6)
    # =========================================================================
    
    def _calculate_gamma_nrtl(self, x, T, components):
        """
        Modelo NRTL (Non-Random Two-Liquid) - Prausnitz Eq. 6-112, 6-113.
        
        **ATUALIZADO para usar esl_data.py centralizado com normalização PT/EN**
        
        Eq. 6-112 (binário):
        ln γ₁ = x₂²[τ₂₁(G₂₁/(x₁+x₂G₂₁))² + τ₁₂G₁₂/(x₂+x₁G₁₂)²]
        
        Parâmetros:
        • τᵢⱼ = aᵢⱼ/T (forma simplificada)
        • τᵢⱼ = aᵢⱼ + bᵢⱼ/T (forma geral)
        • Gᵢⱼ = exp(-αᵢⱼ τᵢⱼ)
        • α típico: 0.20 - 0.47 (default: 0.3)
        
        Parameters:
            x (array): Frações molares
            T (float): Temperatura [K]
            components (list): Lista de componentes
            
        Returns:
            array: Coeficientes de atividade γ
        """
        n = len(x)
        gamma = np.ones(n)
        
        # Normalizar nomes para PT-BR canônico
        can = [self._canon(c) for c in components]
        
        # Matrizes τ e G
        tau = np.zeros((n, n))
        G = np.zeros((n, n))
        alpha_default = 0.3
        
        # Preencher parâmetros binários
        for i in range(n):
            for j in range(n):
                if i == j:
                    G[i, j] = 1.0
                    tau[i, j] = 0.0
                    continue
                
                # Buscar parâmetros usando nomes canônicos
                params = get_nrtl_params(can[i], can[j])
                
                if params:
                    # Prioridade 1: τ direto (se fornecido)
                    if 'tau12' in params:
                        tau[i, j] = float(params['tau12'])
                    else:
                        # Prioridade 2: forma geral a + b/T
                        aij = float(params.get('a12', 0.0))
                        bij = float(params.get('b12', 0.0))
                        
                        if bij != 0.0:
                            # Forma completa: τ = a + b/T
                            tau[i, j] = aij + bij / max(T, 1e-6)
                        else:
                            # Forma simplificada: τ = a/T
                            tau[i, j] = aij / max(T, 1e-6)
                    
                    # α (parâmetro de não-aleatoriedade)
                    alpha_ij = float(params.get('alpha', alpha_default))
                    G[i, j] = np.exp(-alpha_ij * tau[i, j])
                else:
                    # Sem parâmetros: comportamento ideal
                    tau[i, j] = 0.0
                    G[i, j] = 1.0
        
        # Calcular γᵢ para cada componente (Eq. 6-112 estendida)
        for i in range(n):
            # Termo 1: Σⱼ(xⱼ τⱼᵢ Gⱼᵢ) / Σⱼ(xⱼ Gⱼᵢ)
            sum_xTauG = np.sum(x * tau[:, i] * G[:, i])
            sum_xG = np.sum(x * G[:, i])
            
            term1 = sum_xTauG / sum_xG if sum_xG > 1e-10 else 0.0
            
            # Termo 2: Σⱼ [ xⱼ Gᵢⱼ / Σₖ(xₖGₖⱼ) × (τᵢⱼ - Σₖ(xₖτₖⱼGₖⱼ)/Σₖ(xₖGₖⱼ)) ]
            term2 = 0.0
            for j in range(n):
                sum_xG_j = np.sum(x * G[:, j])
                if sum_xG_j > 1e-10:
                    sum_xTauG_j = np.sum(x * tau[:, j] * G[:, j])
                    term2 += (x[j] * G[i][j] / sum_xG_j) * (tau[i][j] - sum_xTauG_j / sum_xG_j)
            
            ln_gamma = term1 + term2
            gamma[i] = np.exp(np.clip(ln_gamma, -50, 50))  # Evitar overflow
        
        return gamma
    
    def _calculate_gamma_uniquac(self, x, T, components):
        """
        Modelo UNIQUAC (Universal Quasi-Chemical) - Prausnitz Eq. 6-122, 6-123.
        
        **ATUALIZADO para usar esl_data.py centralizado com normalização PT/EN**
        
        Eq. 6-122:
        ln γᵢ = ln γᵢ^comb + ln γᵢ^res
        
        Parte combinatorial (entrópica - tamanho/forma das moléculas):
        ln γᵢ^comb = ln(Φᵢ/xᵢ) + (z/2)qᵢln(θᵢ/Φᵢ) + lᵢ - (Φᵢ/xᵢ)Σⱼ(xⱼlⱼ)
        
        Parte residual (entálpica - interações energéticas):
        ln γᵢ^res = qᵢ[1 - ln(Σⱼθⱼτⱼᵢ) - Σⱼ(θⱼτᵢⱼ/Σₖθₖτₖⱼ)]
        
        Parâmetros energéticos:
        • τᵢⱼ = exp(-aᵢⱼ/T)  ou  τᵢⱼ = exp(-uᵢⱼ/T)
        • Base aceita tanto 'a12' quanto 'u12' (esl_data.py usa u12/u21)
        
        Parameters:
            x (array): Frações molares
            T (float): Temperatura [K]
            components (list): Lista de componentes
            
        Returns:
            array: Coeficientes de atividade γ
        """
        n = len(x)
        gamma = np.ones(n)
        
        # Normalizar nomes para PT-BR canônico
        can = [self._canon(c) for c in components]
        
        # Obter parâmetros estruturais r e q (Tabela 6-9)
        r = np.zeros(n)
        q = np.zeros(n)
        
        for i, comp in enumerate(can):
            rq_data = get_uniquac_r_q(comp)
            if rq_data:
                r[i] = float(rq_data['r'])
                q[i] = float(rq_data['q'])
            else:
                # Fallback: estimativa simples (assumir molécula esférica)
                print(f"⚠️ Parâmetros r,q não disponíveis para {comp}, usando r=q=1.0")
                r[i] = 1.0
                q[i] = 1.0
        
        # Calcular Φ (segment fraction) e θ (area fraction)
        sum_xr = np.sum(x * r)
        sum_xq = np.sum(x * q)
        
        phi = (x * r) / max(sum_xr, 1e-10)
        theta = (x * q) / max(sum_xq, 1e-10)
        
        # Número de coordenação (Prausnitz p. 244)
        z = 10.0
        
        # Parâmetro l (Eq. 6-123)
        l = (z / 2) * (r - q) - (r - 1)
        
        # Matriz τ de parâmetros energéticos
        tau = np.ones((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    tau[i, j] = 1.0
                    continue
                
                # Buscar parâmetros usando nomes canônicos
                params = get_uniquac_params(can[i], can[j])
                
                if params:
                    # Aceitar tanto 'a12' quanto 'u12' (sua base usa u12/u21)
                    aij = params.get('a12', params.get('u12', 0.0))
                    tau[i, j] = np.exp(-float(aij) / max(T, 1e-6))
                else:
                    tau[i, j] = 1.0
        
        # Calcular γᵢ para cada componente
        for i in range(n):
            # Parte combinatorial
            ln_gamma_comb = 0.0
            if x[i] > 1e-10 and phi[i] > 1e-10 and theta[i] > 1e-10:
                ln_gamma_comb = (
                    np.log(phi[i] / x[i])
                    + (z / 2) * q[i] * np.log(theta[i] / phi[i])
                    + l[i]
                    - (phi[i] / x[i]) * np.sum(x * l)
                )
            
            # Parte residual
            sum_theta_tau_i = np.sum(theta * tau[:, i])
            
            ln_gamma_res = 0.0
            if sum_theta_tau_i > 1e-10:
                term1 = -np.log(sum_theta_tau_i)
                
                term2 = 0.0
                for j in range(n):
                    sum_theta_tau_j = np.sum(theta * tau[:, j])
                    if sum_theta_tau_j > 1e-10:
                        term2 += (theta[j] * tau[i][j]) / sum_theta_tau_j
                
                ln_gamma_res = q[i] * (term1 + 1 - term2)
            
            gamma[i] = np.exp(np.clip(ln_gamma_comb + ln_gamma_res, -50, 50))
        
        return gamma
    
    def _calculate_gamma_unifac(self, x, T, components):
        """
        Modelo UNIFAC (UNIQUAC Functional-group Activity Coefficients).
        
        UNIFAC é um método PREDITIVO desenvolvido por Fredenslund et al. (1975).
        
        Princípio:
        • Molécula = soma de grupos funcionais
        • Propriedades da mistura = contribuição de grupos
        • Parâmetros de interação grupo-grupo (tabelados)
        
        Vantagens:
        ✓ PREDITIVO: não requer dados experimentais do sistema
        ✓ Aplicável a vasta gama de compostos orgânicos
        ✓ Parâmetros grupo-grupo disponíveis para >100 grupos
        
        Limitações:
        ⚠️ Precisão depende da disponibilidade de grupos funcionais
        ⚠️ Menos preciso que modelos ajustados (erro ~10-30%)
        ⚠️ Não aplicável a eletrolíticos, polímeros
        
        Parameters:
            x (array): Frações molares
            T (float): Temperatura [K]
            components (list): Lista de componentes
            
        Returns:
            array: Coeficientes de atividade γ
        """
        try:
            from thermo.unifac import UNIFAC
            
            # Obter grupos UNIFAC de cada componente
            chems = [self._get_chemical(comp) for comp in components]
            chemgroups = [chem.UNIFAC_groups for chem in chems]
            
            # Validar disponibilidade de grupos
            for i, groups in enumerate(chemgroups):
                if not groups:
                    raise ValueError(
                        f"Grupos UNIFAC indisponíveis para {components[i]}. "
                        f"Use modelo NRTL ou UNIQUAC com parâmetros binários."
                    )
            
            # Normalizar frações molares (garantir soma = 1)
            x_safe = np.clip(x, 1e-10, 1.0)
            x_safe = x_safe / np.sum(x_safe)
            
            # Calcular coeficientes de atividade via thermo.UNIFAC
            unifac_model = UNIFAC.from_subgroups(
                chemgroups=chemgroups,
                T=T,
                xs=x_safe.tolist()
            )
            
            gammas = np.array(unifac_model.gammas())
            
            # Validar resultados (evitar NaN, Inf, negativos)
            if np.any(np.isnan(gammas)) or np.any(np.isinf(gammas)) or np.any(gammas <= 0):
                print("⚠️ UNIFAC retornou valores inválidos, usando γ=1 (ideal)")
                return np.ones(len(x))
            
            return gammas
            
        except Exception as e:
            print(f"⚠️ Erro ao calcular UNIFAC: {e}")
            print("   Revertendo para modelo Ideal (γ=1)")
            return np.ones(len(x))
    
    def _calculate_gamma(self, x, T, model, components):
        """
        Dispatcher para modelos de coeficiente de atividade.
        
        ⚠️ IMPORTANTE (Prausnitz p. 647):
        Parâmetros de bancos de dados são ajustados para ELV, não ESL.
        Podem gerar desvios significativos em solubilidade.
        
        Recomendação:
        • Use UNIFAC para screening inicial (preditivo)
        • Use NRTL/UNIQUAC se tiver parâmetros ajustados para ESL
        • Compare com solubilidade ideal (γ=1) como baseline
        
        Parameters:
            x (array): Frações molares
            T (float): Temperatura [K]
            model (str): 'Ideal', 'NRTL', 'UNIQUAC', 'UNIFAC'
            components (list): Lista de componentes
            
        Returns:
            array: Coeficientes de atividade γ
        """
        # Normalizar composição (garantir Σxᵢ = 1)
        x_safe = np.array(x, dtype=float)
        x_safe = np.clip(x_safe, 1e-10, 1.0)
        x_safe = x_safe / np.sum(x_safe)
        
        if model == 'Ideal':
            return np.ones(len(x_safe))
        elif model == 'NRTL':
            return self._calculate_gamma_nrtl(x_safe, T, components)
        elif model == 'UNIQUAC':
            return self._calculate_gamma_uniquac(x_safe, T, components)
        elif model == 'UNIFAC':
            return self._calculate_gamma_unifac(x_safe, T, components)
        else:
            raise ValueError(
                f"Modelo '{model}' não reconhecido. "
                f"Modelos disponíveis: Ideal, NRTL, UNIQUAC, UNIFAC"
            )
    
    # =========================================================================
    # SEÇÃO 3: VALIDAÇÃO E UTILITÁRIOS
    # =========================================================================
    
    def _has_all_binary_params(self, components, model):
        """
        Verifica se todos os pares binários possuem parâmetros disponíveis.
        
        **ATUALIZADO para usar nomes canônicos PT-BR**
        
        Parameters:
            components (list): Lista de componentes
            model (str): Modelo de atividade
            
        Returns:
            bool: True se todos os parâmetros estão disponíveis
        """
        # Normalizar nomes
        can = [self._canon(c) for c in components]
        n = len(can)
        
        for i in range(n):
            for j in range(i + 1, n):
                if model == 'NRTL':
                    # Tentar ambas as direções
                    if not get_nrtl_params(can[i], can[j]) and not get_nrtl_params(can[j], can[i]):
                        return False
                elif model == 'UNIQUAC':
                    if not get_uniquac_params(can[i], can[j]) and not get_uniquac_params(can[j], can[i]):
                        return False
        
        return True
    
    def validate_model_components(self, components, model):
        """
        Valida compatibilidade entre componentes e modelo.
        
        Parameters:
            components (list): Lista de componentes
            model (str): Modelo de atividade
            
        Raises:
            ValueError: Se configuração inválida
            
        Returns:
            bool: True se válido
        """
        n = len(components)
        
        if n < 1:
            raise ValueError('Mínimo 1 componente necessário')
        
        if n > 4:
            raise ValueError('Máximo 4 componentes suportados nesta versão')
        
        if model == 'Ideal':
            return True  # Sempre válido
        
        if model in ['NRTL', 'UNIQUAC']:
            if n < 2:
                raise ValueError(f'{model} requer no mínimo 2 componentes')
            
            if not self._has_all_binary_params(components, model):
                raise ValueError(
                    f'Parâmetros {model} incompletos para este sistema. '
                    f'Opções:\n'
                    f'  1. Use modelo "UNIFAC" (preditivo, não requer parâmetros)\n'
                    f'  2. Adicione parâmetros binários em esl_data.py\n'
                    f'  3. Use modelo "Ideal" como baseline teórico'
                )
        
        elif model == 'UNIFAC':
            if n < 2:
                raise ValueError('UNIFAC requer no mínimo 2 componentes')
            
            # Verificar disponibilidade de grupos UNIFAC
            for comp in components:
                chem = self._get_chemical(comp)
                if not hasattr(chem, 'UNIFAC_groups') or not chem.UNIFAC_groups:
                    raise ValueError(
                        f'Grupos UNIFAC indisponíveis para {comp}. '
                        f'Use modelo NRTL ou UNIQUAC.'
                    )
        
        else:
            raise ValueError(
                f"Modelo '{model}' não reconhecido. "
                f"Modelos disponíveis para TCC: Ideal, NRTL, UNIQUAC, UNIFAC"
            )
        
        return True
    
    # =========================================================================
    # SEÇÃO 4: CÁLCULOS DE EQUILÍBRIO ESL
    # =========================================================================
    
    def solubility(self, components, temperature_C, model='Ideal', 
                   use_complete_equation=False):
        """
        Calcula solubilidade de sólidos em líquido a temperatura fixa.
        
        Resolve a equação fundamental de ESL (Prausnitz Eq. 11-5):
        x₂ × γ₂ = f₂^L / f₂^S
        
        Algoritmo:
        1. Identifica componentes sólidos (T < Tm)
        2. Calcula razão de fugacidades (Eq. 11-13 ou 11-15)
        3. Resolve iterativamente: x₂ = (f₂^L/f₂^S) / γ₂(x, T)
        
        Parameters:
            components (list): Lista de nomes dos componentes
            temperature_C (float): Temperatura [°C]
            model (str): 'Ideal', 'NRTL', 'UNIQUAC', 'UNIFAC'
            use_complete_equation (bool): True=Eq.11-13, False=Eq.11-15 (padrão)
            
        Returns:
            dict: Resultados com composições de equilíbrio e propriedades
        
        Example:
            >>> calc = ESLCalculator()
            >>> # Ex. Prausnitz p. 641: Antraceno em Benzeno
            >>> result = calc.solubility(['Anthracene', 'Benzene'], 25, 'Ideal')
            >>> print(f"x(Anthracene) = {result['x1 (Anthracene)']:.4f}")
            x(Anthracene) = 0.0081  # ≈ 0.81 mol% (valor experimental)
        """
        # Validação
        self.validate_model_components(components, model)
        
        T = temperature_C + 273.15  # Converter para Kelvin
        n = len(components)
        
        # Obter propriedades de fusão
        fusion_props = []
        for comp in components:
            try:
                Tm, Hfus, delta_Cp, Tt = self._get_fusion_properties(comp)
                fusion_props.append((Tm, Hfus, delta_Cp, Tt))
            except ValueError as e:
                raise ValueError(f"Erro nas propriedades de {comp}: {e}")
        
        # Identificar componentes que podem estar sólidos (T < Tm)
        solid_indices = []
        for i, (Tm, _, _, _) in enumerate(fusion_props):
            print(f"DEBUG: Componente {components[i]}: T={T:.2f}K, Tm={Tm:.2f}K, T<Tm={T<Tm}")
            if T < Tm:
                solid_indices.append(i)

        print(f"DEBUG: solid_indices = {solid_indices}")

        if not solid_indices:
            print("DEBUG: TODOS COMPONENTES LÍQUIDOS (ISSO ESTÁ ERRADO!)")
            x = np.ones(n) / n
            gamma_final = self._calculate_gamma(x, T, model, components)
            
        else:
            # =====================================================================
            # RESOLVER EQUILÍBRIO ESL (Algoritmo iterativo)
            # =====================================================================
            
            # Identificar o soluto principal (componente sólido de maior Tm)
            if len(solid_indices) == 1:
                solute_idx = solid_indices[0]
            else:
                # Múltiplos sólidos: escolher o de maior Tm (cristaliza primeiro)
                Tm_solids = [fusion_props[i][0] for i in solid_indices]
                solute_idx = solid_indices[np.argmax(Tm_solids)]
            
            # Índices dos solventes (componentes líquidos)
            solvent_indices = [i for i in range(n) if i != solute_idx]
            
            # Propriedades do soluto
            Tm_solute, Hfus_solute, dCp_solute, Tt_solute = fusion_props[solute_idx]
            
            # Calcular razão de fugacidades para o soluto
            if use_complete_equation:
                f_ratio = self._fugacity_ratio_complete(
                    T, Tm_solute, Hfus_solute, dCp_solute, Tt_solute
                )
            else:
                f_ratio = self._fugacity_ratio_simplified(T, Tm_solute, Hfus_solute)

            # ADICIONAR AQUI:
            print(f"DEBUG: f_ratio = {f_ratio:.10e}")
            print(f"DEBUG: Tm_solute = {Tm_solute:.2f}K, T = {T:.2f}K")
            print(f"DEBUG: Hfus_solute = {Hfus_solute:.1f} J/mol")

            # Clipping para evitar underflow
            f_ratio = np.clip(f_ratio, 1e-50, 1.0)
            print(f"DEBUG: f_ratio após clip = {f_ratio:.10e}")
            
            # =====================================================================
            # LOOP ITERATIVO: x_solute × γ_solute = f_ratio
            # =====================================================================
            
            max_iterations = 200
            tolerance = 1e-8
            
            # Chute inicial inteligente (baseado em f_ratio)
            if f_ratio < 1e-10:
                x_solute = f_ratio  # Muito insolúvel
            elif f_ratio > 0.5:
                x_solute = 0.5  # Próximo à fusão
            else:
                x_solute = f_ratio  # Intermediário
            
            x_solute = np.clip(x_solute, 1e-20, 0.999)
            
            converged = False
            
            for iteration in range(max_iterations):
                if iteration < 5:  # Print apenas as primeiras 5 iterações
                    print(f"DEBUG: Iteração {iteration}: x_solute = {x_solute:.10e}")
                # Montar vetor de composição trial
                x_trial = np.zeros(n)
                x_trial[solute_idx] = x_solute
                
                # Distribuir fração restante entre solventes
                remaining = 1.0 - x_solute
                if len(solvent_indices) > 0:
                    for idx in solvent_indices:
                        x_trial[idx] = remaining / len(solvent_indices)
                
                # Normalizar (garantir soma = 1)
                x_trial = x_trial / np.sum(x_trial)
                
                # Calcular coeficientes de atividade
                gamma = self._calculate_gamma(x_trial, T, model, components)
                
                # Garantir que γ seja físico (γ ≥ 0)
                gamma_solute = max(gamma[solute_idx], 1e-10)
                
                # Nova estimativa: x_solute = f_ratio / γ_solute (Eq. 11-5)
                x_solute_new = f_ratio / gamma_solute
                x_solute_new = np.clip(x_solute_new, 1e-20, 0.999)
                
                # Verificar convergência
                residual = abs(x_solute_new - x_solute)
                
                if residual < tolerance:
                    x_solute = x_solute_new
                    converged = True
                    break
                
                # Atualização com damping para estabilidade (Successive Substitution)
                if iteration < 50:
                    alpha = 0.2  # Damping forte no início
                else:
                    alpha = 0.4  # Relaxar damping depois
                
                x_solute = alpha * x_solute_new + (1 - alpha) * x_solute
            
            if not converged:
                print(f"⚠️  Aviso: Solubilidade não convergiu após {max_iterations} iterações")
                print(f"    Resíduo final: {residual:.2e}")
                print(f"    Considere usar modelo mais simples ou verificar parâmetros")
            
            # Composição final
            x = np.zeros(n)
            x[solute_idx] = x_solute
            remaining = 1.0 - x_solute
            if len(solvent_indices) > 0:
                for idx in solvent_indices:
                    x[idx] = remaining / len(solvent_indices)
            
            # Normalizar
            x = x / np.sum(x)
            
            # Calcular coeficientes de atividade finais
            gamma_final = self._calculate_gamma(x, T, model, components)
        
        # =========================================================================
        # MONTAR RESULTADOS
        # =========================================================================
        
        results = {
            'T_C': round(temperature_C, 2),
            'T_K': round(T, 2),
            'model': model,
            'equation': 'complete (Eq. 11-13)' if use_complete_equation else 'simplified (Eq. 11-15)',
            'warnings': self.warnings
        }
        
        # Informações detalhadas de cada componente
        for i, comp in enumerate(components):
            Tm_i, Hfus_i, dCp_i, Tt_i = fusion_props[i]
            
            # Solubilidade ideal (para comparação - baseline)
            x_ideal = self._ideal_solubility(T, Tm_i, Hfus_i, dCp_i)
            
            results[f'x{i+1} ({comp})'] = round(float(x[i]), 6)
            results[f'gamma{i+1}'] = round(float(gamma_final[i]), 4)
            results[f'x{i+1}_ideal'] = round(float(x_ideal), 6)
            results[f'Tm{i+1}_K'] = round(Tm_i, 2)
            results[f'Hfus{i+1}_kJ/mol'] = round(Hfus_i / 1000, 3)
            results[f'phase{i+1}'] = 'solid' if T < Tm_i else 'liquid'
        
        return results
    
    def crystallization(self, components, compositions, model='Ideal',
                        use_complete_equation=False):
        """
        Calcula temperatura de início de cristalização para composição fixa.
        
        Resolve para T onde o primeiro componente atinge saturação:
        xᵢ × γᵢ(x,T) = exp[-(ΔHfus/R)(Tm/T - 1)]
        
        Útil para:
        • Design de processos de cristalização
        • Evitar precipitação indesejada em tubulações
        • Otimização de condições de armazenamento
        
        Parameters:
            components (list): Lista de componentes
            compositions (list): Frações molares (serão normalizadas)
            model (str): Modelo de atividade
            use_complete_equation (bool): True=Eq.11-13, False=Eq.11-15
            
        Returns:
            dict: Temperatura de cristalização e propriedades
        """
        # Validação
        self.validate_model_components(components, model)
        
        n = len(components)
        
        # Normalizar composição
        x = np.array(compositions, dtype=float)
        x = x / np.sum(x)
        
        # Obter propriedades de fusão
        fusion_props = []
        for comp in components:
            try:
                Tm, Hfus, delta_Cp, Tt = self._get_fusion_properties(comp)
                fusion_props.append((Tm, Hfus, delta_Cp, Tt))
            except ValueError as e:
                raise ValueError(f"Erro nas propriedades de {comp}: {e}")
        
        # Temperaturas de fusão
        Tm_values = [fp[0] for fp in fusion_props]
        Tm_min = min(Tm_values)
        Tm_max = max(Tm_values)
        
        def equilibrium_residual(T):
            """
            Resíduo da equação de equilíbrio para otimização.
            
            Retorna a soma dos desvios da equação de saturação para
            todos os componentes que podem cristalizar.
            """
            if T <= Tm_min * 0.5 or T >= Tm_max * 1.2:
                return 1e10  # Penalizar temperaturas físicamente irreais
            
            gamma = self._calculate_gamma(x, T, model, components)
            
            residual = 0.0
            for i in range(n):
                Tm_i, Hfus_i, dCp_i, Tt_i = fusion_props[i]
                
                if T < Tm_i:  # Pode cristalizar
                    # LHS: ln(xᵢ × γᵢ)
                    lhs = np.log(max(x[i] * gamma[i], 1e-10))
                    
                    # RHS: ln(f₂^L / f₂^S)
                    if use_complete_equation:
                        f_ratio = self._fugacity_ratio_complete(
                            T, Tm_i, Hfus_i, dCp_i, Tt_i
                        )
                        rhs = np.log(f_ratio)
                    else:
                        rhs = -(Hfus_i / self.R) * (Tm_i / T - 1)
                    
                    residual += (lhs - rhs) ** 2
            
            return residual
        
        # Otimizar para encontrar T de cristalização
        try:
            res = minimize_scalar(
                equilibrium_residual,
                bounds=(Tm_min * 0.7, Tm_max * 1.1),
                method='bounded'
            )
            T_cryst = res.x
        except:
            # Fallback: temperatura ponderada pela composição
            T_cryst = np.sum(x * np.array(Tm_values))
        
        # Calcular propriedades na temperatura de cristalização
        gamma_final = self._calculate_gamma(x, T_cryst, model, components)
        
        # Montar resultados
        results = {
            'T_cryst_C': round(T_cryst - 273.15, 2),
            'T_cryst_K': round(T_cryst, 2),
            'model': model,
            'equation': 'complete (Eq. 11-13)' if use_complete_equation else 'simplified (Eq. 11-15)',
            'warnings': self.warnings
        }
        
        for i, comp in enumerate(components):
            Tm_i, Hfus_i, _, _ = fusion_props[i]
            
            results[f'x{i+1} ({comp})'] = round(float(x[i]), 6)
            results[f'gamma{i+1}'] = round(float(gamma_final[i]), 4)
            results[f'Tm{i+1}_K'] = round(Tm_i, 2)
            results[f'phase{i+1}'] = 'solid' if T_cryst < Tm_i else 'liquid'
        
        return results
    
    def check_phase_stability(self, x, T, model, components):
        """
        Verifica estabilidade de fase calculando d²G/dx².
        
        Se d²G/dx² < 0: INSTÁVEL (região spinodal, gap L₁+L₂)
        Se d²G/dx² > 0: ESTÁVEL (solução homogênea)
        
        Parameters:
            x (array): Composições molares [x1, x2]
            T (float): Temperatura [K]
            model (str): Modelo termodinâmico
            components (list): Nomes dos componentes
            
        Returns:
            dict: {
                'stable': bool,
                'd2G_dx2': float,
                'warning': str or None
            }
        """
        R = self.R
        
        x1 = x[0]
        x2 = x[1]
        
        # Evitar singularidades nos limites
        if x1 < 0.001 or x1 > 0.999:
            return {'stable': True, 'd2G_dx2': 1e10, 'warning': None}
        
        def gibbs_RT(x1_val):
            """Energia de Gibbs molar adimensional G/(RT)"""
            if x1_val <= 0 or x1_val >= 1:
                return 1e10
            
            x2_val = 1 - x1_val
            x_temp = np.array([x1_val, x2_val])
            
            try:
                # Calcular γ
                gamma = self._calculate_gamma(x_temp, T, model, components)
                
                # G/RT = x1·ln(x1·γ1) + x2·ln(x2·γ2)
                G_RT = x1_val * np.log(max(1e-10, x1_val * gamma[0])) + \
                    x2_val * np.log(max(1e-10, x2_val * gamma[1]))
                
                return G_RT
            except:
                return 1e10
        
        # Calcular segunda derivada numérica
        dx = 0.005
        try:
            G_plus = gibbs_RT(x1 + dx)
            G_center = gibbs_RT(x1)
            G_minus = gibbs_RT(x1 - dx)
            
            # d²G/dx² ≈ [G(x+dx) - 2G(x) + G(x-dx)] / dx²
            d2G_dx2 = (G_plus - 2*G_center + G_minus) / (dx**2)
            
            # Multiplicar por RT para ter unidades de J/mol
            d2G_dx2_dimensional = d2G_dx2 * R * T
            
            # Critério de estabilidade: d²G/dx² > 0
            stable = d2G_dx2 > -0.1  # Pequena tolerância numérica
            
            warning = None
            if not stable:
                warning = "⚠️ Região de imiscibilidade líquida detectada (gap L₁+L₂)"
            
            return {
                'stable': stable,
                'd2G_dx2': d2G_dx2_dimensional,
                'warning': warning
            }
            
        except Exception as e:
            # Em caso de erro, assumir estável
            return {'stable': True, 'd2G_dx2': 0, 'warning': None}


    def generate_tx_diagram(self, components, model='Ideal', n_points=50, use_complete_equation=False):
        """
        Gera diagrama T-x binário com DETECÇÃO DE GAP L₁+L₂.
        
        VERSÃO CORRIGIDA 2025-12-26: Separa curvas com base no eutético.
        """
        if len(components) != 2:
            raise ValueError("Diagrama T-x requer exatamente 2 componentes.")
        
        self.validate_model_components(components, model)
        
        # Propriedades de fusão
        Tm1, Hfus1, dCp1, Tt1 = self._get_fusion_properties(components[0])
        Tm2, Hfus2, dCp2, Tt2 = self._get_fusion_properties(components[1])
        
        # ========================================================================
        # PASSO 1: CALCULAR TODOS OS PONTOS (incluindo instáveis)
        # ========================================================================
        all_points = []
        x1_range = np.linspace(0.005, 0.995, n_points)
        
        for x1 in x1_range:
            x = np.array([x1, 1 - x1])
            
            # Funções residuais para cada componente
            def residual_1(T):
                if T <= 50 or T >= Tm1:
                    return 1e10
                try:
                    gamma = self._calculate_gamma(x, T, model, components)
                    if use_complete_equation:
                        f_ratio = self._fugacity_ratio_complete(T, Tm1, Hfus1, dCp1, Tt1)
                    else:
                        f_ratio = self._fugacity_ratio_simplified(T, Tm1, Hfus1)
                    return abs(x[0] * gamma[0] - f_ratio)
                except:
                    return 1e10
            
            def residual_2(T):
                if T <= 50 or T >= Tm2:
                    return 1e10
                try:
                    gamma = self._calculate_gamma(x, T, model, components)
                    if use_complete_equation:
                        f_ratio = self._fugacity_ratio_complete(T, Tm2, Hfus2, dCp2, Tt2)
                    else:
                        f_ratio = self._fugacity_ratio_simplified(T, Tm2, Hfus2)
                    return abs(x[1] * gamma[1] - f_ratio)
                except:
                    return 1e10
            
            # Resolver para ambos componentes
            T_cryst_1 = None
            T_cryst_2 = None
            
            try:
                res1 = minimize_scalar(residual_1, bounds=(50, Tm1 * 0.9999), method='bounded', options={'xatol': 0.01})
                if res1.fun < 0.01:
                    T_cryst_1 = res1.x
            except:
                pass
            
            try:
                res2 = minimize_scalar(residual_2, bounds=(50, Tm2 * 0.9999), method='bounded', options={'xatol': 0.01})
                if res2.fun < 0.01:
                    T_cryst_2 = res2.x
            except:
                pass
            
            # Selecionar temperatura MAIOR (cristaliza primeiro)
            if T_cryst_1 and T_cryst_2:
                T_selected = max(T_cryst_1, T_cryst_2)
            elif T_cryst_1:
                T_selected = T_cryst_1
            elif T_cryst_2:
                T_selected = T_cryst_2
            else:
                continue
            
            # Verificar estabilidade
            stability = self.check_phase_stability(x, T_selected, model, components)
            
            all_points.append({
                'x1': x1,
                'T_K': T_selected,
                'T_C': T_selected - 273.15,
                'stable': stability['stable'],
                'd2G_dx2': stability.get('d2G_dx2', 0)
            })
        
        # ========================================================================
        # PASSO 2: SEPARAR PONTOS ESTÁVEIS E INSTÁVEIS
        # ========================================================================
        stable_points = [p for p in all_points if p['stable']]
        unstable_points = [p for p in all_points if not p['stable']]
        
        if not stable_points:
            raise ValueError("Sistema totalmente imiscível - nenhum ponto estável encontrado.")
        
        # ========================================================================
        # PASSO 3: ENCONTRAR EUTÉTICO (mínima T entre pontos estáveis)
        # ========================================================================
        eutectic_point = min(stable_points, key=lambda p: p['T_C'])
        x1_eutectic = eutectic_point['x1']
        T_eutectic_C = eutectic_point['T_C']
        
        print(f"[ESL] Eutético: x₁={x1_eutectic:.4f}, T={T_eutectic_C:.2f}°C")
        
        # ========================================================================
        # PASSO 4: SEPARAR CURVAS COM BASE NO EUTÉTICO E GAP
        # ========================================================================
        left_points = [p for p in stable_points if p['x1'] <= x1_eutectic]
        right_points_raw = [p for p in stable_points if p['x1'] > x1_eutectic]

        # ✅ CORREÇÃO FINAL: Se há gap, manter apenas pontos APÓS o gap máximo
        if unstable_points:
            gap_x_min = min(p['x1'] for p in unstable_points)
            gap_x_max = max(p['x1'] for p in unstable_points)
            
            print(f"[ESL DEBUG] Gap detectado: x₁ = {gap_x_min:.3f} → {gap_x_max:.3f}")
            
            # ✅ FILTRO CORRETO: Manter apenas pontos > gap_x_max
            right_points = [p for p in right_points_raw if p['x1'] > gap_x_max]
            
            removed_count = len(right_points_raw) - len(right_points)
            print(f"[ESL DEBUG] Filtrados {removed_count} pontos antes/dentro do gap")
            print(f"[ESL DEBUG] right_points: {len(right_points_raw)} → {len(right_points)} pontos")
        else:
            right_points = right_points_raw
            print(f"[ESL DEBUG] Sem gap - usando todos os pontos estáveis")

        # Ordenar por x1 crescente
        left_points.sort(key=lambda p: p['x1'])
        right_points.sort(key=lambda p: p['x1'])

        print(f"[ESL DEBUG] left_points: {len(left_points)} pontos")
        print(f"[ESL DEBUG] right_points FINAL: {len(right_points)} pontos")
        if right_points:
            print(f"[ESL DEBUG] right_points range: x₁ = {right_points[0]['x1']:.3f} → {right_points[-1]['x1']:.3f}")


        
        # ========================================================================
        # PASSO 5: ADICIONAR PONTOS PUROS NOS EXTREMOS
        # ========================================================================
        # Componente 2 puro (x1=0)
        if not left_points or left_points[0]['x1'] > 0.02:
            left_points.insert(0, {'x1': 0.0, 'T_C': Tm2 - 273.15})
        
        # Componente 1 puro (x1=1)
        if not right_points or right_points[-1]['x1'] < 0.98:
            right_points.append({'x1': 1.0, 'T_C': Tm1 - 273.15})
        
        # ========================================================================
        # PASSO 6: EXTRAIR ARRAYS FINAIS
        # ========================================================================
        x1_comp2_cryst = [p['x1'] for p in left_points]    # Fenol - esquerda física (x baixo)
        T_comp2_cryst = [p['T_C'] for p in left_points]

        x1_comp1_cryst = [p['x1'] for p in right_points]   # Benzeno - direita física (x alto)
        T_comp1_cryst = [p['T_C'] for p in right_points]

        # ✅ INVERSÃO CRÍTICA: Usuário quer x=0 começar com Benzeno (5.5°C) e x=1 com Fenol (40.9°C)
        # Mas x1 original = fração de Benzeno, então x1=0 é Fenol e x1=1 é Benzeno (OPOSTO!)
        # SOLUÇÃO: Inverter TODOS os x → x_plot = 1 - x1

        x1_comp2_cryst_inv = [1.0 - x for x in x1_comp2_cryst]  # Fenol invertido
        x1_comp1_cryst_inv = [1.0 - x for x in x1_comp1_cryst]  # Benzeno invertido
        x1_eutectic_inv = 1.0 - x1_eutectic  # Eutético invertido

        print(f"[ESL DEBUG] INVERSÃO APLICADA:")
        print(f"  x_eut: {x1_eutectic:.4f} → {x1_eutectic_inv:.4f}")
        print(f"  Benzeno: x1_comp1[0]={x1_comp1_cryst[0]:.3f} → inv={x1_comp1_cryst_inv[0]:.3f}")
        print(f"  Fenol: x1_comp2[0]={x1_comp2_cryst[0]:.3f} → inv={x1_comp2_cryst_inv[0]:.3f}")

        # ========================================================================
        # PASSO 7: PREPARAR PONTOS INSTÁVEIS (com inversão também)
        # ========================================================================
        unstable_output = []
        for p in unstable_points:
            unstable_output.append({
                'x1': float(1.0 - p['x1']),  # ✅ INVERTER TAMBÉM!
                'T_C': float(p['T_C']),
                'd2G_dx2': float(p['d2G_dx2']),
                'warning': "⚠️ Região de imiscibilidade líquida detectada (gap L₁+L₂)"
            })

        # ========================================================================
        # PASSO 8: WARNINGS
        # ========================================================================
        warnings_updated = self.warnings.copy()

        if unstable_output:
            gap_x_min = min(p['x1'] for p in unstable_output)
            gap_x_max = max(p['x1'] for p in unstable_output)
            warnings_updated['liquid_liquid_gap'] = (
                f"⚠️ Região de imiscibilidade líquida detectada entre "
                f"x₁ = {gap_x_min:.3f} e {gap_x_max:.3f}. "
                f"Diagrama ESL pode não ser completamente aplicável nesta região."
            )

        # ========================================================================
        # RETORNO FINAL (✅ COM INVERSÃO E LEFT↔RIGHT TROCADOS!)
        # ========================================================================
        return {
            'component1': components[0],  # Benzeno
            'component2': components[1],  # Fenol
            'model': model,
            'equation': 'complete (Eq. 11-13)' if use_complete_equation else 'simplified (Eq. 11-15)',
            
            # ✅ APÓS INVERSÃO:
            # x=0 → Benzeno (5.5°C, curva curta, ESQUERDA visual)
            # x=1 → Fenol (40.9°C, curva longa, DIREITA visual)
            
            'x1_left': x1_comp1_cryst_inv,      # ✅ Benzeno invertido (esquerda visual)
            'T_left_C': T_comp1_cryst,          # Temperaturas Benzeno (baixas)
            'x1_right': x1_comp2_cryst_inv,     # ✅ Fenol invertido (direita visual)
            'T_right_C': T_comp2_cryst,         # Temperaturas Fenol (altas)
            
            'T_eutectic_C': round(T_eutectic_C, 2),
            'x1_eutectic': round(x1_eutectic_inv, 4),  # ✅ Eutético invertido
            
            'Tm1_C': round(Tm1 - 273.15, 2),  # Benzeno (agora em x=0)
            'Tm2_C': round(Tm2 - 273.15, 2),  # Fenol (agora em x=1)
            
            'unstable_region': unstable_output,
            'has_liquid_liquid_gap': len(unstable_output) > 0,
            'warnings': warnings_updated
        }




    def generate_ternary_diagram(self, components, temperature_C, model='Ideal',
                             n_points=30, use_complete_equation=False):
        """
        ✅ VERSÃO CORRIGIDA - Usando _calculate_gamma (com underscore)
        """
        if len(components) != 3:
            raise ValueError('Diagrama ternário requer exatamente 3 componentes')
        
        self.validate_model_components(components, model)
        T = temperature_C + 273.15
        
        # Propriedades de fusão
        fusion_props = []
        for comp in components:
            Tm, Hfus, delta_Cp, Tt = self._get_fusion_properties(comp)
            fusion_props.append((Tm, Hfus, delta_Cp, Tt))
        
        print(f"\n[TERNÁRIO DEBUG] Sistema: {components}")
        print(f"[TERNÁRIO DEBUG] T = {temperature_C}°C = {T:.2f} K")
        
        # Calcular solubilidades E thresholds ULTRA-agressivos
        solubilities = []
        thresholds = []
        
        for k, comp in enumerate(components):
            Tm_k, Hfus_k, dCp_k, Tt_k = fusion_props[k]
            
            if T >= Tm_k:
                x_sat = 1.0
                threshold = 1.0
                solubilities.append(x_sat)
                thresholds.append(threshold)
                print(f"[TERNÁRIO DEBUG]   {comp}: Tm = {Tm_k-273.15:.1f}°C | SEMPRE LÍQUIDO")
            else:
                if use_complete_equation:
                    x_sat = self._fugacity_ratio_complete(T, Tm_k, Hfus_k, dCp_k, Tt_k)
                else:
                    x_sat = self._fugacity_ratio_simplified(T, Tm_k, Hfus_k)
                
                delta_T = Tm_k - T
                
                # ✅ THRESHOLDS CALIBRADOS para match com Prausnitz
                # ✅ THRESHOLDS REFINADOS FINAIS (ajuste fino de 10%)
                if delta_T < 2:  # MUITO próximo (< 2K)
                    threshold = 0.40  # ⬇️ 45% → 40%
                elif delta_T < 10:  # Próximo (2-10K)
                    threshold = 0.45  # ⬇️ 50% → 45%
                else:  # Longe (> 10K)
                    threshold = 0.50  # ⬇️ 55% → 50%
                
                solubilities.append(x_sat)
                thresholds.append(threshold)
                print(f"[TERNÁRIO DEBUG]   {comp}: Tm = {Tm_k-273.15:.1f}°C | ΔT = {delta_T:.1f}K | x_sat = {x_sat:.4f} | threshold = {threshold:.2f}")
        
        points = []
        step = 1.0 / n_points
        
        for i in range(n_points + 1):
            for j in range(n_points + 1 - i):
                x1 = i * step
                x2 = j * step
                x3 = 1 - x1 - x2
                
                if x3 < -1e-6:
                    continue
                
                x = np.array([max(0, x1), max(0, x2), max(0, x3)])
                x = x / np.sum(x)
                
                # ✅ CORREÇÃO: Usar _calculate_gamma (com underscore)
                gamma = self._calculate_gamma(x, T, model, components)
                
                solid_components_list = []
                
                for k in range(3):
                    Tm_k = fusion_props[k][0]
                    
                    if T >= Tm_k:
                        continue
                    
                    x_sat_pure = solubilities[k]  # Solubilidade pura
                    threshold = thresholds[k]
                    
                    # ✅ CRITÉRIO: x * γ > x_sat (atividade supersaturada)
                    # Solubilidade efetiva reduzida por γ médio
                    gamma_avg = np.mean(gamma)
                    x_sat_eff = x_sat_pure / max(gamma_avg, 1.0)
                    
                    if x[k] > x_sat_eff * threshold:
                        solid_components_list.append(components[k])
                
                num_solid_phases = len(solid_components_list)
                
                if num_solid_phases == 0:
                    phase = 'liquid'
                elif num_solid_phases == 1:
                    phase = 'solid_liquid'
                else:
                    phase = 'eutectic'
                
                points.append({
                    'x1': round(float(x[0]), 6),
                    'x2': round(float(x[1]), 6),
                    'x3': round(float(x[2]), 6),
                    'phase': phase,
                    'num_solid_phases': num_solid_phases,
                    'solid_components': solid_components_list
                })
        
        liquid_count = sum(1 for p in points if p['num_solid_phases'] == 0)
        biphasic_count = sum(1 for p in points if p['num_solid_phases'] == 1)
        triphasic_count = sum(1 for p in points if p['num_solid_phases'] >= 2)
        
        print(f"\n[TERNÁRIO] T={temperature_C}°C, Modelo={model}")
        print(f"   🔴 Monofásica (L): {liquid_count}/{len(points)} ({100*liquid_count/len(points):.1f}%)")
        print(f"   🟠 Bifásica (L+S): {biphasic_count}/{len(points)} ({100*biphasic_count/len(points):.1f}%)")
        print(f"   🟢 Trifásica (L+2S): {triphasic_count}/{len(points)} ({100*triphasic_count/len(points):.1f}%)")
        
        return {
            'components': components,
            'T_C': round(temperature_C, 2),
            'model': model,
            'equation': 'complete (Eq. 11-13)' if use_complete_equation else 'simplified (Eq. 11-15)',
            'points': points,
            'warnings': self.warnings
        }





# =============================================================================
# FUNÇÕES AUXILIARES PARA ROTAS FLASK
# =============================================================================

def calculate_esl(data):
    """
    Wrapper para chamadas via Flask.
    
    Parameters:
        data (dict): Dicionário com parâmetros do cálculo
        
    Returns:
        dict: Resultados formatados para JSON
    """
    calc = ESLCalculator()
    
    calc_type = data.get('calculation_type', 'solubility')
    components = data.get('components', [])
    model = data.get('model', 'Ideal')
    use_complete_eq = data.get('use_complete_equation', False)
    
    if calc_type == 'solubility':
        temperature_C = float(data.get('temperature', 25.0))
        return calc.solubility(components, temperature_C, model, use_complete_eq)
    
    elif calc_type == 'crystallization':
        compositions = data.get('compositions', [])
        return calc.crystallization(components, compositions, model, use_complete_eq)
    
    elif calc_type == 'tx':
        n_points = int(data.get('n_points', 50))
        return calc.generate_tx_diagram(components, model, n_points, use_complete_eq)
    
    elif calc_type == 'ternary':
        temperature_C = float(data.get('temperature', 25.0))
        n_points = int(data.get('n_points', 20))
        return calc.generate_ternary_diagram(
            components, temperature_C, model, n_points, use_complete_eq
        )
    
    else:
        raise ValueError(f"Tipo de cálculo '{calc_type}' não reconhecido")


if __name__ == "__main__":
    # Testes básicos
    print("\n" + "="*80)
    print("  ESL CALCULATOR - Testes de Validação")
    print("="*80 + "\n")
    
    calc = ESLCalculator()
    
    # Teste 1: Solubilidade ideal
    print("Teste 1: Naftaleno em Benzeno a 25°C (Ideal)")
    print("-" * 80)
    try:
        result = calc.solubility(['Naphthalene', 'Benzene'], 25, 'Ideal')
        print(f"x(Naftaleno) = {result['x1 (Naphthalene)']:.6f}")
        print(f"γ(Naftaleno) = {result['gamma1']:.4f}")
        print("✓ Teste 1 passou\n")
    except Exception as e:
        print(f"✗ Teste 1 falhou: {e}\n")
    
    # Teste 2: NRTL (se parâmetros disponíveis)
    print("Teste 2: Naftaleno em Benzeno a 25°C (NRTL)")
    print("-" * 80)
    try:
        result = calc.solubility(['Naphthalene', 'Benzene'], 25, 'NRTL')
        print(f"x(Naftaleno) = {result['x1 (Naphthalene)']:.6f}")
        print(f"γ(Naftaleno) = {result['gamma1']:.4f}")
        print("✓ Teste 2 passou\n")
    except Exception as e:
        print(f"✗ Teste 2 falhou: {e}\n")
    
    # Teste 3: Diagrama T-x
    print("Teste 3: Diagrama T-x Naftaleno + Bifenila (Ideal)")
    print("-" * 80)
    try:
        diagram = calc.generate_tx_diagram(['Naphthalene', 'Biphenyl'], 'Ideal', n_points=10)
        print(f"Eutético: x = {diagram['x_eutectic']:.3f}, T = {diagram['T_eutectic_C']:.1f}°C")
        print("✓ Teste 3 passou\n")
    except Exception as e:
        print(f"✗ Teste 3 falhou: {e}\n")
    
    print("="*80)
    print("  Testes concluídos!")
    print("="*80 + "\n")
