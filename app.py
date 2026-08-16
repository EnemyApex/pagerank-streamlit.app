import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="PageRank Visualizer", layout="centered")
st.title("🚀 PageRank - Implémentation & Expérimentation")
st.write("Teste l'algorithme de Google depuis ton téléphone")

d = st.sidebar.slider("Facteur d'amortissement d", 0.5, 0.99, 0.85, 0.01)

option = st.selectbox("Choisis un graphe", ["Exemple Web", "Aléatoire 20 nœuds"])

if option == "Aléatoire 20 nœuds":
    G = nx.erdos_renyi_graph(20, 0.2, directed=True, seed=42)
else:
    G = nx.DiGraph()
    G.add_edges_from([('A','B'),('A','C'),('B','C'),('C','A'),('D','A'),('D','C')])

def pagerank(G, d=0.85, max_iter=50):
    N = G.number_of_nodes()
    pr = {n: 1/N for n in G.nodes()}
    for _ in range(max_iter):
        new_pr = {(1-d)/N : 0} # reset
        new_pr = {}
        for n in G.nodes():
            rank = (1-d)/N
            for pred in G.predecessors(n):
                rank += d * pr[pred] / max(1, G.out_degree(pred))
            new_pr[n] = rank
        pr = new_pr
    return pr

if st.button("Lancer PageRank"):
    scores = pagerank(G, d)

    st.subheader("Top Scores")
    for node, score in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:10]:
        st.write(f"**{node}** : `{score:.4f}`")

    fig, ax = plt.subplots()
    pos = nx.spring_layout(G)
    sizes = [scores[n]*8000 for n in G.nodes()]
    nx.draw(G, pos, ax=ax, with_labels=True, node_size=sizes, node_color=list(scores.values()), cmap='Blues')
    st.pyplot(fig)
