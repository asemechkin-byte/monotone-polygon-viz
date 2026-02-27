import streamlit as st
import math
import matplotlib.pyplot as plt
import networkx as nx
import random

# --- WEBPAGE CONFIG ---
st.set_page_config(page_title="Monotone Polygon Embedder", layout="wide")
st.title("🛡️ Monotone Polygon Visibility Embedding")
st.markdown("This tool generates a random triangulated graph and embeds it as a monotone polygon step-by-step.")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Settings")
    num_v = st.slider("Number of Vertices", 6, 12, 8)
    if st.button("Generate New Random Graph"):
        st.rerun()

# --- THE ALGORITHM (Simplified for the Web) ---
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
        if v is not None:
            t = random.uniform(0.3, 0.7)
            mx = p_l[0] + (p_r[0] - p_l[0]) * t
            my = max(p_l[1], p_r[1]) + 2.5
            self.positions[v] = (mx, my)
            self.marked.add(v)
            if tuple(sorted((l, r))) != (1, 2):
                self.edges.discard(tuple(sorted((l, r))))
            self.edges.add(tuple(sorted((l, v))))
            self.edges.add(tuple(sorted((v, r))))
            self.triangle(self.positions[l], (mx, my), l, v)
            self.triangle((mx, my), self.positions[r], v, r)

# --- EXECUTION AND DISPLAY ---
adj = generate_random_polygon_triangulation(num_v)
embedder = MonotoneEmbedder(adj)
embedder.triangle(embedder.positions[1], embedder.positions[2], 1, 2)

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Topological Blueprint")
    fig1, ax1 = plt.subplots()
    G = nx.Graph(adj)
    nx.draw(G, nx.spring_layout(G), with_labels=True, node_color='lightgreen', ax=ax1)
    st.pyplot(fig1)

with col2:
    st.subheader("2. Final Geometric Embedding")
    fig2, ax2 = plt.subplots()
    for edge in embedder.edges:
        p1, p2 = embedder.positions[edge[0]], embedder.positions[edge[1]]
        ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], 'black', linewidth=1.5)
    for node, pos in embedder.positions.items():
        ax2.scatter(pos[0], pos[1], color='dodgerblue', s=100)
        ax2.text(pos[0]+0.2, pos[1], str(node))
    ax2.set_aspect('equal')
    ax2.axis('off')
    st.pyplot(fig2)
