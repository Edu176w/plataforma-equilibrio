import json
from pathlib import Path

BASE = Path(r"venv/Lib/site-packages/thermo/Interaction Parameters/ChemSep")
UNIQUAC_FILE = BASE / "uniquac.json"
NRTL_FILE = BASE / "nrtl.json"

OUT_UNIQUAC = Path("ell_uniquac_params.json")
OUT_NRTL = Path("ell_nrtl_params.json")


def load_chemsep_data(path: Path):
    with open(path, "r") as f:
        obj = json.load(f)
    return obj["data"]  # dict: "CAS1 CAS2" -> {params}


def export_from(data: dict, out_path: Path):
    out = {}
    for key, rec in data.items():
        # key é algo como "67-56-1 7732-18-5"
        try:
            cas1, cas2 = key.split()
        except ValueError:
            # chave estranha, pula
            continue

        new_key = f"{cas1}__{cas2}"

        # copiar todos os campos do registro
        params = dict(rec)
        params["cas1"] = cas1
        params["cas2"] = cas2

        out[new_key] = params

    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Salvo {len(out)} pares em {out_path}")


def main():
    print("Lendo UNIQUAC ChemSep/thermo...")
    udata = load_chemsep_data(UNIQUAC_FILE)
    export_from(udata, OUT_UNIQUAC)

    print("Lendo NRTL ChemSep/thermo...")
    ndata = load_chemsep_data(NRTL_FILE)
    export_from(ndata, OUT_NRTL)


if __name__ == "__main__":
    main()
