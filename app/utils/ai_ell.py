'''
app/utils/ai_ell.py
VERSÃO 2.0 - Compatível com NumPy 2.x

Sistema de recomendações e logging para módulo ELL
Baseado em histórico de simulações e base de conhecimento estática

Correções aplicadas:
- ✅ Conversão de tipos NumPy para Python nativos
- ✅ Tratamento robusto de serialização JSON
- ✅ Compatibilidade total com NumPy 2.3.5
'''

import time
import json
import numpy as np
from sqlalchemy import func
from app import db
from app.models import Simulation

# ============================================================================
# FUNÇÕES AUXILIARES DE CONVERSÃO
# ============================================================================

def convert_to_native_types(obj):
    '''
    Converte recursivamente tipos NumPy para tipos nativos Python
    
    Args:
        obj: Objeto a ser convertido (pode ser dict, list, NumPy type, etc.)
    
    Returns:
        Objeto convertido para tipos nativos Python
    '''
    if obj is None:
        return None
    
    # Tipos NumPy escalares
    if isinstance(obj, (np.integer, np.signedinteger)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.complexfloating)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return [convert_to_native_types(item) for item in obj.tolist()]
    
    # Coleções Python
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native_types(item) for item in obj]
    
    # Já é tipo nativo
    return obj

def safe_json_dumps(obj):
    '''
    Serialização JSON segura com conversão automática de tipos NumPy
    
    Args:
        obj: Objeto a ser serializado
    
    Returns:
        str: String JSON
    '''
    try:
        # Tentar conversão direta
        return json.dumps(obj, ensure_ascii=False)
    except (TypeError, ValueError):
        # Se falhar, converter tipos NumPy primeiro
        obj_converted = convert_to_native_types(obj)
        return json.dumps(obj_converted, ensure_ascii=False)

# ============================================================================
# LOG DE SIMULAÇÕES ELL
# ============================================================================

def log_ell_simulation(
    user_id,
    calculation_type,
    model,
    components,
    conditions,
    results,
    success=True,
    error_message=None,
    start_time=None
):
    """
    Registra uma simulação do módulo ELL na tabela Simulation.
    
    Args:
        user_id: id do usuário autenticado (ou None)
        calculation_type: 'ell_flash', 'ternary_diagram', 'binodal', 'tie_lines'
        model: 'NRTL', 'UNIQUAC' (sem 'Ideal' para ELL)
        components: lista de strings com os nomes dos componentes (3 componentes)
        conditions: dict com T, composições globais, etc.
        results: dict com os resultados calculados (beta, x_L1, x_L2, K, etc.)
        success: bool indicando sucesso do cálculo
        error_message: mensagem de erro (se houver)
        start_time: timestamp do início do cálculo (para calcular tempo de execução)
    """
    try:
        exec_time = None
        if start_time is not None:
            exec_time = float(time.time() - start_time)

        # Converter para tipos nativos antes de serializar
        components_safe = convert_to_native_types(components)
        conditions_safe = convert_to_native_types(conditions)
        results_safe = convert_to_native_types(results)

        sim = Simulation(
            user_id=user_id,
            module='ell',
            calculation_type=str(calculation_type),
            model=str(model),
            components=safe_json_dumps(components_safe),
            conditions=safe_json_dumps(conditions_safe),
            results=safe_json_dumps(results_safe),
            execution_time=exec_time,
            success=bool(success),
            error_message=str(error_message) if error_message else None,
        )
        db.session.add(sim)
        db.session.commit()
        print(f'[AI_ELL] ✅ Simulação ELL registrada: {model} - {calculation_type}')
    except Exception as e:
        db.session.rollback()
        print(f'[AI_ELL] ❌ Erro ao salvar simulação ELL: {e}')

# ============================================================================
# BASE DE CONHECIMENTO ESTÁTICA PARA ELL
# ============================================================================

ELL_KB_SYSTEMS = [
    {
        "components_key": ["water", "1,1,2-trichloroethane", "acetone"],
        "label": "água-TCE-acetona",
        "preferred_models": ["NRTL"],
        "table_reference": "E-5",
        "recommended_ranges": {
            "temperature_C": {"min": 20.0, "max": 30.0},
        },
        "prefill": {
            "temperature_C": 25.0,
            "z_feed": [0.30, 0.40, 0.30],
        },
        "notes": "Sistema clássico com dados experimentais NRTL validados (Bender and Block, 1975). Par água-TCE é parcialmente miscível."
    },
    {
        "components_key": ["water", "tce", "acetone"],
        "label": "água-TCE-acetona (alias)",
        "preferred_models": ["NRTL"],
        "table_reference": "E-5",
        "recommended_ranges": {
            "temperature_C": {"min": 20.0, "max": 30.0},
        },
        "prefill": {
            "temperature_C": 25.0,
            "z_feed": [0.30, 0.40, 0.30],
        },
        "notes": "Alias para 1,1,2-trichloroethane = TCE"
    },
    {
        "components_key": ["benzene", "water", "ethanol"],
        "label": "benzeno-água-etanol",
        "preferred_models": ["UNIQUAC", "NRTL"],
        "table_reference": "E-6",
        "recommended_ranges": {
            "temperature_C": {"min": 20.0, "max": 30.0},
        },
        "prefill": {
            "temperature_C": 25.0,
            "z_feed": [0.35, 0.30, 0.35],
        },
        "notes": "Sistema ternário típico com região de imiscibilidade extensa. Par benzeno-água é imiscível, etanol é solvente mútuo."
    },
    {
        "components_key": ["acetonitrile", "n-heptane", "benzene"],
        "label": "acetonitrila-n-heptano-benzeno",
        "preferred_models": ["UNIQUAC"],
        "table_reference": "E-6",
        "recommended_ranges": {
            "temperature_C": {"min": 40.0, "max": 50.0},
        },
        "prefill": {
            "temperature_C": 45.0,
            "z_feed": [0.40, 0.30, 0.30],
        },
        "notes": "Sistema com dados experimentais a 45°C. Par acetonitrila-heptano é parcialmente miscível."
    },
    {
        "components_key": ["acetonitrile", "heptane", "benzene"],
        "label": "acetonitrila-heptano-benzeno (alias)",
        "preferred_models": ["UNIQUAC"],
        "table_reference": "E-6",
        "recommended_ranges": {
            "temperature_C": {"min": 40.0, "max": 50.0},
        },
        "prefill": {
            "temperature_C": 45.0,
            "z_feed": [0.40, 0.30, 0.30],
        },
        "notes": "Alias para n-heptane = heptane"
    },
    {
        "components_key": ["cyclohexane", "nitromethane", "benzene"],
        "label": "ciclohexano-nitrometano-benzeno",
        "preferred_models": ["UNIQUAC"],
        "table_reference": "E-6",
        "recommended_ranges": {
            "temperature_C": {"min": 20.0, "max": 30.0},
        },
        "prefill": {
            "temperature_C": 25.0,
            "z_feed": [0.35, 0.35, 0.30],
        },
        "notes": "Sistema com região de imiscibilidade entre ciclohexano e nitrometano."
    },
    {
        "components_key": ["2,2,4-trimethylpentane", "furfural", "cyclohexane"],
        "label": "isooctano-furfural-ciclohexano",
        "preferred_models": ["UNIQUAC"],
        "table_reference": "E-6",
        "recommended_ranges": {
            "temperature_C": {"min": 20.0, "max": 30.0},
        },
        "prefill": {
            "temperature_C": 25.0,
            "z_feed": [0.30, 0.40, 0.30],
        },
        "notes": "Sistema industrial típico de extração líquido-líquido com furfural."
    },
]

BEST_COMPONENTS_FOR_MODEL = [
    {
        "model": "NRTL",
        "examples": [
            "água-solvente orgânico-álcool (ex: água-TCE-acetona)",
            "sistemas com forte imiscibilidade",
            "extração líquido-líquido industrial",
        ],
        "notes": "Parâmetro α crítico para região de miscibilidade. NRTL é preferido para sistemas com associações moleculares fortes."
    },
    {
        "model": "UNIQUAC",
        "examples": [
            "misturas ternárias com aromáticos (ex: benzeno-água-etanol)",
            "sistemas com diferenças de tamanho molecular significativas",
            "extração com solventes polares (ex: furfural)",
        ],
        "notes": "Termo combinatorial importante para ELL. UNIQUAC é robusto para ampla variedade de sistemas."
    },
]

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def _normalize_components(components):
    """Normaliza lista de componentes para comparação."""
    if not components:
        return []
    
    aliases = {
        'tce': '1,1,2-trichloroethane',
        'heptane': 'n-heptane',
        'isooctane': '2,2,4-trimethylpentane',
    }
    
    normalized = []
    for c in components:
        c_lower = str(c).strip().lower()
        c_normalized = aliases.get(c_lower, c_lower)
        normalized.append(c_normalized)
    
    return sorted(normalized)

def _match_system_in_kb(components_norm):
    """Tenta encontrar o sistema na base estática ELL_KB_SYSTEMS."""
    for entry in ELL_KB_SYSTEMS:
        if _normalize_components(entry["components_key"]) == components_norm:
            return entry
    return None

# ============================================================================
# RECOMENDAÇÃO DE MODELO
# ============================================================================

def recommend_model_for_ell(components, calculation_type):
    """
    Recomendação enriquecida de modelo termodinâmico para ELL.
    
    Args:
        components (list): Lista com 3 nomes de componentes
        calculation_type (str): 'ell_flash', 'ternary_diagram', 'binodal', 'tie_lines'
    
    Returns:
        dict: Recomendação completa (sempre com tipos Python nativos)
    """
    components_norm = _normalize_components(components)
    
    # Validar número de componentes
    if len(components_norm) != 3:
        return {
            "recommended_model": "NRTL",
            "strategy": "error",
            "details": {
                "reason": "ELL requer exatamente 3 componentes para sistema ternário. Por favor, selecione 3 componentes."
            },
            "recommended_models_for_components": ["NRTL", "UNIQUAC"],
            "best_components_for_model": BEST_COMPONENTS_FOR_MODEL,
        }
    
    comp_key_str = json.dumps(sorted(components), ensure_ascii=False)

    # ---------------------------
    # 1) Uso do histórico (caso exista)
    # ---------------------------
    try:
        sims = (
            db.session.query(
                Simulation.model,
                func.count(Simulation.id).label('n'),
                func.avg(Simulation.execution_time).label('avg_time'),
                func.avg(
                    (Simulation.success == True).cast(db.Integer)  # noqa: E712
                ).label('success_rate'),
            )
            .filter(
                Simulation.module == 'ell',
                Simulation.calculation_type == calculation_type,
                Simulation.components.like('%' + comp_key_str.strip('[]') + '%'),
            )
            .group_by(Simulation.model)
            .all()
        )

        if sims:
            best = max(
                sims,
                key=lambda s: (float(s.success_rate or 0), -float(s.avg_time or 0)),
            )

            ordered = sorted(
                sims,
                key=lambda s: (float(s.success_rate or 0), -float(s.avg_time or 0)),
                reverse=True,
            )
            recommended_models_for_components = [str(s.model) for s in ordered]

            base = {
                "recommended_model": str(best.model),
                "strategy": "historical",
                "details": {
                    "success_rate": float(best.success_rate or 0),
                    "avg_time": float(best.avg_time or 0),
                    "samples": int(best.n or 0),
                    "reason": (
                        "Modelo escolhido com base no histórico de simulações ELL "
                        f"para este sistema ternário e tipo de cálculo ({calculation_type}). "
                        f"Taxa de sucesso: {float(best.success_rate or 0):.1%}"
                    ),
                },
                "recommended_models_for_components": recommended_models_for_components,
                "best_components_for_model": BEST_COMPONENTS_FOR_MODEL,
            }

            kb_entry = _match_system_in_kb(components_norm)
            if kb_entry:
                base["recommended_ranges"] = kb_entry.get("recommended_ranges")
                base["prefill"] = kb_entry.get("prefill")
                base["details"]["table_reference"] = kb_entry.get("table_reference")
                base["details"]["notes"] = kb_entry.get("notes")

            return base

    except Exception as e:
        print(f'[AI_ELL] ⚠️ Erro na consulta de histórico ELL: {e}')

    # ---------------------------
    # 2) Base estática por sistema
    # ---------------------------
    kb_entry = _match_system_in_kb(components_norm)
    if kb_entry:
        preferred = kb_entry.get("preferred_models") or ["UNIQUAC"]
        recommended_model = str(preferred[0])

        return {
            "recommended_model": recommended_model,
            "strategy": "kb_system",
            "details": {
                "reason": (
                    f"Sistema clássico encontrado: {kb_entry['label']}. "
                    f"Modelos {', '.join(preferred)} são recomendados pela literatura."
                ),
                "table_reference": str(kb_entry.get("table_reference", "")),
                "notes": str(kb_entry.get("notes", ""))
            },
            "recommended_models_for_components": [str(m) for m in preferred],
            "best_components_for_model": BEST_COMPONENTS_FOR_MODEL,
            "recommended_ranges": kb_entry.get("recommended_ranges"),
            "prefill": kb_entry.get("prefill"),
        }

    # ---------------------------
    # 3) Fallback baseado em regras
    # ---------------------------
    comps_lower_str = " ".join(components_norm)

    polar_markers = [
        "water", "água", "agua",
        "ethanol", "etanol",
        "methanol", "metanol",
        "acetone", "acetona",
        "furfural",
        "nitromethane", "nitrometano",
        "acetonitrile", "acetonitrila",
    ]
    
    apolar_markers = [
        "hexane", "heptane", "octane",
        "cyclohexane", "ciclohexano",
        "benzene", "benzeno",
        "toluene", "tolueno",
        "trichloroethane", "tce",
        "trimethylpentane", "isooctane",
    ]

    has_polar = any(p in comps_lower_str for p in polar_markers)
    has_apolar = any(a in comps_lower_str for a in apolar_markers)
    has_water = "water" in comps_lower_str or "água" in comps_lower_str or "agua" in comps_lower_str

    if has_water and has_apolar:
        base_model = "NRTL"
        reason = (
            "Sistema contém água e componentes apolares, típico de extração líquido-líquido. "
            "NRTL é recomendado para sistemas com forte imiscibilidade e associações moleculares."
        )
        extra_models = ["NRTL", "UNIQUAC"]
    
    elif has_polar and has_apolar:
        base_model = "UNIQUAC"
        reason = (
            "Sistema misto polar/apolar. UNIQUAC oferece boa robustez para ampla faixa de "
            "misturas não ideais com diferenças de tamanho molecular."
        )
        extra_models = ["UNIQUAC", "NRTL"]
    
    else:
        base_model = "UNIQUAC"
        reason = (
            "Sistema ternário genérico. UNIQUAC é recomendado como modelo robusto "
            "para ELL com termo combinatorial importante para diferenças de tamanho."
        )
        extra_models = ["UNIQUAC", "NRTL"]

    generic_ranges = {
        "temperature_C": {"min": 20.0, "max": 40.0},
    }

    prefill = {
        "temperature_C": 25.0,
        "z_feed": [0.33, 0.33, 0.34],
    }

    return {
        "recommended_model": base_model,
        "strategy": "rule_based",
        "details": {
            "reason": reason,
        },
        "recommended_models_for_components": extra_models,
        "best_components_for_model": BEST_COMPONENTS_FOR_MODEL,
        "recommended_ranges": generic_ranges,
        "prefill": prefill,
    }

# ============================================================================
# ANÁLISE DE SISTEMA ELL (Compatibilidade)
# ============================================================================

def analyze_ell_system(components, calculation_type):
    """
    Análise simplificada de sistema ELL para interface com calculadora.
    Esta é uma função wrapper que chama recommend_model_for_ell().
    
    Args:
        components (list): Lista com 3 componentes
        calculation_type (str): 'flash' ou 'ternary'
    
    Returns:
        dict: Recomendação de modelo e condições
    """
    # Mapear tipos de cálculo
    calc_type_map = {
        'flash': 'ell_flash',
        'ternary': 'ternary_diagram',
        'ternary_diagram': 'ternary_diagram',
        'ell_flash': 'ell_flash',
    }
    
    calc_type = calc_type_map.get(calculation_type, 'ell_flash')
    
    # Chamar recommend_model_for_ell
    return recommend_model_for_ell(components, calc_type)


# ============================================================================
# TESTE DE COMPATIBILIDADE
# ============================================================================

if __name__ == '__main__':
    print("[AI_ELL] Testando módulo de recomendações...")
    
    # Teste 1: Sistema clássico
    rec = recommend_model_for_ell(['water', 'tce', 'acetone'], 'ell_flash')
    print(f"✅ Recomendação para Water/TCE/Acetone: {rec['recommended_model']}")
    print(f"   Estratégia: {rec['strategy']}")
    
    # Teste 2: Sistema UNIQUAC
    rec2 = recommend_model_for_ell(['benzene', 'water', 'ethanol'], 'ternary_diagram')
    print(f"✅ Recomendação para Benzene/Water/Ethanol: {rec2['recommended_model']}")
    
    # Teste 3: Conversão de tipos NumPy
    test_data = {
        'beta': np.float64(0.456),
        'x_L1': np.array([0.1, 0.8, 0.1]),
        'converged': np.bool_(True)
    }
    converted = convert_to_native_types(test_data)
    print(f"✅ Conversão de tipos NumPy: {type(converted['beta']).__name__}")
    
    print("[AI_ELL] ✅ Módulo de recomendações carregado com sucesso!")
