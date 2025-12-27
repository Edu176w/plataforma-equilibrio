# app/utils/ai_elv.py

import time
import json
from sqlalchemy import func
from app import db
from app.models import Simulation


# ==========================
# LOG DE SIMULAÇÕES ELV
# ==========================

def log_elv_simulation(
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
    Registra uma simulação do módulo ELV na tabela Simulation.

    - user_id: id do usuário autenticado (ou None)
    - calculation_type: 'bubble', 'dew', 'flash', 'txy', 'pxy', etc.
    - model: 'Ideal', 'NRTL', 'UNIQUAC', 'UNIFAC'
    - components: lista de strings com os nomes dos componentes
    - conditions: dict com T, P, composições etc.
    - results: dict com os resultados calculados
    """
    try:
        exec_time = None
        if start_time is not None:
            exec_time = time.time() - start_time

        sim = Simulation(
            user_id=user_id,
            module='elv',
            calculation_type=calculation_type,
            model=model,
            components=json.dumps(components, ensure_ascii=False),
            conditions=json.dumps(conditions, ensure_ascii=False),
            results=json.dumps(results, ensure_ascii=False),
            execution_time=exec_time,
            success=success,
            error_message=error_message,
        )
        db.session.add(sim)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f'[AI_ELV] Erro ao salvar simulação ELV: {e}')


# ==========================
# BASE DE CONHECIMENTO ESTÁTICA
# ==========================

# Sistemas “clássicos” com sugestões específicas
ELV_KB_SYSTEMS = [
    {
        "components_key": ["ethanol", "water"],
        "label": "etanol-água",
        "preferred_models": ["NRTL", "UNIQUAC"],
        "recommended_ranges": {
            "temperature_C": {"min": 70.0, "max": 90.0},
            "pressure_kPa": {"min": 90.0, "max": 110.0},
        },
        "prefill": {
            "temperature_C": 78.0,
            "pressure_kPa": 101.325,
            "liquid_compositions": [0.5, 0.5],
        },
    },
    {
        "components_key": ["benzene", "toluene"],
        "label": "benzeno-tolueno",
        "preferred_models": ["Ideal", "UNIQUAC"],
        "recommended_ranges": {
            "temperature_C": {"min": 80.0, "max": 120.0},
            "pressure_kPa": {"min": 80.0, "max": 150.0},
        },
        "prefill": {
            "temperature_C": 100.0,
            "pressure_kPa": 101.325,
            "liquid_compositions": [0.5, 0.5],
        },
    },
    {
        "components_key": ["acetone", "chloroform"],
        "label": "acetona-clorofórmio",
        "preferred_models": ["UNIQUAC"],
        "recommended_ranges": {
            "temperature_C": {"min": 50.0, "max": 90.0},
            "pressure_kPa": {"min": 80.0, "max": 120.0},
        },
        "prefill": {
            "temperature_C": 60.0,
            "pressure_kPa": 101.325,
            "liquid_compositions": [0.5, 0.5],
        },
    },
]

# Sistemas típicos por modelo (para exibição na UI)
BEST_COMPONENTS_FOR_MODEL = [
    {
        "model": "Ideal",
        "examples": [
            "benzeno-tolueno",
            "propano-butano",
            "n-hexano-n-heptano",
        ],
    },
    {
        "model": "NRTL",
        "examples": [
            "água-etanol",
            "água-acetona",
            "água-ácido acético",
        ],
    },
    {
        "model": "UNIQUAC",
        "examples": [
            "benzeno-clorobenzeno",
            "acetona-clorofórmio",
            "misturas altamente não ideais em geral",
        ],
    },
    {
        "model": "UNIFAC",
        "examples": [
            "misturas sem dados experimentais",
            "séries homólogas (álcoois, alcanos, cetonas)",
        ],
    },
]


def _normalize_components(components):
    """Normaliza lista de componentes para comparação."""
    if not components:
        return []
    return sorted([str(c).strip().lower() for c in components])


def _match_system_in_kb(components_norm):
    """Tenta encontrar o sistema na base estática ELV_KB_SYSTEMS."""
    for entry in ELV_KB_SYSTEMS:
        if _normalize_components(entry["components_key"]) == components_norm:
            return entry
    return None


# ==========================
# RECOMENDAÇÃO DE MODELO
# ==========================

def recommend_model_for_elv(components, calculation_type):
    """
    Recomendação enriquecida de modelo termodinâmico para ELV.

    Saída (dict) usada pelo frontend:
    - recommended_model: string
    - strategy: 'historical', 'kb_system', 'rule_based'
    - details: dict (motivo, métricas etc.)
    - recommended_models_for_components: lista de modelos adequados
    - best_components_for_model: lista com exemplos por modelo
    - recommended_ranges: dict com faixas de T/P (quando aplicável)
    - prefill: dict com T, P, x para autopreenchimento (quando disponível)
    """
    components_norm = _normalize_components(components)
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
                # média de sucesso convertendo bool -> int
                func.avg(
                    (Simulation.success == True).cast(db.Integer)  # noqa: E712
                ).label('success_rate'),
            )
            .filter(
                Simulation.module == 'elv',
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
            recommended_models_for_components = [s.model for s in ordered]

            base = {
                "recommended_model": best.model,
                "strategy": "historical",
                "details": {
                    "success_rate": float(best.success_rate or 0),
                    "avg_time": float(best.avg_time or 0),
                    "samples": int(best.n or 0),
                    "reason": (
                        "Modelo escolhido com base no histórico de simulações "
                        "para esse sistema e tipo de cálculo."
                    ),
                },
                "recommended_models_for_components": recommended_models_for_components,
                "best_components_for_model": BEST_COMPONENTS_FOR_MODEL,
            }

            kb_entry = _match_system_in_kb(components_norm)
            if kb_entry:
                base["recommended_ranges"] = kb_entry.get("recommended_ranges")
                base["prefill"] = kb_entry.get("prefill")

            return base

    except Exception as e:
        print(f'[AI_ELV] Erro na consulta de histórico ELV: {e}')

    # ---------------------------
    # 2) Base estática por sistema
    # ---------------------------
    kb_entry = _match_system_in_kb(components_norm)
    if kb_entry:
        preferred = kb_entry.get("preferred_models") or ["UNIQUAC"]
        recommended_model = preferred[0]

        return {
            "recommended_model": recommended_model,
            "strategy": "kb_system",
            "details": {
                "reason": (
                    f"Sistema clássico ({kb_entry['label']}); "
                    f"modelos {', '.join(preferred)} costumam descrever bem o ELV."
                )
            },
            "recommended_models_for_components": preferred,
            "best_components_for_model": BEST_COMPONENTS_FOR_MODEL,
            "recommended_ranges": kb_entry.get("recommended_ranges"),
            "prefill": kb_entry.get("prefill"),
        }

    # ---------------------------
    # 3) Fallback baseado em regras simples
    # ---------------------------
    comps_lower_str = " ".join(components_norm)

    polar_markers = [
        "water", "água", "agua",
        "ethanol", "etanol",
        "methanol", "metanol",
        "propanol", "propan-1-ol", "propan-2-ol",
        "acetic acid", "ácido acético",
        "acetone", "acetona",
    ]
    apolar_markers = [
        "hexane", "heptane", "octane",
        "pentane", "butane", "propane",
        "benzene", "toluene",
    ]

    has_polar = any(p in comps_lower_str for p in polar_markers)
    has_apolar = any(a in comps_lower_str for a in apolar_markers)

    if has_polar and not has_apolar:
        base_model = "NRTL"
        reason = (
            "Mistura majoritariamente polar/associativa; "
            "NRTL costuma representar melhor interações específicas e forte não-idealidade."
        )
        extra_models = ["NRTL", "UNIQUAC", "UNIFAC", "Ideal"]
    elif has_apolar and not has_polar:
        base_model = "Ideal"
        reason = (
            "Mistura predominantemente apolar; o comportamento tende a ser próximo do ideal."
        )
        extra_models = ["Ideal", "UNIQUAC", "UNIFAC"]
    else:
        base_model = "UNIQUAC"
        reason = (
            "Sistema genérico ou misto; UNIQUAC oferece boa robustez "
            "para ampla faixa de misturas não ideais."
        )
        extra_models = ["UNIQUAC", "NRTL", "UNIFAC", "Ideal"]

    generic_ranges = {
        "temperature_C": {"min": 40.0, "max": 120.0},
        "pressure_kPa": {"min": 50.0, "max": 200.0},
    }

    n = max(1, len(components_norm))
    prefill = {
        "liquid_compositions": [1.0 / n for _ in range(n)],
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
