import streamlit as st
import math
import matplotlib.pyplot as plt
import networkx as nx
import random

# --- WEBPAGE CONFIG ---
st.set_page_config(page_title="Monotone Polygon Embedder", layout="wide")

st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stPlot { margin-bottom: 3rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Monotone Polygon Visibility Embedding")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    num_v = st.slider("Number of Vertices", 6, 12, 8)
    plot_height = st.slider("Plot Height", 5, 12, 8)
    if st.button("🔄 Generate New Random Graph", use_container_width=True):
        st.rerun()

# --- GENERATOR ---
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

# --- EMBEDDER ---
class MonotoneEmbedder:
    def __init__(self, adj):
        self.adj = adj  # We use this for logic
        self.positions = {1: (0.0, 0.0), 2: (10.0, 0.0)}
        self.marked = {1, 2}
        self.draw_edges = {(1, 2)} # We use this only for drawing

    def triangle(self, p_l, p_r, l, r):
        # Look at the ORIGINAL graph for neighbors
        common = set(self.adj.get(l, [])).intersection(set(self.adj.get(r, [])))
        v = next((c for c in sorted(list(common)) if c not in self.marked), None)
        
        if v is not None:
            # Interpolation logic
            t = 0.8 if v == 4 else (0.2 if v == 6 else random.uniform(0.3, 0.7))
            mx = p_l[0] + (p_r[0] - p_l[0]) * t
            my = max(p_l[1], p_r[1]) + 2.5
            
            self.positions[v] = (mx, my)
            self.marked.add(v)
            
            # Add new edges to drawing set
            self.draw_edges.add(tuple(sorted((l, v))))
            self.draw_edges.add(tuple(sorted((v, r))))
            
            # Recurse into the two new triangles
            self.triangle(self.positions[l], (mx, my), l, v)
            self.triangle((mx, my), self.positions[r], v, r)

# --- RUN ---
adj = generate_random_polygon_triangulation(num_v)
embedder = MonotoneEmbedder(adj)
embedder.triangle(embedder.positions[1], embedder.positions[2], 1, 2)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📍 Topological Blueprint")
    fig1, ax1 = plt.subplots(figsize=(7, plot_height))
    G = nx.Graph(adj)
    nx.draw(G, nx.spring_layout(G), with_labels=True, node_color='#90ee90', ax=ax1)
    st.pyplot(fig1)

with col2:
    st.subheader("📐 Monotone Embedding")
    fig2, ax2 = plt.subplots(figsize=(7, plot_height))
    # Draw all edges from the drawing set
    for edge in embedder.draw_edges:
        p1, p2 = embedder.positions[edge[0]], embedder.positions[edge[1]]
        ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', linewidth=2)
    for node, pos in embedder.positions.items():
        ax2.scatter(pos[0], pos[1], color='#1f77b4', s=200, zorder=3)
        ax2.text(pos[0]+0.3, pos[1], f"v{node}", fontweight='bold')
    ax2.set_aspect('equal')
    ax2.axis('off')
    st.pyplot(fig2)
