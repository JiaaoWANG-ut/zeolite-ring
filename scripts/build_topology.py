#!/usr/bin/env python3
"""Batch precompute topology JSON for every CIF in all-cif/."""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIF_DIR = os.path.join(ROOT, "all-cif")
OUT_DIR = os.path.join(ROOT, "data", "topology")
TOPOLOGY_TMP = os.path.join(ROOT, "topology.json")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    cifs = sorted(f for f in os.listdir(CIF_DIR) if f.endswith(".cif"))
    total = len(cifs)
    failed = []

    for i, cif in enumerate(cifs, start=1):
        name = cif.replace(".cif", "")
        out_path = os.path.join(OUT_DIR, f"{name}.json")

        if os.path.exists(out_path):
            print(f"[{i}/{total}] SKIP {name}")
            continue

        cif_path = os.path.join(CIF_DIR, cif)
        try:
            subprocess.run(
                [sys.executable, os.path.join(ROOT, "process_topology.py"), cif_path],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            with open(TOPOLOGY_TMP, encoding="utf-8") as handle:
                data = json.load(handle)
            with open(out_path, "w", encoding="utf-8") as handle:
                json.dump(data, handle)
            print(f"[{i}/{total}] DONE {name}")
        except subprocess.CalledProcessError as exc:
            failed.append(name)
            print(f"[{i}/{total}] FAIL {name}: {exc.stderr or exc}")

    if failed:
        print(f"\nFailed ({len(failed)}): {', '.join(failed)}")
        sys.exit(1)

    print(f"\nBuild complete: {total} frameworks in {OUT_DIR}")


if __name__ == "__main__":
    main()
