import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import random
import math  # Added to fix the math.pi error

# --- WEBPAGE CONFIG ---
st.set_page_config(page_title="Monotone Polygon Embedder", layout="wide")

st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stPlot { margin-bottom: 3rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Monotone Polygon Boundary Embedding")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    num_v = st.slider("Number of Vertices", 6, 30, 9) # Range 6-30, Default 9
    plot_height = st.slider("Plot Height", 5, 12, 8)
    show_triangulation = st.checkbox("Show Internal Triangulation", value=False)
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

# --- EXECUTION ---
adj = generate_random_polygon_triangulation(num_v)
embedder = MonotoneEmbedder(adj)
embedder.triangle(embedder.positions[1], embedder.positions[2], 1, 2)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📍 Topological Blueprint")
    fig1, ax1 = plt.subplots(figsize=(7, plot_height))
    G = nx.Graph(adj)
    
    # Walk the boundary to ensure a Crossing-Free (Outerplanar) drawing
    edge_map = {}
    for u, v in embedder.boundary_edges:
        edge_map.setdefault(u, []).append(v)
        edge_map.setdefault(v, []).append(u)
    
    curr, visited = 1, []
    for _ in range(len(adj)):
        visited
