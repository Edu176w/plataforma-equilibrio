# app/utils/ai_esl.py
"""
AI-Powered Recommendations for ESL Module
===============================================================================

Fornece recomendações inteligentes de modelos termodinâmicos para cálculos de
Equilíbrio Sólido-Líquido (ESL) baseadas em:

1. Histórico de simulações bem-sucedidas
2. Base de conhecimento de sistemas eutéticos conhecidos
3. Propriedades termodinâmicas dos componentes (Tm, ΔHfus, polaridade)
4. Regras heurísticas de Prausnitz et al.
5. Disponibilidade de parâmetros binários

Referências:
- Prausnitz et al. (1999), Capítulo 11
- NIST WebBook
- Literatura de sistemas eutéticos

Autor: Plataforma de Equilíbrio de Fases
Data: 2025-12-20
"""

import time
import json
from typing import List, Dict, Optional, Any
from sqlalchemy import func
from app import db
from app.models import Simulation

# Importar dados ESL se disponíveis
try:
    from app.data.esl_data import (
        get_component_data,
        get_eutectic_systems,
        list_available_components,
    )
    HAS_ESL_DATA = True
except ImportError:
    HAS_ESL_DATA = False
    def get_component_data(name): return None
    def get_eutectic_systems(): return []
    def list_available_components(): return []


# ============================================================================
# LOG DE SIMULAÇÕES ESL
# ============================================================================

def log_esl_simulation(
    user_id: Optional[int],
    calculation_type: str,
    model: str,
    components: List[str],
    conditions: Dict[str, Any],
    results: Dict[str, Any],
    success: bool = True,
    error_message: Optional[str] = None,
    start_time: Optional[float] = None
) -> None:
    """
    Registra uma simulação do módulo ESL na tabela Simulation.

    Args:
        user_id: ID do usuário autenticado (ou None)
        calculation_type: 'solubility', 'crystallization', 'tx', 'ternary'
        model: 'Ideal', 'NRTL', 'UNIQUAC', 'UNIFAC'
        components: Lista de nomes dos componentes
        conditions: Dict com T, composições, etc.
        results: Dict com os resultados calculados
        success: Se o cálculo foi bem-sucedido
        error_message: Mensagem de erro (se houver)
        start_time: Timestamp do início do cálculo
    """
    try:
        exec_time = None
        if start_time is not None:
            exec_time = time.time() - start_time

        sim = Simulation(
            user_id=user_id,
            module='esl',
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
        
        print(f'[AI_ESL] Simulação registrada: {calculation_type} com {model} para {components}')
        
    except Exception as e:
        db.session.rollback()
        print(f'[AI_ESL] Erro ao salvar simulação ESL: {e}')


# ============================================================================
# BASE DE CONHECIMENTO ESTÁTICA (SISTEMAS CLÁSSICOS ESL)
# ============================================================================

# Sistemas eutéticos clássicos da literatura
ESL_KB_SYSTEMS = [
    {
        "components_key": ["naphthalene", "benzene"],
        "label": "Naftaleno-Benzeno",
        "preferred_models": ["Ideal", "UNIQUAC"],
        "recommended_ranges": {
            "temperature_C": {"min": -12.0, "max": 80.0},
        },
        "prefill": {
            "temperature_C": 25.0,
            "liquid_compositions": [0.5, 0.5],
        },
        "eutectic": {
            "T_C": -12.0,
            "x1": 0.19,
        },
        "notes": "Sistema ideal clássico para validação. Eutético bem caracterizado.",
        "reference": "Prausnitz et al. (1999), Example 11-2"
    },
    {
        "components_key": ["phenol", "water"],
        "label": "Fenol-Água",
        "preferred_models": ["NRTL", "UNIQUAC"],
        "recommended_ranges": {
            "temperature_C": {"min": 20.0, "max": 80.0},
        },
        "prefill": {
            "temperature_C": 40.0,
            "liquid_compositions": [0.5, 0.5],
        },
        "notes": "Sistema com forte ligação de hidrogênio. NRTL recomendado.",
        "reference": "NIST WebBook + Literatura"
    },
    {
        "components_key": ["urea", "water"],
        "label": "Ureia-Água",
        "preferred_models": ["UNIQUAC"],
        "recommended_ranges": {
            "temperature_C": {"min": 10.0, "max": 90.0},
        },
        "prefill": {
            "temperature_C": 25.0,
            "liquid_compositions": [0.3, 0.7],
        },
        "notes": "Grande diferença de tamanho molecular. UNIQUAC captura efeitos entrópicos.",
        "reference": "UNIQUAC original paper"
    },
    {
        "components_key": ["benzoic acid", "toluene"],
        "label": "Ácido Benzoico-Tolueno",
        "preferred_models": ["UNIQUAC", "NRTL"],
        "recommended_ranges": {
            "temperature_C": {"min": 20.0, "max": 100.0},
        },
        "prefill": {
            "temperature_C": 60.0,
            "liquid_compositions": [0.4, 0.6],
        },
        "notes": "Ácido carboxílico em solvente aromático. Não-idealidade moderada.",
        "reference": "DECHEMA"
    },
    {
        "components_key": ["naphthalene", "diphenylamine"],
        "label": "Naftaleno-Difenilamina",
        "preferred_models": ["Ideal", "UNIQUAC"],
        "recommended_ranges": {
            "temperature_C": {"min": 30.0, "max": 100.0},
        },
        "prefill": {
            "temperature_C": 50.0,
            "liquid_compositions": [0.5, 0.5],
        },
        "eutectic": {
            "T_C": 30.0,
            "x1": 0.44,
        },
        "notes": "Sistema orgânico aromático. Comportamento próximo do ideal.",
        "reference": "Prausnitz et al. (1999)"
    },
    {
        "components_key": ["biphenyl", "naphthalene"],
        "label": "Bifenil-Naftaleno",
        "preferred_models": ["Ideal"],
        "recommended_ranges": {
            "temperature_C": {"min": 20.0, "max": 80.0},
        },
        "prefill": {
            "temperature_C": 40.0,
            "liquid_compositions": [0.5, 0.5],
        },
        "eutectic": {
            "T_C": 39.0,
            "x1": 0.57,
        },
        "notes": "Sistema ideal clássico. Aromáticos similares.",
        "reference": "Landolt-Börnstein"
    },
    {
        "components_key": ["p-dichlorobenzene", "p-dibromobenzene"],
        "label": "p-Diclorobenzeno-p-Dibromobenzeno",
        "preferred_models": ["Ideal", "UNIQUAC"],
        "recommended_ranges": {
            "temperature_C": {"min": 40.0, "max": 90.0},
        },
        "prefill": {
            "temperature_C": 60.0,
            "liquid_compositions": [0.5, 0.5],
        },
        "eutectic": {
            "T_C": 51.0,
            "x1": 0.48,
        },
        "notes": "Isômeros para-substituídos. Comportamento simétrico próximo do ideal.",
        "reference": "Journal of Chemical & Engineering Data"
    },
]


# Sistemas típicos por modelo (para exibição na UI)
BEST_COMPONENTS_FOR_MODEL_ESL = [
    {
        "model": "Ideal",
        "examples": [
            "Naftaleno-Benzeno",
            "Bifenil-Naftaleno",
            "Hidrocarbonetos aromáticos similares",
            "Misturas orgânicas não-polares",
        ],
        "characteristics": "Componentes com estrutura e polaridade similares. γ ≈ 1.",
        "limitations": "Não captura desvios por ligação H, associação molecular ou grande assimetria."
    },
    {
        "model": "NRTL",
        "examples": [
            "Fenol-Água",
            "Álcoois-Hidrocarbonetos",
            "Sistemas com ligação de hidrogênio",
            "Misturas polares/apolares",
        ],
        "characteristics": "Parâmetro α captura interações locais. Bom para sistemas não-aleatórios.",
        "limitations": "Requer parâmetros binários ajustados. Sensível ao valor de α."
    },
    {
        "model": "UNIQUAC",
        "examples": [
            "Ureia-Água",
            "Ácidos orgânicos em solventes",
            "Sistemas com grande diferença de tamanho molecular",
            "Polímeros em solventes",
        ],
        "characteristics": "Separa contribuições combinatorial (tamanho/forma) e residual (energética).",
        "limitations": "Requer parâmetros r (volume) e q (área superficial) além de τ."
    },
    {
        "model": "UNIFAC",
        "examples": [
            "Misturas sem dados experimentais",
            "Predição de solubilidade de novos compostos",
            "Sistemas multicomponentes complexos",
            "Screening preliminar",
        ],
        "characteristics": "Método de contribuição de grupos. Totalmente preditivo.",
        "limitations": "Grupos funcionais devem estar na base. Precisão menor que modelos ajustados."
    },
]


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def _normalize_components(components: List[str]) -> List[str]:
    """Normaliza lista de componentes para comparação case-insensitive."""
    if not components:
        return []
    return sorted([str(c).strip().lower() for c in components])


def _match_system_in_kb(components_norm: List[str]) -> Optional[Dict[str, Any]]:
    """Tenta encontrar o sistema na base estática ESL_KB_SYSTEMS."""
    for entry in ESL_KB_SYSTEMS:
        if _normalize_components(entry["components_key"]) == components_norm:
            return entry
    return None


def _get_component_properties(component_name: str) -> Optional[Dict[str, Any]]:
    """Obtém propriedades ESL do componente da base de dados."""
    if not HAS_ESL_DATA:
        return None
    
    try:
        return get_component_data(component_name)
    except Exception as e:
        print(f'[AI_ESL] Erro ao obter propriedades de {component_name}: {e}')
        return None


def _analyze_component_polarity(components: List[str]) -> Dict[str, Any]:
    """
    Analisa polaridade e características químicas dos componentes.
    
    Returns:
        Dict com has_polar, has_nonpolar, has_aromatic, has_aliphatic, etc.
    """
    # Marcadores químicos
    polar_markers = [
        "water", "água", "agua",
        "ethanol", "etanol",
        "methanol", "metanol",
        "phenol", "fenol",
        "acetic acid", "ácido acético",
        "urea", "ureia",
        "glycerol", "glicerol",
        "acetone", "acetona",
    ]
    
    aromatic_markers = [
        "benzene", "benzeno",
        "toluene", "tolueno",
        "naphthalene", "naftaleno",
        "anthracene", "antraceno",
        "phenyl", "fenil",
        "biphenyl", "bifenil",
    ]
    
    aliphatic_markers = [
        "hexane", "hexano",
        "heptane", "heptano",
        "octane", "octano",
        "decane", "decano",
        "cyclohexane", "ciclohexano",
    ]
    
    acid_markers = [
        "acid", "ácido",
        "carboxylic", "carboxílico",
    ]
    
    salt_markers = [
        "sodium", "sódio",
        "chloride", "cloreto",
        "sulfate", "sulfato",
        "nitrate", "nitrato",
    ]
    
    comps_lower = " ".join([c.lower() for c in components])
    
    return {
        "has_polar": any(p in comps_lower for p in polar_markers),
        "has_aromatic": any(a in comps_lower for a in aromatic_markers),
        "has_aliphatic": any(a in comps_lower for a in aliphatic_markers),
        "has_acid": any(a in comps_lower for a in acid_markers),
        "has_salt": any(s in comps_lower for s in salt_markers),
        "all_organic": not any(s in comps_lower for s in salt_markers + ["water", "água"]),
    }


def _check_model_parameters_availability(
    components: List[str], 
    model: str
) -> Dict[str, Any]:
    """
    Verifica disponibilidade de parâmetros binários para o modelo.
    
    Returns:
        Dict com available (bool), missing_pairs (list), coverage (float 0-1)
    """
    # Simplificação: assumir que UNIFAC sempre disponível (grupos), 
    # outros modelos dependem de parâmetros binários
    
    if model == "UNIFAC":
        return {
            "available": True,
            "missing_pairs": [],
            "coverage": 1.0,
            "note": "UNIFAC é preditivo (não requer parâmetros binários)"
        }
    
    if model == "Ideal":
        return {
            "available": True,
            "missing_pairs": [],
            "coverage": 1.0,
            "note": "Modelo Ideal não requer parâmetros"
        }
    
    # Para NRTL/UNIQUAC: verificar se há dados (simulação via thermo library)
    # Na prática, isso deveria consultar banco de parâmetros
    # Aqui vamos usar heurística simples
    
    n = len(components)
    total_pairs = n * (n - 1) // 2
    
    # Heurística: sistemas com água ou compostos muito específicos 
    # podem não ter parâmetros
    analysis = _analyze_component_polarity(components)
    
    if analysis["has_salt"]:
        coverage = 0.3  # Sais geralmente têm poucos parâmetros
    elif analysis["has_polar"] and not analysis["all_organic"]:
        coverage = 0.7  # Água + orgânicos: cobertura moderada
    elif analysis["has_aromatic"] or analysis["has_aliphatic"]:
        coverage = 0.9  # Hidrocarbonetos: boa cobertura
    else:
        coverage = 0.6  # Casos gerais
    
    return {
        "available": coverage > 0.5,
        "missing_pairs": [],  # Não temos info detalhada aqui
        "coverage": coverage,
        "note": f"Cobertura estimada de parâmetros: {coverage*100:.0f}%"
    }


# ============================================================================
# RECOMENDAÇÃO DE MODELO (FUNÇÃO PRINCIPAL)
# ============================================================================

def recommend_model_for_esl(
    components: List[str], 
    calculation_type: str
) -> Dict[str, Any]:
    """
    Recomendação inteligente de modelo termodinâmico para ESL.

    Estratégias (em ordem de prioridade):
    1. **Historical**: Baseado em simulações anteriores bem-sucedidas
    2. **KB System**: Sistema eutético conhecido na base de conhecimento
    3. **Property-based**: Análise de propriedades ESL (Tm, ΔHfus, polaridade)
    4. **Rule-based**: Regras heurísticas gerais

    Args:
        components: Lista de nomes dos componentes
        calculation_type: 'solubility', 'crystallization', 'tx', 'ternary'

    Returns:
        Dict com:
        - recommended_model: string (modelo sugerido)
        - strategy: string (estratégia usada)
        - details: dict (razão, métricas, etc.)
        - recommended_models_for_components: list (outros modelos adequados)
        - best_components_for_model: list (exemplos por modelo)
        - recommended_ranges: dict (faixas de T recomendadas)
        - prefill: dict (valores padrão para T, x)
        - eutectic: dict (ponto eutético se conhecido)
        - parameter_availability: dict (disponibilidade de parâmetros)
    """
    components_norm = _normalize_components(components)
    
    # ------------------------------------------------------------------
    # ESTRATÉGIA 1: HISTÓRICO DE SIMULAÇÕES
    # ------------------------------------------------------------------
    historical_result = _recommend_from_history(components, components_norm, calculation_type)
    if historical_result:
        return _enrich_recommendation(historical_result, components_norm)
    
    # ------------------------------------------------------------------
    # ESTRATÉGIA 2: BASE DE CONHECIMENTO (SISTEMAS CLÁSSICOS)
    # ------------------------------------------------------------------
    kb_result = _recommend_from_kb(components_norm)
    if kb_result:
        return _enrich_recommendation(kb_result, components_norm)
    
    # ------------------------------------------------------------------
    # ESTRATÉGIA 3: BASEADO EM PROPRIEDADES ESL
    # ------------------------------------------------------------------
    property_result = _recommend_from_properties(components, components_norm)
    if property_result:
        return _enrich_recommendation(property_result, components_norm)
    
    # ------------------------------------------------------------------
    # ESTRATÉGIA 4: REGRAS HEURÍSTICAS GERAIS
    # ------------------------------------------------------------------
    rule_result = _recommend_from_rules(components, components_norm)
    return _enrich_recommendation(rule_result, components_norm)


# ============================================================================
# ESTRATÉGIAS DE RECOMENDAÇÃO
# ============================================================================

def _recommend_from_history(
    components: List[str],
    components_norm: List[str],
    calculation_type: str
) -> Optional[Dict[str, Any]]:
    """Recomendação baseada no histórico de simulações."""
    try:
        # Buscar no componente normalizado (aproximado)
        comp_pattern = '%'.join(components_norm[:2])  # Primeiros 2 componentes
        
        sims = (
            db.session.query(
                Simulation.model,
                func.count(Simulation.id).label('n'),
                func.avg(Simulation.execution_time).label('avg_time'),
                func.sum((Simulation.success == True).cast(db.Integer)).label('success_count'),
            )
            .filter(
                Simulation.module == 'esl',
                Simulation.calculation_type == calculation_type,
                Simulation.components.like(f'%{comp_pattern}%'),
            )
            .group_by(Simulation.model)
            .having(func.count(Simulation.id) >= 3)  # Mínimo 3 simulações
            .all()
        )

        if not sims:
            return None

        # Calcular success rate
        sims_with_rate = [
            {
                'model': s.model,
                'n': int(s.n),
                'avg_time': float(s.avg_time or 0),
                'success_count': int(s.success_count or 0),
                'success_rate': float(s.success_count or 0) / float(s.n) if s.n > 0 else 0
            }
            for s in sims
        ]

        # Ordenar por success rate e depois por tempo
        best = max(
            sims_with_rate,
            key=lambda s: (s['success_rate'], -s['avg_time']),
        )

        ordered = sorted(
            sims_with_rate,
            key=lambda s: (s['success_rate'], -s['avg_time']),
            reverse=True,
        )
        recommended_models_list = [s['model'] for s in ordered]

        return {
            "recommended_model": best['model'],
            "strategy": "historical",
            "details": {
                "success_rate": best['success_rate'],
                "avg_time": best['avg_time'],
                "samples": best['n'],
                "reason": (
                    f"Modelo {best['model']} tem {best['success_rate']*100:.1f}% de sucesso "
                    f"em {best['n']} simulações anteriores para este sistema ESL."
                ),
            },
            "recommended_models_for_components": recommended_models_list,
        }

    except Exception as e:
        print(f'[AI_ESL] Erro na consulta de histórico ESL: {e}')
        return None


def _recommend_from_kb(components_norm: List[str]) -> Optional[Dict[str, Any]]:
    """Recomendação baseada em sistemas eutéticos conhecidos."""
    kb_entry = _match_system_in_kb(components_norm)
    if not kb_entry:
        return None

    preferred = kb_entry.get("preferred_models") or ["UNIQUAC"]
    recommended_model = preferred[0]

    return {
        "recommended_model": recommended_model,
        "strategy": "kb_system",
        "details": {
            "reason": (
                f"Sistema eutético clássico: {kb_entry['label']}. "
                f"{kb_entry.get('notes', '')} "
                f"Referência: {kb_entry.get('reference', 'Literatura')}"
            )
        },
        "recommended_models_for_components": preferred,
        "recommended_ranges": kb_entry.get("recommended_ranges"),
        "prefill": kb_entry.get("prefill"),
        "eutectic": kb_entry.get("eutectic"),
    }


def _recommend_from_properties(
    components: List[str],
    components_norm: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Recomendação baseada em propriedades ESL (Tm, ΔHfus) dos componentes.
    Usa dados da base esl_data.py se disponível.
    """
    if not HAS_ESL_DATA:
        return None

    try:
        props_list = []
        for comp_name in components:
            props = _get_component_properties(comp_name)
            if props:
                props_list.append(props)
        
        if len(props_list) < len(components):
            # Nem todos componentes têm dados ESL
            return None
        
        # Analisar propriedades
        Tm_values = [p.get('Tm_C') for p in props_list if p.get('Tm_C')]
        Hfus_values = [p.get('Hfus_kJ_mol') for p in props_list if p.get('Hfus_kJ_mol')]
        
        if not Tm_values or not Hfus_values:
            return None
        
        # Calcular diferenças relativas
        Tm_range = max(Tm_values) - min(Tm_values)
        Tm_avg = sum(Tm_values) / len(Tm_values)
        Hfus_range = max(Hfus_values) - min(Hfus_values)
        
        # Heurísticas baseadas em Prausnitz:
        # - Tm similar + ΔHfus similar → comportamento mais ideal
        # - Grande diferença em Tm ou ΔHfus → não-idealidade
        
        Tm_similarity = Tm_range / Tm_avg if Tm_avg > 0 else 1.0
        
        analysis = _analyze_component_polarity(components)
        
        if Tm_similarity < 0.2 and analysis["all_organic"] and not analysis["has_acid"]:
            # Muito similar + orgânicos → Ideal
            recommended_model = "Ideal"
            reason = (
                f"Temperaturas de fusão similares (ΔTm={Tm_range:.1f}°C) e "
                f"componentes orgânicos não-polares sugerem comportamento próximo do ideal."
            )
            extra_models = ["Ideal", "UNIQUAC", "UNIFAC"]
            
        elif analysis["has_polar"] and not analysis["all_organic"]:
            # Polar + agua/inorgânico → NRTL
            recommended_model = "NRTL"
            reason = (
                "Sistema contém componentes polares com possível ligação de hidrogênio. "
                "NRTL captura bem interações específicas locais."
            )
            extra_models = ["NRTL", "UNIQUAC", "UNIFAC", "Ideal"]
            
        elif Tm_similarity > 0.5 or Hfus_range > 20:
            # Grande diferença → UNIQUAC (efeitos de tamanho)
            recommended_model = "UNIQUAC"
            reason = (
                f"Grande diferença nas temperaturas de fusão (ΔTm={Tm_range:.1f}°C) "
                f"ou entalpias (ΔHfus={Hfus_range:.1f} kJ/mol). "
                "UNIQUAC separa efeitos combinatoriais e energéticos."
            )
            extra_models = ["UNIQUAC", "NRTL", "UNIFAC", "Ideal"]
            
        else:
            # Caso intermediário → UNIQUAC
            recommended_model = "UNIQUAC"
            reason = (
                "Sistema com não-idealidade moderada. "
                "UNIQUAC oferece boa robustez para ESL."
            )
            extra_models = ["UNIQUAC", "NRTL", "UNIFAC", "Ideal"]
        
        # Faixas recomendadas baseadas em Tm
        T_min = min(Tm_values) - 20
        T_max = max(Tm_values) + 20
        
        return {
            "recommended_model": recommended_model,
            "strategy": "property_based",
            "details": {
                "reason": reason,
                "Tm_range_C": Tm_range,
                "Tm_avg_C": Tm_avg,
                "Hfus_range_kJ_mol": Hfus_range,
            },
            "recommended_models_for_components": extra_models,
            "recommended_ranges": {
                "temperature_C": {"min": T_min, "max": T_max},
            },
            "prefill": {
                "temperature_C": Tm_avg - 10,  # 10°C abaixo da média
                "liquid_compositions": [1.0/len(components)] * len(components),
            },
        }
        
    except Exception as e:
        print(f'[AI_ESL] Erro na análise de propriedades: {e}')
        return None


def _recommend_from_rules(
    components: List[str],
    components_norm: List[str]
) -> Dict[str, Any]:
    """
    Recomendação baseada em regras heurísticas gerais (fallback).
    Sempre retorna uma recomendação.
    """
    analysis = _analyze_component_polarity(components)
    
    if analysis["has_salt"]:
        base_model = "Ideal"
        reason = (
            "⚠️ Sistema contém eletrólitos (sais). "
            "O modelo Ideal NÃO é adequado para eletrólitos! "
            "Considere usar modelos específicos como Pitzer, eNRTL ou MSE se disponíveis. "
            "Para aproximação, NRTL pode ser usado com parâmetros ajustados."
        )
        extra_models = ["Ideal", "NRTL"]
        
    elif analysis["has_polar"] and analysis["has_aromatic"]:
        # Polar + aromático (ex: fenol-benzeno)
        base_model = "NRTL"
        reason = (
            "Mistura de componentes polares e aromáticos. "
            "NRTL captura bem interações específicas e não-aleatoriedade local."
        )
        extra_models = ["NRTL", "UNIQUAC", "UNIFAC", "Ideal"]
        
    elif analysis["all_organic"] and (analysis["has_aromatic"] or analysis["has_aliphatic"]):
        # Hidrocarbonetos puros
        base_model = "Ideal"
        reason = (
            "Sistema predominantemente de hidrocarbonetos aromáticos/alifáticos. "
            "Comportamento tende a ser próximo do ideal se moléculas forem similares."
        )
        extra_models = ["Ideal", "UNIQUAC", "UNIFAC"]
        
    elif analysis["has_acid"]:
        # Ácidos (podem dimerizar)
        base_model = "UNIQUAC"
        reason = (
            "Sistema contém ácidos carboxílicos. "
            "UNIQUAC ou NRTL são recomendados para capturar associação molecular."
        )
        extra_models = ["UNIQUAC", "NRTL", "UNIFAC", "Ideal"]
        
    else:
        # Caso mais genérico
        base_model = "UNIQUAC"
        reason = (
            "Sistema genérico sem características químicas marcantes. "
            "UNIQUAC oferece boa robustez para ampla faixa de misturas não-ideais em ESL. "
            "Se não houver parâmetros disponíveis, use UNIFAC (preditivo)."
        )
        extra_models = ["UNIQUAC", "UNIFAC", "NRTL", "Ideal"]
    
    # Faixas genéricas
    generic_ranges = {
        "temperature_C": {"min": 0.0, "max": 100.0},
    }
    
    n = max(1, len(components_norm))
    prefill = {
        "temperature_C": 25.0,
        "liquid_compositions": [1.0 / n for _ in range(n)],
    }
    
    return {
        "recommended_model": base_model,
        "strategy": "rule_based",
        "details": {
            "reason": reason,
            "chemical_analysis": analysis,
        },
        "recommended_models_for_components": extra_models,
        "recommended_ranges": generic_ranges,
        "prefill": prefill,
    }


# ============================================================================
# ENRIQUECIMENTO DA RECOMENDAÇÃO
# ============================================================================

def _enrich_recommendation(
    base_recommendation: Dict[str, Any],
    components_norm: List[str]
) -> Dict[str, Any]:
    """
    Enriquece recomendação com informações adicionais:
    - best_components_for_model (exemplos por modelo)
    - parameter_availability (disponibilidade de parâmetros)
    - eutectic (ponto eutético se disponível na base)
    """
    result = base_recommendation.copy()
    
    # Adicionar exemplos de sistemas por modelo
    if "best_components_for_model" not in result:
        result["best_components_for_model"] = BEST_COMPONENTS_FOR_MODEL_ESL
    
    # Verificar disponibilidade de parâmetros
    components_original = result.get("components_original", [])
    model = result.get("recommended_model", "Ideal")
    
    param_availability = _check_model_parameters_availability(
        components_original if components_original else list(components_norm),
        model
    )
    result["parameter_availability"] = param_availability
    
    # Tentar buscar sistema eutético na base de dados ESL
    if "eutectic" not in result and HAS_ESL_DATA:
        try:
            eutectic_systems = get_eutectic_systems()
            for sys in eutectic_systems:
                sys_comps_norm = _normalize_components(sys.get("components", []))
                if sys_comps_norm == components_norm:
                    result["eutectic"] = {
                        "T_C": sys.get("T_eutectic_C"),
                        "x1": sys.get("composition_eutectic", {}).get("x1"),
                    }
                    break
        except Exception as e:
            print(f'[AI_ESL] Erro ao buscar sistema eutético: {e}')
    
    return result


# ============================================================================
# ANÁLISE DE QUALIDADE DE RESULTADOS ESL
# ============================================================================

def analyze_esl_result_quality(
    results: Dict[str, Any],
    components: List[str],
    model: str
) -> Dict[str, Any]:
    """
    Analisa a qualidade dos resultados ESL baseado em critérios de Prausnitz.
    
    Returns:
        Dict com quality_score (0-1), issues (list), recommendations (list)
    """
    issues = []
    recommendations = []
    quality_score = 1.0
    
    # Verificar se gamma está razoável (0.01 < γ < 100 para maioria dos casos)
    for key, value in results.items():
        if key.startswith('gamma') and isinstance(value, (int, float)):
            if value < 0.01:
                issues.append(f"{key} muito baixo ({value:.4f}). Possível erro numérico.")
                quality_score -= 0.2
            elif value > 100:
                issues.append(f"{key} muito alto ({value:.2f}). Verificar parâmetros do modelo.")
                quality_score -= 0.2
    
    # Verificar solubilidade (x < 1 e x > 0)
    for key, value in results.items():
        if key.startswith('x') and '(' in key and isinstance(value, (int, float)):
            if value < 0 or value > 1:
                issues.append(f"Fração molar {key} fora da faixa física: {value:.4f}")
                quality_score -= 0.3
    
    # Recomendações baseadas no modelo
    if model == "Ideal" and len(issues) > 0:
        recommendations.append(
            "Modelo Ideal apresenta desvios. Considere usar NRTL ou UNIQUAC para este sistema."
        )
    
    if model in ["NRTL", "UNIQUAC"] and "parâmetros" in str(issues).lower():
        recommendations.append(
            "Parâmetros binários podem estar inadequados. "
            "Verifique a fonte dos parâmetros ou use UNIFAC (preditivo)."
        )
    
    quality_score = max(0.0, min(1.0, quality_score))
    
    return {
        "quality_score": quality_score,
        "issues": issues,
        "recommendations": recommendations,
        "overall_status": "good" if quality_score > 0.8 else "warning" if quality_score > 0.5 else "poor"
    }
