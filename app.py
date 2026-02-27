import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import random
import math

# 1. SETUP PAGE
st.set_page_config(page_title="Monotone Polygon Embedder", layout="wide")

st.title("🛡️ Monotone Polygon Boundary Embedding")

# 2. SIDEBAR
with st.sidebar:
    st.header("Settings")
    num_v = st.slider("Number of Vertices", 6, 30, 9)
    plot_height = st.slider("Plot Height", 5, 12, 8)
    show_triangulation = st.checkbox("Show Internal Triangulation", value=False)
    if st.button("🔄 Generate New Random Graph", use_container_width=True):
        st.rerun()

# 3. ALGORITHM LOGIC
def generate_random_polygon_triangulation(n):
    adj = {1: [2], 2: [1]}
    boundary_edges = [(1, 2)]
    for i in range(3, n + 1):
        u, v = random.choice(boundary_edges)
        boundary_edges.remove((u, v))
        adj[i] = [u, v]
        adj[u].append(i)
        adj[v].append(i)
        boundary_edges.append((u, i))
        boundary_edges.append((i, v))
    return adj

class MonotoneEmbedder:
    def __init__(self, adj):
        self.adj = adj
        self.positions = {1: (0.0, 0.0), 2: (10.0, 0.0)}
        self.marked = {1, 2}
        self.all_edges = set()
        self.boundary_edges = {(1, 2)}

    def triangle(self, p_l, p_r, l, r):
        common = set(self.adj.get(l, [])).intersection(set(self.adj.get(r, [])))
        v = next((c for c in sorted(list(common)) if c not in self.marked), None)
        
        if v is not None:
            t = 0.8 if v == 4 else (0.2 if v == 6 else random.uniform(0.3, 0.7))
            mx = p_l[0] + (p_r[0] - p_l[0]) * t
            my = max(p_l[1], p_r[1]) + 2.5
            
            self.positions[v] = (mx, my)
            self.marked.add(v)
            
            if tuple(sorted((l, r))) != (1, 2):
                self.boundary_edges.discard(tuple(sorted((l, r))))
            
            self.boundary_edges.add(tuple(sorted((l, v))))
            self.boundary_edges.add(tuple(sorted((v, r))))
            self.all_edges.add(tuple(sorted((l, v))))
            self.all_edges.add(tuple(sorted((v, r))))
            self.all_edges.add(tuple(sorted((l, r))))

            self.triangle(self.positions[l], (mx, my), l, v)
            self.triangle((mx, my), self.positions[r], v, r)

# 4. RUN THE EMBEDDING
adj = generate_random_polygon_triangulation(num_v)
embedder = MonotoneEmbedder(adj)
embedder.triangle(embedder.positions[1], embedder.positions[2], 1, 2)

# 5. VISUALIZATION
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📍 Topological Blueprint")
    fig1, ax1 = plt.subplots(figsize=(7, plot_height))
    G = nx.Graph(adj)
    
    # Ordering nodes for the maximal outerplanar circle
    edge_map = {}
    for u, v in embedder.boundary_edges:
        edge_map.setdefault(u, []).append(v)
        edge_map.setdefault(v, []).append(u)
    
    curr, visited = 1, []
    for _ in range(len(adj)):
        visited.append(curr)
        neighbors = edge_map.get(curr, [])
        next_nodes = [n for n in neighbors if n not in visited]
        if not next_nodes: break
        curr = next_nodes[0]
    
   # Manual Circular Layout with organic jitter
    pos_circ = {}
    for i, node in enumerate(visited):
        # We add a tiny random offset to the angle and the radius
        # This keeps nodes on the "outside" but makes it look less robotic
        jitter_angle = random.uniform(-0.1, 0.1) 
        jitter_radius = random.uniform(0.9, 1.1)
        angle = (2 * math.pi * i / len(visited)) + jitter_angle
        pos_circ[node] = (jitter_radius * math.cos(angle), jitter_radius * math.sin(angle))
    
    nx.draw(G, pos_circ, with_labels=True, node_color='#90ee90', 
            edge_color='#dddddd', node_size=800, font_weight='bold', ax=ax1)
    nx.draw_networkx_edges(G, pos_circ, edgelist=list(embedder.boundary_edges), 
                           width=3, edge_color='black', ax=ax1)
    st.pyplot(fig1)

with col2:
    st.subheader("📐 Monotone Embedding")
    fig2, ax2 = plt.subplots(figsize=(7, plot_height))
    
    edges_to_draw = embedder.all_edges if show_triangulation else embedder.boundary_edges
    
    for edge in edges_to_draw:
        p1, p2 = embedder.positions[edge[0]], embedder.positions[edge[1]]
        is_boundary = edge in embedder.boundary_edges
        alpha_val = 1.0 if (not show_triangulation or is_boundary) else 0.2
        ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', linewidth=2, alpha=alpha_val)
    
    for node, pos in embedder.positions.items():
        ax2.scatter(pos[0], pos[1], color='#1f77b4', s=200, zorder=3)
        ax2.text(pos[0]+0.3, pos[1], f"v{node}", fontweight='bold')
        
    ax2.set_aspect('equal')
    ax2.axis('off')
    st.pyplot(fig2)
