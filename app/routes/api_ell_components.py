from flask import Blueprint, jsonify
from pathlib import Path
import json

from app.utils.component_database import ComponentDatabase

bp = Blueprint('api_ell_components', __name__)
component_db = ComponentDatabase()


def _load_json_safe(path: Path):
    try:
        with path.open(encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


@bp.route('/api/ell/components/by-model/<model>', methods=['GET'])
def get_ell_components_by_model(model):
    """
    Listar componentes disponíveis para um modelo específico (ELL),
    usando exclusivamente os arquivos:
      - ell_nrtl_params.json
      - ell_uniquac_params.json
      - ell_unifac_params.json
    """
    try:
        model = model.upper()

        # IDEAL: todos os componentes do banco
        if model == 'IDEAL':
            all_comps = component_db.list_all_components()
            formatted = [_format_component(c) for c in all_comps]
            return jsonify({
                'success': True,
                'model': model,
                'components': formatted,
                'count': len(formatted),
                'total_available': len(all_comps),
            })

        # Caminho base do projeto (raiz)
        base_dir = Path(__file__).resolve().parents[2]

        all_comps = component_db.list_all_components()

        if model == 'NRTL':
            # ------------ ELL NRTL via CAS em ell_nrtl_params.json ------------
            ell_nrtl = _load_json_safe(base_dir / 'ell_nrtl_params.json')

            cas_with_nrtl = set()
            for key in ell_nrtl.keys():  # chaves tipo "CAS1__CAS2"
                try:
                    cas1, cas2 = key.split('__')
                    cas_with_nrtl.add(cas1.strip())
                    cas_with_nrtl.add(cas2.strip())
                except ValueError:
                    continue

            filtered = []
            for comp in all_comps:
                cas = str(comp.get('cas') or '').strip()
                if cas in cas_with_nrtl:
                    filtered.append(_format_component(comp))

            return jsonify({
                'success': True,
                'model': model,
                'components': filtered,
                'count': len(filtered),
                'total_available': len(all_comps),
            })

        elif model == 'UNIQUAC':
            # ------------ ELL UNIQUAC via CAS em data/ell_uniquac_params.py ----
            import sys

            data_dir = base_dir / 'data'
            if str(data_dir) not in sys.path:
                sys.path.insert(0, str(data_dir))

            try:
                from ell_uniquac_params import ELL_UNIQUAC_PARAMS, ELL_UNIQUAC_RQ
            except ImportError as e:
                return jsonify({
                    'success': False,
                    'model': model,
                    'components': [],
                    'count': 0,
                    'total_available': len(all_comps),
                    'error': f'Erro ao importar ell_uniquac_params.py: {e}',
                }), 500

            # CAS que aparecem em pares binários ou têm r,q definidos
            cas_with_uq = set()
            for cas1, cas2 in ELL_UNIQUAC_PARAMS.keys():
                cas_with_uq.add(str(cas1).strip())
                cas_with_uq.add(str(cas2).strip())
            for cas in ELL_UNIQUAC_RQ.keys():
                cas_with_uq.add(str(cas).strip())

            filtered = []
            for comp in all_comps:
                cas = str(comp.get('cas') or '').strip()
                if cas in cas_with_uq:
                    filtered.append(_format_component(comp))

            return jsonify({
                'success': True,
                'model': model,
                'components': filtered,
                'count': len(filtered),
                'total_available': len(all_comps),
            })


        elif model == 'UNIFAC':
            # ------------ ELL UNIFAC via CAS em ell_unifac_params.json --------
            ell_unifac = _load_json_safe(base_dir / 'ell_unifac_params.json')
            comp_groups = ell_unifac.get('component_groups', {})
            cas_with_unifac = {str(cas).strip() for cas in comp_groups.keys()}

            filtered = []
            for comp in all_comps:
                cas = str(comp.get('cas') or '').strip()
                if cas in cas_with_unifac:
                    filtered.append(_format_component(comp))

            return jsonify({
                'success': True,
                'model': model,
                'components': filtered,
                'count': len(filtered),
                'total_available': len(all_comps),
            })

        else:
            return jsonify({
                'success': False,
                'error': 'Modelo inválido. Use: IDEAL, NRTL, UNIQUAC ou UNIFAC',
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


def _format_component(comp: dict) -> dict:
    """Formato padrão usado no frontend (ELL/ELV)."""
    return {
        'name': comp['name'],
        'name_en': comp.get('name_en', comp['name']),
        'formula': comp['formula'],
        'cas': comp['cas'],
        'MW': comp['MW'],
        'Tb': comp['Tb'],
        'Tm': comp['Tm'],
        'Tc': comp['Tc'],
        'Pc': comp['Pc'],
        'Vc': comp.get('Vc'),
        'omega': comp['omega'],
        'dipole': comp.get('dipole'),
        'UNIFAC_R': comp.get('UNIFAC_R'),
        'UNIFAC_Q': comp.get('UNIFAC_Q'),
    }
