import os
import json
import numpy as np
from pymatgen.core import Structure
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Edge:
    j: int
    offset: Tuple[int, int, int]

def _add_shift(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def get_ring_counts(cif_path):
    try:
        struct = Structure.from_file(cif_path)
    except: return 0, 0
    si_indices = [i for i, s in enumerate(struct) if s.species_string == "Si"]
    idx_map = {old: new for new, old in enumerate(si_indices)}
    n_si = len(si_indices)
    tt_adj = [[] for _ in range(n_si)]
    for i_local, i_orig in enumerate(si_indices):
        site = struct[i_orig]
        neighbors = struct.get_neighbors(site, r=3.5)
        for nb in neighbors:
            if nb.species_string == "Si":
                tt_adj[i_local].append(Edge(j=idx_map[nb.index], offset=tuple(map(int, nb.image))))
    
    results = {}
    for size in [5, 6]:
        found = 0
        seen = set()
        target_angle = 108.0 if size == 5 else 120.0
        for root_idx in range(n_si):
            root_node = (root_idx, (0, 0, 0))
            def dfs(curr_node, path):
                nonlocal found
                if len(path) == size:
                    for e in tt_adj[curr_node[0]]:
                        if (e.j, _add_shift(curr_node[1], e.offset)) == root_node:
                            coords = []
                            for idx, off in path:
                                p = np.array(struct[si_indices[idx]].coords)
                                p += np.dot(np.array(off), struct.lattice.matrix)
                                coords.append(p)
                            coords = np.array(coords)
                            centered = coords - np.mean(coords, axis=0)
                            _, s, vh = np.linalg.svd(centered)
                            if np.sqrt(np.mean(np.dot(centered, vh[2])**2)) < 0.2:
                                ok = True
                                for i in range(size):
                                    v1 = coords[i-1] - coords[i]
                                    v2 = coords[(i+1)%size] - coords[i]
                                    angle = np.degrees(np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))))
                                    if abs(angle - target_angle) > 20.0: ok = False; break
                                if ok:
                                    canon = tuple(sorted([p[0] for p in path]))
                                    if canon not in seen:
                                        seen.add(canon); found += 1
                    return
                if found > 20: return
                for e in tt_adj[curr_node[0]]:
                    next_node = (e.j, _add_shift(curr_node[1], e.offset))
                    if next_node not in path:
                        path.append(next_node); dfs(next_node, path); path.pop()
            dfs(root_node, [root_node])
        results[size] = found
    return results[5], results[6]

def main():
    cif_dir = "all-cif"
    metadata = {}
    files = [f for f in os.listdir(cif_dir) if f.endswith(".cif")]
    for i, filename in enumerate(files):
        r5, r6 = get_ring_counts(os.path.join(cif_dir, filename))
        metadata[filename.replace(".cif", "")] = {"rings5": r5, "rings6": r6, "rings": r6} # keep 'rings' for backward compat
        if i % 20 == 0: print(f"Progress: {i}/{len(files)}...")
    with open("zeolite_metadata.json", "w") as f: json.dump(metadata, f)
    print("Pre-scan complete.")

if __name__ == "__main__": main()
