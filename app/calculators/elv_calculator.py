from thermo.chemical import Chemical
from scipy.optimize import fsolve, brentq
import numpy as np
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

try:
    from nrtl_params import get_nrtl_params, NRTL_PARAMS
    from uniquac_params import get_uniquac_params, UNIQUAC_PARAMS, get_uniquac_r_q
except:
    NRTL_PARAMS = {}
    UNIQUAC_PARAMS = {}

    def get_nrtl_params(c1, c2): return None
    def get_uniquac_params(c1, c2): return None
    def get_uniquac_r_q(c): return None


class ELVCalculator:
    def __init__(self):
        self.cache = {}
        self.R = 8.314

    # ==========================
    # UTILITÁRIOS INTERNOS
    # ==========================

    def _get_chemical(self, name):
        if name not in self.cache:
            self.cache[name] = Chemical(name)
        return self.cache[name]

    def _get_vapor_pressure(self, chem, T):
        return chem.VaporPressure(T)

    def _has_all_binary_params(self, components, model):
        """Verificar se todos os pares binários têm parâmetros."""
        n = len(components)
        for i in range(n):
            for j in range(i + 1, n):
                if model == 'NRTL':
                    if not get_nrtl_params(components[i], components[j]):
                        return False
                elif model == 'UNIQUAC':
                    if not get_uniquac_params(components[i], components[j]):
                        return False
        return True

    def validate_model_components(self, components, model):
        """Validar se os componentes são compatíveis com o modelo."""
        n = len(components)

        if model == 'Ideal':
            return True

        if model in ['NRTL', 'UNIQUAC']:
            if n < 2 or n > 4:
                raise ValueError(f'{model} suporta 2 a 4 componentes')

            if not self._has_all_binary_params(components, model):
                raise ValueError(f'Parametros {model} incompletos para estes componentes')

        elif model == 'UNIFAC':
            if n < 2 or n > 4:
                raise ValueError('UNIFAC suporta 2 a 4 componentes')

            for comp in components:
                chem = self._get_chemical(comp)
                if not hasattr(chem, 'UNIFAC_groups') or not chem.UNIFAC_groups:
                    raise ValueError(f'Grupos UNIFAC nao disponiveis para {comp}')

        return True

    # ==========================
    # γ (λ) – MODELOS DE ATIVIDADE
    # ==========================

    def _calculate_gamma_nrtl(self, x, T, components):
        """NRTL para N componentes usando parâmetros binários."""
        n = len(x)
        gamma = np.ones(n)

        tau = np.zeros((n, n))
        G = np.zeros((n, n))
        alpha = 0.3

        for i in range(n):
            for j in range(n):
                if i != j:
                    params = get_nrtl_params(components[i], components[j])
                    if params:
                        tau[i][j] = params['a12'] / T
                        alpha = params['alpha']
                        G[i][j] = np.exp(-alpha * tau[i][j])
                    else:
                        G[i][j] = 1.0
                else:
                    G[i][i] = 1.0

        for i in range(n):
            sum1 = sum(x[j] * tau[j][i] * G[j][i] for j in range(n))
            sum2 = sum(x[j] * G[j][i] for j in range(n))
            term1 = sum1 / sum2 if sum2 > 1e-10 else 0.0

            term2 = 0.0
            for j in range(n):
                sum3 = sum(x[k] * tau[k][j] * G[k][j] for k in range(n))
                sum4 = sum(x[k] * G[k][j] for k in range(n))
                if sum4 > 1e-10:
                    term2 += (x[j] * G[i][j] / sum4) * (tau[i][j] - sum3 / sum4)

            gamma[i] = np.exp(term1 + term2)

        return gamma

    def _calculate_gamma_uniquac(self, x, T, components):
        """UNIQUAC para N componentes."""
        n = len(x)

        r = np.zeros(n)
        q = np.zeros(n)
        for i, comp in enumerate(components):
            rq = get_uniquac_r_q(comp)
            if not rq:
                return np.ones(n)
            r[i] = rq['r']
            q[i] = rq['q']

        sum_xr = np.sum(x * r)
        sum_xq = np.sum(x * q)

        phi = (x * r) / sum_xr if sum_xr > 1e-10 else np.zeros(n)
        theta = (x * q) / sum_xq if sum_xq > 1e-10 else np.zeros(n)

        z = 10
        l = z / 2 * (r - q) - (r - 1)

        tau = np.ones((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    params = get_uniquac_params(components[i], components[j])
                    if params:
                        tau[i][j] = np.exp(-params['a12'] / T)

        ln_gamma_comb = np.zeros(n)
        for i in range(n):
            if x[i] > 1e-10 and phi[i] > 1e-10:
                ln_gamma_comb[i] = (
                    np.log(phi[i] / x[i])
                    + z / 2 * q[i] * np.log(theta[i] / phi[i])
                    + l[i]
                )
                ln_gamma_comb[i] -= (phi[i] / x[i]) * np.sum(x * l)

        ln_gamma_res = np.zeros(n)
        for i in range(n):
            sum1 = np.sum(theta * tau[:, i])
            sum2 = 0.0
            for j in range(n):
                sum3 = np.sum(theta * tau[:, j])
                if sum3 > 1e-10:
                    sum2 += theta[j] * tau[i][j] / sum3

            if sum1 > 1e-10:
                ln_gamma_res[i] = q[i] * (1 - np.log(sum1) - sum2)

        gamma = np.exp(ln_gamma_comb + ln_gamma_res)
        return gamma

    def _calculate_gamma_unifac(self, x, T, components):
        """UNIFAC para N componentes."""
        try:
            from thermo.unifac import UNIFAC

            chems = [self._get_chemical(comp) for comp in components]
            chemgroups = [chem.UNIFAC_groups for chem in chems]

            x_safe = np.clip(x, 1e-10, 1.0)
            x_safe = x_safe / np.sum(x_safe)

            unifac_model = UNIFAC.from_subgroups(chemgroups=chemgroups, T=T, xs=x_safe)
            gammas = np.array(unifac_model.gammas())

            if np.any(np.isnan(gammas)) or np.any(np.isinf(gammas)) or np.any(gammas <= 0):
                return np.ones(len(x))

            return gammas
        except:
            return np.ones(len(x))

    def _calculate_gamma(self, x, T, model, components):
        if model == 'Ideal':
            return np.ones(len(x))
        elif model == 'NRTL':
            return self._calculate_gamma_nrtl(x, T, components)
        elif model == 'UNIQUAC':
            return self._calculate_gamma_uniquac(x, T, components)
        elif model == 'UNIFAC':
            return self._calculate_gamma_unifac(x, T, components)
        return np.ones(len(x))

    # ========================================================================
    # ==================== CÁLCULOS PONTUAIS =================================
    # ========================================================================

    def bubble_point(self, components, temperature_C, x, model='Ideal'):
        self.validate_model_components(components, model)

        T = temperature_C + 273.15
        n = len(components)
        x = np.array(x) / np.sum(x)

        chems = [self._get_chemical(comp) for comp in components]
        P_sat = np.array([self._get_vapor_pressure(chem, T) for chem in chems])
        gamma = self._calculate_gamma(x, T, model, components)

        P_bubble = np.sum(x * gamma * P_sat)
        y = (x * gamma * P_sat) / P_bubble

        results = {
            'P (kPa)': round(P_bubble / 1000, 2),
            'P (bar)': round(P_bubble / 1e5, 4),
            'P (atm)': round(P_bubble / 101325, 4),
            'T (C)': round(temperature_C, 2),
            'T (K)': round(T, 2),
            'model': model
        }

        for i in range(n):
            idx = i + 1
            comp = components[i]
            results[f'x{idx} ({comp})'] = round(x[i], 4)
            results[f'y{idx} ({comp})'] = round(y[i], 4)
            results[f'lambda{idx}'] = round(gamma[i], 4)
            results[f'P{idx}_sat (kPa)'] = round(P_sat[i] / 1000, 2)
            results[f'K{idx}'] = round(y[i] / x[i], 4) if x[i] > 1e-10 else 0.0

        return results

    def bubble_temperature(self, components, pressure_kPa, x, model='Ideal'):
        self.validate_model_components(components, model)

        P = pressure_kPa * 1000
        n = len(components)
        x = np.array(x) / np.sum(x)

        chems = [self._get_chemical(comp) for comp in components]
        T_guess = np.sum([x[i] * chems[i].Tb for i in range(n) if chems[i].Tb])

        def objective(T):
            try:
                P_sat = np.array([self._get_vapor_pressure(chems[i], T) for i in range(n)])
                gamma = self._calculate_gamma(x, T, model, components)
                return np.sum(x * gamma * P_sat) - P
            except:
                return 1e10

        T_bubble = fsolve(objective, T_guess)[0]
        P_sat = np.array([self._get_vapor_pressure(chems[i], T_bubble) for i in range(n)])
        gamma = self._calculate_gamma(x, T_bubble, model, components)
        y = (x * gamma * P_sat) / P

        results = {
            'T (C)': round(T_bubble - 273.15, 2),
            'T (K)': round(T_bubble, 2),
            'P (kPa)': round(pressure_kPa, 2),
            'P (bar)': round(pressure_kPa / 100, 4),
            'P (atm)': round(pressure_kPa / 101.325, 4),
            'model': model
        }

        for i in range(n):
            idx = i + 1
            comp = components[i]
            results[f'x{idx} ({comp})'] = round(x[i], 4)
            results[f'y{idx} ({comp})'] = round(y[i], 4)
            results[f'lambda{idx}'] = round(gamma[i], 4)
            results[f'P{idx}_sat (kPa)'] = round(P_sat[i] / 1000, 2)
            results[f'K{idx}'] = round(y[i] / x[i], 4) if x[i] > 1e-10 else 0.0

        return results

    def dew_point(self, components, temperature_C, y, model='Ideal'):
        """Ponto de orvalho a T fixa."""
        self.validate_model_components(components, model)

        T = temperature_C + 273.15
        n = len(components)
        y = np.array(y) / np.sum(y)

        chems = [self._get_chemical(comp) for comp in components]
        P_sat = np.array([self._get_vapor_pressure(chem, T) for chem in chems])

        P_guess = 1.0 / np.sum(y / P_sat)
        x_guess = y * P_guess / P_sat
        x_guess = np.clip(x_guess, 1e-8, 1.0)
        x_guess = x_guess / np.sum(x_guess)

        def objective(x):
            x_norm = np.clip(x, 1e-10, 1.0)
            x_norm = x_norm / np.sum(x_norm)
            gamma = self._calculate_gamma(x_norm, T, model, components)
            P_calc = np.sum(x_norm * gamma * P_sat)
            residual = y * P_calc - x_norm * gamma * P_sat
            return residual[:-1]

        try:
            from scipy.optimize import least_squares
            sol = least_squares(
                objective,
                x_guess[:-1],
                bounds=(1e-10, 1.0),
                max_nfev=1000,
                ftol=1e-10
            )
            x_solved = np.append(sol.x, 1 - np.sum(sol.x))
            if not sol.success or sol.cost > 1e-6:
                raise ValueError("Convergencia fraca")
        except:
            try:
                sol = fsolve(objective, x_guess[:-1], full_output=True, maxfev=2000)
                x_solved = np.append(sol[0], 1 - np.sum(sol[0]))
                if sol[2] != 1:
                    raise ValueError("fsolve nao convergiu")
            except:
                x = x_guess.copy()
                for _ in range(50):
                    gamma = self._calculate_gamma(x, T, model, components)
                    P_calc = np.sum(x * gamma * P_sat)
                    x_new = y * P_calc / (gamma * P_sat)
                    x_new = np.clip(x_new, 1e-10, 1.0)
                    x_new = x_new / np.sum(x_new)
                    if np.linalg.norm(x_new - x) < 1e-8:
                        break
                    x = x_new
                x_solved = x

        x = np.clip(x_solved, 1e-10, 1.0)
        x = x / np.sum(x)
        gamma = self._calculate_gamma(x, T, model, components)
        P_dew = np.sum(x * gamma * P_sat)

        if P_dew < 0 or P_dew > 1e8:
            raise ValueError(f"Pressao invalida: {P_dew} Pa")

        results = {
            'P (kPa)': round(P_dew / 1000, 2),
            'P (bar)': round(P_dew / 1e5, 4),
            'P (atm)': round(P_dew / 101325, 4),
            'T (C)': round(temperature_C, 2),
            'T (K)': round(T, 2),
            'model': model
        }

        for i in range(n):
            idx = i + 1
            comp = components[i]
            # orvalho: y é entrada, x é fase líquida calculada
            results[f'y{idx} ({comp})'] = round(y[i], 4)
            results[f'x{idx} ({comp})'] = round(x[i], 4)
            results[f'lambda{idx}'] = round(gamma[i], 4)
            results[f'P{idx}_sat (kPa)'] = round(P_sat[i] / 1000, 2)
            results[f'K{idx}'] = round(y[i] / x[i], 4) if x[i] > 1e-10 else 0.0

        return results

    def dew_temperature(self, components, pressure_kPa, y, model='Ideal'):
        """Temperatura de orvalho a P fixa."""
        self.validate_model_components(components, model)

        P = pressure_kPa * 1000
        n = len(components)
        y = np.array(y) / np.sum(y)

        chems = [self._get_chemical(comp) for comp in components]
        T_guess = np.sum([y[i] * chems[i].Tb for i in range(n) if chems[i].Tb])

        def objective(T):
            if T < 200 or T > 600:
                return 1e10
            try:
                P_sat = np.array([self._get_vapor_pressure(chems[i], T) for i in range(n)])

                x = y * P / P_sat
                x = np.clip(x, 1e-10, 1.0)
                x = x / np.sum(x)

                for _ in range(30):
                    gamma = self._calculate_gamma(x, T, model, components)
                    x_new = y * P / (gamma * P_sat)
                    x_new = np.clip(x_new, 1e-10, 1.0)
                    x_new = x_new / np.sum(x_new)

                    if np.linalg.norm(x_new - x) < 1e-9:
                        break
                    x = x_new

                gamma = self._calculate_gamma(x, T, model, components)
                P_calc = np.sum(x * gamma * P_sat)

                return P_calc - P
            except Exception:
                return 1e10

        try:
            T_dew = brentq(objective, 200, 600, maxiter=200, xtol=1e-6)
        except:
            try:
                sol = fsolve(objective, T_guess, full_output=True, maxfev=2000)
                T_dew = sol[0][0] if isinstance(sol[0], np.ndarray) else sol[0]
                if sol[2] != 1 or T_dew < 200 or T_dew > 600:
                    raise ValueError("Convergencia ruim")
            except:
                T_dew = T_guess

        P_sat = np.array([self._get_vapor_pressure(chems[i], T_dew) for i in range(n)])
        x = y * P / P_sat
        x = np.clip(x, 1e-10, 1.0)
        x = x / np.sum(x)

        for _ in range(30):
            gamma = self._calculate_gamma(x, T_dew, model, components)
            x_new = y * P / (gamma * P_sat)
            x_new = np.clip(x_new, 1e-10, 1.0)
            x_new = x_new / np.sum(x_new)
            if np.linalg.norm(x_new - x) < 1e-9:
                break
            x = x_new

        results = {
            'T (C)': round(T_dew - 273.15, 2),
            'T (K)': round(T_dew, 2),
            'P (kPa)': round(pressure_kPa, 2),
            'P (bar)': round(pressure_kPa / 100, 4),
            'P (atm)': round(pressure_kPa / 101.325, 4),
            'model': model
        }

        gamma = self._calculate_gamma(x, T_dew, model, components)
        for i in range(n):
            idx = i + 1
            comp = components[i]
            results[f'y{idx} ({comp})'] = round(y[i], 4)
            results[f'x{idx} ({comp})'] = round(x[i], 4)
            results[f'lambda{idx}'] = round(gamma[i], 4)
            results[f'P{idx}_sat (kPa)'] = round(P_sat[i] / 1000, 2)
            results[f'K{idx}'] = round(y[i] / x[i], 4) if x[i] > 1e-10 else 0.0

        return results

    def flash_calculation(self, components, temperature_C, pressure_kPa, z, model='Ideal'):
        """
        Flash isotérmico:
        - Iteração com coeficiente de atividade (λ)
        - Inclui P_i,sat nos resultados
        """
        self.validate_model_components(components, model)

        T = temperature_C + 273.15
        P = pressure_kPa * 1000
        n = len(components)
        z = np.array(z) / np.sum(z)

        chems = [self._get_chemical(comp) for comp in components]
        P_sat = np.array([self._get_vapor_pressure(chem, T) for chem in chems])

        # Chute inicial: K ideal (Raoult)
        K = P_sat / P

        # Equação de Rachford–Rice
        def rachford_rice(beta):
            if beta <= 0 or beta >= 1:
                return 1e10
            return np.sum(z * (K - 1) / (1 + beta * (K - 1)))

        # Determinar beta inicial
        try:
            if np.all(K > 1):
                beta = 1.0   # tudo vapor
            elif np.all(K < 1):
                beta = 0.0   # tudo líquido
            else:
                beta = brentq(rachford_rice, 1e-8, 1 - 1e-8, maxiter=100)
        except:
            beta = 0.5

        # Composições iniciais
        x = z / (1 + beta * (K - 1))
        y = K * x

        # Iteração com λ
        for _ in range(20):
            x = np.clip(x, 1e-10, 1.0)
            x = x / np.sum(x)

            gamma = self._calculate_gamma(x, T, model, components)
            K_new = gamma * P_sat / P

            if np.linalg.norm(K_new - K) < 1e-6:
                break

            K = K_new

            try:
                if np.all(K > 1):
                    beta = 1.0
                elif np.all(K < 1):
                    beta = 0.0
                else:
                    beta = brentq(rachford_rice, 1e-8, 1 - 1e-8, maxiter=100)
            except:
                pass

            x = z / (1 + beta * (K - 1))
            y = K * x

        x = np.clip(x, 1e-10, 1.0)
        x = x / np.sum(x)
        y = np.clip(y, 1e-10, 1.0)
        y = y / np.sum(y)
        beta = np.clip(beta, 0.0, 1.0)

        results = {
            'Fracao vapor (beta)': round(beta, 4),
            'Fracao liquido (1-beta)': round(1 - beta, 4),
            'T (C)': round(temperature_C, 2),
            'T (K)': round(T, 2),
            'P (kPa)': round(pressure_kPa, 2),
            'P (bar)': round(pressure_kPa / 100, 4),
            'P (atm)': round(pressure_kPa / 101.325, 4),
            'model': model
        }

        gamma = self._calculate_gamma(x, T, model, components)
        for i in range(n):
            idx = i + 1
            comp = components[i]
            results[f'z{idx} ({comp})'] = round(z[i], 4)
            results[f'x{idx} ({comp})'] = round(x[i], 4)
            results[f'y{idx} ({comp})'] = round(y[i], 4)
            results[f'K{idx}'] = round(K[i], 4)
            results[f'lambda{idx}'] = round(gamma[i], 4)
            results[f'P{idx}_sat (kPa)'] = round(P_sat[i] / 1000, 2)

        return results

    # ========================================================================
    # ==================== DIAGRAMAS BINÁRIOS ================================
    # ========================================================================

    def generate_pxy_diagram(self, components, temperature_C, model='Ideal'):
        """Gerar diagrama P–x–y para sistema binário."""
        if len(components) != 2:
            raise ValueError('Diagrama P-x-y apenas para sistemas binarios')

        self.validate_model_components(components, model)

        x_bubble = np.linspace(0.001, 0.999, 50)
        P_bubble = []
        y_bubble = []

        for x1 in x_bubble:
            try:
                result = self.bubble_point(components, temperature_C, [x1, 1 - x1], model)
                P_bubble.append(result['P (kPa)'])
                y_bubble.append(result[f'y1 ({components[0]})'])
            except:
                continue

        y_dew = np.linspace(0.001, 0.999, 50)
        P_dew = []
        x_dew = []

        for y1 in y_dew:
            try:
                result = self.dew_point(components, temperature_C, [y1, 1 - y1], model)
                P_dew.append(result['P (kPa)'])
                x_dew.append(result[f'x1 ({components[0]})'])
            except:
                continue

        return {
            'x_bubble': x_bubble[:len(P_bubble)].tolist(),
            'P_bubble': P_bubble,
            'y_bubble': y_bubble,
            'y_dew': y_dew[:len(P_dew)].tolist(),
            'P_dew': P_dew,
            'x_dew': x_dew,
            'T_C': temperature_C,
            'component1': components[0],
            'component2': components[1]
        }

    def generate_txy_diagram(self, components, pressure_kPa, model='Ideal'):
        """Gerar diagrama T–x–y para sistema binário."""
        if len(components) != 2:
            raise ValueError('Diagrama T-x-y apenas para sistemas binarios')

        self.validate_model_components(components, model)

        # Curva de bolha
        x_values = np.linspace(0.0, 1.0, 50)  # ✅ DE 0 A 1
        x_bubble = []
        T_bubble = []
        y_bubble = []

        for x1 in x_values:
            try:
                x_calc = [x1, 1 - x1]
                
                # Evitar divisão por zero, mas permitir valores extremos
                if x1 < 1e-8:
                    x_calc = [1e-8, 1 - 1e-8]
                elif x1 > 1 - 1e-8:
                    x_calc = [1 - 1e-8, 1e-8]
                
                result = self.bubble_temperature(components, pressure_kPa, x_calc, model)
                T = result['T (C)']

                if T < -50 or T > 300:
                    continue

                x_bubble.append(x1)  # ✅ VALOR ORIGINAL (0 até 1)
                T_bubble.append(T)
                y_bubble.append(result[f'y1 ({components[0]})'])
            except Exception as e:
                print(f"Erro em x1={x1}: {e}")  # Debug
                continue

        # Curva de orvalho
        y_values = np.linspace(0.0, 1.0, 50)  # ✅ DE 0 A 1
        y_dew = []
        T_dew = []
        x_dew = []

        for y1 in y_values:
            try:
                y_calc = [y1, 1 - y1]
                
                # Evitar divisão por zero
                if y1 < 1e-8:
                    y_calc = [1e-8, 1 - 1e-8]
                elif y1 > 1 - 1e-8:
                    y_calc = [1 - 1e-8, 1e-8]
                
                result = self.dew_temperature(components, pressure_kPa, y_calc, model)
                T = result['T (C)']

                if T < -50 or T > 300:
                    continue

                y_dew.append(y1)  # ✅ VALOR ORIGINAL (0 até 1)
                T_dew.append(T)
                x_dew.append(result[f'x1 ({components[0]})'])
            except Exception as e:
                print(f"Erro em y1={y1}: {e}")  # Debug
                continue

        return {
            'x_bubble': x_bubble,
            'T_bubble': T_bubble,
            'y_bubble': y_bubble,
            'y_dew': y_dew,
            'T_dew': T_dew,
            'x_dew': x_dew,
            'P_kPa': pressure_kPa,
            'component1': components[0],
            'component2': components[1]
        }

