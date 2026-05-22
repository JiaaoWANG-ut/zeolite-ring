import numpy as np
from pymatgen.core import Structure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_si_framework(cif_path, bond_cutoff=4.0, supercell=[1, 1, 1]):
    # Load structure
    struct = Structure.from_file(cif_path)
    
    # Create supercell if requested
    struct.make_supercell(supercell)
    
    # Extract only Si atoms
    si_indices = [i for i, site in enumerate(struct) if site.species_string == "Si"]
    si_sites = [struct[i] for i in si_indices]
    
    # Get coordinates
    coords = np.array([site.coords for site in si_sites])
    
    # Setup plot
    fig = plt.figure(figsize=(12, 10), dpi=150)
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot atoms
    # Using a nice color: 'royalblue' or 'deepskyblue'
    ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], 
               s=200, c='#4682B4', edgecolors='white', linewidth=0.5, alpha=0.9, label='Si')
    
    # Find and plot bonds
    num_si = len(si_sites)
    bonds_drawn = set()
    
    for i in range(num_si):
        # Use get_neighbors to find atoms within bond_cutoff
        # Since we are already in a supercell, we can search within the structure
        # But to be safe with PBC, we use the original structure's logic if needed.
        # However, for a simple visualization of a supercell, we can just compute distances between sites in the structure.
        
        # Using struct.get_neighbors on the current si_site
        site = si_sites[i]
        neighbors = struct.get_neighbors(site, r=bond_cutoff)
        
        for neighbor in neighbors:
            if neighbor.species_string == "Si":
                # Get coordinates of both ends
                c1 = site.coords
                c2 = neighbor.coords
                
                # Create a unique key for the bond to avoid double drawing
                bond_key = tuple(sorted([tuple(np.round(c1, 3)), tuple(np.round(c2, 3))]))
                
                if bond_key not in bonds_drawn:
                    ax.plot([c1[0], c2[0]], [c1[1], c2[1]], [c1[2], c2[2]], 
                            color='#708090', linewidth=2, alpha=0.6)
                    bonds_drawn.add(bond_key)

    # Aesthetics
    ax.set_axis_off()
    ax.set_title(f"Si Framework of {cif_path}\nBonds < {bond_cutoff}Å", fontsize=20, pad=10, fontname='DejaVu Sans', fontweight='bold')
    
    # Equal aspect ratio
    max_range = np.array([coords[:,0].max()-coords[:,0].min(), 
                          coords[:,1].max()-coords[:,1].min(), 
                          coords[:,2].max()-coords[:,2].min()]).max() / 2.0

    mid_x = (coords[:,0].max()+coords[:,0].min()) * 0.5
    mid_y = (coords[:,1].max()+coords[:,1].min()) * 0.5
    mid_z = (coords[:,2].max()+coords[:,2].min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    # Set background color
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    plt.tight_layout()
    output_path = "si_framework.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=False)
    # plt.show()  # Removed to avoid hanging in terminal
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    # Use a 2x2x2 supercell for a more complete framework visualization
    plot_si_framework("LTA.cif", bond_cutoff=4.0, supercell=[2, 2, 2])
