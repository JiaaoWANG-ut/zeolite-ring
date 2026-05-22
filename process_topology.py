import os
import json
import sys
import numpy as np
from pymatgen.core import Structure
from dataclasses import dataclass
from typing import List, Tuple

Shift = Tuple[int, int, int]

@dataclass(frozen=True)
class Edge:
    j: int
    offset: Shift

def _add_shift(a: Shift, b: Shift) -> Shift:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def _get_tt_adjacency(struct, cutoff=3.5) -> Tuple[List[List[Edge]], List[int]]:
    si_indices = [i for i, s in enumerate(struct) if s.species_string == "Si"]
    idx_map = {old: new for new, old in enumerate(si_indices)}
    n_si = len(si_indices)
    tt_adj = [[] for _ in range(n_si)]
    for i_local, i_orig in enumerate(si_indices):
        site = struct[i_orig]
        neighbors = struct.get_neighbors(site, r=cutoff)
        for nb in neighbors:
            if nb.species_string == "Si":
                tt_adj[i_local].append(Edge(j=idx_map[nb.index], offset=tuple(map(int, nb.image))))
    return tt_adj, si_indices

def find_rings_exhaustive(tt_adj, struct, si_indices, ring_size):
    unique_rings = []
    seen_canonical = set()
    n_si = len(si_indices)

    def process_found_ring(path):
        cycle_coords = []
        for idx, off in path:
            p = np.array(struct[si_indices[idx]].coords)
            p += np.dot(np.array(off), struct.lattice.matrix)
            cycle_coords.append(p)
        
        cycle_coords = np.array(cycle_coords)
        centered = cycle_coords - np.mean(cycle_coords, axis=0)
        _, s, vh = np.linalg.svd(centered)
        rms = np.sqrt(np.mean(np.dot(centered, vh[2])**2))
        
        # 原始较严格的平面性判据
        if rms > 0.2:
            return

        # 原始较严格的键角判据
        target_angle = 108.0 if ring_size == 5 else 120.0
        for i in range(ring_size):
            p_prev = cycle_coords[i-1]
            p_curr = cycle_coords[i]
            p_next = cycle_coords[(i+1)%ring_size]
            v1 = p_prev - p_curr
            v2 = p_next - p_curr
            cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
            if abs(angle - target_angle) > 20.0:
                return

        off0 = path[0][1]
        norm_nodes = []
        for idx, off in path:
            norm_nodes.append((idx, (off[0]-off0[0], off[1]-off0[1], off[2]-off0[2])))
        
        def get_canon(p):
            variants = []
            for i in range(len(p)):
                rot = p[i:] + p[:i]
                r_off0 = rot[0][1]
                v = tuple((idx, (o[0]-r_off0[0], o[1]-r_off0[1], o[2]-r_off0[2])) for idx, o in rot)
                variants.append(v)
                rev = rot[::-1]
                rv_off0 = rev[0][1]
                rv = tuple((idx, (o[0]-rv_off0[0], o[1]-rv_off0[1], o[2]-rv_off0[2])) for idx, o in rev)
                variants.append(rv)
            return min(variants)

        canon = get_canon(norm_nodes)
        if canon not in seen_canonical:
            seen_canonical.add(canon)
            unique_rings.append([{"idx": n[0], "offset": list(n[1])} for n in canon])

    for root_idx in range(n_si):
        root_node = (root_idx, (0, 0, 0))
        def dfs(curr_node, path):
            if len(path) == ring_size:
                curr_idx, curr_shift = curr_node
                for e in tt_adj[curr_idx]:
                    if (e.j, _add_shift(curr_shift, e.offset)) == root_node:
                        process_found_ring(list(path))
                return
            for e in tt_adj[curr_node[0]]:
                next_node = (e.j, _add_shift(curr_node[1], e.offset))
                if next_node not in path:
                    path.append(next_node)
                    dfs(next_node, path)
                    path.pop()
        dfs(root_node, [root_node])
    return unique_rings

def process_zeolite(cif_path):
    if not os.path.exists(cif_path): return
    struct = Structure.from_file(cif_path)
    tt_adj, si_indices = _get_tt_adjacency(struct)
    
    cycles5 = find_rings_exhaustive(tt_adj, struct, si_indices, 5)
    cycles6 = find_rings_exhaustive(tt_adj, struct, si_indices, 6)
    
    bonds = []
    for i in range(len(tt_adj)):
        for e in tt_adj[i]:
            if i < e.j or (i == e.j and any(o > 0 for o in e.offset)):
                bonds.append({"from": i, "to": e.j, "offset": list(e.offset)})

    output = {
        "lattice": struct.lattice.matrix.tolist(),
        "points": [s.coords.tolist() for s in struct if s.species_string == "Si"],
        "bonds": bonds,
        "cycles5": cycles5,
        "cycles6": cycles6
    }
    with open("topology.json", "w") as f: json.dump(output, f)
    print(f"DONE: {os.path.basename(cif_path)} (5MR: {len(cycles5)}, 6MR: {len(cycles6)})")

if __name__ == "__main__":
    process_zeolite(sys.argv[1] if len(sys.argv) > 1 else "LTA.cif")
