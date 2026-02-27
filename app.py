import streamlit as st
import math
import matplotlib.pyplot as plt
import networkx as nx
import random

# --- WEBPAGE CONFIG ---
st.set_page_config(
    page_title="Monotone Polygon Embedder", 
    layout="wide", # This uses the full width of your browser
    initial_sidebar_state="expanded"
)

# Custom CSS to add padding between elements
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stPlot {
        margin-bottom: 3rem;
    }
    </style>
    """, unsafe_allow_html=True) # <--- 'unsafe_allow_html' is the correct name

st.title("🛡️ Monotone Polygon Visibility Embedding")
st.write("Constructing planar monotone embeddings from random triangulations.")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Graph Controls")
    num_v = st.slider("Number of Vertices", 6, 12, 8)
    # Adding height control for presentation flexibility
    plot_height = st.slider("Plot Height", 5, 12, 8)
    st.divider()
    if st.button("🔄 Generate New Random Graph", use_container_width=True):
        st.rerun()

# --- THE ALGORITHM ---
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
        self.edges = {(1, 2)}

    def triangle(self, p_l, p_r, l, r):
        common = set(self.adj.get(l, [])).intersection(set(self.adj.get(r, [])))
        v = next((c for c in sorted(list(common)) if c not in self.marked), None)
def triangle(self, p_l, p_r, l, r):
        common = set(self.adj.get(l, [])).intersection(set(self.adj.get(r, [])))
        v = next((c for c in sorted(list(common)) if c not in self.marked), None)
        
        if v is not None:
            # Interpolation logic
            t = 0.8 if v == 4 else (0.2 if v == 6 else random.uniform(0.3, 0.7))
            mx = p_l[0] + (p_r[0] - p_l[0]) * t
            my = max(p_l[1], p_r[1]) + 2.5
            
            self.positions[v] = (mx, my)
            self.marked.add(v)
            
            # Add the two new triangle sides
            self.edges.add(tuple(sorted((l, v))))
            self.edges.add(tuple(sorted((v, r))))
            
            # Remove the base edge (except for the initial floor)
            if tuple(sorted((l, r))) != (1, 2):
                self.edges.discard(tuple(sorted((l, r))))

            # Recursive calls
            self.triangle(self.positions[l], (mx, my), l, v)
            self.triangle((mx, my), self.positions[r], v, r)

# --- EXECUTION ---
adj = generate_random_polygon_triangulation(num_v)
embedder = MonotoneEmbedder(adj)
embedder.triangle(embedder.positions[1], embedder.positions[2], 1, 2)

# --- LAYOUT & POLISHING ---
# We use a slight gap (gap="large") and specific column ratios
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📍 Topological Blueprint")
    st.info("The abstract graph structure before geometric embedding.")
    # Increasing figsize and using a clear layout
    fig1, ax1 = plt.subplots(figsize=(7, plot_height))
    G = nx.Graph(adj)
    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='#90ee90', 
            node_size=1000, edge_color='#666666', font_weight='bold', ax=ax1)
    st.pyplot(fig1)

with col2:
    st.subheader("📐 Monotone Embedding")
    st.success(f"Final monotone polygon with {num_v} vertices.")
    fig2, ax2 = plt.subplots(figsize=(7, plot_height))
    
    # Drawing edges
    for edge in embedder.edges:
        p1, p2 = embedder.positions[edge[0]], embedder.positions[edge[1]]
        ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', linewidth=2, zorder=1)
    
    # Drawing vertices
    for node, pos in embedder.positions.items():
        ax2.scatter(pos[0], pos[1], color='#1f77b4', s=250, edgecolors='black', zorder=2)
        ax2.text(pos[0]+0.3, pos[1], f"v{node}", fontsize=12, fontweight='bold')
    
    ax2.set_aspect('equal')
    ax2.axis('off')
    st.pyplot(fig2)
